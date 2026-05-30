import requests
import time
import json
import hashlib
import csv
import os
from urllib.parse import quote
from pathlib import Path


# ======================
# 1. 配置区
# ======================

OID = "716346290"      # 视频 aid，也就是接口里的 oid
TYPE = 1              # 1 表示视频评论
MODE = 3              # 3 一般是热门/综合排序，2 一般是按时间
MAX_PAGES = 50        # 最多爬多少页
SLEEP = 1.2           # 每页间隔，别太快

COOKIE = r"""
buvid3=56FEC1DF-5748-D67A-3738-6FB0C2A211B897753infoc; b_nut=1774279197; buvid_fp=d40b9a502557c4478d29ffe87b8a9238; _uuid=7A6E2E4F-CC9E-ED96-41051-101484110621A836891infoc; home_feed_column=5; browser_resolution=1920-911; buvid4=95260B2C-C5E7-11D3-8BA4-B59BD39E0CC299830-026032323-jXAwpThs/uHcVLyEMMrcEA%3D%3D; CURRENT_QUALITY=0; rpdid=|(Jlk)RJuu|~0J'u~~Yl||J~R; SESSDATA=5efc8e10%2C1792052401%2C7fd53%2A41CjBvo3tsfUYzNiZGgz23jnfTX7NsY_jgEW8FdF6XXrzFOCwD5e2dO5nhvl6Zv0jvdIUSVk56dUMzYXVzMk1XZTlIdWdWNXBBN0tMdjdjVkFpYlVKa3BZMlQ2Z0JEb3FmTHB0aEFtODRoZ3NreFZURzY4X21ObVBnVmFNNVJRYk5rYW5FVlEtdjRnIIEC; bili_jct=d72ba988e8ee8af4f73a2d8a06363fdd; DedeUserID=437579001; CURRENT_FNVAL=4048
""".strip()

# SESSDATA=5efc8e10%2C1792052401%2C7fd53%2A41CjBvo3tsfUYzNiZGgz23jnfTX7NsY_jgEW8FdF6XXrzFOCwD5e2dO5nhvl6Zv0jvdIUSVk56dUMzYXVzMk1XZTlIdWdWNXBBN0tMdjdjVkFpYlVKa3BZMlQ2Z0JEb3FmTHB0aEFtODRoZ3NreFZURzY4X21ObVBnVmFNNVJRYk5rYW5FVlEtdjRnIIEC; bili_jct=d72ba988e8ee8af4f73a2d8a06363fdd; DedeUserID=437579001; buvid3=56FEC1DF-5748-D67A-3738-6FB0C2A211B897753infoc;

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


def get_wbi_keys(session: requests.Session):
    """
    获取 img_key 和 sub_key
    """
    url = "https://api.bilibili.com/x/web-interface/nav"
    res = session.get(url, timeout=10)
    res.raise_for_status()

    data = res.json()
    wbi_img = data["data"]["wbi_img"]

    img_url = wbi_img["img_url"]
    sub_url = wbi_img["sub_url"]

    img_key = Path(img_url).stem
    sub_key = Path(sub_url).stem

    return img_key, sub_key


def enc_wbi(params: dict, img_key: str, sub_key: str) -> dict:
    """
    给参数加 wts 和 w_rid
    """
    mixin_key = get_mixin_key(img_key + sub_key)

    params = params.copy()
    params["wts"] = int(time.time())

    # 过滤特殊字符
    chr_filter = "!'()*"
    clean_params = {}
    for k, v in params.items():
        if isinstance(v, str):
            v = ''.join(ch for ch in v if ch not in chr_filter)
        clean_params[k] = v

    # 按 key 排序
    query = '&'.join(
        f"{quote(str(k), safe='')}={quote(str(clean_params[k]), safe='')}"
        for k in sorted(clean_params)
    )

    w_rid = hashlib.md5((query + mixin_key).encode("utf-8")).hexdigest()
    clean_params["w_rid"] = w_rid

    return clean_params


# ======================
# 3. 评论请求
# ======================

def get_comment_page(session, img_key, sub_key, offset=""):
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


def parse_reply(reply: dict):
    member = reply.get("member") or {}
    content = reply.get("content") or {}

    return {
        "rpid": reply.get("rpid"),
        "用户": member.get("uname"),
        "uid": member.get("mid"),
        "性别": member.get("sex"),
        "等级": member.get("level_info", {}).get("current_level"),
        "评论": content.get("message"),
        "点赞": reply.get("like"),
        "回复数": reply.get("rcount"),
        "时间": time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(reply.get("ctime", 0))
        ) if reply.get("ctime") else "",
    }


def crawl_comments():
    session = requests.Session()

    session.headers.update({
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "origin": "https://www.bilibili.com",
        "referer": "https://www.bilibili.com/video/BV13X4y1P7z7/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/148.0.0.0 Safari/537.36",
        "cookie": COOKIE
    })

    img_key, sub_key = get_wbi_keys(session)
    print("img_key:", img_key)
    print("sub_key:", sub_key)

    offset = ""
    all_comments = []
    seen_rpids = set()

    for page in range(1, MAX_PAGES + 1):
        print(f"\n正在爬取第 {page} 页，offset = {offset!r}")

        data = get_comment_page(session, img_key, sub_key, offset)

        if data.get("code") != 0:
            print("请求失败：", data)
            break

        reply_data = data.get("data") or {}
        replies = reply_data.get("replies") or []

        if not replies:
            print("没有更多评论了")
            break

        for reply in replies:
            item = parse_reply(reply)

            if item["rpid"] in seen_rpids:
                continue

            seen_rpids.add(item["rpid"])
            all_comments.append(item)

            print(
                f'{item["用户"]}: {item["评论"]} '
                f'{item["点赞"]}'
            )

            # 注意：这里顺便保存接口自带的少量楼中楼回复
            # 如果要完整楼中楼，需要另写 /x/v2/reply/reply 接口
            child_replies = reply.get("replies") or []
            for child in child_replies:
                child_item = parse_reply(child)
                if child_item["rpid"] not in seen_rpids:
                    seen_rpids.add(child_item["rpid"])
                    all_comments.append(child_item)

        cursor = reply_data.get("cursor") or {}
        pagination_reply = cursor.get("pagination_reply") or {}

        next_offset = pagination_reply.get("next_offset")

        if not next_offset:
            print("next_offset 为空，爬取结束")
            break

        offset = next_offset
        time.sleep(SLEEP)

    save_to_csv(all_comments)
    print(f"\n完成，共保存 {len(all_comments)} 条评论")


def save_to_csv(comments):
    filename = "bilibili_comments.csv"

    if not comments:
        print("没有数据可保存")
        return

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=comments[0].keys())
        writer.writeheader()
        writer.writerows(comments)

    print(f"已保存到：{os.path.abspath(filename)}")


if __name__ == "__main__":
    crawl_comments()