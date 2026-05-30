import requests
import time
import json
import hashlib
import csv
import os
from urllib.parse import quote, urlparse


# ======================
# 1. 配置区
# ======================

OID = "716346290"        # 视频 aid，也就是评论接口里的 oid
TYPE = 1                # 1 表示视频评论
MODE = 3                # 3 热门/综合，2 按时间
MAX_PAGES = 50          # 主评论最多爬多少页
SLEEP = 1.2             # 主评论每页间隔
LIKE_LIMIT = 100        # 只保存点赞数 >= 100 的评论

CRAWL_FULL_SUB_REPLIES = True    # 是否完整爬取楼中楼
SUB_REPLY_PS = 20                # 楼中楼每页数量
SUB_REPLY_SLEEP = 0.6            # 楼中楼翻页间隔

OUTPUT_FILE = "bilibili_comments_like_100.csv"


# Cookie 可填可不填
# 注意：不要写中文，例如“你的SESSDATA”
# 可以直接复制浏览器里的 Cookie 整段
COOKIE = r"""buvid3=56FEC1DF-5748-D67A-3738-6FB0C2A211B897753infoc; SESSDATA=5efc8e10%2C1792052401%2C7fd53%2A41CjBvo3tsfUYzNiZGgz23jnfTX7NsY_jgEW8FdF6XXrzFOCwD5e2dO5nhvl6Zv0jvdIUSVk56dUMzYXVzMk1XZTlIdWdWNXBBN0tMdjdjVkFpYlVKa3BZMlQ2Z0JEb3FmTHB0aEFtODRoZ3NreFZURzY4X21ObVBnVmFNNVJRYk5rYW5FVlEtdjRnIIEC; bili_jct=d72ba988e8ee8af4f73a2d8a06363fdd; DedeUserID=437579001""".strip()

# 不想用 Cookie 就改成：
# COOKIE = ""


# ======================
# 2. WBI 签名算法
# ======================

MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32,
    15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19,
    29, 28, 14, 39, 12, 38, 41, 13,
    37, 48, 7, 16, 24, 55, 40, 61,
    26, 17, 0, 1, 60, 51, 30, 4,
    22, 25, 54, 21, 56, 59, 6, 63,
    57, 62, 11, 36, 20, 34, 44, 52
]


def get_mixin_key(orig: str) -> str:
    return ''.join(orig[i] for i in MIXIN_KEY_ENC_TAB)[:32]


def get_file_stem_from_url(url: str) -> str:
    path = urlparse(url).path
    filename = os.path.basename(path)
    return os.path.splitext(filename)[0]


def get_wbi_keys(session: requests.Session):
    """
    获取 img_key 和 sub_key
    """
    url = "https://api.bilibili.com/x/web-interface/nav"

    res = session.get(url, timeout=10)
    res.raise_for_status()

    data = res.json()

    if data.get("code") != 0:
        raise Exception(f"获取 WBI key 失败：{data}")

    wbi_img = data["data"]["wbi_img"]

    img_url = wbi_img["img_url"]
    sub_url = wbi_img["sub_url"]

    img_key = get_file_stem_from_url(img_url)
    sub_key = get_file_stem_from_url(sub_url)

    return img_key, sub_key


def enc_wbi(params: dict, img_key: str, sub_key: str) -> dict:
    """
    给参数添加 wts 和 w_rid
    """
    mixin_key = get_mixin_key(img_key + sub_key)

    params = params.copy()
    params["wts"] = int(time.time())

    chr_filter = "!'()*"
    clean_params = {}

    for k, v in params.items():
        if isinstance(v, str):
            v = ''.join(ch for ch in v if ch not in chr_filter)
        clean_params[k] = v

    query = '&'.join(
        f"{quote(str(k), safe='')}={quote(str(clean_params[k]), safe='')}"
        for k in sorted(clean_params)
    )

    w_rid = hashlib.md5((query + mixin_key).encode("utf-8")).hexdigest()
    clean_params["w_rid"] = w_rid

    return clean_params


