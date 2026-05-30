import requests


headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://www.cnmaker.org.cn",
    "Referer": "https://www.cnmaker.org.cn/ds/products.html",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}
cookies = {
    "__jsluid_s": "01a6863f676003e5b06dd5ff52094ae2",
    "JSESSIONID": "0F38120AE013B1FCA607ABCCB4472C03",
    "Hm_lvt_ff8d2c4152fbe13646e0c6b015950a3b": "1780130417",
    "Hm_lpvt_ff8d2c4152fbe13646e0c6b015950a3b": "1780130417",
    "HMACCOUNT": "45FC6488ADA4CC26"
}
url = "https://www.cnmaker.org.cn/doPost"
data = {
    "PFJlcXVlc3QgIGFjdGlvbj0iZHMvYWN0aW9ucy9nZXRQcm9kdWN0cy54bWwiIHJlcXVlc3Q9IkpTT04iIHJlc3BvbnNlPSJKU09OIiA+PERhdGE+eyJzdGFydF9pbmRleCI6MTIsInBhZ2Vfc2l6ZSI6MTIsImNsYXNzaWQiOiIiLCJ0aXRsZSI6IiJ9PC9EYXRhPjwvUmVxdWVzdD4": ""
}
response = requests.post(url, headers=headers, cookies=cookies, data=data)

print(response.text)
print(response)