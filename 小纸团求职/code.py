import requests
import time
import random

# 1. 保持与抓包一致的请求头和 Cookie
headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9",
    "content-type": "application/json",
    "referer": "https://servicewechat.com/wx99fe41e810bd74fa/19/page-frame.html",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541b18) XWEB/20079",
    "xweb_xhr": "1"
}
cookies = {
    "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3ODQzNjA3MDksInVzZXJfaWQiOjQxMTYyMX0.2-wTMVq5mWntpxwflcHVN4Fb2v3peQf3Dpe_4vblipc"
}

url = "https://apiv2.paperball-edu.com/aicv/announcements"

# 2. 初始参数设定
page = 1
ipp = 20
total_scraped = 0

print("=" * 80)
print(f"{'职位名称':<35} | {'公司名称':<20} | {'城市'}")
print("=" * 80)

# 3. 开始翻页循环
while True:
    params = {
        "type": "didShow",
        "ipp": str(ipp),
        "page": str(page),
        "created_at_start": "2026-07-10 00:00:00",  # 可按需修改起始时间
        "created_at_end": "2026-07-10 23:59:59"  # 可按需修改结束时间
    }

    try:
        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=10)
        response.raise_for_status()

        json_data = response.json()
        data_node = json_data.get("data", {})
        objects = data_node.get("objects", [])
        total = data_node.get("total", 0)

        if not objects:
            print(f"\n>> 第 {page} 页无数据，爬取自动结束。")
            break

        # 4. 遍历当前页的数据并输出到控制台
        for job in objects:
            # 提取职位名 (截断过长的名字以保证控制台排版整洁)
            raw_job_name = job.get("name", "未知职位")
            job_name = (raw_job_name[:32] + '..') if len(raw_job_name) > 32 else raw_job_name

            # 提取公司名
            company_info = job.get("company", {})
            company_name = company_info.get("name", "未知公司")

            # 提取城市列表并拼接成字符串
            cities_info = job.get("cities", [])
            city_names = ",".join([c.get("name", "") for c in cities_info]) if cities_info else "未知城市"

            # 格式化输出
            print(f"{job_name:<35} | {company_name:<20} | {city_names}")
            total_scraped += 1

        print("-" * 80)
        print(f">> 第 {page} 页抓取完成，当前进度: {total_scraped}/{total}")
        print("-" * 80)

        # 5. 判断是否翻页结束 (当前页数 * 每页数量 >= 总数据量)
        if page * ipp >= total:
            print("\n>> 所有页面数据已全部抓取完毕！")
            break

        # 翻页
        page += 1

        # 6. 随机休眠防封 (1.5秒 到 3.5秒之间)
        time.sleep(random.uniform(1.5, 3.5))

    except requests.exceptions.RequestException as e:
        print(f"\n>> 网络请求报错，可能是 Token 过期或被拦截: {e}")
        break
    except Exception as e:
        print(f"\n>> 数据解析报错: {e}")
        break

print("=" * 80)
print(f"任务结束。总计输出 {total_scraped} 条数据。")