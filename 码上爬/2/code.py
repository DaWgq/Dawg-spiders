import requests
import time

headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.mashangpa.com/problem-detail/2/",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
}
cookies = {
    "Hm_lvt_0d2227abf9548feda3b9cb6fddee26c0": "1776777924,1777023360",
    "HMACCOUNT": "45FC6488ADA4CC26",
    "sessionid": "cltgpy5soaoykvyavu7q8jagr2bv6g1e",
    "Hm_lpvt_0d2227abf9548feda3b9cb6fddee26c0": "1777033428"
}
url = "https://www.mashangpa.com/api/problem-detail/2/data/"

# 初始化总总和
total_sum_all_pages = 0

# 遍历第1页到第20页
for page in range(1, 21):
    params = {
        "page": str(page)
    }

    response = requests.get(url, headers=headers, cookies=cookies, params=params)

    # 解析JSON响应
    data = response.json()

    # 获取current_array并求和
    current_array = data.get('current_array', [])
    page_sum = sum(current_array)
    total_sum_all_pages += page_sum

    print(f"第{page}页: current_array={current_array}, 本页总和={page_sum}")

    # 添加短暂延迟,避免请求过快
    time.sleep(0.5)

print("\n" + "=" * 50)
print(f"所有19页的数组元素总和: {total_sum_all_pages}")