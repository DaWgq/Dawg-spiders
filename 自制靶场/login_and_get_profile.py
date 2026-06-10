import requests
import json


# ========== 第一步：登录 ==========

headers_login = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": "http://localhost:3000",
    "Referer": "http://localhost:3000/login/plain",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
    "sec-ch-ua": '"Chromium";v="148", "Microsoft Edge";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}
cookies = {"satoken": "be8ab89a-3dcf-470d-a55a-7c9e9171bee0"}

login_url = "http://localhost:3000/api/login/plain"
login_data = json.dumps(
    {"username": "admin", "password": "123456"}, separators=(",", ":")
)

print("=== 第一步：登录 ===")
resp_login = requests.post(
    login_url, headers=headers_login, cookies=cookies, data=login_data
)
print("登录响应状态码:", resp_login)
print("登录响应体:", resp_login.text)

# 尝试从登录响应中提取 token（假设返回 JSON 格式，如 {"token": "xxx"}）
try:
    login_json = resp_login.json()
    # 兼容多种可能的字段名
    token = (
        login_json.get("token")
        or login_json.get("data", {}).get("token")
        or login_json.get("access_token")
    )
except Exception:
    token = None

if not token:
    print("\n[警告] 未能从登录响应中自动提取 token，将尝试继续...")
else:
    print(f"\n提取到的 token: {token}")


# ========== 第二步：使用 token 获取用户信息 ==========

headers_profile = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    # 如果从登录拿到了 token，就用动态 token；否则回退到硬编码的测试 token
    "Authorization": f"Bearer {token}"
    if token
    else "Bearer eyJhbGciOiJIUzM4NCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsInR5cGUiOiJhY2Nlc3MiLCJpYXQiOjE3ODAzMDEyNzEsImV4cCI6MTc4MDMwMzA3MX0.vDFUoOXOTOEbz7eysXYv9hAD_4AS3nnrfkCkypSxWs8tdhNjCwv_m7HpgbLG8PQs",
    "Connection": "keep-alive",
    "Referer": "http://localhost:3000/profile",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
    "sec-ch-ua": '"Chromium";v="148", "Microsoft Edge";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

profile_url = "http://localhost:3000/api/user/profile"

print("\n=== 第二步：获取用户信息 ===")
resp_profile = requests.get(profile_url, headers=headers_profile, cookies=cookies)
print("用户信息响应状态码:", resp_profile)
print("用户信息响应体:", resp_profile.text)
