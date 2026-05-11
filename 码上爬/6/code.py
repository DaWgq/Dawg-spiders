import requests
import hashlib
import time
import random

import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


url = "https://www.mashangpa.com/api/problem-detail/6/data/"

cookies = {
    "sessionid": "cltgpy5soaoykvyavu7q8jagr2bv6g1e",
    "Hm_lvt_0d2227abf9548feda3b9cb6fddee26c0": "1776777924,1777023360,1777108116,1777194996",
    "HMACCOUNT": "45FC6488ADA4CC26",
    "Hm_lpvt_0d2227abf9548feda3b9cb6fddee26c0": "1777195867"
}

save_file = "problem6_result.csv"
progress_file = "progress.txt"

AES_KEY = "xxxxxxxxoooooooo"
AES_IV = "0123456789ABCDEF"


def get_sign():
    tt = str(int(time.time() * 1000))
    s = hashlib.md5(("sssssbbbbb" + tt).encode("utf-8")).hexdigest()
    return s, tt


def get_headers():
    s, tt = get_sign()

    return {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.mashangpa.com/problem-detail/6/",
        "s": s,
        "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "tt": tt,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
    }


def decrypt_t(encrypted_hex):
    encrypted_bytes = bytes.fromhex(encrypted_hex)

    cipher = AES.new(
        AES_KEY.encode("utf-8"),
        AES.MODE_CBC,
        AES_IV.encode("utf-8")
    )

    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    decrypted_bytes = unpad(decrypted_bytes, AES.block_size)

    text = decrypted_bytes.decode("utf-8")

    try:
        return json.loads(text)
    except Exception:
        return text


def get_start_page():
    return 1





def fetch_page(page, max_retry=5):
    for retry in range(1, max_retry + 1):
        try:
            headers = get_headers()

            params = {
                "page": str(page)
            }

            response = requests.get(
                url,
                headers=headers,
                cookies=cookies,
                params=params,
                timeout=20
            )

            print(f"第 {page} 页状态码：{response.status_code}")

            if response.status_code == 200:
                res_json = response.json()

                encrypted_hex = res_json.get("t")
                if not encrypted_hex:
                    print("返回中没有 t 字段：", res_json)
                    return res_json

                data = decrypt_t(encrypted_hex)
                return data

            print(f"第 {page} 页响应异常：{response.text[:200]}")

        except Exception as e:
            print(f"第 {page} 页第 {retry} 次失败：{e}")

        sleep_time = random.uniform(2, 5)
        print(f"等待 {sleep_time:.1f} 秒后重试...")
        time.sleep(sleep_time)

    return None


def main():
    start_page = get_start_page()
    end_page = 20

    print(f"从第 {start_page} 页开始采集")

    total_sum = 0  # 用于累加所有页面的 current_array 总和
    page_count = 0  # 记录成功采集的页数

    for page in range(start_page, end_page + 1):
        data = fetch_page(page)

        if data is None:
            print(f"第 {page} 页失败次数过多，停止。")
            break

        print(f"第 {page} 页解密成功：")
        print(data)

        # 提取 current_array 并累加
        current_array = data.get("current_array", [])
        if current_array:
            page_sum = sum(current_array)
            total_sum += page_sum
            page_count += 1
            print(f"第 {page} 页 current_array: {current_array}")
            print(f"第 {page} 页小计: {page_sum}, 累计总和: {total_sum}")
        else:
            print(f"第 {page} 页没有 current_array 数据")

        sleep_time = random.uniform(1.5, 4)
        print(f"等待 {sleep_time:.1f} 秒继续下一页...")
        time.sleep(sleep_time)

    print("="*50)
    print(f"采集完成！")
    print(f"成功采集页数: {page_count}")
    print(f"所有页面 current_array 总和: {total_sum}")
    print("="*50)


if __name__ == "__main__":
    main()