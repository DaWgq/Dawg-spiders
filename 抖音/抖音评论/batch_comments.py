import json
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright


COMMENT_API = "https://www.douyin.com/aweme/v1/web/comment/list/"
BASE_PARAMS = {
    "device_platform": "webapp",
    "aid": "6383",
    "channel": "channel_pc_web",
    "item_type": "0",
    "whale_cut_token": "",
    "cut_version": "1",
    "rcFT": "",
    "update_version_code": "170400",
    "pc_client_type": "1",
    "pc_libra_divert": "Windows",
    "support_h265": "1",
    "support_dash": "1",
    "cpu_core_num": "12",
    "version_code": "170400",
    "version_name": "17.4.0",
    "cookie_enabled": "true",
    "screen_width": "1920",
    "screen_height": "1080",
    "browser_language": "zh-CN",
    "browser_platform": "Win32",
    "browser_name": "Chrome",
    "browser_version": "148.0.0.0",
    "browser_online": "true",
    "engine_name": "Blink",
    "engine_version": "148.0.0.0",
    "os_name": "Windows",
    "os_version": "10",
    "device_memory": "16",
    "platform": "PC",
    "downlink": "10",
    "effective_type": "4g",
    "round_trip_time": "150",
    "count": "20",
}


def build_url(aweme_id: str, cursor: int, extra_params: dict = None) -> str:
    params = dict(BASE_PARAMS)
    if extra_params:
        params.update(extra_params)
    params["aweme_id"] = aweme_id
    params["cursor"] = str(cursor)

    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{COMMENT_API}?{query}"


def collect_comments(
    aweme_id: str, max_count: int = None, headless: bool = True
) -> list[dict]:
    all_comments = []
    cursor = 0
    has_more = True
    retries = 3

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/148.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        video_url = f"https://www.douyin.com/video/{aweme_id}"
        print(f"[*] Loading page: {video_url}")
        page.goto(video_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)

        fetch_count = 0
        while has_more:
            if max_count and len(all_comments) >= max_count:
                break

            api_url = build_url(aweme_id, cursor)

            for attempt in range(retries):
                try:
                    result = page.evaluate(
                        """
                        async (url) => {
                            const resp = await fetch(url, {
                                credentials: 'include',
                                headers: {
                                    'Accept': 'application/json, text/plain, */*',
                                    'Referer': 'https://www.douyin.com/'
                                }
                            });
                            if (!resp.ok) {
                                return { error: 'HTTP ' + resp.status };
                            }
                            const data = await resp.json();
                            return {
                                comments: data.comments || [],
                                cursor: data.cursor,
                                has_more: data.has_more,
                                total: data.total,
                                status_code: data.status_code,
                                error: null
                            };
                        }
                    """,
                        api_url,
                    )
                    break
                except Exception as e:
                    print(f"    [!] Attempt {attempt + 1} failed: {e}")
                    time.sleep(3)
                    result = {"error": str(e)}
            else:
                print("    [!] All retries exhausted, stopping.")
                break

            if result.get("error"):
                print(f"    [!] API error: {result['error']}")
                break

            comments = result["comments"]
            cursor = result.get("cursor", cursor)
            has_more = result.get("has_more", 0) == 1

            for c in comments:
                all_comments.append(
                    {
                        "cid": c.get("cid"),
                        "text": c.get("text"),
                        "create_time": c.get("create_time"),
                        "digg_count": c.get("digg_count"),
                        "reply_comment_total": c.get("reply_comment_total"),
                        "ip_label": c.get("ip_label"),
                        "nickname": c.get("user", {}).get("nickname"),
                        "uid": c.get("user", {}).get("uid"),
                        "sec_uid": c.get("user", {}).get("sec_uid"),
                    }
                )

            fetch_count += len(comments)
            print(
                f"    [>] Fetched {len(comments)} comments "
                f"(total: {len(all_comments)}, cursor: {cursor}, "
                f"has_more: {has_more})"
            )
            time.sleep(1)

        browser.close()

    return all_comments


def save_results(aweme_id: str, comments: list[dict], output_dir: str = "."):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comments_{aweme_id}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    data = {
        "aweme_id": aweme_id,
        "collected_at": datetime.now().isoformat(),
        "total": len(comments),
        "comments": comments,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n[+] Saved {len(comments)} comments to: {filepath}")
    return filepath


if __name__ == "__main__":
    import sys

    aweme_id = sys.argv[1] if len(sys.argv) > 1 else "7635719632166341926"

    print(f"[*] Starting comment collection for video: {aweme_id}")
    comments = collect_comments(aweme_id, headless=True)

    if comments:
        save_results(aweme_id, comments, output_dir=".")
        print(f"[+] Done! Total: {len(comments)} comments collected.")
    else:
        print("[!] No comments collected.")
