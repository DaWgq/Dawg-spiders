"""
B站评论批量爬取 - 支持自动 wbi 签名和分页翻页

用法:
    python reverse.py                    # 默认爬取 BV1V69xB8EJD 的评论
    python reverse.py BVxxxxxxxxxx      # 爬取指定视频的评论
    python reverse.py 116488203737008   # 也可以直接给 oid
"""

import requests
import hashlib
import time
import re
import json
import sys
from urllib.parse import urlencode, quote


# ============================================================
# wbi 签名算法（参考 B站前端源码实现）
# ============================================================

# 固定置换表（mixin key 重排表，B站 wbi 签名固定使用的数组）
MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
    37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
    22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52,
]


def get_mixin_key(raw: str) -> str:
    """根据置换表重排字符串，取前 32 位作为 mixin key"""
    chars = []
    for idx in MIXIN_KEY_ENC_TAB:
        if idx < len(raw):
            chars.append(raw[idx])
    return "".join(chars)[:32]


def get_wbi_keys(session: requests.Session = None) -> tuple:
    """
    从 B站 nav 接口获取 wbi_img 的 img_key 和 sub_key
    返回 (img_key, sub_key)，如果获取失败返回 (None, None)
    """
    s = session or requests.Session()
    try:
        resp = s.get(
            "https://api.bilibili.com/x/web-interface/nav",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.bilibili.com/",
            },
            timeout=10,
        )
        data = resp.json()
        wbi_img = data.get("data", {}).get("wbi_img", {})
        img_url = wbi_img.get("img_url", "")
        sub_url = wbi_img.get("sub_url", "")
        if not img_url or not sub_url:
            return None, None

        # 从 URL 中提取文件名（去掉路径和扩展名）
        img_key = img_url.rsplit("/", 1)[-1].split(".")[0]
        sub_key = sub_url.rsplit("/", 1)[-1].split(".")[0]
        return img_key, sub_key
    except Exception as e:
        print(f"[!] 获取 wbi_keys 失败: {e}")
        return None, None


def sign_params(params: dict, img_key: str, sub_key: str) -> dict:
    """
    对请求参数进行 wbi 签名，自动添加 w_rid 和 wts 字段
    返回新的参数字典（不修改原字典）
    """
    mixin_key = get_mixin_key(img_key + sub_key)
    signed = dict(params)
    signed["wts"] = int(time.time())

    # 按键名排序
    sorted_keys = sorted(signed.keys())
    parts = []
    for k in sorted_keys:
        v = signed[k]
        if v is None:
            continue
        # 字符串值需要先移除特殊字符 !'()*
        if isinstance(v, str):
            v = re.sub(r"[!'()*]", "", v)
        parts.append(f"{quote(str(k))}={quote(str(v))}")

    query_string = "&".join(parts)
    w_rid = hashlib.md5((query_string + mixin_key).encode()).hexdigest()
    signed["w_rid"] = w_rid
    return signed


# ============================================================
# 评论爬取核心
# ============================================================


def get_oid_from_bvid(bvid: str, session: requests.Session) -> str:
    """通过 BV 号获取视频的 oid (aid)"""
    resp = session.get(
        "https://api.bilibili.com/x/web-interface/view",
        params={"bvid": bvid},
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": f"https://www.bilibili.com/video/{bvid}/",
        },
        timeout=10,
    )
    data = resp.json()
    aid = data.get("data", {}).get("aid")
    if not aid:
        raise Exception(f"获取 oid 失败: {data}")
    return str(aid)


