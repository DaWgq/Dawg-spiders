import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import binascii
import json
import csv
import time


def decrypt_hex(cipher_hex: str) -> str:
    key = b"Dt8j9wGw%6HbxfFn"
    iv = b"0123456789ABCDEF"
    cipher_bytes = binascii.unhexlify(cipher_hex)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain = unpad(cipher.decrypt(cipher_bytes), AES.block_size)
    return plain.decode("utf-8")


headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://jzsc.mohurd.gov.cn/data/company",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "accessToken;": "",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "timeout": "30000",
    "v": "231012"
}

cookies = {
    "Hm_lvt_b1b4b9ea61b6f1627192160766a9c55c": "1776519128",
    "Hm_lpvt_b1b4b9ea61b6f1627192160766a9c55c": "1776519128",
    "HMACCOUNT": "45FC6488ADA4CC26"
}

url = "https://jzsc.mohurd.gov.cn/APi/webApi/dataservice/query/comp/list"


def fetch_page(page_num: int, page_size: int = 15):
    params = {
        "pg": str(page_num),
        "pgsz": str(page_size),
        "total": "0"
    }

    response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=30)
    response.raise_for_status()

    cipher_text = response.text.strip()
    plain_text = decrypt_hex(cipher_text)
    result = json.loads(plain_text)

    return result


def main():
    output_file = "company_list.csv"
    page_num = 1
    page_size = 15

    total_pages = None
    total_count = None
    all_rows = []

    while True:
        try:
            result = fetch_page(page_num, page_size)
            data = result.get("data", {})
            company_list = data.get("list", [])

            if not company_list:
                print(f"第 {page_num} 页无数据，结束抓取")
                break

            if total_count is None:
                total_count = data.get("total", 0)
                total_pages = (total_count + page_size - 1) // page_size
                print(f"总数: {total_count}，总页数: {total_pages}")

            print(f"正在抓取第 {page_num}/{total_pages} 页，当前页 {len(company_list)} 条")

            for item in company_list:
                row = {
                    "QY_NAME": item.get("QY_NAME", ""),
                    "QY_FR_NAME": item.get("QY_FR_NAME", ""),
                    "QY_REGION_NAME": item.get("QY_REGION_NAME", "")
                }
                all_rows.append(row)

            if total_pages is not None and page_num >= total_pages:
                break

            page_num += 1
            time.sleep(0.5)

        except Exception as e:
            print(f"第 {page_num} 页抓取失败: {e}")
            break

    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["QY_NAME", "QY_FR_NAME", "QY_REGION_NAME"]
        )
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"抓取完成，共保存 {len(all_rows)} 条数据到 {output_file}")


if __name__ == "__main__":
    main()