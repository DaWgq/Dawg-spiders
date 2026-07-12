import requests
import json
import base64
import random
import string
import time
import csv
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# ================= 1. 网易云加密核心算法 =================

MODULUS = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
PUBKEY = "010001"
NONCE = "0CoJUm6Qyw8W8jud"


def get_random_secret_key(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def aes_encrypt(text, key):
    iv = b"0102030405060708"
    pad_text = pad(text.encode('utf-8'), 16)
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
    return base64.b64encode(cipher.encrypt(pad_text)).decode('utf-8')


def rsa_encrypt(text, pub_key, modulus):
    text = text[::-1]
    m = int(text.encode('utf-8').hex(), 16)
    e = int(pub_key, 16)
    n = int(modulus, 16)
    c = pow(m, e, n)
    return format(c, 'x').zfill(256)


def get_weapi_data(plaintext_dict):
    text = json.dumps(plaintext_dict)
    secret_key = get_random_secret_key()
    enc_text = aes_encrypt(text, NONCE)
    params = aes_encrypt(enc_text, secret_key)
    enc_sec_key = rsa_encrypt(secret_key, PUBKEY, MODULUS)
    return {
        "params": params,
        "encSecKey": enc_sec_key
    }


# ================= 2. 爬虫请求配置 =================

headers = {
    "accept": "*/*",
    "origin": "https://music.163.com",
    "referer": "https://music.163.com/playlist?id=469708961",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
}

cookies = {
    "MUSIC_U": "00C4AB8F0E8D326ADDAC504E172CE3EF7AC3E38CFD7FDD68D58ABF36B48245345409DE2FBB66F131393B1F1D38A01A3361EB2539D4A9BA19F1334A04C227E2124E1867D92AC6673D02261EB078CD8E0FB110789E30FBCC2B4EC3679E9ECB3D2924EF42EBEFCC346E4BEDB9244B377E69B34370642C32F782CE50804C4D30590916A040AC2D74FB8B206AB29E89D5703DF901AE9CE995423D7A7C3913246DE48CAF7120D6B41346CE3CBCED3F603E581CF82A32B99D274101B32F8470B38DC3AFF058AEA0ACBF4B3FF3A95EC21DC0D1D2E20B884CB6E3316E9B25A0AAFEB9F6D08FE9152DC95230B3EA16886AD735FAD277028DBE0D6A9C066E267E79FB366703BD07D02A80EC2356CED036DBA55DCD84E9DD6067DF90D7BABA41A8DDCC404741C6BDADED905DFD4270627E858D6A4C7B9BFFBE86CA2C7B10712A2B2B621C173EA1DFA4BC0F79F45DED9D40216C0E2CC0DBA55D88E1E841948E9173B7EB2F86435DE75403E800D5DCD58DCCEED7D696B140A19254D9EC99AD925EFD2A43AFD2AE82BD8015C7491A5F149BA57EFA2AC04CB2BFB79E407C13134255FF8C7D6549817C",
    "__csrf": "a528b19909b8f836a8ab4e1388843ed6"
}

url_params = {
    "csrf_token": "a528b19909b8f836a8ab4e1388843ed6"
}
api_url = "https://music.163.com/weapi/comment/resource/comments/get"


# ================= 3. 数据存储配置 =================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "网易云评论.csv")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")

os.makedirs(DATA_DIR, exist_ok=True)

FIELDNAMES = [
    "comment_id",
    "page",
    "is_hot",
    "thread_id",
    "parent_comment_id",
    "user_id",
    "nickname",
    "vip_type",
    "content",
    "time",
    "time_str",
    "liked_count",
    "reply_count",
    "ip_location",
    "be_replied_count",
]


# ================= 4. 网络重试配置 =================

MAX_RETRIES = 5
RETRY_BASE_WAIT = 2
RETRY_MAX_WAIT = 60

# 请求间隔（秒）：文明爬虫，3-5 秒随机
SLEEP_MIN = 3.0
SLEEP_MAX = 5.0


# ================= 5. 断点续爬与增量保存 =================

def load_progress():
    """加载断点续爬进度：已完成页码集合 + 已见评论 ID 集合 + 游标 cursor。"""
    if not os.path.exists(PROGRESS_FILE):
        return set(), set(), "-1", 0, False
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        completed_pages = set(data.get("completed_pages", []))
        seen_ids = set(data.get("seen_ids", []))
        cursor = data.get("cursor", "-1")
        last_page = data.get("last_page", 0)
        hot_done = data.get("hot_comments_done", False)
        print(f"读取到断点进度：已完成 {len(completed_pages)} 页，已去重 {len(seen_ids)} 条评论")
        return completed_pages, seen_ids, cursor, last_page, hot_done
    except Exception as e:
        print(f"读取进度文件失败（{repr(e)}），从头开始")
        return set(), set(), "-1", 0, False


def save_progress(completed_pages, seen_ids, cursor, last_page, hot_done):
    """持久化断点进度，原子替换避免写一半崩溃损坏文件。"""
    tmp = PROGRESS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({
            "completed_pages": sorted(completed_pages),
            "seen_ids": list(seen_ids),
            "cursor": cursor,
            "last_page": last_page,
            "hot_comments_done": hot_done,
        }, f, ensure_ascii=False)
    os.replace(tmp, PROGRESS_FILE)


def open_csv_writer():
    """打开 CSV，已存在则追加，不存在则新建并写表头。"""
    file_exists = os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 0
    f = open(OUTPUT_FILE, "a", encoding="utf-8-sig", newline="")
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    if not file_exists:
        writer.writeheader()
        f.flush()
    return f, writer


# ================= 6. 请求与解析 =================

def request_with_retry(encrypted_form_data):
    """带指数退避的重试请求，应对网络波动与限流。"""
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                api_url,
                headers=headers,
                cookies=cookies,
                params=url_params,
                data=encrypted_form_data,
                timeout=15
            )
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


