import base64
import html
import json
import os
import re
import sys
import time
from datetime import datetime

from curl_cffi import requests

PAGE_SIZE = 1000
OUTPUT_DIR = "crawled_data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "products.jsonl")
PROGRESS_FILE = os.path.join(OUTPUT_DIR, "progress.txt")
SESSION_FILE = os.path.join(OUTPUT_DIR, "session.json")

HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Origin": "https://www.cnmaker.org.cn",
    "Referer": "https://www.cnmaker.org.cn/ds/products.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}

API_URL = "https://www.cnmaker.org.cn/doPost"
INIT_URL = "https://www.cnmaker.org.cn/ds/products.html"


def make_payload(start_index, page_size=PAGE_SIZE, classid="", title=""):
    data_obj = {
        "start_index": start_index,
        "page_size": page_size,
        "classid": classid,
        "title": title,
    }
    data_json = json.dumps(data_obj, separators=(",", ":"), ensure_ascii=False)
    xml = f'<Request  action="ds/actions/getProducts.xml" request="JSON" response="JSON" ><Data>{data_json}</Data></Request>'
    return base64.b64encode(xml.encode()).decode()


def init_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    resp = session.get(INIT_URL, impersonate="chrome")
    if resp.status_code != 200:
        print(f"Failed to init session: {resp.status_code}")
        sys.exit(1)
    print(
        f"Session initialized. Cookie: __jsluid_s={session.cookies.get('__jsluid_s', 'N/A')[:16]}..."
    )
    return session


def fetch_page(session, start_index):
    payload = make_payload(start_index)
    resp = session.post(API_URL, data=payload, impersonate="chrome")
    if resp.status_code != 200:
        print(f"HTTP error {resp.status_code} at start_index={start_index}")
        return None, None
    try:
        data = resp.json()
    except json.JSONDecodeError:
        print(f"JSON decode error at start_index={start_index}: {resp.text[:200]}")
        return None, None
    result = data.get("Result", {})
    if not result.get("Success"):
        print(f"API error at start_index={start_index}: {result}")
        return None, None
    result_data = result.get("Data", {})
    products = result_data.get("products", [])
    total_count = result_data.get("total_count", 0)
    return products, total_count


HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def clean_html(text):
    if not text:
        return text
    text = html.unescape(text)
    text = HTML_TAG_RE.sub(" ", text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text


TEXT_FIELDS = {"product_name", "description", "maker_name", "class_name", "nickname"}


def clean_product(product):
    cleaned = {}
    for key, value in product.items():
        if isinstance(value, str) and key in TEXT_FIELDS:
            cleaned[key] = clean_html(value)
        else:
            cleaned[key] = value
    return cleaned


def save_products(products, filepath):
    with open(filepath, "a", encoding="utf-8") as f:
        for product in products:
            cleaned = clean_product(product)
            f.write(json.dumps(cleaned, ensure_ascii=False) + "\n")


def save_progress(start_index, total_count, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"{start_index},{total_count},{datetime.now().isoformat()}")


def load_progress(filepath):
    if not os.path.exists(filepath):
        return 0, 0
    with open(filepath, encoding="utf-8") as f:
        line = f.read().strip()
        parts = line.split(",")
        return int(parts[0]), int(parts[1])


def load_existing_count(filepath):
    if not os.path.exists(filepath):
        return 0
    with open(filepath, encoding="utf-8") as f:
        return sum(1 for _ in f)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    last_start_index, known_total = load_progress(PROGRESS_FILE)
    existing_count = load_existing_count(OUTPUT_FILE)

    print(f"Existing records: {existing_count}")
    print(f"Resuming from start_index={last_start_index}")

    session = init_session()

    if known_total == 0:
        products, total_count = fetch_page(session, 0)
        if products is None:
            print("Failed to fetch first page, exiting.")
            sys.exit(1)
        known_total = total_count
        save_products(products, OUTPUT_FILE)
        last_start_index = PAGE_SIZE
        save_progress(last_start_index, known_total, PROGRESS_FILE)
        print(f"Total products: {known_total}")
    else:
        print(f"Known total: {known_total}")

    start = last_start_index
    total_pages = (known_total + PAGE_SIZE - 1) // PAGE_SIZE
    current_page = start // PAGE_SIZE + 1

    print(
        f"Fetching pages {current_page} to {total_pages} (start_index {start} to {known_total})"
    )

    consecutive_failures = 0
    max_failures = 5

    for start_index in range(start, known_total, PAGE_SIZE):
        products, _ = fetch_page(session, start_index)
        if products is None:
            consecutive_failures += 1
            if consecutive_failures >= max_failures:
                print(f"Too many consecutive failures ({max_failures}), stopping.")
                break
            wait = 2**consecutive_failures
            print(f"Retrying in {wait}s...")
            time.sleep(wait)
            products, _ = fetch_page(session, start_index)
            if products is None:
                continue
        else:
            consecutive_failures = 0

        save_products(products, OUTPUT_FILE)
        save_progress(start_index + PAGE_SIZE, known_total, PROGRESS_FILE)

        if (start_index // PAGE_SIZE) % 10 == 0:
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] Page {current_page}/{total_pages} (start_index={start_index}, {len(products)} items)"
            )

        current_page += 1
        time.sleep(0.3)

    final_count = load_existing_count(OUTPUT_FILE)
    print(f"\nDone! Total products saved: {final_count}")


if __name__ == "__main__":
    main()
