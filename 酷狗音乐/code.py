import os
import socket
from pathlib import Path

import requests


PROXY_HOST = "127.0.0.1"
PROXY_PORT = 6789
PROXY_HTTP = f"http://{PROXY_HOST}:{PROXY_PORT}"
PROXY_SOCKS = f"socks5://{PROXY_HOST}:{PROXY_PORT}"

URL = (
    "https://webfs.kugou.com/202607251353/"
    "a1477579a1a54a19c357a6c66709bf76/v3/"
    "b7f1bbbc3003e84b154c66686ccc3741/yp/full/"
    "ap1014_us642977047_mii0w1iw8z2ai2iphcu80ooo2ki81120_"
    "pi406_mx937410822_s3385672614.mp3"
)
OUTPUT_FILE = Path(__file__).with_name("下载音乐.mp3")

HEADERS = {
    "sec-ch-ua-platform": '"Windows"',
    "Referer": "https://www.kugou.com/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    ),
    "sec-ch-ua": (
        '"Not;A=Brand";v="8", "Chromium";v="150", '
        '"Google Chrome";v="150"'
    ),
    "Range": "bytes=0-",
    "sec-ch-ua-mobile": "?0",
}


def configure_proxy() -> None:
    """为 requests 及其子进程配置本地 Clash/Mihomo 代理。"""
    proxy_variables = {
        "HTTP_PROXY": PROXY_HTTP,
        "HTTPS_PROXY": PROXY_HTTP,
        "ALL_PROXY": PROXY_SOCKS,
        "NO_PROXY": "localhost,127.0.0.1,::1",
        "http_proxy": PROXY_HTTP,
        "https_proxy": PROXY_HTTP,
        "all_proxy": PROXY_SOCKS,
        "no_proxy": "localhost,127.0.0.1,::1",
    }
    os.environ.update(proxy_variables)

    try:
        with socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=2):
            pass
    except OSError as exc:
        raise RuntimeError(
            f"本地代理 {PROXY_HOST}:{PROXY_PORT} 不可用，已停止下载。"
        ) from exc


def download_mp3(url: str, output_file: Path) -> None:
    """流式下载 MP3，完成后再把临时文件替换为正式文件。"""
    temporary_file = output_file.with_suffix(output_file.suffix + ".part")

    try:
        with requests.get(
            url,
            headers=HEADERS,
            proxies={"http": PROXY_HTTP, "https": PROXY_HTTP},
            stream=True,
            timeout=(10, 30),
        ) as response:
            response.raise_for_status()

            with temporary_file.open("wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        file.write(chunk)

        if temporary_file.stat().st_size == 0:
            raise RuntimeError("下载结果为空，未生成 MP3 文件。")

        temporary_file.replace(output_file)
        size_mb = output_file.stat().st_size / 1024 / 1024
        print(f"下载完成：{output_file}（{size_mb:.2f} MB）")
    except Exception:
        temporary_file.unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    configure_proxy()
    download_mp3(URL, OUTPUT_FILE)
