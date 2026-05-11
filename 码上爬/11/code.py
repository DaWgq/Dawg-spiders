import time
import json
import os
import random
import requests
from urllib.parse import urlencode


# ==========================
# 配置区
# ==========================

BASE_URL = "https://www.mashangpa.com/api/problem-detail/11/data/"

START_PAGE = 1
END_PAGE = 20

SAVE_FILE = "problem_11_data.json"
PROGRESS_FILE = "problem_11_progress.json"

HEADERS = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.mashangpa.com/problem-detail/11/",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/147.0.0.0 Safari/537.36"
}

COOKIES = {
    "sessionid": "cltgpy5soaoykvyavu7q8jagr2bv6g1e",
    "Hm_lvt_0d2227abf9548feda3b9cb6fddee26c0": "1777628901,1777723369,1777783255,1777786730",
    "Hm_lpvt_0d2227abf9548feda3b9cb6fddee26c0": "1777786730",
    "HMACCOUNT": "45FC6488ADA4CC26"
}


# ==========================
# 加密参数生成
# ==========================

def get_ts():
    """
    生成秒级时间戳
    对应 JS:
    Math.floor(new Date().getTime() / 1000)
    """
    return int(time.time())


def encrypt_m(page, ts):
    """
    wasm encrypt 还原逻辑：

    encrypt(page, ts) = page + ts / 3 + 16358

    wasm 中是 i32.div_s，
    对正数时间戳来说，等价于 Python 的 //
    """
    return int(page) + int(ts) // 3 + 16358


def build_params(page):
    ts = get_ts()
    m = encrypt_m(page, ts)

    return {
        "page": str(page),
        "m": str(m),
        "_ts": str(ts)
    }


# ==========================
# 文件读写
# ==========================

def load_json_file(filename, default):
    if not os.path.exists(filename):
        return default

    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json_file(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_progress():
    return load_json_file(PROGRESS_FILE, {
        "finished_pages": []
    })


def save_progress(progress):
    save_json_file(PROGRESS_FILE, progress)


def load_saved_data():
    return load_json_file(SAVE_FILE, [])


def save_data(data):
    save_json_file(SAVE_FILE, data)


# ==========================
# 请求函数
# ==========================

def fetch_page(session, page, max_retry=3):
    params = build_params(page)

    for retry in range(1, max_retry + 1):
        try:
            query = urlencode(params)
            full_url = f"{BASE_URL}?{query}"

            print(f"\n正在请求第 {page} 页")
            print(f"请求 URL: {full_url}")

            response = session.get(
                BASE_URL,
                headers=HEADERS,
                cookies=COOKIES,
                params=params,
                timeout=15
            )

            print(f"状态码: {response.status_code}")

            if response.status_code != 200:
                print(f"第 {page} 页状态码异常，正在重试 {retry}/{max_retry}")
                time.sleep(1.5 * retry)
                continue

            try:
                result = response.json()
            except Exception:
                print("响应不是 JSON：")
                print(response.text[:500])
                time.sleep(1.5 * retry)
                continue

            return {
                "page": page,
                "params": params,
                "response": result
            }

        except requests.exceptions.RequestException as e:
            print(f"第 {page} 页请求异常: {e}")
            print(f"正在重试 {retry}/{max_retry}")
            time.sleep(1.5 * retry)

    print(f"第 {page} 页请求失败，已跳过")
    return None


# ==========================
# 主程序
# ==========================

def main():
    session = requests.Session()

    all_data = load_saved_data()
    progress = load_progress()

    finished_pages = set(progress.get("finished_pages", []))

    print("========== 开始爬取 ==========")
    print(f"目标页码: {START_PAGE} - {END_PAGE}")
    print(f"已完成页码: {sorted(finished_pages)}")

    # 用于累加所有页面的 current_array
    total_sum = 0
    
    for page in range(START_PAGE, END_PAGE + 1):
        if page in finished_pages:
            print(f"第 {page} 页已爬取，跳过")
            continue

        page_result = fetch_page(session, page)

        if page_result is None:
            continue

        # 提取当前页的 current_array 并累加
        response_data = page_result.get("response", {})
        current_array = response_data.get("current_array", [])
        
        if current_array:
            page_sum = sum(current_array)
            total_sum += page_sum
            print(f"第 {page} 页 current_array: {current_array}")
            print(f"第 {page} 页总和: {page_sum}")
            print(f"累计总和: {total_sum}")

        all_data.append(page_result)
        finished_pages.add(page)

        progress["finished_pages"] = sorted(list(finished_pages))

        save_data(all_data)
        save_progress(progress)

        print(f"第 {page} 页保存成功")

        # 随机延迟，别请求太猛
        sleep_time = random.uniform(1.0, 2.5)
        print(f"休眠 {sleep_time:.2f} 秒")
        time.sleep(sleep_time)

    print("\n========== 爬取完成 ==========")
    print(f"数据保存到: {SAVE_FILE}")
    print(f"进度保存到: {PROGRESS_FILE}")
    print(f"\n20页 current_array 累加总和: {total_sum}")


if __name__ == "__main__":
    main()