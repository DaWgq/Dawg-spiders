import requests
import csv
from datetime import datetime


headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://accounts.klei.com/account/rewards",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}
cookies = {
    "session": "XoeYFeN2KpuZMM7jqsA8Wv06b2wex_p1cEzVaIlU2KY"
}
url = "https://accounts.klei.com/account/rewards/items.json"
response = requests.get(url, headers=headers, cookies=cookies)

# 解析JSON数据
data = response.json()

# 检查请求是否成功
if data.get('ok') and 'data' in data and 'Items' in data['data']:
    items = data['data']['Items']
    
    # 生成文件名（带时间戳）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'科雷物品_{timestamp}.csv'
    
    # 写入CSV文件
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['Name', 'Cost_Name', 'Cost_Amount', 'ItemType', 'Description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # 写入表头
        writer.writeheader()
        
        # 写入数据行
        for item in items:
            writer.writerow({
                'Name': item.get('Name', ''),
                'Cost_Name': item.get('Cost', {}).get('Name', ''),
                'Cost_Amount': item.get('Cost', {}).get('Amount', 0),
                'ItemType': item.get('ItemType', ''),
                'Description': item.get('Description', '')
            })
    
    print(f'成功保存 {len(items)} 条数据到文件: {filename}')
else:
    print('数据获取失败或数据格式错误')
    print(response.text)