def fetch_replies(
    oid: str,
    mode: int = 3,
    cookies: dict = None,
    headers: dict = None,
    page_size: int = 20,
    max_pages: int = None,
    session: requests.Session = None,
    img_key: str = None,
    sub_key: str = None,
):
    """
    批量爬取 B站视频评论（生成器，逐页返回）

    参数:
        oid:         视频 aid
        mode:        评论排序模式 (2=按时间, 3=按热度)
        cookies:     cookie 字典
        headers:     自定义请求头
        page_size:   每页评论数（B站默认 20）
        max_pages:   最大爬取页数，None 表示爬完所有页
        session:     可复用 session
        img_key:     wbi 签名 key（可提前获取以复用）
        sub_key:     wbi 签名 key

    每页 yield:
        {
            "page": int,
            "replies": [...],
            "cursor": {...},
            "total_count": int,
        }
    """
    sess = session or requests.Session()

    # 准备请求头
    base_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
        "Origin": "https://www.bilibili.com",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    if headers:
        base_headers.update(headers)
    sess.headers.update(base_headers)

    # 获取 wbi 签名密钥（只在首次获取）
    if img_key is None or sub_key is None:
        img_key, sub_key = get_wbi_keys(sess)
        if not img_key or not sub_key:
            raise Exception("无法获取 wbi 签名密钥")

    # 分页参数
    pagination_str = json.dumps({"offset": ""})

    page = 0
    while True:
        # 构造请求参数
        params = {
            "oid": oid,
            "type": "1",
            "mode": str(mode),
            "pagination_str": pagination_str,
            "plat": "1",
            "seek_rpid": "",
            "web_location": "1315875",
        }

        # wbi 签名
        signed_params = sign_params(params, img_key, sub_key)

        try:
            resp = sess.get(
                "https://api.bilibili.com/x/v2/reply/wbi/main",
                params=signed_params,
                cookies=cookies,
                timeout=15,
            )
            data = resp.json()
        except Exception as e:
            print(f"[!] 第 {page + 1} 页请求失败: {e}")
            break

        if data.get("code") != 0:
            print(f"[!] API 返回错误: code={data.get('code')}, message={data.get('message')}")
            break

        inner = data.get("data", {})
        cursor = inner.get("cursor", {})
        replies = inner.get("replies", [])
        total_count = inner.get("cursor", {}).get("all_count", 0)

        if not replies:
            print("[*] 已无更多评论")
            break

        page += 1
        yield {
            "page": page,
            "replies": replies,
            "cursor": cursor,
            "total_count": total_count,
        }

        print(f"[+] 第 {page} 页: 获取 {len(replies)} 条评论 (总计 {total_count} 条)")

        # 检查是否还有下一页
        if cursor.get("is_end", False):
            print("[*] 已到达最后一页")
            break

        if max_pages and page >= max_pages:
            print(f"[*] 已达到最大页数 {max_pages}")
            break

        # 更新分页 offset
        pagination_reply = cursor.get("pagination_reply", {})
        next_offset = pagination_reply.get("next_offset", "")
        pagination_str = json.dumps({"offset": next_offset})


def parse_reply(reply: dict) -> dict:
    """解析单条评论，提取关键字段"""
    member = reply.get("member", {})
    return {
        "rpid": reply.get("rpid"),
        "rpid_str": reply.get("rpid_str"),
        "oid": reply.get("oid"),
        "mid": reply.get("mid"),
        "uname": member.get("uname", ""),
        "sex": member.get("sex", ""),
        "level": member.get("level_info", {}).get("current_level", 0),
        "content": reply.get("content", {}).get("message", ""),
        "ctime": reply.get("ctime"),
        "like": reply.get("like", 0),
        "rcount": reply.get("rcount", 0),  # 回复数
        "root": reply.get("root"),
        "parent": reply.get("parent"),
        "dialog": reply.get("dialog"),
        "pictures": reply.get("content", {}).get("pictures", []),
    }


