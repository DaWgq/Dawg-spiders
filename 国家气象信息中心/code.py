import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://data.cma.cn/search/uSearch.html?keywords=%E4%BA%91%E5%8D%97",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

COOKIES = {
    "PHPSESSID": "cte3v1rqti6ifmqdotu44fmvf7",
    "lbinsertroute": "e5f8e2ad362bc9490f97e734625f0327",
    "Hm_lvt_d9508cf73ee2d3c3a3f628fe26bd31ab": "1781063349",
    "HMACCOUNT": "45FC6488ADA4CC26",
    "_pk_id.6.dd70": "517883a60fd6b533.1781063350.",
    "_pk_ses.6.dd70": "1",
    "login_id_chat": "0",
    "Hm_lpvt_d9508cf73ee2d3c3a3f628fe26bd31ab": "1781063469",
    "login_name_chat": "0",
}

HTML_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
}

SEARCH_URL = "https://data.cma.cn/search/searchPage"
BASE_URL = "https://data.cma.cn"
OUTPUT_DIR = "articles"

TOTAL_PAGES = 150
PAGE_SIZE = 10
SEARCH_KEYWORD = "云南"

SESSION = requests.Session()
SESSION.headers.update(HEADERS)
SESSION.cookies.update(COOKIES)


def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.strip()
    if len(name) > 80:
        name = name[:80]
    return name


def fetch_article_list(page_no):
    params = {
        "keywords": SEARCH_KEYWORD,
        "pageNo": str(page_no),
        "pageSize": str(PAGE_SIZE),
        "dataClass": "",
        "spatial": "",
        "timeRes": "",
        "selKey": "",
        "orderBy": "desc",
        "secondKey": "",
        "seClass": "news",
        "categoryId": "3",
        "menuId": "",
        "orderType": "zh",
    }
    resp = SESSION.get(SEARCH_URL, params=params, timeout=30)
    data = resp.json()
    if data.get("returnCode") != 0:
        print(f"  [WARN] API returned code {data.get('returnCode')} for page {page_no}")
        return []
    news = data.get("news", {})
    return news.get("DS", [])


def fetch_article_detail(article_url):
    full_url = BASE_URL + article_url
    resp = SESSION.get(full_url, headers=HTML_HEADERS, timeout=30)
    resp.encoding = "utf-8"
    return resp.text


def parse_article_html(html):
    soup = BeautifulSoup(html, "html.parser")

    title_elem = soup.select_one("#titleDiv")
    title = title_elem.get_text(strip=True) if title_elem else ""

    article_elem = soup.select_one("#articleDiv")
    if not article_elem:
        return title, "", []

    md_lines = []
    images = []

    for child in article_elem.children:
        if not hasattr(child, "name"):
            continue

        if child.name == "p":
            imgs = child.find_all("img")
            if imgs:
                for img in imgs:
                    src = img.get("src", "")
                    if src:
                        if src.startswith("//"):
                            src = "https:" + src
                        images.append(src)
                        md_lines.append(f"\n![图片]({src})\n")
            else:
                text = child.get_text(strip=True)
                if text:
                    md_lines.append(text + "\n")

    body = "\n".join(md_lines)
    return title, body, images


def save_markdown(title, body, article_id, created):
    safe_title = sanitize_filename(title)
    filename = f"{article_id}_{safe_title}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"> 发布时间: {created}\n\n")
        f.write(body)

    return filepath


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    total_articles = 0
    total_saved = 0

    for page in range(1, TOTAL_PAGES + 1):
        print(f"\n[PAGE {page}/{TOTAL_PAGES}] Fetching article list...")
        articles = fetch_article_list(page)

        if not articles:
            print(f"  No articles on page {page}, skipping.")
            time.sleep(1)
            continue

        print(f"  Got {len(articles)} articles.")

        for idx, article in enumerate(articles):
            article_id = article.get("ArticleID", "")
            title = article.get("Title", "")
            created = article.get("Created", "")
            url = article.get("url", "")

            if not url:
                print(f"    [{idx + 1}] SKIP: no url for {title}")
                continue

            total_articles += 1
            print(f"    [{idx + 1}] {title}")

            try:
                html = fetch_article_detail(url)
                detail_title, body, images = parse_article_html(html)

                if not body.strip():
                    content_text = article.get("Content", "")
                    if content_text:
                        body = content_text + "\n"

                if body.strip():
                    filepath = save_markdown(
                        detail_title or title, body, article_id, created
                    )
                    total_saved += 1
                    print(f"           -> saved: {filepath}")
                else:
                    print(f"           -> SKIP: empty body")

            except Exception as e:
                print(f"           -> ERROR: {e}")

            time.sleep(1.5)

        print(f"  Page {page} done. Total saved so far: {total_saved}")
        time.sleep(2)

    print(f"\n{'=' * 50}")
    print(f"DONE! Total articles processed: {total_articles}, saved: {total_saved}")
    print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    main()
