import requests
import csv
import time
import uuid
import base64
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
    return base64.b64encode(cipher.encrypt(text.encode("utf-8"))).decode("utf-8")


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

    data = {
        "account": rsa_encrypt(account),
        "password": rsa_encrypt(password),
    }

    resp = s.post(
        "https://passport-api.mihoyo.com/account/ma-cn-passport/web/loginByPassword",
        json=data,
    )
    result = resp.json()

    if result.get("retcode") == 0:
        return s
    raise Exception(f"Login failed: {result}")


def get_action_logs(session, start_time, end_time):
    resp = session.get(
        "https://passport-api.mihoyo.com/account/ma-cn-passport/passport/getActionLogs",
        params={"start_time": start_time, "end_time": end_time},
    )
    result = resp.json()
    if result.get("retcode") != 0:
        raise Exception(f"getActionLogs failed: {result}")
    return result["data"]["logs"]


ACTION_LABELS = {
    1: "登录",
    7: "登出",
    100: "修改密码",
    101: "修改邮箱",
    102: "绑定手机",
    103: "解绑手机",
    104: "绑定邮箱",
    105: "解绑邮箱",
    201: "实名认证",
    202: "实名信息修改",
    401: "冻结账号",
    402: "解冻账号",
    501: "第三方绑定",
    502: "第三方解绑",
}


def main():
    account = "15322349311"
    password = "943576081zdkZDK"

    print("[*] 正在登录米哈游...")
    try:
        session = login(account, password)
        print("[+] 登录成功")
    except Exception as e:
        print(f"[!] 登录失败: {e}")
        return

    now = int(time.time())
    one_month_ago = now - 30 * 24 * 3600

    print(f"[*] 正在获取活动日志 (start={one_month_ago}, end={now})...")
    logs = get_action_logs(session, one_month_ago, now)
    print(f"[+] 获取到 {len(logs)} 条记录")

    for log in logs:
        log["action_label"] = ACTION_LABELS.get(log["action"], f"未知({log['action']})")
        log["log_time_readable"] = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(int(log["log_time"]))
        )

    csv_path = "D:\\Dawg-spiders\\米哈游\\action_logs.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "action",
                "action_label",
                "biz",
                "device_name",
                "addr",
                "ip",
                "log_time",
                "log_time_readable",
            ],
        )
        writer.writeheader()
        writer.writerows(logs)

    print(f"[+] 已保存到 {csv_path}")
    for log in logs:
        print(
            f"    {log['action_label']:8s} | {log['biz']:6s} | {log['device_name']:10s} | {log['addr']:20s} | {log['log_time_readable']}"
        )


if __name__ == "__main__":
    main()
