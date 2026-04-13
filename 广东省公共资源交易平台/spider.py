import requests
import json
import time


headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": "https://ygp.gdzwfw.gov.cn",
    "Referer": "https://ygp.gdzwfw.gov.cn/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "X-Dgi-Req-App": "ggzy-portal",
    "X-Dgi-Req-Nonce": "E1k0YTXeDawSGyQV",
    "X-Dgi-Req-Signature": "41af454aa0edf21638e7eaf9a7f3eff8250070348d9cf1851e05c0cf26b5d121",
    "X-Dgi-Req-Timestamp": "1776088303626",
    "sec-ch-ua": "\"Chromium\";v=\"146\", \"Not-A.Brand\";v=\"24\", \"Google Chrome\";v=\"146\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}
cookies = {
    "_horizon_sid": "1419be5a-bd78-4436-a943-51bf11c07cb7",
    "_horizon_uid": "f6f1bd55-f790-4a2c-9b40-84beb4b8cdb0"
}
url = "https://ygp.gdzwfw.gov.cn/ggzy-portal/mhyy/config/cms/article/queryList"

# 保存结果的列表
result_list = []

# 总共194页
total_pages = 194

for page in range(1, total_pages + 1):
    data = {
        "siteCode": "",
        "categoryCode": "20000-01",
        "title": "",
        "pageNo": page,
        "pageSize": 10,
        "total": "1931"
    }
    data = json.dumps(data, separators=(',', ':'))
    
    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=10)
        response.raise_for_status()
        json_data = response.json()
        
        # 提取数据
        page_data = json_data.get("data", {}).get("pageData", [])
        for item in page_data:
            result_list.append({
                "id": item.get("id"),
                "siteName": item.get("siteName"),
                "title": item.get("title")
            })
            print(item.get("title"), item.get("siteName"), item.get("id"))
        print(f"第 {page}/{total_pages} 页爬取成功，当前共 {len(result_list)} 条数据")
        
        # 每爬取一页暂停2秒，避免请求过于频繁
        if page < total_pages:
            time.sleep(2)
            
    except Exception as e:
        print(f"第 {page} 页爬取出错: {e}")
        # 出错时暂停更长时间
        time.sleep(5)
        continue

# 保存结果到JSON文件
with open("result.json", "w", encoding="utf-8") as f:
    json.dump(result_list, f, ensure_ascii=False, indent=2)

print(f"爬取完成！共获取 {len(result_list)} 条数据，已保存到 result.json")