def crawl_all_replies(
    oid: str,
    mode: int = 3,
    cookies: dict = None,
    max_pages: int = None,
    session: requests.Session = None,
) -> list:
    """
    一次性爬取所有评论，返回完整列表
    """
    all_replies = []
    sess = session or requests.Session()

    # 预先获取 wbi keys
    img_key, sub_key = get_wbi_keys(sess)

    for page_data in fetch_replies(
        oid=oid,
        mode=mode,
        cookies=cookies,
        max_pages=max_pages,
        session=sess,
        img_key=img_key,
        sub_key=sub_key,
    ):
        for reply in page_data["replies"]:
            all_replies.append(parse_reply(reply))

    return all_replies


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    # ---------- 配置区 ----------
    # Cookie（必须，否则可能拿不到数据或被限流）
    COOKIES = {
        "buvid3": "56FEC1DF-5748-D67A-3738-6FB0C2A211B897753infoc",
        "b_nut": "1774279197",
        "buvid_fp": "d40b9a502557c4478d29ffe87b8a9238",
        "_uuid": "7A6E2E4F-CC9E-ED96-41051-101484110621A836891infoc",
        "home_feed_column": "5",
        "browser_resolution": "1920-911",
        "buvid4": "95260B2C-C5E7-11D3-8BA4-B59BD39E0CC299830-026032323-jXAwpThs/uHcVLyEMMrcEA%3D%3D",
        "CURRENT_QUALITY": "0",
        "rpdid": "|(Jlk)RJuu|~0J'u~~Yl||J~R",
        "SESSDATA": "5efc8e10%2C1792052401%2C7fd53%2A41CjBvo3tsfUYzNiZGgz23jnfTX7NsY_jgEW8FdF6XXrzFOCwD5e2dO5nhvl6Zv0jvdIUSVk56dUMzYXVzMk1XZTlIdWdWNXBBN0tMdjdjVkFpYlVKa3BZMlQ2Z0JEb3FmTHB0aEFtODRoZ3NreFZURzY4X21ObVBnVmFNNVJRYk5rYW5FVlEtdjRnIIEC",
        "bili_jct": "d72ba988e8ee8af4f73a2d8a06363fdd",
        "DedeUserID": "437579001",
        "DedeUserID__ckMd5": "d4fd9e3306c0831a",
        "theme-tip-show": "SHOWED",
        "theme-avatar-tip-show": "SHOWED",
        "bili_ticket": "eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3ODI2MTMwNjIsImlhdCI6MTc4MjM1MzgwMiwicGx0IjotMX0.JB56NZAQwMD-g5PufPM_ppFZgPUEn50qkmxx_nCj_r8",
        "bili_ticket_expires": "1782613002",
        "sid": "5zdx0e26",
        "CURRENT_FNVAL": "4048",
        "b_lsid": "01BB43AF_19EFC929AED",
    }

    # 目标视频 BV 号 或 直接 oid
    TARGET = sys.argv[1] if len(sys.argv) > 1 else "BV1V69xB8EJD"

    # 最大爬取页数（None = 全部）
    MAX_PAGES = None

    # 评论排序: 2 = 按时间倒序, 3 = 按热度
    MODE = 3
    # ---------------------------

    sess = requests.Session()

    # 解析输入：BV 号或纯 oid
    if TARGET.upper().startswith("BV"):
        print(f"[*] 正在获取视频 {TARGET} 的 oid...")
        oid = get_oid_from_bvid(TARGET, sess)
        print(f"[+] oid = {oid}")
    else:
        oid = TARGET

    # 批量爬取
    print(f"[*] 开始爬取评论 (oid={oid}, mode={MODE}, max_pages={MAX_PAGES or '全部'})")
    print("-" * 50)

    all_replies = crawl_all_replies(
        oid=oid,
        mode=MODE,
        cookies=COOKIES,
        max_pages=MAX_PAGES,
        session=sess,
    )

    print("-" * 50)
    print(f"[+] 共爬取 {len(all_replies)} 条评论")

    # 保存到文件
    output_file = f"comments_{oid}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_replies, f, ensure_ascii=False, indent=2)
    print(f"[+] 已保存到 {output_file}")

    # 打印前几条预览
    print("\n[*] 前 5 条评论预览:")
    for i, reply in enumerate(all_replies[:5]):
        print(f"  [{i + 1}] {reply['uname']} (Lv.{reply['level']}): {reply['content'][:80]}...  👍{reply['like']}")
