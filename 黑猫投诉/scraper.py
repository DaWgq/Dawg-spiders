import hashlib
import time
import random
import string
import requests
import pandas as pd
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE_URL = "https://tousu.sina.com.cn/api/index/feed"
SECRET = "$d6eb7ff91ee257475%"
PAGE_SIZE = 10
TOTAL_ITEMS = 10000
REQUEST_INTERVAL = (1.5, 3.5)

HEADERS = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "referer": "https://tousu.sina.com.cn/",
    "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}

COOKIES = {
    "SUB": "_2AkMe7xPFf8NxqwFRm_kRy27laoV0yQDEieKos-IeJRMyHRl-yD9kqmAOtRB6NW89Krw1I1RkOmCeakvsgBs7JCUg-6xv",
    "SUBP": "0033WrSXqPxfM72-Ws9jqgMF55529P9D9W5fafjwF2lboJBPU1BdUqMB",
}

PROXIES = []


def generate_rs(length=16):
    chars = string.digits + string.ascii_letters
    return "".join(random.choices(chars, k=length))


def generate_signature(ts, rs, type_, page_size, page):
    items = [str(ts), rs, SECRET, str(type_), str(page_size), str(page)]
    items.sort()
    raw = "".join(items)
    return hashlib.sha256(raw.encode()).hexdigest()


def fetch_page(type_, page, session):
    ts = int(time.time() * 1000)
    rs = generate_rs()
    signature = generate_signature(ts, rs, type_, PAGE_SIZE, page)

    params = {
        "ts": str(ts),
        "rs": rs,
        "signature": signature,
        "type": str(type_),
        "page_size": str(PAGE_SIZE),
        "page": str(page),
    }

    for attempt in range(3):
        try:
            resp = session.get(
                BASE_URL, headers=HEADERS, cookies=COOKIES, params=params, timeout=15
            )

            if resp.status_code == 456:
                return {"items": [], "stop": True, "reason": "ip_banned"}

            if resp.status_code != 200:
                if attempt < 2:
                    time.sleep(3 + random.random() * 3)
                    continue
                return {"items": [], "stop": True, "reason": f"http_{resp.status_code}"}

            data = resp.json()
            break
        except Exception as e:
            if attempt < 2:
                time.sleep(2 + random.random() * 2)
                continue
            return {"items": [], "stop": True, "reason": f"exception: {e}"}
    else:
        return {"items": [], "stop": True, "reason": "all_retries_failed"}

    status = data.get("result", {}).get("status", {})
    code = status.get("code")

    if code == 10017:
        return {"items": [], "stop": True, "reason": "login_required"}
    if code == 10019:
        return {"items": [], "stop": True, "reason": "page_not_exist"}
    if code != 0:
        return {"items": [], "stop": True, "reason": f"error_{code}"}

    lists = data.get("result", {}).get("data", {}).get("lists", [])
    pager = data.get("result", {}).get("data", {}).get("pager", {})

    if pager:
        current = pager.get("current", 0)
        total = pager.get("page_amount", 0)
        if total and current and current >= total:
            return {"items": lists, "stop": True, "reason": "last_page"}

    return {"items": lists, "stop": False, "reason": "ok"}


def parse_item(item):
    main = item.get("main", {})
    author = item.get("author", {})
    return {
        "id": main.get("id"),
        "sn": main.get("sn"),
        "title": main.get("title"),
        "company": main.get("cotitle"),
        "appeal": main.get("appeal"),
        "issue": main.get("issue"),
        "status": main.get("status"),
        "summary": main.get("summary"),
        "cost": main.get("cost"),
        "timestamp": main.get("timestamp"),
        "upvote_amount": main.get("upvote_amount"),
        "share_amount": main.get("share_amount"),
        "comment_amount": main.get("comment_amount"),
        "url": main.get("url"),
        "nickname": author.get("title"),
    }


def main():
    all_items = []
    session = requests.Session()

    if PROXIES:
        session.proxies = {
            "http": random.choice(PROXIES),
            "https": random.choice(PROXIES),
        }

    types_to_try = [1, 2, 3, 4]
    reason = ""

    for type_ in types_to_try:
        if len(all_items) >= TOTAL_ITEMS:
            break

        print(f"\n=== type={type_} ===")
        page = 1

        while len(all_items) < TOTAL_ITEMS:
            result = fetch_page(type_, page, session)
            items = result["items"]
            reason = result["reason"]

            if reason == "ip_banned":
                print(f"  IP被封禁，停止爬取")
                all_items.extend(items)
                break

            if reason in ("login_required", "page_not_exist"):
                print(f"  停止: {reason} (已获{len(all_items)}条)")
                break

            if items:
                all_items.extend(items)
                print(f"  p{page} +{len(items)} ={len(all_items)}条")

            if result["stop"]:
                break

            page += 1
            time.sleep(random.uniform(*REQUEST_INTERVAL))

        if reason == "ip_banned":
            break

    all_items = all_items[:TOTAL_ITEMS]
    records = [parse_item(item) for item in all_items]

    output_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(
        output_dir, f"黑猫投诉数据_{time.strftime('%Y%m%d_%H%M%S')}.xlsx"
    )

    df = pd.DataFrame(records)
    df.to_excel(filename, index=False, engine="openpyxl")

    print(f"\n{'=' * 50}")
    print(f"完成！共 {len(records)} 条")
    print(f"保存: {filename}")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