def parse_comment(comment, page, is_hot):
    """单条评论 dict -> CSV 行 dict。"""
    user = comment.get("user", {}) or {}
    ip_loc = comment.get("ipLocation", {}) or {}
    if isinstance(ip_loc, dict):
        ip_location = ip_loc.get("location", "") or ""
    else:
        ip_location = str(ip_loc)

    be_replied = comment.get("beReplied", []) or []
    timestamp = comment.get("time", 0) or 0

    return {
        "comment_id": comment.get("commentId", ""),
        "page": page,
        "is_hot": 1 if is_hot else 0,
        "thread_id": comment.get("threadId", ""),
        "parent_comment_id": comment.get("parentCommentId", 0),
        "user_id": user.get("userId", ""),
        "nickname": user.get("nickname", "") or "",
        "vip_type": user.get("vipType", 0) or 0,
        "content": (comment.get("content", "") or "").replace("\r", " ").replace("\n", " "),
        "time": timestamp,
        "time_str": comment.get("timeStr", "") or "",
        "liked_count": comment.get("likedCount", 0) or 0,
        "reply_count": comment.get("replyCount", 0) or 0,
        "ip_location": ip_location,
        "be_replied_count": len(be_replied),
    }


def write_comments(comments, writer, seen_ids, page, is_hot, csv_file):
    """增量写入评论，已见 ID 自动去重。返回新增条数。"""
    new_rows = 0
    for comment in comments:
        comment_id = comment.get("commentId")
        if comment_id and comment_id in seen_ids:
            continue
        if comment_id:
            seen_ids.add(comment_id)

        row = parse_comment(comment, page, is_hot)
        writer.writerow(row)
        new_rows += 1

    csv_file.flush()
    return new_rows


# ================= 7. 翻页爬取主流程 =================

def scrape_comments(thread_id, max_pages=100):
    """
    抓取指定 thread_id 的评论，默认 100 页。
    断点续爬：每抓完一页立刻写盘 + 保存进度，崩溃后下次运行从上次位置继续。
    """
    completed_pages, seen_ids, cursor, last_page, hot_done = load_progress()
    csv_file, writer = open_csv_writer()

    rows_total = 0

    try:
        for page in range(1, max_pages + 1):
            if page in completed_pages:
                print(f"[{page}/{max_pages}] 已完成，跳过")
                continue

            print(f"--- [{page}/{max_pages}] 正在抓取 ---")

            plaintext_payload = {
                "cursor": cursor,
                "pageSize": 20,
                "orderType": 1,
                "pageNo": page,
                "threadId": thread_id
            }

            encrypted_form_data = get_weapi_data(plaintext_payload)

            try:
                response = request_with_retry(encrypted_form_data)
                res_json = response.json()

                if res_json.get("code") != 200:
                    print(f"  接口返回异常 code={res_json.get('code')} msg={res_json.get('message', '')}")
                    time.sleep(3)
                    continue

                data = res_json.get("data", {}) or {}
                comments = data.get("comments", []) or []
                hot_comments = data.get("hotComments", []) or []
                has_more = data.get("hasMore", False)
                next_cursor = data.get("cursor", "")

                print(f"  普通评论 {len(comments)} 条，热评 {len(hot_comments)} 条，hasMore={has_more}")

                # 终止条件 1：评论列表为空（真的没数据了）
                if not comments:
                    print("  本页普通评论为空，判定已抓取完毕")
                    completed_pages.add(page)
                    save_progress(completed_pages, seen_ids, cursor, page, hot_done)
                    break

                # 终止条件 2：cursor 不再变化（API 没有更多数据可给）
                if next_cursor and next_cursor == cursor and page > 1:
                    print(f"  cursor 未变化（{cursor}），判定已抓取完毕")
                    completed_pages.add(page)
                    save_progress(completed_pages, seen_ids, cursor, page, hot_done)
                    break

                new_rows = 0

                # 热评只在第一页返回，且只写一次
                if hot_comments and not hot_done:
                    new_rows += write_comments(hot_comments, writer, seen_ids, page, is_hot=True, csv_file=csv_file)
                    hot_done = True

                new_rows += write_comments(comments, writer, seen_ids, page, is_hot=False, csv_file=csv_file)
                rows_total += new_rows

                cursor = next_cursor or cursor
                completed_pages.add(page)
                save_progress(completed_pages, seen_ids, cursor, page, hot_done)

                print(f"  新增 {new_rows} 条，累计本次 {rows_total} 条，已写入 {OUTPUT_FILE}")

                # 注意：不依赖 hasMore 判断终止，网易云的 hasMore 不可靠
                if not has_more:
                    pass

                sleep_time = random.uniform(SLEEP_MIN, SLEEP_MAX)
                print(f"  等待 {sleep_time:.2f} 秒...\n")
                time.sleep(sleep_time)

            except Exception as e:
                print(f"  请求异常（重试耗尽）：{repr(e)}")
                print("  跳过该页，下次运行会续爬此处\n")
                time.sleep(3)
    finally:
        csv_file.close()

    print(f"\n本次新增保存 {rows_total} 条评论")
    print(f"CSV 文件：{OUTPUT_FILE}")
    print(f"进度文件：{PROGRESS_FILE}")
    print(f"已完成 {len(completed_pages)}/{max_pages} 页")


# 执行抓取任务
if __name__ == "__main__":
    # 歌单 469708961 的评论
    target_thread_id = "A_PL_0_469708961"

    # 抓取 100 页，每页约 20 条
    scrape_comments(target_thread_id, max_pages=100)
