import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

import requests
from tqdm import tqdm

try:
    from Crypto.Cipher import AES  # pycryptodome
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


HEADERS = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "priority": "i",
    "range": "bytes=0-",
    "referer": "https://www.cupfox.in/",
    "sec-ch-ua": "\"Google Chrome\";v=\"149\", \"Chromium\";v=\"149\", \"Not)A;Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "video",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "cross-site",
    "sec-fetch-storage-access": "active",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
}

# 网络波动重试配置
MAX_RETRIES = 8          # 单个分片最大重试次数
RETRY_BACKOFF = 1.5      # 退避基数（秒），每次乘以该系数
RETRY_STATUS = (408, 429, 500, 502, 503, 504)
TIMEOUT = (10, 30)       # (连接, 读取)
CONCURRENCY = 16         # 分片并发下载数


def make_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def fetch_text(session, url):
    """带重试地获取文本内容（m3u8 播放列表 / 密钥）。"""
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = session.get(url, timeout=TIMEOUT)
            if r.status_code in RETRY_STATUS or r.status_code >= 500:
                raise requests.HTTPError(f"status {r.status_code}", response=r)
            r.raise_for_status()
            return r.text
        except Exception as e:
            last_err = e
            wait = RETRY_BACKOFF ** attempt
            print(f"  [重试 {attempt}/{MAX_RETRIES}] {url} -> {e}，{wait:.1f}s 后重试",
                  file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"获取失败: {url} -> {last_err}")


def parse_m3u8(text, base_url):
    """解析 m3u8，返回 (变体列表, 分片列表, 加密信息)。

    变体列表: [(bandwidth, uri)] —— 仅主播放列表非空
    分片列表: [uri]
    加密信息: dict 或 None
    """
    variants = []
    segments = []
    key_info = None
    cur_key = None

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            if line.startswith("#EXT-X-STREAM-INF"):
                m = re.search(r"BANDWIDTH=(\d+)", line)
                bandwidth = int(m.group(1)) if m else 0
                # URI 在下一行
                cur_key = ("variant", bandwidth)
            elif line.startswith("#EXT-X-KEY"):
                method = re.search(r'METHOD="?([^,]+)"?', line)
                uri = re.search(r'URI="([^"]+)"', line)
                iv = re.search(r"IV=0x([0-9a-fA-F]+)", line)
                if method and method.group(1) != "NONE":
                    key_info = {
                        "method": method.group(1),
                        "uri": uri.group(1) if uri else None,
                        "iv": bytes.fromhex(iv.group(1)) if iv else None,
                    }
            continue
        # 非 # 开头 -> 是一个 URI
        if cur_key and cur_key[0] == "variant":
            variants.append((cur_key[1], urljoin(base_url, line)))
            cur_key = None
        else:
            segments.append(urljoin(base_url, line))

    return variants, segments, key_info


def get_media_playlist(session, url):
    """若为主播放列表则取最高码率变体，返回媒体播放列表文本与其 URL。"""
    text = fetch_text(session, url)
    variants, segments, key_info = parse_m3u8(text, url)
    if variants:  # 主播放列表 -> 选最高码率
        variants.sort(reverse=True)
        chosen = variants[0][1]
        print(f"主播放列表，选择最高码率变体: {chosen}")
        return get_media_playlist(session, chosen)
    return text, url, segments, key_info


def download_segment(session, url, key_cipher_iv):
    """下载单个分片，带重试与退避；若加密则解密。返回 bytes 或 None（彻底失败）。"""
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = session.get(url, timeout=TIMEOUT)
            if r.status_code in RETRY_STATUS or r.status_code >= 500:
                raise requests.HTTPError(f"status {r.status_code}")
            r.raise_for_status()
            data = r.content
            if key_cipher_iv is not None:
                cipher, iv = key_cipher_iv
                if iv is None:
                    # IV 默认为分片序号——此处无法得知序号，退回使用全 0
                    iv = b"\x00" * 16
                data = cipher.decrypt(data)
            return data
        except Exception as e:
            last_err = e
            wait = min(RETRY_BACKOFF ** attempt, 30)
            time.sleep(wait)
    print(f"  [放弃] {url} -> {last_err}", file=sys.stderr)
    return None


def resolve_key(session, key_info):
    """获取解密密钥，返回 (cipher, iv) 或 None。"""
    if not key_info or key_info["method"] != "AES-128":
        return None
    if not HAS_CRYPTO:
        raise RuntimeError("流已加密(AES-128)，需安装 pycryptodome: pip install pycryptodome")
    key = bytes.fromhex(fetch_text(session, urljoin("", key_info["uri"])).strip())
    # key_info["uri"] 可能是相对路径，需要基于播放列表 URL 解析——交由调用方
    cipher = AES.new(key, AES.MODE_CBC)
    return (cipher, key_info["iv"])


def download_m3u8(url, output_path, concurrency=CONCURRENCY):
    session = make_session()
    print(f"获取播放列表: {url}")
    text, media_url, segments, key_info = get_media_playlist(session, url)
    print(f"共 {len(segments)} 个分片")

    if not segments:
        print("未找到分片，退出")
        return

    # 解析密钥 URI 基于媒体播放列表 URL
    cipher_iv = None
    if key_info:
        if key_info["uri"]:
            key_url = urljoin(media_url, key_info["uri"])
            key_info["uri"] = key_url
        cipher_iv = resolve_key(session, key_info)

    results = [None] * len(segments)
    failed = []

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        future_to_idx = {
            pool.submit(download_segment, session, seg, cipher_iv): i
            for i, seg in enumerate(segments)
        }
        with tqdm(total=len(segments), unit="seg", desc="下载") as bar:
            for fut in as_completed(future_to_idx):
                idx = future_to_idx[fut]
                data = fut.result()
                if data is None:
                    failed.append(idx)
                else:
                    results[idx] = data
                bar.update(1)

    if failed:
        print(f"警告: {len(failed)} 个分片下载失败: {failed}", file=sys.stderr)

    # 合并写入
    print(f"合并写入: {output_path}")
    tmp_path = output_path + ".tmp"
    with open(tmp_path, "wb") as f:
        for i in range(len(segments)):
            if results[i] is not None:
                f.write(results[i])

    # 尝试用 ffmpeg 转封装为 mp4；失败则直接改名
    remuxed = try_ffmpeg_remux(tmp_path, output_path)
    if not remuxed:
        os.replace(tmp_path, output_path)
        print("（未找到 ffmpeg，已直接合并为 .mp4；多数播放器可正常播放）")
    else:
        os.remove(tmp_path)
    print(f"完成: {output_path}")


def try_ffmpeg_remux(ts_path, mp4_path):
    """用 ffmpeg 将 ts 流复制封装为 mp4（无需重编码）。成功返回 True。"""
    import shutil
    import subprocess
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return False
    try:
        subprocess.run(
            [ffmpeg, "-y", "-i", ts_path, "-c", "copy", "-bsf:a", "aac_adtstoasc",
             mp4_path],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return True
    except Exception:
        return False


if __name__ == "__main__":
    M3U8_URL = "https://v.lzcdn31.com/20260422/5613_6cd2d9fa/2000k/hls/mixed.m3u8"
    OUTPUT = "output.mp4"
    download_m3u8(M3U8_URL, OUTPUT)
