import requests


headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Authorization": "9ef6fa06-f6dd-43d6-af06-b98b48acac89",
    "Proxy-Connection": "keep-alive",
    "Referer": "http://8.148.6.214:8081/student/list",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
}
cookies = {
    "ab15b4377af9fb6f19093c2f98301668_ssl": "ba7735f5-6666-4c4f-9156-101876f9e300.eC_HmclVSwrnFspR2ZONTPmjdNM",
    "Authorization": "9ef6fa06-f6dd-43d6-af06-b98b48acac89"
}
url = "http://8.148.6.214:8081/api/student/page"
params = {
    "current": "1",
    "pageSize": "10",
    "keyword": ""
}
response = requests.get(url, headers=headers, cookies=cookies, params=params, verify=False)

print(response.text)
print(response)