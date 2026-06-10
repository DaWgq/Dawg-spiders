import re
import csv
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote


# =========================
# 1. 配置区
# =========================

KEYWORD = "再里印屈赤"
SEARCH_PAGES = 5
COMMENT_PAGES_PER_POST = 20
COMMENT_COUNT = 20

cookies = {
    "SINAGLOBAL": "3823732915230.027.1773378800964",
    "XSRF-TOKEN": "lBFlPdDT_5jJZ9Cnh25GdOms",
    "SCF": "Ah1uWPnNAf1klTmG6nvEPc99T2BLg067X1gYo1t4nVbIg5ql_9FUygF3tebdDv3ADvgndmkHUeHo6uhg81ZHKds.",
    "SUB": "_2A25HJTV0DeRhGeBH6lAZ-CvKwzyIHXVkW8i8rDV8PUNbmtAYLXnukW9NQcAPjkh9QjI3LgRynlhrzXTIzLG4aLNs",
    "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9W5C2LQPrLDvysl7wQhiy9nK5NHD95Qc1K2E1hnfSon7Ws4Dqcj1i--NiKyFiK.Neo-Eeo5t",
    "ALF": "02_1783157285",
    "_s_tentry": "weibo.com",
    "Apache": "7689164403256.149.1780565306124",
    "ULV": "1780565306127:2:1:1:7689164403256.149.1780565306124:1773378800965",
    "WBPSESS": "QYcuJePEwJoYPvmbpIhBsSjdpJQxijYbPNpEp-bE_3IPdYEFBzc0VfwX3WNtpWc9XOzyx01qodqULGTUOgP1f1qC-yhAGgRG8ZP4CPsP5PgsF3Nzm1YO2XMFSZBeN3AN6hn-yZrTkPUXq3JnDqYBsQ=="
}

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/148.0.0.0 Safari/537.36",
}

ajax_headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "client-version": "3.0.0",
    "server-version": "v2026.06.03.2",
    "user-agent": headers["user-agent"],
    "x-requested-with": "XMLHttpRequest",
}

if cookies.get("XSRF-TOKEN"):
    ajax_headers["x-xsrf-token"] = cookies["XSRF-TOKEN"]


# =========================
# 2. mid 转 mblogid
# =========================

BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def base62_encode(num):
    num = int(num)
    if num == 0:
        return "0"

    result = ""
    while num:
        num, rem = divmod(num, 62)
        result = BASE62[rem] + result

    return result


def mid_to_mblogid(mid):
    """
    数字 mid 转微博短 ID。
    例如：
    5305743126561473 -> R2pp6rwWd
    """
    mid = str(mid)
    result = []

    for i in range(len(mid), 0, -7):
        start = max(i - 7, 0)
        part = mid[start:i]
        encoded = base62_encode(part)

        if start > 0:
            encoded = encoded.zfill(4)

        result.append(encoded)

    return "".join(reversed(result))


# =========================
# 3. requests 抓搜索页帖子
# =========================

def parse_search_posts(html):
    soup = BeautifulSoup(html, "lxml")

    posts = []
    seen = set()

    cards = soup.select('div.card-wrap[action-type="feed_list_item"]')

    for card in cards:
        mid = card.get("mid")
        if not mid:
            continue

        uid = None
        mblogid = None
        post_url = None

        # 方法一：从 tbinfo 里取 uid
        tbinfo = card.get("tbinfo", "")
        uid_match = re.search(r"ouid=(\d+)", tbinfo)
        if uid_match:
            uid = uid_match.group(1)

        # 方法二：从头像链接里取 uid
        if not uid:
            avatar_a = card.select_one("div.avator a[href]")
            if avatar_a:
                href = avatar_a.get("href", "")
                uid_match = re.search(r"weibo\.com/(?:u/)?(\d+)", href)
                if uid_match:
                    uid = uid_match.group(1)

        # 方法三：从正文链接里取 uid 和 mblogid
        for a in card.select("a[href]"):
            href = a.get("href", "")

            match = re.search(r"weibo\.com/(\d+)/([0-9A-Za-z]+)", href)
            if match:
                uid = match.group(1)
                mblogid = match.group(2)
                post_url = "https://weibo.com/{}/{}".format(uid, mblogid)
                break

        # 如果没拿到 mblogid，就用 mid 自己转
        if uid and not mblogid:
            mblogid = mid_to_mblogid(mid)
            post_url = f"https://weibo.com/{uid}/{mblogid}"

        if not uid:
            continue

        key = f"{uid}_{mid}"
        if key in seen:
            continue

        seen.add(key)

        posts.append({
            "uid": uid,
            "mid": mid,
            "mblogid": mblogid,
            "url": post_url
        })

    return posts


