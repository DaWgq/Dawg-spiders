import requests
import csv
import time
import random


headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "origin": "https://v.qq.com",
    "priority": "u=1, i",
    "referer": "https://v.qq.com/",
    "sec-ch-ua": "\"Google Chrome\";v=\"149\", \"Chromium\";v=\"149\", \"Not)A;Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
}


# 这个就是你 URL 里的视频弹幕 ID
video_id = "b4102aosz5u"

# 每次请求 30 秒
step = 30 * 1000

# 视频总时长，自己改，比如 45 分钟
total_minutes = 47
total_ms = total_minutes * 60 * 1000

output_file = "腾讯视频弹幕.csv"

seen_ids = set()
rows = []


for start in range(0, total_ms, step):
    end = start + step

    url = f"https://dm.video.qq.com/barrage/segment/{video_id}/t/v1/{start}/{end}"

    try:
        response = requests.get(url, headers=headers, timeout=10)

        print(f"正在请求：{start // 1000}s - {end // 1000}s，状态码：{response.status_code}")

        if response.status_code != 200:
            print("请求失败，跳过该时间段")
            continue

        data = response.json()

        barrage_list = data.get("barrage_list", [])

        print(f"该时间段获取到 {len(barrage_list)} 条弹幕")

        for item in barrage_list:
            content = item.get("content", "").strip()

            if not content:
                continue

            barrage_id = item.get("id", "")

            # 去重
            if barrage_id and barrage_id in seen_ids:
                continue

            if barrage_id:
                seen_ids.add(barrage_id)

            rows.append({
                "id": barrage_id,
                "time_offset": item.get("time_offset", ""),
                "time_second": int(item.get("time_offset", 0)) // 1000 if str(item.get("time_offset", "")).isdigit() else "",
                "up_count": item.get("up_count", ""),
                "content": content,
                "segment_start": start,
                "segment_end": end
            })

        # 随机等待，别请求太快
        sleep_time = random.uniform(1.5, 3.5)
        print(f"等待 {sleep_time:.2f} 秒...\n")
        time.sleep(sleep_time)

    except Exception as e:
        print(f"请求异常：{repr(e)}")
        print("跳过该时间段\n")
        time.sleep(3)


with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
    fieldnames = [
        "id",
        "time_offset",
        "time_second",
        "up_count",
        "content",
        "segment_start",
        "segment_end"
    ]

    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


print(f"爬取完成，共保存 {len(rows)} 条弹幕")
print(f"保存文件：{output_file}")