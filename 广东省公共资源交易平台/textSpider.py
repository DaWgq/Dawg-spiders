import re

import requests
import json
import os
import time


# 只保留中文字符
def keep_chinese(text):
    return "".join(re.findall(r"[\u4e00-\u9fff]", text))


def sanitize_filename(name):
    """去除文件名中的非法字符"""
    return re.sub(r'[\\/:*?"<>|]', "_", name)


headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://ygp.gdzwfw.gov.cn/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "X-Dgi-Req-App": "ggzy-portal",
    "X-Dgi-Req-Nonce": "m3dZK3XaVpHzjics",
    "X-Dgi-Req-Signature": "9f1e997be282e5026c5d355b576a8d324bbe8cdddc9eadbe405aa4fb6b4f4fcc",
    "X-Dgi-Req-Timestamp": "1776089962776",
    "sec-ch-ua": "\"Chromium\";v=\"146\", \"Not-A.Brand\";v=\"24\", \"Google Chrome\";v=\"146\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}
cookies = {
    "_horizon_sid": "1419be5a-bd78-4436-a943-51bf11c07cb7",
    "_horizon_uid": "f6f1bd55-f790-4a2c-9b40-84beb4b8cdb0"
}

# 读取result.json
current_dir = os.path.dirname(__file__)
result_path = os.path.join(current_dir, "result.json")
with open(result_path, "r", encoding="utf-8") as f:
    data_list = json.load(f)

print(f"共 {len(data_list)} 条数据需要爬取")

# 创建存储目录
output_dir = os.path.join(current_dir, "articles")
os.makedirs(output_dir, exist_ok=True)

# 记录已爬取的title（断点续传）
crawled_titles = set()
for filename in os.listdir(output_dir):
    if filename.endswith(".txt"):
        crawled_titles.add(filename.replace(".txt", ""))

url_template = "https://ygp.gdzwfw.gov.cn/ggzy-portal/mhyy/config/cms/article/{}"
params = {"siteCode": "44"}

total = len(data_list)
success_count = 0
fail_count = 0

for idx, item in enumerate(data_list):
    item_id = item["id"]
    title = item["title"]
    site_name = item["siteName"]

    # 跳过已爬取的
    safe_title = sanitize_filename(title)
    if safe_title in crawled_titles:
        print(f"[{idx + 1}/{total}] 跳过已爬取: {title}")
        continue

    url = url_template.format(item_id)
    filepath = os.path.join(output_dir, f"{safe_title}.txt")

    try:
        print(f"[{idx + 1}/{total}] 正在爬取: {title}")
        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=10)
        response.raise_for_status()
        json_data = response.json()

        # 提取content字段并清洗，只保留中文
        content = json_data.get("data", {}).get("content", "")
        if not content:
            print(f"  ⚠ 未找到content字段")
            fail_count += 1
            continue

        chinese_content = keep_chinese(content)
        if not chinese_content:
            print(f"  ⚠ content中无中文内容")
            fail_count += 1
            continue

        # 以title作为文件名（清洗非法字符）
        filename = f"{safe_title}.txt"

        # 持久化存储
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(chinese_content)

        success_count += 1
        print(f"  ✓ 保存成功: {filename} (提取中文 {len(chinese_content)} 字)")

    except Exception as e:
        fail_count += 1
        print(f"  ✗ 爬取失败: {e}")

    # 控制请求频率，每次间隔2秒
    if idx < total - 1:
        time.sleep(2)

print(f"\n爬取完成！成功: {success_count} 条，失败: {fail_count} 条")
print(f"文件保存在: {output_dir}")