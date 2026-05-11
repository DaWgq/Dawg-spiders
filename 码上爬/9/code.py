import time
import base64
import hmac
import hashlib
import requests
import json
import os


def get_params(page):
    # 13位毫秒时间戳
    ts = str(int(time.time() * 1000))

    # tt = btoa(timestamp)
    tt = base64.b64encode(ts.encode("utf-8")).decode("utf-8")

    # m = HmacSHA1("9527" + timestamp, "xxxooo")
    text = "9527" + ts
    key = "xxxooo"

    m = hmac.new(
        key.encode("utf-8"),
        text.encode("utf-8"),
        hashlib.sha1
    ).hexdigest()

    return {
        "page": page,
        "m": m,
        "tt": tt
    }


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "origin": "https://www.mashangpa.com",
    "pragma": "no-cache",
    "referer": "https://www.mashangpa.com/problem-detail/9/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}

cookies = {
    "sessionid": "cltgpy5soaoykvyavu7q8jagr2bv6g1e"
}

url = "https://www.mashangpa.com/api/problem-detail/9/data/"
progress_file = "mashangpa_9_progress.json"
result_file = "mashangpa_9_result.json"

# 加载进度文件（如果存在）
def load_progress():
    if os.path.exists(progress_file):
        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"completed_pages": [], "total_array": [0] * 10}

# 保存进度
def save_progress(progress_data):
    with open(progress_file, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=4)

# 初始化或加载进度
progress = load_progress()
total_array = progress.get("total_array", [0] * 10)
completed_pages = set(progress.get("completed_pages", []))

print(f"已完成的页数: {sorted(completed_pages)}")
print(f"当前累加数组: {total_array}")
print()

# 批量爬取20页数据（断点续爬）
for page in range(1, 21):
    # 跳过已完成的页面
    if page in completed_pages:
        print(f"第 {page} 页已完成，跳过")
        continue
    
    print(f"正在爬取第 {page} 页...")
    
    data = get_params(page)
    
    success = False
    retry_count = 0
    max_retries = 3
    
    while not success and retry_count < max_retries:
        try:
            resp = requests.post(
                url,
                headers=headers,
                cookies=cookies,
                data=json.dumps(data, separators=(",", ":")),
                timeout=10
            )
            
            if resp.status_code == 200:
                result = resp.json()
                current_array = result.get("current_array", [])
                
                # 检查是否获取到有效数据
                if len(current_array) == 10:
                    # 累加当前页的数组值
                    for i in range(len(current_array)):
                        total_array[i] += current_array[i]
                    
                    print(f"第 {page} 页爬取成功，current_array: {current_array}")
                    
                    # 标记该页已完成并保存进度
                    completed_pages.add(page)
                    progress["completed_pages"] = sorted(list(completed_pages))
                    progress["total_array"] = total_array
                    save_progress(progress)
                    
                    success = True
                else:
                    print(f"第 {page} 页数据异常（数组长度:{len(current_array)}），将重试...")
                    retry_count += 1
                    time.sleep(2)
            else:
                print(f"第 {page} 页请求失败，状态码: {resp.status_code}，将重试...")
                retry_count += 1
                time.sleep(2)
                
        except Exception as e:
            print(f"第 {page} 页爬取出错: {str(e)}，将重试...")
            retry_count += 1
            time.sleep(2)
    
    if not success:
        print(f"⚠️ 第 {page} 页经过{max_retries}次重试后仍然失败，请稍后重新运行程序继续爬取")
    
    # 添加延迟，避免请求过快
    time.sleep(1)

# 输出最终结果
print("\n" + "="*50)
print(f"20页数据累加结果 (已完成{len(completed_pages)}页):")
print(f"total_array: {total_array}")
print(f"数组总和: {sum(total_array)}")
print("="*50)

# 保存结果到文件（只有全部完成才保存最终结果）
if len(completed_pages) == 20:
    result_data = {
        "total_pages": 20,
        "total_array": total_array,
        "sum": sum(total_array)
    }
    
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=4)
    
    print("\n✅ 所有页面爬取完成！结果已保存到", result_file)
    
    # 清理进度文件
    if os.path.exists(progress_file):
        os.remove(progress_file)
        print("进度文件已清理")
else:
    print(f"\n⚠️ 还有 {20 - len(completed_pages)} 页未完成，请重新运行程序继续爬取")
    print("进度已保存，下次运行将从断点继续")