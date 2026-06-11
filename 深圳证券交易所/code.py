import csv
import time
import requests


headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Referer": "https://www.szse.cn/market/fund/volume/etf/index.html",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "X-Request-Type": "ajax",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

url = "https://www.szse.cn/api/report/ShowReport/data"
session = requests.Session()
session.headers.update(headers)

csv_file = open("fund_data.csv", "w", newline="", encoding="utf-8-sig")
writer = csv.writer(csv_file)
writer.writerow(["日期", "基金代码", "基金简称", "基金规模（万份）"])

total_pages = 1272

for page in range(1, total_pages + 1):
    params = {
        "SHOWTYPE": "JSON",
        "CATALOGID": "scsj_fund_jjgm",
        "TABKEY": "tab1",
        "txtStart": "2026-04-13",
        "txtEnd": "2026-06-10",
        "jjlb": "ETF",
        "PAGENO": page,
        "random": str(time.time()),
    }

    try:
        resp = session.get(url, params=params, timeout=30)
        data = resp.json()
        records = data[0]["data"]

        for item in records:
            writer.writerow(
                [
                    item["size_date"],
                    item["fund_code"],
                    item["security_short_name"],
                    item["current_size"],
                ]
            )

        print(f"第 {page}/{total_pages} 页完成，获取 {len(records)} 条")
    except Exception as e:
        print(f"第 {page} 页出错: {e}")

    time.sleep(0.5)

csv_file.close()
print("全部完成！")
