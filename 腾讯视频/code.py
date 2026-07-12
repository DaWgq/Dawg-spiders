import requests
import csv
import time
import random
import json
import os


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
progress_file = "腾讯视频弹幕.progress.json"

fieldnames = [
    "id",
    "time_offset",
    "time_second",
    "up_count",
    "content",
    "segment_start",
    "segment_end"
]

# 网络重试配置
MAX_RETRIES = 5          # 单个分段最大重试次数
RETRY_BASE_WAIT = 2      # 重试基础等待秒数，指数退避
RETRY_MAX_WAIT = 60      # 单次重试最长等待


def load_progress():
    """加载断点续爬进度：已完成分段 + 已见弹幕 id，用于去重。"""
    if not os.path.exists(progress_file):
        return set(), set()
    try:
        with open(progress_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        completed = set(data.get("completed", []))
        seen_ids = set(data.get("seen_ids", []))
        print(f"读取到断点进度：已完成 {len(completed)} 个分段，已去重 {len(seen_ids)} 条弹幕")
        return completed, seen_ids
    except Exception as e:
        print(f"读取进度文件失败（{repr(e)}），从头开始")
        return set(), set()


def save_progress(completed, seen_ids):
    """持久化断点进度，崩溃后可从上次位置续爬。"""
    tmp = progress_file + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({
            "completed": sorted(completed),
            "seen_ids": list(seen_ids),
        }, f, ensure_ascii=False)
    # 原子替换，避免写一半崩溃损坏进度文件
    os.replace(tmp, progress_file)


def open_csv_writer():
    """打开 CSV，已存在则追加，不存在则新建并写表头。"""
    file_exists = os.path.exists(output_file) and os.path.getsize(output_file) > 0
    f = open(output_file, "a", encoding="utf-8-sig", newline="")
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    if not file_exists:
        writer.writeheader()
        f.flush()
    return f, writer


def request_with_retry(url):
    """带指数退避的重试请求，应对网络波动。"""
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            # 5xx / 429 视为可重试
            if response.status_code in (429,) or 500 <= response.status_code < 600:
                raise requests.HTTPError(f"状态码 {response.status_code}")
            return response
        except Exception as e:
            last_exc = e
            if attempt >= MAX_RETRIES:
                break
            wait = min(RETRY_BASE_WAIT * (2 ** (attempt - 1)) + random.uniform(0, 1), RETRY_MAX_WAIT)
            print(f"  第 {attempt}/{MAX_RETRIES} 次请求失败（{repr(e)}），{wait:.1f}s 后重试...")
            time.sleep(wait)
    raise last_exc


def main():
    completed, seen_ids = load_progress()
    csv_file, writer = open_csv_writer()

    total_segments = len(range(0, total_ms, step))
    rows_total = 0

    try:
        for idx, start in enumerate(range(0, total_ms, step), 1):
            end = start + step

            # 断点续爬：跳过已完成的分段
            if start in completed:
                print(f"[{idx}/{total_segments}] {start // 1000}s-{end // 1000}s 已完成，跳过")
                continue

            url = f"https://dm.video.qq.com/barrage/segment/{video_id}/t/v1/{start}/{end}"

            print(f"[{idx}/{total_segments}] 请求：{start // 1000}s - {end // 1000}s")

            try:
                response = request_with_retry(url)

                if response.status_code != 200:
                    print(f"  状态码 {response.status_code}，跳过该时间段（下次续爬会重试）")
                    continue

                data = response.json()
                barrage_list = data.get("barrage_list", [])
                print(f"  获取到 {len(barrage_list)} 条弹幕")

                new_rows = 0
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

                    row = {
                        "id": barrage_id,
                        "time_offset": item.get("time_offset", ""),
                        "time_second": int(item.get("time_offset", 0)) // 1000 if str(item.get("time_offset", "")).isdigit() else "",
                        "up_count": item.get("up_count", ""),
                        "content": content,
                        "segment_start": start,
                        "segment_end": end
                    }
                    # 增量保存：拿到数据立刻写盘，崩溃也不丢
                    writer.writerow(row)
                    new_rows += 1

                csv_file.flush()
                rows_total += new_rows

                # 标记该分段完成并持久化进度
                completed.add(start)
                save_progress(completed, seen_ids)

                print(f"  新增 {new_rows} 条，已写入文件，累计本次 {rows_total} 条")

                # 随机等待，别请求太快
                sleep_time = random.uniform(1.5, 3.5)
                print(f"  等待 {sleep_time:.2f} 秒...\n")
                time.sleep(sleep_time)

            except Exception as e:
                print(f"  请求异常（重试耗尽）：{repr(e)}")
                print("  跳过该时间段，下次运行会续爬此处\n")
                time.sleep(3)
    finally:
        csv_file.close()

    print(f"\n本次新增保存 {rows_total} 条弹幕")
    print(f"文件：{output_file}")
    print(f"已完成分段 {len(completed)}/{total_segments}")


if __name__ == "__main__":
    main()
