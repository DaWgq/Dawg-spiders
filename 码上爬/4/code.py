import time
import hashlib
import requests
import random


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "referer": "https://www.mashangpa.com/problem-detail/4/",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
}

cookies = {
    "sessionid": "cltgpy5soaoykvyavu7q8jagr2bv6g1e",
    "Hm_lvt_0d2227abf9548feda3b9cb6fddee26c0": "1776777924,1777023360,1777108116",
    "Hm_lpvt_0d2227abf9548feda3b9cb6fddee26c0": "1777108116",
    "HMACCOUNT": "45FC6488ADA4CC26"
}

url = "https://www.mashangpa.com/api/problem-detail/4/data/"


def get_sign(page):
    timestamp = int(time.time() * 1000)
    raw = "tuling" + str(timestamp) + str(page)
    sign = hashlib.md5(raw.encode("utf-8")).hexdigest()
    return timestamp, sign


def crawl_page(page):
    timestamp, sign = get_sign(page)

    params = {
        "page": page,
        "sign": sign,
        "_ts": timestamp
    }

    response = requests.get(
        url,
        headers=headers,
        cookies=cookies,
        params=params,
        timeout=15
    )

    response.raise_for_status()
    return response.json()


total_sum = 0
all_numbers = []

for page in range(1, 21):
    data = crawl_page(page)

    current_array = data.get("current_array", [])

    page_sum = sum(current_array)
    total_sum += page_sum
    all_numbers.extend(current_array)

    print(f"第 {page} 页 current_array = {current_array}")
    print(f"第 {page} 页小计 = {page_sum}")
    print("-" * 50)

    time.sleep(random.uniform(0.5, 1.2))


print("全部数字数量：", len(all_numbers))
print("20页总和：", total_sum)