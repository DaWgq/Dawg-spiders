import time
import random
import json
import base64
import hashlib
import requests
import csv
import os
from datetime import datetime
import re


# =========================
# 基础配置
# =========================

# 这里是字体映射表，需要按你当前这次请求的字体来改
FONT_MAP = {
    "&#xedba;": "1",
    "&#xed98;": "9",
    "&#xf7b3;": "0",
    "&#xe83f;": "6",
    "&#xf70e;": "5",
    "&#xe85f;": "8",
    "&#xed4f;": "4",
    "&#xf0f0;": "3",
    "&#xefef;": "2",
}


URL = "https://piaofang.maoyan.com/i/api/dashboard-ajax"
PATH = "/i/api/dashboard-ajax"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/148.0.0.0 Safari/537.36"
)

SIGN_SECRET = "A013F70DB97834C0A5492378BD76C53A"
MYG_PREFIX = "581409236#"

COOKIES = {
    "_lxsdk_cuid": "19eb7cf610fc8-030357773390b7-26061151-1fa400-19eb7cf610fc8",
    "_lxsdk": "19eb7cf610fc8-030357773390b7-26061151-1fa400-19eb7cf610fc8",
    "_lx_utm": "utm_source%3Dgoogle%26utm_medium%3Dorganic",
    "_lxsdk_s": "19eb7cf610f-8c3-825-999%7C%7C1",
}

UID = "cfd702dbd41c89b6dcf6dbb9badff3d6fcea4615"

CHANNEL_ID = "40009"
SVERSION = "2"
ORDER_TYPE = "0"
WUKONG_READY = "h5"

MOVIE_CSV = "maoyan_movie.csv"
WEB_CSV = "maoyan_web.csv"

PRINT_JSON_TO_CONSOLE = True


# =========================
# 签名工具
# =========================

def md5_hex(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()
def decode_maoyan_font(text: str) -> str:
    """
    把猫眼字体加密数字转成明文数字。
    例如：
    &#xedba;&#xed98;&#xf7b3;.&#xe83f;&#xf70e;万 -> 190.65万
    """

    if not text:
        return ""

    text = str(text)

    for code, num in FONT_MAP.items():
        text = text.replace(code, num)

    return text

def b64_ua(ua: str) -> str:
    return base64.b64encode(ua.encode("utf-8")).decode("utf-8")


def now_ms() -> int:
    return int(time.time() * 1000)


def make_trace_id() -> str:
    return str(random.randint(10**18, 10**19 - 1))


def make_sign_key(timestamp: str, index: str) -> str:
    ua_b64 = b64_ua(UA)

    raw = (
        f"method=GET"
        f"&timeStamp={timestamp}"
        f"&User-Agent={ua_b64}"
        f"&index={index}"
        f"&channelId={CHANNEL_ID}"
        f"&sVersion={SVERSION}"
        f"&key={SIGN_SECRET}"
    )

    return md5_hex(raw)


def make_mygsig(params: dict, ts1: int, mygsig_ts: int) -> str:
    sign_obj = {
        **params,
        "path": PATH,
    }

    ordered_keys = [
        "channelId",
        "index",
        "orderType",
        "path",
        "signKey",
        "sVersion",
        "timeStamp",
        "User-Agent",
        "uuid",
        "WuKongReady",
    ]

    values = []

    for key in ordered_keys:
        value = sign_obj.get(key)

        if isinstance(value, (dict, list)):
            value = json.dumps(value, separators=(",", ":"), ensure_ascii=False)

        values.append(str(value))

    qb_str = "_".join(values)
    raw = f"{MYG_PREFIX}{qb_str}${mygsig_ts}"
    ms1 = md5_hex(raw)

    mygsig_obj = {
        "m1": "0.0.3",
        "m2": 0,
        "m3": "0.0.67_tool",
        "ms1": ms1,
        "ts": mygsig_ts,
        "ts1": ts1,
    }

    return json.dumps(mygsig_obj, separators=(",", ":"), ensure_ascii=False)


def build_request():
    req_ts = now_ms()
    timestamp = str(req_ts)
    index = str(random.randint(1, 1000))
    ua_b64 = b64_ua(UA)

    uuid = COOKIES["_lxsdk_cuid"]

    sign_key = make_sign_key(
        timestamp=timestamp,
        index=index,
    )

    params = {
        "orderType": ORDER_TYPE,
        "uuid": uuid,
        "timeStamp": timestamp,
        "User-Agent": ua_b64,
        "index": index,
        "channelId": CHANNEL_ID,
        "sVersion": SVERSION,
        "signKey": sign_key,
        "WuKongReady": WUKONG_READY,
    }

    ts1 = req_ts - random.randint(500, 2000)
    mygsig_ts = req_ts + random.randint(10, 100)

    mygsig = make_mygsig(
        params=params,
        ts1=ts1,
        mygsig_ts=mygsig_ts,
    )

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "m-appkey": "fe_com.sankuai.movie.fe.ipro",
        "m-traceid": make_trace_id(),
        "mygsig": mygsig,
        "priority": "u=1, i",
        "referer": "https://piaofang.maoyan.com/dashboard",
        "sec-ch-ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "uid": UID,
        "user-agent": UA,
        "signKey": sign_key,
    }

    return headers, params


