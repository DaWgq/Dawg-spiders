import requests
import json
import csv
import time
import random
import re

headers = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.sse.com.cn/",
    "Sec-Fetch-Dest": "script",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}
cookies = {
    "ba17301551dcbaf9_gdp_session_id": "6da0ffb0-7426-4154-9d0f-432c445e1bdd",
    "gdp_user_id": "gioenc-1704569d%2Cd5dg%2C52e7%2C9d47%2Ce62b1e50ba3a",
    "ba17301551dcbaf9_gdp_session_id_sent": "6da0ffb0-7426-4154-9d0f-432c445e1bdd",
    "ba17301551dcbaf9_gdp_sequence_ids": "{%22globalKey%22:6%2C%22VISIT%22:2%2C%22PAGE%22:3%2C%22VIEW_CLICK%22:3}",
}

url = "https://query.sse.com.cn/commonQuery.do"

csv_file = "etf_data.csv"
with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["日期", "基金代码", "基金简称", "基金规模（万份）"])

    for page in range(1, 861):
        params = {
            "jsonCallBack": "jsonpCallback66567043",
            "isPagination": "true",
            "pageHelp.pageSize": "25",
            "pageHelp.pageNo": str(page),
            "pageHelp.beginPage": str(page),
            "pageHelp.cacheSize": "1",
            "pageHelp.endPage": str(page),
            "sqlId": "COMMON_SSE_ZQPZ_ETFZL_XXPL_ETFGM_SEARCH_L",
            "STAT_DATE": "",
            "_": str(int(time.time() * 1000)),
        }

        try:
            response = requests.get(
                url, headers=headers, cookies=cookies, params=params, timeout=30
            )
            text = response.text

            json_str = re.sub(r"^jsonpCallback\d+\(|\)$", "", text)
            data = json.loads(json_str)

            records = data.get("pageHelp", {}).get("data", [])
            if not records:
                print(f"第{page}页无数据，可能已到末尾")
                break

            for item in records:
                writer.writerow(
                    [
                        item.get("STAT_DATE", ""),
                        item.get("SEC_CODE", ""),
                        item.get("SEC_NAME", ""),
                        item.get("TOT_VOL", ""),
                    ]
                )

            print(f"第{page}页完成，获取{len(records)}条数据")

        except Exception as e:
            print(f"第{page}页请求失败: {e}")

        delay = random.uniform(3, 6)
        time.sleep(delay)

print(f"\n全部完成，数据已保存至 {csv_file}")
