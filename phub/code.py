import requests

url = (
    "https://hv-h.phncdn.com/hls/c6251/videos/202607/31/57289955/"
    "720P_4000K_57289955.mp4/index-v1-a1.m3u8"
    "?h=fk%2FAZZqV%2BABg4lqahyyZIfzMQ9c%3D&e=1786464624&f=1"
)

headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "origin": "https://cn.pornhub.com",
    "priority": "u=1, i",
    "referer": "https://cn.pornhub.com/",
    "sec-ch-ua": '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
}

response = requests.get(url, headers=headers, timeout=30)
response.raise_for_status()

print(response.text)