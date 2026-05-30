import base64
import json
import random
import string
import time
from datetime import datetime

import requests
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad


# =========================
# 1. 基础配置：按你的抓包填写
# =========================

SEARCH_WORD = "私募基金"
TOTAL_PAGES = 20

PAGE_ID = "4dbf6fd2f2dfc9e2cb54a2e632331d87"
REQUEST_TOKEN = "eemsAr6Q1tnP0LJmKHrjIiks"
SESSION_COOKIE = "a6959fef-7003-4779-8849-35a794e0d8dc"

URL = "https://wenshu.court.gov.cn/website/parse/rest.q4w"

REFERER = (
    "https://wenshu.court.gov.cn/website/wenshu/181217BMTKHNT2W0/"
    f"index.html?pageId={PAGE_ID}&s21=%E7%A7%81%E5%8B%9F%E5%9F%BA%E9%87%91"
)


headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://wenshu.court.gov.cn",
    "Referer": REFERER,
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/148.0.0.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

cookies = {
    "SESSION": SESSION_COOKIE
}


# =========================
# 2. 复现前端 random(24)
# =========================

def js_random_24(size=24):
    chars = string.digits + string.ascii_lowercase + string.ascii_uppercase
    return "".join(random.choice(chars) for _ in range(size))


# =========================
# 3. 字符串转二进制
#    对应前端 strTobinary()
# =========================

def str_to_binary(s: str) -> str:
    return " ".join(bin(ord(ch))[2:] for ch in s)


# =========================
# 4. 3DES 加密 timestamp
#    对应 DES3.encrypt(timestamp, salt, iv)
# =========================

def encrypt_timestamp(timestamp: str, salt: str, iv: str) -> str:
    key = salt.encode("utf-8")   # 24字节
    iv_bytes = iv.encode("utf-8")  # 8字节，如 20260516

    cipher = DES3.new(key, DES3.MODE_CBC, iv=iv_bytes)
    encrypted = cipher.encrypt(pad(timestamp.encode("utf-8"), 8))

    return base64.b64encode(encrypted).decode("utf-8")


# =========================
# 5. 生成 ciphertext
# =========================

def generate_ciphertext() -> str:
    timestamp = str(int(time.time() * 1000))
    salt = js_random_24(24)
    iv = datetime.now().strftime("%Y%m%d")

    enc = encrypt_timestamp(timestamp, salt, iv)
    final_str = salt + iv + enc

    return str_to_binary(final_str)


# =========================
# 6. 解密响应 result
#    对应 DES3.decrypt(result, secretKey)
# =========================

def decrypt_result(result: str, secret_key: str) -> str:
    key = secret_key.encode("utf-8")
    iv = datetime.now().strftime("%Y%m%d").encode("utf-8")

    cipher = DES3.new(key, DES3.MODE_CBC, iv=iv)
    ciphertext_bytes = base64.b64decode(result)

    plaintext = unpad(cipher.decrypt(ciphertext_bytes), 8)
    return plaintext.decode("utf-8")


# =========================
# 7. 请求单页
# =========================

def fetch_one_page(session: requests.Session, page_num: int):
    query_condition = json.dumps(
        [{"key": "s21", "value": SEARCH_WORD}],
        ensure_ascii=False,
        separators=(",", ":")
    )

    data = {
        "pageId": PAGE_ID,
        "s21": SEARCH_WORD,
        "sortFields": "s50:desc",
        "ciphertext": generate_ciphertext(),
        "pageNum": str(page_num),
        "queryCondition": query_condition,
        "cfg": "com.lawyee.judge.dc.parse.dto.SearchDataDsoDTO@queryDoc",
        "__RequestVerificationToken": REQUEST_TOKEN,
        "wh": "572",
        "ww": "1920",
        "cs": "0"
    }

    resp = session.post(
        URL,
        headers=headers,
        cookies=cookies,
        data=data,
        timeout=20
    )

    resp.raise_for_status()
    outer_json = resp.json()

    return outer_json


# =========================
# 8. 主程序：翻页 + 解密 + 控制台输出
# =========================

def main():
    session = requests.Session()

    for page in range(1, TOTAL_PAGES + 1):
        print("\n" + "=" * 80)
        print(f"正在抓取第 {page} 页")
        print("=" * 80)

        try:
            outer_json = fetch_one_page(session, page)

            code = outer_json.get("code")
            success = outer_json.get("success")
            result = outer_json.get("result")
            secret_key = outer_json.get("secretKey")

            print(f"[接口状态] code={code}, success={success}")

            if not result or not secret_key:
                print("[异常] 当前页没有 result 或 secretKey")
                print(json.dumps(outer_json, ensure_ascii=False, indent=2))
                continue

            plaintext = decrypt_result(result, secret_key)

            try:
                page_data = json.loads(plaintext)
                print(json.dumps(page_data, ensure_ascii=False, indent=2))
            except json.JSONDecodeError:
                print("[提示] 解密成功，但结果不是标准 JSON，原文如下：")
                print(plaintext)

            time.sleep(1)

        except Exception as e:
            print(f"[第 {page} 页失败] {type(e).__name__}: {e}")
            time.sleep(2)


if __name__ == "__main__":
    main()