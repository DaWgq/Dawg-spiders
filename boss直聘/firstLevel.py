import requests
import time
import random

# 你的原始 headers 和 cookies
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-ch-ua": "\"Chromium\";v=\"148\", \"Microsoft Edge\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "zp_token": "V2RNMuFOf031xoVtRuxxwbLiyy7DrSzSg~|RNMuFOf031xoVtRuxxwbLiyy7Drfwik~",
    "x-requested-with": "XMLHttpRequest",
    "traceid": "F-0019e915d241eTP0ivi0yh",
    "token": "7PXlYq2jGhJWY52s",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.zhipin.com/web/geek/jobs?city=101280600&query=ai%E5%AE%9E%E4%B9%A0",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "priority": "u=1, i"
}

cookies = {
    "Hm_lvt_194df3105ad7148dcf2b98a91b5e727a": "1780551145",
    "HMACCOUNT": "4218FB3A02F37806",
    "__g": "sem_bingpc",
    "wt2": "Do0yiyFcgkcp6Daghvb0Kprb3lVp3tnYNMHUlaSzB5sbV_4WPl_3SuQzzwMzSqarm7ongohk03-AIjTr3r5HKtQ~~",
    "wbg": "0",
    "zp_at": "Cc4_1UN3Piq7pI2XgCwUc6jmUixEfXvmaU7LxMimCAU~",
    "ab_guid": "816c5654-f1a4-4058-ac55-760f1e1dd3cb",
    "lastCity": "101280100",
    "__zp_seo_uuid__": "94363b9c-c3e7-4290-8630-51db37fcbd46",
    "__l": "r=https%3A%2F%2Fcn.bing.com%2F&l=%2Fwww.zhipin.com%2Fsem%2F10.html%3F_ts%3D1780552650819%26sid%3Dsem_bingpc%26qudao%3Dbing_pc_H120003UY5%26plan%3DBOSS-%25E5%25BF%2585%25E5%25BA%2594-%25E5%2593%2581%25E7%2589%258C%26unit%3D%25E7%25B2%25BE%25E5%2587%2586%26keyword%3Dboss%25E7%259B%25B4%25E8%2581%2598%26msclkid%3D905c111b130a188a2b057b3a00c306fa&s=1&g=%2Fwww.zhipin.com%2Fsem%2F10.html%3F_ts%3D1780552650819%26sid%3Dsem_bingpc%26qudao%3Dbing_pc_H120003UY5%26plan%3DBOSS-%25E5%25BF%2585%25E5%25BA%2594-%25E5%2593%2581%25E7%2589%258C%26unit%3D%25E7%25B2%25BE%25E5%2587%2586%26keyword%3Dboss%25E7%259B%25B4%25E8%2581%2598%26msclkid%3D905c111b130a188a2b057b3a00c306fa&s=3&friend_source=0",
    "Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a": "1780552652",
    "__zp_stoken__": "0df7gNTTDn8K4w6TCtlFBO1I1KDk3TjU0TzVMNTR8JDo6S1BQTRjDnsOPw4QZFW3DoMSRw5E0KU83UjU0OTc1UBlPQzo6NFA2OsWLw4s4NjrCsjU%2FI8OGwrXDhyMXbMOKB8OtwrgGwrLDi0HEgsK1BhscwojCuig7HgRWBSJtYx0FIWsEBApWChNVByFaVFRXVGwHIAVWIAgaFU4IwrTCusODQ8OMwrjDgzvCt2zCtTo6S1AoNjrCuzQoUTQ3T1A3xYvEusWRxLnEuMWLxLrFkcOhxIvDr8S6xZHEucOLxYvEusWRw7nDq8WLxLrFkcS5w7rCuj1PwqHCusKjxK7CuXPDqsSUwprDi8SOw4vCrEjCicK9wrZdwqJiXH3ChGVTbFNbwqTDjmFrwr1da2Fdw4PDjcK2wqTCg2hjdGtpHMKQwoHDknMgHlRyBDYTFXHDig%3D%3D",
    "__c": "1780551146",
    "__a": "48939414.1780551145..1780551146.21.1.21.21",
    "bst": "V2RNMuFOf031xoVtRuxxwbLiyy7DrSzSg~|RNMuFOf031xoVtRuxxwbLiyy7Drfwik~",
    "__zp_sseed__": "QxG307Q2Z07rxdsOa7bgENDI7nrnFXFIgF6bTRxXpfk=",
    "__zp_sname__": "0f41efed",
    "__zp_sts__": "1780555262511"}

url = "https://www.zhipin.com/wapi/zpgeek/search/joblist.json"

# 假设我们要爬取前 5 页
max_pages = 5

for page in range(1, max_pages + 1):
    print(f"================ 正在爬取第 {page} 页 ================")

    # 动态构造请求参数
    # 结合你的 referer，通常需要把搜索条件传进去，加上 page 和 时间戳
    params = {
        "query": "ai实习",
        "city": "101280600",
        "page": page,
        "pageSize": 30,  # 默认通常是 30 条一页
        "_": str(int(time.time() * 1000))  # 动态生成当前时间戳
    }

    try:
        # 注意：虽然你提供的是 requests.post，但该接口有时是 GET 请求。
        # 如果 POST 抓不到数据，请尝试改为 requests.get(url, headers=headers, cookies=cookies, params=params)
        response = requests.post(url, headers=headers, cookies=cookies, params=params)

        if response.status_code == 200:
            # 解析 JSON 数据
            data = response.json()

            # 检查返回结果中是否有报错（例如提示风控、要求验证）
            if data.get("code") == 0:
                job_list = data.get("zpData", {}).get("jobList", [])
                print(f"成功获取 {len(job_list)} 条职位信息！")
                # 在这里处理你的职位信息...
            else:
                print(f"第 {page} 页请求失败，服务器返回信息: {data.get('message')}")
                print("⚠️ 这通常意味着你的 Cookie (__zp_stoken__) 已经失效被识别为爬虫。")
                break  # Token失效，退出循环
        else:
            print(f"HTTP 请求失败，状态码: {response.status_code}")
            break

    except Exception as e:
        print(f"请求发生异常: {e}")
        break

    # 随机休眠 3 到 8 秒，模拟真人翻页速度，防止IP被封
    sleep_time = random.uniform(3, 8)
    print(f"休眠 {sleep_time:.2f} 秒后继续...\n")
    time.sleep(sleep_time)