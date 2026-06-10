import requests
import json
import base64
import uuid
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDvekdPMHN3AYhm/vktJT+YJr7
cI5DcsNKqdsx5DZX0gDuWFuIjzdwButrIYPNmRJ1G8ybDIF7oDW2eEpm5sMbL9zs
9ExXCdvqrn51qELbqj0XxtMTIpaCHFSI50PfPpTFV9Xt/hmyVwokoOXFlAEgCn+Q
CgGs52bFoYMtyi+xEQIDAQAB
-----END PUBLIC KEY-----"""

key = RSA.import_key(PUBLIC_KEY_PEM)
cipher = PKCS1_v1_5.new(key)


def rsa_encrypt(text):
    ciphertext = cipher.encrypt(text.encode("utf-8"))
    return base64.b64encode(ciphertext).decode("utf-8")


def login(account, password):
    device_id = str(uuid.uuid4())
    lifecycle_id = hex(int(time.time() * 1000))[2:12]

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Content-Type": "application/json",
        "Origin": "https://user.mihoyo.com",
        "Referer": "https://user.mihoyo.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "x-rpc-app_id": "dw9y09jqjpxc",
        "x-rpc-client_type": "4",
        "x-rpc-device_fp": "38d818f8368c1",
        "x-rpc-device_id": device_id,
        "x-rpc-device_model": "Chrome%20148.0.0.0",
        "x-rpc-device_name": "Chrome",
        "x-rpc-device_os": "Windows%2010%2064-bit",
        "x-rpc-game_biz": "plat_cn",
        "x-rpc-lifecycle_id": lifecycle_id,
        "x-rpc-mi_referrer": "https://user.mihoyo.com/login-platform/index.html?app_id=dw9y09jqjpxc&theme=passport&token_type=4&game_biz=plat_cn&message_origin=https%253A%252F%252Fuser.mihoyo.com&succ_back_type=message%253Alogin-platform%253Alogin-success&fail_back_type=message%253Alogin-platform%253Alogin-fail&ux_mode=popup&iframe_level=1#/login/password",
        "x-rpc-sdk_version": "2.52.0",
        "x-rpc-source": "v2.webLogin",
    }

    cookies = {
        "_MHYUUID": device_id,
        "DEVICEFP_SEED_ID": "6bc4e8b35944de4b",
        "DEVICEFP_SEED_TIME": str(int(time.time() * 1000)),
        "DEVICEFP": "38d818f8368c1",
        "MIHOYO_LOGIN_PLATFORM_LIFECYCLE_ID": lifecycle_id,
    }

    s = requests.Session()
    s.cookies.update(cookies)
    s.headers.update(headers)

    url = "https://passport-api.mihoyo.com/account/ma-cn-passport/web/loginByPassword"
    data = {
        "account": rsa_encrypt(account),
        "password": rsa_encrypt(password),
    }

    resp = s.post(url, json=data)
    result = resp.json()

    if result.get("retcode") == 0:
        print("=== 登录成功 ===")
        print(
            "用户信息:",
            json.dumps(result["data"]["user_info"], indent=2, ensure_ascii=False),
        )
        print("\n=== 重要 Token ===")
        for k in [
            "cookie_token",
            "ltoken",
            "ltuid",
            "account_id",
            "cookie_token_v2",
            "ltoken_v2",
            "ltmid_v2",
            "ltuid_v2",
            "account_mid_v2",
            "account_id_v2",
        ]:
            if k in s.cookies:
                print(f"  {k} = {s.cookies[k]}")
    else:
        print("登录失败:", result)

    return s.cookies.get_dict()


if __name__ == "__main__":
    cookies = login("15322349311", "943576081zdkZDK")