def crawl_search_posts(session, keyword, pages=5):
    all_posts = []
    seen = set()

    for page in range(1, pages + 1):
        url = "https://s.weibo.com/weibo"

        params = {
            "q": keyword,
            "page": page
        }

        print(f"\n正在抓搜索第 {page} 页")

        response = session.get(
            url,
            headers=headers,
            cookies=cookies,
            params=params,
            timeout=15
        )

        print("搜索页状态码：", response.status_code)

        if response.status_code != 200:
            print(response.text[:300])
            break

        html = response.text

        # 简单判断是否被风控或跳登录
        if "登录" in html and "card-wrap" not in html:
            print("可能需要登录或 cookie 已失效")
            break

        posts = parse_search_posts(html)

        print(f"第 {page} 页解析到 {len(posts)} 条微博")

        for post in posts:
            key = post["mid"]
            if key not in seen:
                seen.add(key)
                all_posts.append(post)
                print(post)

        time.sleep(random.uniform(2, 4))

    return all_posts


# =========================
# 4. 抓单条微博评论
# =========================

def parse_comment(item, post):
    user = item.get("user") or {}

    return {
        "帖子URL": post["url"],
        "帖子MID": post["mid"],
        "博主UID": post["uid"],
        "评论ID": item.get("id"),
        "评论内容": item.get("text_raw") or item.get("text"),
        "评论时间": item.get("created_at"),
        "点赞数": item.get("like_counts"),
        "评论用户": user.get("screen_name"),
        "评论用户ID": user.get("idstr"),
        "评论来源": item.get("source"),
    }


def crawl_post_comments(session, post, max_pages=20):
    url = "https://weibo.com/ajax/statuses/buildComments"

    comments = []
    max_id = None
    max_id_type = None
    page = 1

    while True:
        params = {
            "is_reload": "1",
            "id": post["mid"],
            "is_show_bulletin": "2",
            "is_mix": "0",
            "count": str(COMMENT_COUNT),
            "uid": post["uid"],
            "fetch_level": "0",
            "locale": "zh-CN"
        }

        if max_id:
            params["max_id"] = max_id
            params["max_id_type"] = max_id_type if max_id_type is not None else 0

        temp_headers = ajax_headers.copy()
        temp_headers["referer"] = post["url"]

        try:
            response = session.get(
                url,
                headers=temp_headers,
                cookies=cookies,
                params=params,
                timeout=15
            )

            print(f"评论第 {page} 页，状态码：{response.status_code}")

            if response.status_code != 200:
                print(response.text[:300])
                break

            json_data = response.json()

        except Exception as e:
            print("评论接口请求失败：", e)
            break

        data = json_data.get("data", [])

        if not data:
            print("没有更多评论")
            break

        for item in data:
            comment = parse_comment(item, post)
            comments.append(comment)
            print(comment["评论用户"], comment["评论内容"])

        max_id = json_data.get("max_id")
        max_id_type = json_data.get("max_id_type")

        if not max_id or str(max_id) == "0":
            print("该帖评论翻页结束")
            break

        page += 1

        if max_pages and page > max_pages:
            print("达到评论页数限制")
            break

        time.sleep(random.uniform(1.5, 3.5))

    return comments


# =========================
# 5. 保存 CSV
# =========================

def save_csv(data, filename="weibo_comments.csv"):
    if not data:
        print("没有数据可保存")
        return

    with open(filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"\n保存成功：{filename}，共 {len(data)} 条评论")


# =========================
# 6. 主程序
# =========================

def main():
    session = requests.Session()
    session.cookies.update(cookies)

    posts = crawl_search_posts(
        session=session,
        keyword=KEYWORD,
        pages=SEARCH_PAGES
    )

    print(f"\n总共提取到 {len(posts)} 条微博")

    all_comments = []

    for index, post in enumerate(posts, start=1):
        print(f"\n========== 正在抓第 {index}/{len(posts)} 条微博 ==========")
        print(post)

        comments = crawl_post_comments(
            session=session,
            post=post,
            max_pages=COMMENT_PAGES_PER_POST
        )

        all_comments.extend(comments)

        time.sleep(random.uniform(3, 6))

    save_csv(all_comments)


if __name__ == "__main__":
    main()