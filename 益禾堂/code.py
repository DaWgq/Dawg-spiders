import requests
import json
import time

# 1. 基础配置保持不变
headers = {
    "accept": "v=1.0",
    "content-type": "application/json",
    "qm-from": "wechat",
    "qm-user-token": "SzO6_HUSYG5bCknitGfLU63IuCaNeUMKPMH5rkS9c4XBEslGFF8W2y_z7LjMfBJWqTVFFhS5R_qJitT_zQyxRw",
    "referer": "https://servicewechat.com/wx4080846d0cec2fd5/539/page-frame.html",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541b18) XWEB/20079"
}
url = "https://webapi.qmai.cn/web/catering/shop/catering-shop-list"

# 2. 准备你想抓取的城市ID列表 (这里以北上广深为例)
city_ids = ["110000", "310000", "440100", "440300"]
all_shops = []

# 3. 开始双重循环遍历
for city in city_ids:
    print(f"开始抓取城市ID: {city}")
    page = 1

    while True:
        data = {
            "page": page,
            "pageSize": 50,  # 尝试调大 pageSize
            "saleType": 0,
            "pageType": 0,
            "isAppletShow": 1,
            "cityId": city,
            "eVersion": "1.0",
            "lat": "qBtP46E60eL5RkSbQ/jH+w==",  # 保持死数据
            "lng": "tI0gQ3WkJzMQ5yq0dQNnlw==",  # 保持死数据
            "appid": "wx4080846d0cec2fd5"
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response_json = response.json()

            # 检查接口是否请求成功 (需根据实际接口返回的格式调整，这里假设 data.list 存放数据)
            if response_json.get("code") != 0:
                print(f"请求失败或Token过期: {response_json}")
                break

            shop_list = response_json.get("data", {}).get("list", [])

            # 如果当前页没有数据了，说明该城市抓取完毕，跳出 while 循环
            if not shop_list:
                print(f"城市 {city} 抓取完毕。")
                break

            all_shops.extend(shop_list)
            print(f" - 成功抓取第 {page} 页，获取 {len(shop_list)} 家门店。")

            page += 1

            # 基础防封禁：强制休眠 1-2 秒，模拟真人操作
            time.sleep(1.5)

        except Exception as e:
            print(f"抓取发生异常: {e}")
            break

print(f"抓取任务结束，共获取到 {len(all_shops)} 家门店数据。")