# ======================
# 3. 请求接口
# ======================

def get_main_comment_page(session, img_key, sub_key, offset=""):
    """
    获取主评论页
    """
    pagination_str = json.dumps(
        {"offset": offset},
        ensure_ascii=False,
        separators=(",", ":")
    )

    params = {
        "oid": OID,
        "type": TYPE,
        "mode": MODE,
        "pagination_str": pagination_str,
        "plat": 1,
        "web_location": 1315875
    }

    signed_params = enc_wbi(params, img_key, sub_key)

    url = "https://api.bilibili.com/x/v2/reply/wbi/main"

    res = session.get(url, params=signed_params, timeout=15)
    res.raise_for_status()

    return res.json()


def get_sub_reply_page(session, img_key, sub_key, root_rpid, pn=1):
    """
    获取某条主评论下面的楼中楼回复
    """
    params = {
        "oid": OID,
        "type": TYPE,
        "root": root_rpid,
        "ps": SUB_REPLY_PS,
        "pn": pn,
        "web_location": 1315875
    }

    signed_params = enc_wbi(params, img_key, sub_key)

    url = "https://api.bilibili.com/x/v2/reply/reply"

    res = session.get(url, params=signed_params, timeout=15)
    res.raise_for_status()

    return res.json()


# ======================
# 4. 解析评论
# ======================

def format_time(ctime):
    if not ctime:
        return ""

    return time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(ctime)
    )


def parse_reply(reply: dict, comment_type="主评论", root_rpid=""):
    member = reply.get("member") or {}
    content = reply.get("content") or {}

    return {
        "评论类型": comment_type,
        "rpid": reply.get("rpid"),
        "root": root_rpid or reply.get("root") or "",
        "parent": reply.get("parent") or "",
        "用户": member.get("uname"),
        "uid": member.get("mid"),
        "性别": member.get("sex"),
        "等级": member.get("level_info", {}).get("current_level"),
        "评论": content.get("message"),
        "点赞": reply.get("like") or 0,
        "回复数": reply.get("rcount") or 0,
        "时间": format_time(reply.get("ctime"))
    }


# ======================
# 5. 保存 CSV
# ======================

def save_to_csv(comments, filename):
    if not comments:
        print("没有符合条件的数据可保存")
        return

    fieldnames = [
        "评论类型",
        "rpid",
        "root",
        "parent",
        "用户",
        "uid",
        "性别",
        "等级",
        "评论",
        "点赞",
        "回复数",
        "时间"
    ]

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(comments)

    print(f"\n已保存到：{os.path.abspath(filename)}")


# ======================
# 6. 筛选逻辑
# ======================

def add_if_like_enough(item, liked_comments):
    like_count = item.get("点赞") or 0

    if like_count >= LIKE_LIMIT:
        liked_comments.append(item)

        print(
            f'【符合条件】[{item["评论类型"]}] '
            f'{item["用户"]}: {item["评论"]} '
            f'👍{item["点赞"]}'
        )

        return True

    return False


# ======================
# 7. 完整爬取楼中楼
# ======================

def crawl_full_sub_replies(session, img_key, sub_key, root_rpid, liked_comments, seen_rpids):
    """
    完整爬取某条主评论下的楼中楼回复
    """
    pn = 1

    while True:
        try:
            data = get_sub_reply_page(session, img_key, sub_key, root_rpid, pn)
        except Exception as e:
            print(f"楼中楼请求异常 root={root_rpid}, pn={pn}：{e}")
            break

        if data.get("code") != 0:
            print(f"楼中楼请求失败 root={root_rpid}, pn={pn}：{data}")
            break

        reply_data = data.get("data") or {}
        replies = reply_data.get("replies") or []

        if not replies:
            break

        for child in replies:
            child_item = parse_reply(
                child,
                comment_type="楼中楼",
                root_rpid=root_rpid
            )

            child_rpid = child_item.get("rpid")

            if child_rpid in seen_rpids:
                continue

            seen_rpids.add(child_rpid)
            add_if_like_enough(child_item, liked_comments)

        page_info = reply_data.get("page") or {}
        count = page_info.get("count") or 0
        size = page_info.get("size") or SUB_REPLY_PS

        if pn * size >= count:
            break

        pn += 1
        time.sleep(SUB_REPLY_SLEEP)


