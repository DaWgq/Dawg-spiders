"""
B站评论批量采集
使用 x/v2/reply/main 接口 (无需WBI签名)
"""
import requests
import json
import time


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com/",
}


def get_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def get_reply_page(session: requests.Session, oid: str, mode: int = 3, next: str = "0", pagination_str: str = "{}") -> dict:
    """
    获取一页评论

    参数:
        oid:  视频 aid
        type: 1=视频
        mode: 3=最热, 2=最新
        next: 游标 (第一页传 "0")
        pagination_str: 翻页参数 (JSON字符串, 含 offset)
    """
    params = {
        "oid": oid,
        "type": "1",
        "mode": str(mode),
        "next": next,
        "pagination_str": pagination_str,
    }
    resp = session.get("https://api.bilibili.com/x/v2/reply/main", params=params)
    return resp.json()


def get_all_replies(session: requests.Session, oid: str, mode: int = 3, max_pages: int = 999) -> list:
    """
    批量获取全部评论，自动翻页

    Returns:
        list[dict]: 原始回复数据
    """
    all_replies = []
    page = 1
    cursor = None

    while page <= max_pages:
        if cursor and cursor.get("is_end"):
            print("已到达最后一页")
            break

        pagination_str = "{}"
        next_val = "0"

        if cursor:
            pagination_str = json.dumps({
                "offset": cursor.get("pagination_reply", {}).get("next_offset", ""),
            })
            next_val = cursor.get("next", "0")

        data = get_reply_page(session, oid, mode=mode, next=next_val, pagination_str=pagination_str)

        if data.get("code") != 0:
            print(f"[第{page}页] API错误: {data.get('message')}")
            break

        replies = data.get("data", {}).get("replies", [])
        cursor = data.get("data", {}).get("cursor", {})

        if not replies and page > 1:
            print("[第{page}页] 没有更多评论")
            break

        all_replies.extend(replies)
        print(f"[第{page}页] 获取 {len(replies)} 条, 累计 {len(all_replies)} 条")

        page += 1
        time.sleep(0.8)

    return all_replies


def extract_comments(replies: list) -> list[dict]:
    """
    提取评论关键信息 (平铺, 含子回复)
    """
    results = []

    def flatten(reply_list):
        for reply in reply_list:
            member = reply.get("member", {})
            content = reply.get("content", {})
            level_info = member.get("level_info", {}) or {}
            results.append({
                "rpid": reply.get("rpid"),
                "mid": member.get("mid"),
                "uname": member.get("uname"),
                "avatar": member.get("avatar"),
                "message": (content.get("message", "") or "").replace("\n", " "),
                "like": reply.get("like"),
                "rcount": reply.get("rcount", 0),
                "ctime": reply.get("ctime"),
                "level": level_info.get("current_level", 0),
            })
            if "replies" in reply and reply["replies"]:
                flatten(reply["replies"])

    flatten(replies)
    return results


def save_to_json(comments: list, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)
    print(f"\n已保存 {len(comments)} 条评论到 {filename}")


def save_to_txt(comments: list, filename: str):
    """保存为可读文本格式"""
    with open(filename, "w", encoding="utf-8") as f:
        for i, c in enumerate(comments, 1):
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(c["ctime"]))
            f.write(f"{i}. [{ts}] {c['uname']}(LV{c['level']}): {c['message']}\n")
    print(f"已保存可读文本到 {filename}")


def save_to_csv(comments: list, filename: str):
    """保存为CSV格式"""
    import csv
    with open(filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["序号", "用户ID", "用户名", "评论内容", "点赞数", "回复数", "用户等级", "时间"])
        for i, c in enumerate(comments, 1):
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(c["ctime"]))
            writer.writerow([i, c["mid"], c["uname"], c["message"], c["like"], c["rcount"], c["level"], ts])
    print(f"已保存CSV到 {filename}")


# ============================================================
# 批量爬取多个视频
# ============================================================

def batch_crawl(video_list: list[dict], mode: int = 3, max_pages: int = 999):
    """
    批量爬取多个视频的评论

    video_list: [{"aid": "xxx", "title": "标题"}, ...]
    mode: 3=最热, 2=最新
    """
    session = get_session()

    for video in video_list:
        oid = video["aid"]
        title = video.get("title", oid)
        print(f"\n{'='*50}")
        print(f"正在爬取: {title} (aid={oid})")
        print(f"{'='*50}")

        replies = get_all_replies(session, oid, mode=mode, max_pages=max_pages)

        if replies:
            comments = extract_comments(replies)
            safe_title = title.replace("/", "_").replace("\\", "_").replace(":", "_")
            save_to_json(comments, f"comments_{safe_title}.json")
            save_to_csv(comments, f"comments_{safe_title}.csv")
            save_to_txt(comments, f"comments_{safe_title}.txt")
        else:
            print("未获取到评论")

        time.sleep(1)


if __name__ == "__main__":
    # ========== 配置区 ==========
    oid = "116492163095535"    # 视频 aid
    mode = 3                    # 3=最热, 2=最新
    max_pages = 999             # 最大页数 (默认爬完)
    # ===========================

    session = get_session()
    replies = get_all_replies(session, oid, mode=mode, max_pages=max_pages)

    if replies:
        comments = extract_comments(replies)
        save_to_json(comments, "bilibili_comments.json")
        save_to_csv(comments, "bilibili_comments.csv")
        save_to_txt(comments, "bilibili_comments.txt")

        # 打印前5条
        print("\n=== 前5条评论 ===")
        for c in comments[:5]:
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(c["ctime"]))
            print(f"[{ts}] {c['uname']}(LV{c['level']}): {c['message'][:80]}")
    else:
        print("没有获取到评论")
