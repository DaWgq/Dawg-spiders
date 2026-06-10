import requests


headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Authorization": "Bearer eyJhbGciOiJIUzM4NCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsInR5cGUiOiJhY2Nlc3MiLCJpYXQiOjE3ODAzMDEyNzEsImV4cCI6MTc4MDMwMzA3MX0.vDFUoOXOTOEbz7eysXYv9hAD_4AS3nnrfkCkypSxWs8tdhNjCwv_m7HpgbLG8PQs",
    "Connection": "keep-alive",
    "Referer": "http://localhost:3000/profile",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
    "sec-ch-ua": "\"Chromium\";v=\"148\", \"Microsoft Edge\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}
cookies = {
    "satoken": "be8ab89a-3dcf-470d-a55a-7c9e9171bee0"
}
url = "http://localhost:3000/api/user/profile"
response = requests.get(url, headers=headers, cookies=cookies)

print(response.text)
print(response)