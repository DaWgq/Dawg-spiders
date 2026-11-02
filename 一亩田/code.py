import argparse
import csv
import json
import os
import socket
import time
import uuid
from pathlib import Path
from typing import Any

import requests


URL = (
    "https://m.ymt.com/gfw/dn-price-trend/"
    "hangqing_chandi/api/origin_price_search_v1"
)
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 6789
HTTP_PROXY = f"http://{PROXY_HOST}:{PROXY_PORT}"
SOCKS_PROXY = f"socks5://{PROXY_HOST}:{PROXY_PORT}"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "content-type": "application/json",
    "origin": "https://m.ymt.com",
    "referer": "https://m.ymt.com/hangqing/juhe-8016",
    "user-agent": (
        "Mozilla/5.0 (Linux; Android 15; Pixel 9) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0.0.0 Mobile Safari/537.36"
    ),
    "x-app-version": "V1.0.1",
    "x-user-agent": "4001",
}

COOKIES = {
    "__51uvsct__3JpntAJHFqKIGDSK": "1",
    "__51vcke__3JpntAJHFqKIGDSK": "99980896-ee28-5819-9fe1-0eaef312bbe7",
    "__51vuft__3JpntAJHFqKIGDSK": "1784866242632",
    "Hm_lvt_910abd56d68f662e980cbb010333d8f5": "1784866243",
    "HMACCOUNT": "45FC6488ADA4CC26",
    "acw_tc": "3ccdc17317848662455802671e969f5d343b4c304adb5bae53f227fabc65fc",
    "ymtwebgfwuuid": "6a62e5c5e375bb7255764cb2000000",
    "mymtcominitedUUID": "1",
    "mymtcom_uid": "334542668487162",
}


def configure_proxy(session: requests.Session) -> None:
    """检查本地代理，并确保本进程及 requests 会话只通过该代理联网。"""
    try:
        with socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=2):
            pass
    except OSError as exc:
        raise RuntimeError(
            f"本地代理 {PROXY_HOST}:{PROXY_PORT} 不可用，已停止抓取"
        ) from exc

    proxy_env = {
        "HTTP_PROXY": HTTP_PROXY,
        "HTTPS_PROXY": HTTP_PROXY,
        "ALL_PROXY": SOCKS_PROXY,
        "NO_PROXY": "localhost,127.0.0.1,::1",
        "http_proxy": HTTP_PROXY,
        "https_proxy": HTTP_PROXY,
        "all_proxy": SOCKS_PROXY,
        "no_proxy": "localhost,127.0.0.1,::1",
    }
    os.environ.update(proxy_env)
    session.proxies.update({"http": HTTP_PROXY, "https": HTTP_PROXY})


def build_params() -> list[tuple[str, str]]:
    """生成每次请求需要的查询参数。"""
    return [
        ("app_key", "4001"),
        ("app_key", "4001"),
        ("ts", str(int(time.time() * 1000))),
        ("fCode", "1000010"),
        ("version", "6.2.0"),
        ("channel", "ssr_channel"),
        ("logid", uuid.uuid4().hex),
    ]


def fetch_page(
    session: requests.Session,
    page: int,
    page_size: int,
    timeout: float,
) -> tuple[list[dict[str, Any]], bool]:
    """抓取一页行情，返回该页数据及是否还有下一页。"""
    payload = {
        "product_id": 8016,
        "index": page,
        "length": page_size,
        "breed_id": -1,
        "query": "鲜辣椒",
        "location_id": -1,
        "orderby_name": "trend_val",
        "orderby_sortby": "ASC",
        "stag": {},
    }
    response = session.post(
        URL,
        params=build_params(),
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()

    try:
        body = response.json()
    except requests.exceptions.JSONDecodeError as exc:
        raise RuntimeError(
            f"第 {page} 页没有返回合法 JSON：{response.text[:200]}"
        ) from exc

    if not body.get("success") or body.get("status") != 0:
        raise RuntimeError(f"第 {page} 页接口返回失败：{body}")

    result = body.get("result")
    if not isinstance(result, dict):
        raise RuntimeError(f"第 {page} 页缺少 result 对象")

    items = result.get("list", [])
    if not isinstance(items, list):
        raise RuntimeError(f"第 {page} 页的 result.list 不是列表")

    rows = []
    for item in items:
        if not isinstance(item, dict):
            continue
        rows.append({"page": page, **item})
    return rows, bool(result.get("list_has_more"))


def normalize_csv_value(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return value


def save_csv(rows: list[dict[str, Any]], output: Path) -> None:
    if not rows:
        raise RuntimeError("没有抓取到数据，不生成空 CSV")

    # 保留接口原有字段顺序，同时兼容不同页出现新增字段。
    fieldnames: list[str] = []
    for row in rows:
        for field in row:
            if field not in fieldnames:
                fieldnames.append(field)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {key: normalize_csv_value(value) for key, value in row.items()}
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量抓取一亩田鲜辣椒产地行情")
    parser.add_argument("--pages", type=int, default=10, help="抓取页数，默认 10")
    parser.add_argument(
        "--page-size", type=int, default=10, help="每页条数，默认 10"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("一亩田_鲜辣椒行情.csv"),
        help="CSV 保存路径",
    )
    parser.add_argument(
        "--delay", type=float, default=0.5, help="相邻请求间隔秒数，默认 0.5"
    )
    parser.add_argument(
        "--timeout", type=float, default=15, help="单次请求超时秒数，默认 15"
    )
    args = parser.parse_args()
    if args.pages <= 0 or args.page_size <= 0:
        parser.error("--pages 和 --page-size 必须大于 0")
    if args.delay < 0 or args.timeout <= 0:
        parser.error("--delay 不能小于 0，--timeout 必须大于 0")
    return args


def main() -> None:
    args = parse_args()
    all_rows: list[dict[str, Any]] = []

    with requests.Session() as session:
        configure_proxy(session)
        session.headers.update(HEADERS)
        session.cookies.update(COOKIES)

        for page in range(1, args.pages + 1):
            rows, has_more = fetch_page(
                session=session,
                page=page,
                page_size=args.page_size,
                timeout=args.timeout,
            )
            all_rows.extend(rows)
            print(f"第 {page}/{args.pages} 页完成，本页 {len(rows)} 条")

            if not has_more:
                print("接口提示没有更多数据，提前结束")
                break
            if page < args.pages and args.delay:
                time.sleep(args.delay)

    save_csv(all_rows, args.output)
    print(f"抓取完成，共 {len(all_rows)} 条，已保存到：{args.output.resolve()}")


if __name__ == "__main__":
    main()
