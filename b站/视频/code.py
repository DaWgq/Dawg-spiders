import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import requests


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "origin": "https://www.bilibili.com",
    "priority": "u=1, i",
    "referer": "https://www.bilibili.com/video/BV1y9JnzvEoL/?buvid=13dd75066116875017419915f8f60436&is_story_h5=false&mid=EiDvC%2Fdkv2ukZOZSafkd%2BQ%3D%3D&plat_id=114&share_from=ugc&share_medium=iphone&share_plat=ios&share_session_id=00CFC925-DE97-4AFE-896E-09FD5A9BDF83&share_source=weixin&share_tag=s_i&spmid=united.player-video-detail.0.0&timestamp=1785080051&unique_k=DTTRYNx&up_id=3546717332965403&vd_source=3456678bb253224e626749aced66d92d",
    "sec-ch-ua": "\"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"150\", \"Google Chrome\";v=\"150\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
}
url = "https://upos-sz-mirrorbd.bilivideo.com/upgcxcode/51/65/30082466551/30082466551-1-100029.m4s"
params = {
    "e": "ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=",
    "oi": "236137712",
    "gen": "playurlv3",
    "os": "bdbv",
    "og": "hw",
    "trid": "a4fd96fcc7d7422b8199465b5533159u",
    "uipk": "5",
    "mid": "437579001",
    "platform": "pc",
    "deadline": "1785142821",
    "nbs": "1",
    "upsig": "d41cbd90f89af0b4a258963496a4e15b",
    "uparams": "e,oi,gen,os,og,trid,uipk,mid,platform,deadline,nbs",
    "bvc": "vod",
    "nettype": "0",
    "bw": "1917199",
    "lrs": "-1",
    "agrr": "1",
    "buvid": "56FEC1DF-5748-D67A-3738-6FB0C2A211B897753infoc",
    "build": "0",
    "dl": "0",
    "f": "u_0_0",
    "qn_dyeid": "21f71f93fa48344000ff73006a670205",
    "orderid": "0,3"
}

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 6789
HTTP_PROXY = f"http://{PROXY_HOST}:{PROXY_PORT}"
SOCKS_PROXY = f"socks5://{PROXY_HOST}:{PROXY_PORT}"
CHUNK_SIZE = 1024 * 1024
MAX_RETRIES = 1000
RETRY_DELAY_SECONDS = 3


def configure_proxy():
    try:
        with socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=2):
            pass
    except OSError as exc:
        raise RuntimeError(
            f"本地代理 {PROXY_HOST}:{PROXY_PORT} 不可用，已停止下载。"
        ) from exc

    proxy_environment = {
        "HTTP_PROXY": HTTP_PROXY,
        "HTTPS_PROXY": HTTP_PROXY,
        "ALL_PROXY": SOCKS_PROXY,
        "NO_PROXY": "localhost,127.0.0.1,::1",
        "http_proxy": HTTP_PROXY,
        "https_proxy": HTTP_PROXY,
        "all_proxy": SOCKS_PROXY,
        "no_proxy": "localhost,127.0.0.1,::1",
    }
    os.environ.update(proxy_environment)

    return {
        "http": HTTP_PROXY,
        "https": HTTP_PROXY,
    }


def print_download_progress(downloaded, total, started_at, session_start):
    elapsed = max(time.monotonic() - started_at, 0.001)
    speed = (downloaded - session_start) / elapsed / 1024 / 1024

    if total > 0:
        bar_width = 40
        ratio = min(downloaded / total, 1)
        completed = int(bar_width * ratio)
        progress_bar = "█" * completed + "░" * (bar_width - completed)
        message = (
            f"\r[{progress_bar}] {ratio:6.2%}  "
            f"{downloaded / 1024 / 1024:.2f}/{total / 1024 / 1024:.2f} MB  "
            f"{speed:.2f} MB/s"
        )
    else:
        message = (
            f"\r已下载 {downloaded / 1024 / 1024:.2f} MB  "
            f"{speed:.2f} MB/s"
        )

    sys.stdout.write(message)
    sys.stdout.flush()


def download_video(source_file):
    downloaded_size = source_file.stat().st_size if source_file.exists() else 0
    total_size = 0
    retry_count = 0
    started_at = time.monotonic()
    session_start = downloaded_size

    if downloaded_size:
        print(f"发现未完成文件，将从 {downloaded_size / 1024 / 1024:.2f} MB 处继续下载。")

    while True:
        # 每次请求（包括重试）前都重新确认本地代理可用。
        proxies = configure_proxy()
        request_headers = headers.copy()
        if downloaded_size:
            request_headers["Range"] = f"bytes={downloaded_size}-"

        try:
            with requests.get(
                url,
                headers=request_headers,
                params=params,
                proxies=proxies,
                stream=True,
                timeout=(10, 60),
            ) as response:
                response.raise_for_status()

                if downloaded_size and response.status_code == 206:
                    content_range = response.headers.get("content-range", "")
                    if "/" in content_range:
                        total_text = content_range.rsplit("/", 1)[1]
                        if total_text.isdigit():
                            total_size = int(total_text)
                    file_mode = "ab"
                else:
                    # 服务器不支持断点续传时，只能重新下载，避免拼出损坏文件。
                    if downloaded_size:
                        print("\n服务器未接受断点续传，将从头重新下载。")
                    downloaded_size = 0
                    session_start = 0
                    started_at = time.monotonic()
                    total_size = int(response.headers.get("content-length", 0))
                    file_mode = "wb"

                if total_size == 0:
                    remaining_size = int(response.headers.get("content-length", 0))
                    if remaining_size:
                        total_size = downloaded_size + remaining_size

                with source_file.open(file_mode) as file:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            file.write(chunk)
                            downloaded_size += len(chunk)
                            print_download_progress(
                                downloaded_size,
                                total_size,
                                started_at,
                                session_start,
                            )

            if total_size and downloaded_size < total_size:
                raise requests.exceptions.ConnectionError(
                    f"连接提前结束，尚缺少 {total_size - downloaded_size} 字节"
                )

            print()
            return

        except requests.exceptions.HTTPError:
            # 403、404 等 HTTP 错误通常不是网络波动，继续重试没有意义。
            print()
            raise
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.ChunkedEncodingError,
        ) as exc:
            retry_count += 1
            print(
                f"\n网络连接中断：{exc}\n"
                f"已保留下载进度，准备重试（{retry_count}/{MAX_RETRIES}）……"
            )
            if retry_count >= MAX_RETRIES:
                raise RuntimeError(
                    f"连续重试 {MAX_RETRIES} 次仍然失败，"
                    f"临时文件已保留在：{source_file}"
                ) from exc

            # 网络异常后立即重新验证代理；代理不可用时按策略直接停止。
            configure_proxy()
            time.sleep(RETRY_DELAY_SECONDS)
            downloaded_size = source_file.stat().st_size
            session_start = downloaded_size
            started_at = time.monotonic()


def download_and_convert():
    work_dir = Path(__file__).resolve().parent
    source_file = work_dir / "downloaded_video.m4s"
    output_file = work_dir / "downloaded_video.mp4"

    print("正在下载视频流……")
    download_video(source_file)

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError(
            f"下载完成：{source_file}\n"
            "但未找到 FFmpeg，安装 FFmpeg 后才能转换为 MP4。"
        )

    print("正在转换为 MP4……")
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(source_file),
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(output_file),
        ],
        check=True,
    )

    source_file.unlink()
    print(f"转换完成：{output_file}")


if __name__ == "__main__":
    download_and_convert()