# =========================
# CSV 工具
# =========================

def append_rows_to_csv(file_path: str, fieldnames: list, rows: list):
    if not rows:
        return

    file_exists = os.path.exists(file_path)

    with open(file_path, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerows(rows)


def ts_to_time(ts):
    if not ts:
        return ""

    try:
        ts = int(ts)
        return datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ""

def get_unit_text(obj: dict):
    """
    返回：
    原始 num
    单位
    原始文本
    解密文本
    """

    if not isinstance(obj, dict):
        return "", "", "", ""

    num_raw = obj.get("num", "")
    unit = obj.get("unit", "")

    text_raw = f"{num_raw}{unit}" if num_raw or unit else ""

    num_decode = decode_maoyan_font(num_raw)
    text_decode = f"{num_decode}{unit}" if num_decode or unit else ""

    return num_raw, unit, text_raw, text_decode


# =========================
# 数据解析：电影票房
# =========================

MOVIE_FIELDS = [
    "crawl_time",
    "update_timestamp",
    "update_time",

    "nation_title",
    "nation_box",
    "nation_split_box",
    "nation_show_count",
    "nation_view_count",

    "rank",
    "movie_id",
    "movie_name",
    "release_info",

    "box_rate",
    "box_num_raw",
    "box_unit",
    "box_text_raw",
    "sum_box_desc",

    "split_box_rate",
    "split_box_num_raw",
    "split_box_unit",
    "split_box_text_raw",
    "sum_split_box_desc",

    "show_count",
    "show_count_rate",
    "avg_seat_view",
    "avg_show_view",
]


def parse_movie_rows(data: dict, split_box_num=None, box_num=None):
    movie_list = data.get("movieList", {})
    movie_data = movie_list.get("data", {})

    items = movie_data.get("list", [])
    nation_info = movie_data.get("nationBoxInfo", {})
    update_info = movie_data.get("updateInfo", {})

    update_timestamp = update_info.get("updateTimestamp", "")
    update_time = ts_to_time(update_timestamp)

    nation_box_num, nation_box_unit, nation_box_text_raw, nation_box_text = get_unit_text(
        nation_info.get("nationBoxSplitUnit", {})
    )

    nation_split_num, nation_split_unit, nation_split_text_raw, nation_split_text = get_unit_text(
        nation_info.get("nationSplitBoxSplitUnit", {})
    )

    rows = []
    crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for rank, item in enumerate(items, start=1):
        movie_info = item.get("movieInfo", {})

        box_num_raw, box_unit, box_text_raw, box_text = get_unit_text(
            item.get("boxSplitUnit", {})
        )

        split_box_num_raw, split_box_unit, split_box_text_raw, split_box_text = get_unit_text(
            item.get("splitBoxSplitUnit", {})
        )

        row = {
            "crawl_time": crawl_time,
            "update_timestamp": update_timestamp,
            "update_time": update_time,

            "nation_title": nation_info.get("title", ""),
            "nation_box": nation_box_text,
            "nation_split_box": nation_split_text,
            "nation_show_count": nation_info.get("showCountDesc", ""),
            "nation_view_count": nation_info.get("viewCountDesc", ""),

            "rank": rank,
            "movie_id": movie_info.get("movieId", ""),
            "movie_name": movie_info.get("movieName", ""),
            "release_info": movie_info.get("releaseInfo", ""),

            "box_rate": item.get("boxRate", ""),
            "box_num_raw": box_num,
            "box_unit": box_unit,
            "box_text_raw": box_text,
            "sum_box_desc": item.get("sumBoxDesc", ""),

            "split_box_rate": item.get("splitBoxRate", ""),
            "split_box_num_raw": split_box_num,
            "split_box_unit": split_box_unit,
            "split_box_text_raw": split_box_text,
            "sum_split_box_desc": item.get("sumSplitBoxDesc", ""),

            "show_count": item.get("showCount", ""),
            "show_count_rate": item.get("showCountRate", ""),
            "avg_seat_view": item.get("avgSeatView", ""),
            "avg_show_view": item.get("avgShowView", ""),
        }

        rows.append(row)

    return rows


# =========================
# 数据解析：网播热度
# =========================

WEB_FIELDS = [
    "crawl_time",
    "rank",

    "series_id",
    "series_name",
    "release_info",
    "platform_desc",
    "platform_txt",
    "new_series",

    "curr_heat",
    "curr_heat_desc",
    "bar_value",

    "play_count_num",
    "play_count_unit",
    "play_count_text",
]


def parse_web_rows(data: dict):
    web_list = data.get("webList", {})
    web_data = web_list.get("data", {})

    items = web_data.get("list", [])

    rows = []
    crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for rank, item in enumerate(items, start=1):
        series_info = item.get("seriesInfo", {})

        play_num, play_unit, play_text_raw, play_text = get_unit_text(
            item.get("playCountSplitUnit", {})
        )
        row = {
            "crawl_time": crawl_time,
            "rank": rank,

            "series_id": series_info.get("seriesId", ""),
            "series_name": series_info.get("name", ""),
            "release_info": series_info.get("releaseInfo", ""),
            "platform_desc": series_info.get("platformDesc", ""),
            "platform_txt": series_info.get("platformTxt", ""),
            "new_series": series_info.get("newSeries", ""),

            "curr_heat": item.get("currHeat", ""),
            "curr_heat_desc": item.get("currHeatDesc", ""),
            "bar_value": item.get("barValue", ""),

            "play_count_num": play_num,
            "play_count_unit": play_unit,
            "play_count_text": play_text,
        }

        rows.append(row)

    return rows


def save_parsed_data(data: dict):
    movie_rows = parse_movie_rows(data)
    web_rows = parse_web_rows(data)

    append_rows_to_csv(
        file_path=MOVIE_CSV,
        fieldnames=MOVIE_FIELDS,
        rows=movie_rows,
    )

    append_rows_to_csv(
        file_path=WEB_CSV,
        fieldnames=WEB_FIELDS,
        rows=web_rows,
    )

    print(f"电影数据保存 {len(movie_rows)} 条 -> {MOVIE_CSV}")
    print(f"网播数据保存 {len(web_rows)} 条 -> {WEB_CSV}")


# =========================
# 请求主逻辑
# =========================

def request_once(session: requests.Session):
    headers, params = build_request()

    response = session.get(
        URL,
        headers=headers,
        cookies=COOKIES,
        params=params,
        timeout=15,
    )

    print("=" * 120)
    print("请求时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("状态码:", response.status_code)
    print("请求URL:", response.url)

    try:
        data = response.json()
    except Exception:
        print("响应不是 JSON：")
        print(response.text)
        return response

    if PRINT_JSON_TO_CONSOLE:
        print(json.dumps(data, ensure_ascii=False, indent=2))

    save_parsed_data(data)

    return response


def main():
    session = requests.Session()

    while True:
        try:
            response = request_once(session)

            if response.status_code in [401, 403, 429]:
                print("可能被限制、cookie 失效或签名失效，停止请求。")
                break

        except KeyboardInterrupt:
            print("手动停止。")
            break

        except Exception as e:
            print("请求异常:", repr(e))

        sleep_time = random.uniform(2, 4)
        print(f"等待 {sleep_time:.2f} 秒后继续请求...")
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()