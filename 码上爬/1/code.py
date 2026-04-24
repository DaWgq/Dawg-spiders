import requests


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "priority": "u=1, i",
    "referer": "https://www.mashangpa.com/problem-detail/1/",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
}
cookies = {
    "Hm_lvt_0d2227abf9548feda3b9cb6fddee26c0": "1776777924",
    "HMACCOUNT": "45FC6488ADA4CC26",
    "Hm_lpvt_0d2227abf9548feda3b9cb6fddee26c0": "1776777936"
}
url = "https://www.mashangpa.com/api/problem-detail/1/data/"
params = {
    "page": "1"
}
response = requests.get(url, headers=headers, cookies=cookies, params=params)

print(response.text)
print(response)