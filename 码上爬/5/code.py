import time
import json
import random
import os
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "origin": "https://www.mashangpa.com",
    "pragma": "no-cache",
    "referer": "https://www.mashangpa.com/problem-detail/5/",
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
    "HMACCOUNT": "45FC6488ADA4CC26",
    "Hm_lpvt_0d2227abf9548feda3b9cb6fddee26c0": "1777108628"
}

url = "https://www.mashangpa.com/api/problem-detail/5/data/"

KEY = "jo8j9wGw%6HbxfFn"
IV = "0123456789ABCDEF"

SAVE_FILE = "mashangpa_p5_progress.json"
TOTAL_PAGES = 20
MAX_RETRY = 5


def aes_encrypt_hex(text):
    cipher = AES.new(
        KEY.encode("utf-8"),
        AES.MODE_CBC,
        IV.encode("utf-8")
    )

    encrypted = cipher.encrypt(
        pad(text.encode("utf-8"), AES.block_size)
    )

    return encrypted.hex()


def load_progress():
    """
    读取已经爬过的数据
    """
    if not os.path.exists(SAVE_FILE):
        return {}

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_progress(progress):
    """
    每爬完一页就保存，防止中途断掉
    """
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def build_payload(page):
    timestamp = int(time.time() * 1000)

    params = {
        "page": page,
        "_ts": timestamp
    }

    json_string = json.dumps(params, separators=(",", ":"))
    xl = aes_encrypt_hex(json_string)

    return {
        "xl": xl
    }


def crawl_page(page):
    """
    单页爬取，失败自动重试
    """
    for retry in range(1, MAX_RETRY + 1):
        try:
            payload = build_payload(page)

            response = requests.post(
                url,
                headers=headers,
                cookies=cookies,
                json=payload,
                timeout=15
            )

            print(f"第 {page} 页，第 {retry} 次请求，状态码：{response.status_code}")

            if response.status_code != 200:
                print("响应异常：", response.text[:200])
                time.sleep(random.uniform(1, 3))
                continue

            data = response.json()

            current_array = data.get("current_array", [])

            if not current_array:
                print(f"第 {page} 页 current_array 为空，重试")
                time.sleep(random.uniform(1, 3))
                continue

            return data

        except requests.exceptions.RequestException as e:
            print(f"第 {page} 页网络异常：{e}")
            time.sleep(random.uniform(2, 5))

        except Exception as e:
            print(f"第 {page} 页其他异常：{e}")
            time.sleep(random.uniform(2, 5))

    print(f"第 {page} 页连续失败，暂时跳过")
    return None


def calculate_total(progress):
    total_sum = 0
    total_count = 0

    for page, item in progress.items():
        arr = item.get("current_array", [])
        total_sum += sum(arr)
        total_count += len(arr)

    return total_sum, total_count


def main():
    progress = load_progress()

    print("已保存页数：", list(progress.keys()))

    for page in range(1, TOTAL_PAGES + 1):
        page_key = str(page)

        if page_key in progress:
            print(f"第 {page} 页已爬过，跳过")
            continue

        data = crawl_page(page)

        if data is None:
            print(f"第 {page} 页失败，程序继续后面的页")
            continue

        current_array = data.get("current_array", [])
        page_sum = sum(current_array)

        progress[page_key] = {
            "page": page,
            "current_array": current_array,
            "page_sum": page_sum,
            "raw": data
        }

        save_progress(progress)

        total_sum, total_count = calculate_total(progress)

        print(f"第 {page} 页 current_array：{current_array}")
        print(f"第 {page} 页小计：{page_sum}")
        print(f"当前已累计数量：{total_count}")
        print(f"当前已累计总和：{total_sum}")
        print("-" * 60)

        time.sleep(random.uniform(0.8, 1.5))

    total_sum, total_count = calculate_total(progress)

    print("=" * 60)
    print("爬取结束")
    print("已完成页数：", sorted([int(k) for k in progress.keys()]))
    print("总数字数量：", total_count)
    print("最终总和：", total_sum)
    print("=" * 60)

    if len(progress) < TOTAL_PAGES:
        missing_pages = [
            page for page in range(1, TOTAL_PAGES + 1)
            if str(page) not in progress
        ]
        print("还有这些页没有成功：", missing_pages)
        print("重新运行脚本会自动继续爬这些页")


if __name__ == "__main__":
    main()