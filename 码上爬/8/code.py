import requests
import json
import time
import base64
import os
import random


URL = "https://www.mashangpa.com/api/problem-detail/8/data/"
SAVE_FILE = "page8_result.json"
PROGRESS_FILE = "page8_progress.txt"

SMS = "oooooo"


def get_t(timestamp):
    """
    t = base64(timestamp)
    """
    return base64.b64encode(str(timestamp).encode()).decode()


def get_m(page, timestamp):
    """
    m = OOOoOo("oooooo" + timestamp + page, "oooooo")
    """
    text = SMS + str(timestamp) + str(page)
    key = SMS

    result = []

    for i in range(0, len(text), 4):
        group = list(text[i:i + 4])

        for j, ch in enumerate(group):
            new_code = (ord(ch) + ord(key[j % len(key)])) % 256
            group[j] = chr(new_code)

        result.extend(group)

    return ''.join(hex(ord(ch))[2:].zfill(2) for ch in result)


def build_headers(page):
    timestamp = int(time.time() * 1000)

    headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "origin": "https://www.mashangpa.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.mashangpa.com/problem-detail/8/",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",

        "m": get_m(page, timestamp),
        "t": get_t(timestamp),
    }

    return headers


cookies = {
    "sessionid": "cltgpy5soaoykvyavu7q8jagr2bv6g1e",
    "Hm_lvt_0d2227abf9548feda3b9cb6fddee26c0": "1777194996,1777381181,1777448593,1777628901",
    "Hm_lpvt_0d2227abf9548feda3b9cb6fddee26c0": "1777628901",
    "HMACCOUNT": "45FC6488ADA4CC26",
    "s": "51b351b351b351b370b0b0b09030505110b05171d0"
}


def load_result():
    """
    读取已经保存的数据
    """
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_result(result):
    """
    保存结果
    """
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def load_progress():
    """
    读取上次爬到第几页
    """
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content.isdigit():
                return int(content)
    return 0


def save_progress(page):
    """
    保存当前进度
    """
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        f.write(str(page))


def crawl_page(session, page, retry=3):
    """
    爬取单页，失败自动重试
    """
    for attempt in range(1, retry + 1):
        try:
            headers = build_headers(page)

            data = {
                "page": page
            }

            response = session.post(
                URL,
                headers=headers,
                cookies=cookies,
                data=json.dumps(data, separators=(',', ':')),
                timeout=10
            )

            print(f"第 {page} 页状态码：{response.status_code}")

            if response.status_code == 200:
                return response.json()
            else:
                print(f"第 {page} 页请求失败，响应内容：{response.text[:200]}")

        except Exception as e:
            print(f"第 {page} 页第 {attempt} 次请求异常：{e}")

        time.sleep(random.uniform(1, 2))

    return None


def main():
    session = requests.Session()

    result = load_result()
    last_page = load_progress()

    print(f"当前断点进度：已完成第 {last_page} 页")

    for page in range(1, 21):
        page_key = str(page)

        # 如果文件里已经有这一页，直接跳过
        if page_key in result:
            print(f"第 {page} 页已存在，跳过")
            continue

        # 如果进度显示已经爬过，也跳过
        if page <= last_page:
            print(f"第 {page} 页已完成，跳过")
            continue

        print(f"\n开始爬取第 {page} 页")

        page_data = crawl_page(session, page)

        if page_data is None:
            print(f"第 {page} 页失败，程序停止。下次会从这里继续。")
            break

        result[page_key] = page_data

        save_result(result)
        save_progress(page)

        print(f"第 {page} 页保存成功")
        time.sleep(random.uniform(1.5, 3))

    print("\n爬取结束")
    print(f"数据已保存到：{SAVE_FILE}")
    
    # 计算所有current_array的累加和
    calculate_sum(result)


def calculate_sum(result):
    """
    计算所有页面current_array的累加和
    """
    total_sum = 0
    all_values = []
    
    for page_key in sorted(result.keys(), key=lambda x: int(x)):
        page_data = result[page_key]
        if 'current_array' in page_data:
            current_array = page_data['current_array']
            page_sum = sum(current_array)
            total_sum += page_sum
            all_values.extend(current_array)
            print(f"第 {page_key} 页 current_array: {current_array}, 本页和: {page_sum}")
    
    print("\n" + "="*60)
    print(f"所有页面的current_array总和: {total_sum}")
    print(f"所有数值的个数: {len(all_values)}")
    print(f"所有数值列表: {all_values}")
    print("="*60)
    
    # 将结果保存到文件
    sum_result = {
        "total_sum": total_sum,
        "count": len(all_values),
        "all_values": all_values
    }
    
    sum_file = "mashangpa_8_sum_result.json"
    with open(sum_file, "w", encoding="utf-8") as f:
        json.dump(sum_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n累加结果已保存到: {sum_file}")


if __name__ == "__main__":
    main()