# ======================
# 8. 主爬虫逻辑
# ======================

def crawl_comments():
    session = requests.Session()

    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "origin": "https://www.bilibili.com",
        "referer": "https://www.bilibili.com/video/BV13X4y1P7z7/",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/148.0.0.0 Safari/537.36"
        )
    }

    if COOKIE:
        try:
            COOKIE.encode("latin-1")
        except UnicodeEncodeError:
            raise ValueError(
                "COOKIE 里包含中文或特殊字符，请删除中文占位符，例如：你的SESSDATA、你的bili_jct"
            )

        headers["cookie"] = COOKIE

    session.headers.update(headers)

    img_key, sub_key = get_wbi_keys(session)

    print("img_key:", img_key)
    print("sub_key:", sub_key)

    offset = ""

    liked_comments = []
    seen_rpids = set()

    total_main_comments = 0
    total_checked_comments = 0

    for page in range(1, MAX_PAGES + 1):
        print(f"\n正在爬取主评论第 {page} 页，offset = {offset!r}")

        try:
            data = get_main_comment_page(session, img_key, sub_key, offset)
        except Exception as e:
            print("主评论请求异常：", e)
            break

        if data.get("code") != 0:
            print("主评论请求失败：", data)
            break

        reply_data = data.get("data") or {}
        replies = reply_data.get("replies") or []

        if not replies:
            print("没有更多主评论了")
            break

        for reply in replies:
            main_item = parse_reply(reply, comment_type="主评论")
            main_rpid = main_item.get("rpid")

            if main_rpid in seen_rpids:
                continue

            seen_rpids.add(main_rpid)

            total_main_comments += 1
            total_checked_comments += 1

            add_if_like_enough(main_item, liked_comments)

            # 先处理主评论接口自带的少量楼中楼
            child_replies = reply.get("replies") or []

            for child in child_replies:
                child_item = parse_reply(
                    child,
                    comment_type="楼中楼",
                    root_rpid=main_rpid
                )

                child_rpid = child_item.get("rpid")

                if child_rpid in seen_rpids:
                    continue

                seen_rpids.add(child_rpid)
                total_checked_comments += 1

                add_if_like_enough(child_item, liked_comments)

            # 再完整爬取楼中楼
            rcount = reply.get("rcount") or 0

            if CRAWL_FULL_SUB_REPLIES and rcount > len(child_replies):
                print(f"正在爬取楼中楼 root={main_rpid}，预计回复数：{rcount}")
                crawl_full_sub_replies(
                    session=session,
                    img_key=img_key,
                    sub_key=sub_key,
                    root_rpid=main_rpid,
                    liked_comments=liked_comments,
                    seen_rpids=seen_rpids
                )

        cursor = reply_data.get("cursor") or {}
        pagination_reply = cursor.get("pagination_reply") or {}
        next_offset = pagination_reply.get("next_offset")

        print(f"当前已检查评论数：{len(seen_rpids)}")
        print(f"点赞 >= {LIKE_LIMIT} 的评论数：{len(liked_comments)}")

        if not next_offset:
            print("next_offset 为空，爬取结束")
            break

        offset = next_offset
        time.sleep(SLEEP)

    save_to_csv(liked_comments, OUTPUT_FILE)

    print("\n爬取完成")
    print(f"主评论数量：{total_main_comments}")
    print(f"已检查评论总数：{len(seen_rpids)}")
    print(f"点赞数 >= {LIKE_LIMIT} 的评论数：{len(liked_comments)}")


if __name__ == "__main__":
    crawl_comments()