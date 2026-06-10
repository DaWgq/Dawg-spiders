import requests
import hashlib
import random

USERNAME = str(input('please input you USERNAME:'))
PASSWORD = str(input('please input you PASSWORD:'))
print("initialize login progress.....")

def sha1_hex(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


session = requests.Session()

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://www.doyo.cn",
    "Referer": "https://www.doyo.cn/passport/login?next=/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/148.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

session.headers.update(headers)

# 先访问登录页，初始化 PHPSESSID 等 Cookie
session.get("https://www.doyo.cn/passport/login?next=/", timeout=10)

# 第一步：获取 nonce 和 ts
token_url = "https://www.doyo.cn/User/Passport/token"

params = {
    "username": USERNAME,
    "random": random.random()
}

token_resp = session.get(token_url, params=params, timeout=10)

print("token 状态码:", token_resp.status_code)
print("token 返回:", token_resp.text)

token_json = token_resp.json()

if not token_json.get("result"):
    raise Exception("获取 token 失败")

nonce = str(token_json["nonce"])
ts = str(token_json["ts"])

# 第二步：生成登录密码参数
pwd1 = sha1_hex(PASSWORD)
pwd2 = sha1_hex(nonce + ts + pwd1)

print("第一次 sha1:", pwd1)
print("最终 password:", pwd2)

# 第三步：提交登录
login_url = "https://www.doyo.cn/User/Passport/login"

data = {
    "username": USERNAME,
    "password": pwd2,
    "remberme": "1",   # 注意原网站这里就是 remberme，不是 rememberme
    "next": "JTJG"
}

login_resp = session.post(login_url, data=data, timeout=10)

print("登录状态码:", login_resp.status_code)
print("登录返回:", login_resp.text)
print("当前 Cookie:", session.cookies.get_dict())