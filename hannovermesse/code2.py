import requests
import re
import csv
import time
import json

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.hannovermesse.de",
    "priority": "u=0, i",
    "referer": "https://www.hannovermesse.de/en/search/?category=ep",
    "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
}

TOTAL_PAGES = 482
OUTPUT_FILE = "exhibitor_links.csv"
DELAY = 1.5
EMPTY_LIMIT = 3


def get_state(html):
    m = re.search(r'<input\s+name="state"\s+value="([^"]+)"', html)
    return m.group(1) if m else None


def parse_hrefs(html):
    return re.findall(r'href="(/exhibitor/[^"]+)"', html)


def main():
    session = requests.Session()
    session.headers.update(headers)

    print("Getting fresh session...")
    resp = session.get("https://www.hannovermesse.de/en/search/?category=ep")
    state = get_state(resp.text)
    if not state:
        print("ERROR: Could not find initial state!")
        return
    print(f"Initial state: {state}")

    all_links = set()
    empty_count = 0

    try:
        for page in range(1, TOTAL_PAGES + 1):
            action = json.dumps({"action": "page", "value": str(page)})
            data = {"action": action, "search": "", "state": state, "category": "ep"}

            try:
                resp = session.post(
                    "https://www.hannovermesse.de/en/search/", data=data
                )
            except Exception as e:
                print(f"Page {page}: Request failed - {e}")
                time.sleep(DELAY * 3)
                continue

            if resp.status_code != 200:
                print(f"Page {page}: HTTP {resp.status_code}")
                time.sleep(DELAY * 3)
                continue

            links = parse_hrefs(resp.text)
            all_links.update(links)
            print(
                f"Page {page}: found {len(links)} links (total unique: {len(all_links)})"
            )

            if len(links) == 0:
                empty_count += 1
                if empty_count >= EMPTY_LIMIT:
                    print(f"No results for {EMPTY_LIMIT} consecutive pages, stopping.")
                    break
            else:
                empty_count = 0

            new_state = get_state(resp.text)
            if new_state:
                state = new_state

            time.sleep(DELAY)

    except KeyboardInterrupt:
        print("\nInterrupted, saving results so far...")

    sorted_links = sorted(all_links)
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["exhibitor_url"])
        for link in sorted_links:
            writer.writerow([link])

    print(f"\nDone! Saved {len(sorted_links)} unique links to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
