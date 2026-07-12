import requests
import time
import urllib3
import json
import csv
import os
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGET_URL = "http://121.29.48.71:8080/flow/selectReportAllList.do"
CSV_FILE = "data.csv"
CHECKPOINT_FILE = "checkpoint.json"
TOTAL_PAGES = 300
PAGE_SIZE = 20

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "JSESSIONID=126A4C4AC106A064E5B5A3F7375B1D9B; sidebarStatus=1",
    "Origin": "http://121.29.48.71:8080",
    "Referer": "http://121.29.48.71:8080/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
}

FIELD_NAMES = [
    "id",
    "province",
    "city",
    "county",
    "towns",
    "contactPerson",
    "contactNumber",
    "registeredAddress",
    "productionAddress",
    "name",
    "creditCode",
    "unifiedId",
    "isKeyDischargeEnp",
    "isCcpaEnp",
    "industryCategoryCode",
    "industryCategoryName",
    "enpNatureCode",
    "enpNatureName",
    "year",
    "reportTime",
    "status",
    "longitude",
    "latitude",
    "reportId",
    "createTime",
]


def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_checkpoint(checkpoint):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)


def init_csv():
    file_exists = os.path.exists(CSV_FILE)
    f = open(CSV_FILE, "a", newline="", encoding="utf-8-sig")
    writer = csv.DictWriter(f, fieldnames=FIELD_NAMES)
    if not file_exists:
        writer.writeheader()
    return f, writer


def parse_and_save(writer, json_str):
    data = json.loads(json_str)
    if data.get("status") != 0:
        print(f"  [!] 接口返回异常状态: {data}")
        return 0
    content = data.get("data", {}).get("content", [])
    for item in content:
        row = {field: item.get(field, "") for field in FIELD_NAMES}
        writer.writerow(row)
    return len(content)


def fetch_with_retry(payload, max_retries=5, base_delay=3):
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                TARGET_URL, headers=HEADERS, data=payload, verify=False, timeout=30
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"  [重试 {attempt}/{max_retries}] 请求失败: {e}")
            if attempt < max_retries:
                delay = base_delay * (2 ** (attempt - 1))
                print(f"  等待 {delay} 秒后重试...")
                time.sleep(delay)
            else:
                raise
    return None


def fetch_all():
    checkpoint = load_checkpoint()
    crawled_pages = checkpoint.get("crawled_pages", [])

    csv_file, writer = init_csv()

    try:
        for page_num in range(1, TOTAL_PAGES + 1):
            if page_num in crawled_pages:
                print(f"[跳过] 第 {page_num} 页已爬取")
                continue

            print(f"[爬取] 第 {page_num}/{TOTAL_PAGES} 页...")

            payload = {
                "enterpriseName": "",
                "districtCode": "",
                "industryCategoryCode": "",
                "year": "2025",
                "enpNatureCode": "",
                "isKeyDischargeEnp": "",
                "isCcpaEnp": "",
                "status": "已完成",
                "pageNum": page_num,
                "pageSize": PAGE_SIZE,
            }

            try:
                raw_text = fetch_with_retry(payload)
                count = parse_and_save(writer, raw_text)
                print(f"  -> 获取到 {count} 条数据")

                crawled_pages.append(page_num)
                save_checkpoint({"crawled_pages": crawled_pages})
                csv_file.flush()

            except Exception as e:
                print(f"  [失败] 第 {page_num} 页多次重试后仍然失败: {e}")
                print(
                    f"  [信息] 已爬取 {len(crawled_pages)} 页，断点已保存，下次将从第 {page_num} 页继续"
                )
                break

            time.sleep(2)

    finally:
        csv_file.close()

    print(f"\n====== 爬取完成 ======")
    print(f"共爬取 {len(crawled_pages)} 页，数据已保存至 {CSV_FILE}")


if __name__ == "__main__":
    fetch_all()
