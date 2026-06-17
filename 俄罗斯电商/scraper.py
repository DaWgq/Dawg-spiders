"""
M.Video (mvideo.ru) 评论爬虫
使用 Playwright 驱动真实浏览器，自动处理 Akamai Bot Manager 保护

原理：
  1. 启动 Chromium 浏览器
  2. 访问目标页面，让浏览器自动执行 Akamai JS 完成验证
  3. 在浏览器上下文中通过 fetch() 调用 BFF API
  4. 解析返回的评论 JSON 数据
"""

import asyncio
import json
import time
from pathlib import Path

from playwright.async_api import async_playwright

# ============================================================
# 配置
# ============================================================
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

BASE_URL = "https://www.mvideo.ru"

# 要爬取的商品
PRODUCTS = [
    {
        "id": "400452396",
        "slug": "holodilnik-midea-mdrb472mgf46om-400452396",
        "name": "Холодильник Midea MDRB472MGF46OM",
    }
]


# ============================================================
# 核心爬虫
# ============================================================


class MvideoScraper:
    """M.Video 评论爬虫"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def start(self):
        """启动浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/149.0.0.0 Safari/537.36"
            ),
            locale="ru-RU",
        )
        self.page = await self.context.new_page()

        # 隐藏自动化特征
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['ru-RU', 'ru', 'en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

    async def stop(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def wait_for_akamai(self, timeout: int = 30):
        """
        等待 Akamai 验证完成
        """
        print("[*] Waiting for Akamai validation...")
        start = time.time()

        # Wait for sp.js to load
        try:
            await self.page.wait_for_function(
                """
                () => {
                    const scripts = Array.from(document.querySelectorAll('script[src]'));
                    return scripts.some(s => s.src.includes('sp.js'));
                }
                """,
                timeout=timeout * 1000,
            )
            print(f"  [+] sp.js loaded ({time.time() - start:.1f}s)")
        except Exception:
            print("  [!] sp.js load timeout, continuing...")

        # Wait for gib cookies
        for i in range(20):
            await asyncio.sleep(1)
            cookies = await self.context.cookies()
            gib_cookies = [
                c["name"] for c in cookies if "gib" in c.get("name", "")
            ]
            if len(gib_cookies) >= 3:
                print(
                    f"  [+] Akamai cookies ready: {gib_cookies} ({time.time() - start:.1f}s)"
                )
                return True

        print(
            f"  [!] Warning: only partial Akamai cookies ({time.time() - start:.1f}s)"
        )
        return False

    async def fetch_reviews(
        self, product_id: str, page_num: int = 1, per_page: int = 20
    ) -> dict:
        """Call BFF reviews API in browser context"""
        url = (
            f"{BASE_URL}/bff/reviews/aplaut"
            f"?context=product"
            f"&contextId={product_id}"
            f"&filter="
            f"&sort=helpfulness:desc"
            f"&page={page_num}"
            f"&perPage={per_page}"
        )

        result = await self.page.evaluate(
            """
            async (url) => {
                try {
                    const resp = await fetch(url, {
                        headers: {
                            'accept': 'application/json',
                            'accept-language': 'ru-RU,ru;q=0.9',
                        },
                        credentials: 'include',
                    });
                    const text = await resp.text();
                    try {
                        return JSON.parse(text);
                    } catch (e) {
                        return { _error: 'json_parse', _text: text.substring(0, 300) };
                    }
                } catch (e) {
                    return { _error: e.message };
                }
            }
            """,
            url,
        )

        if "_error" in result:
            print(f"  [!] API call failed: {result['_error']}")
            if "_text" in result:
                print(f"  [!] Response: {result['_text']}")
            return None

        return result

    async def get_all_reviews(self, product_id: str) -> list:
        """Get all reviews for a product"""
        all_reviews = []

        resp = await self.fetch_reviews(product_id, page_num=1)
        if not resp or not resp.get("success"):
            print(f"  [!] Page 1 failed")
            return all_reviews

        body = resp.get("body", {})
        total_pages = body.get("meta", {}).get("totalPages", 1)
        total_count = body.get("totalNumber", 0)
        reviews = body.get("reviews", [])

        print(f"  Product {product_id}: {total_count} reviews, {total_pages} pages")
        all_reviews.extend(reviews)

        for page in range(2, total_pages + 1):
            await asyncio.sleep(0.8)
            resp = await self.fetch_reviews(product_id, page_num=page)
            if resp and resp.get("success"):
                more = resp.get("body", {}).get("reviews", [])
                all_reviews.extend(more)
                print(f"  [+] Page {page}/{total_pages}: {len(more)} reviews")

        return all_reviews

    async def scrape_product(self, product: dict):
        """Scrape all reviews for a single product"""
        product_id = product["id"]
        slug = product["slug"]

        print(f"\n{'='*60}")
        print(f"Scraping: {product['name']} (ID: {product_id})")
        print(f"{'='*60}")

        # Visit the actual product reviews page to trigger Akamai validation
        page_url = f"{BASE_URL}/products/{slug}/reviews"
        print(f"[*] Navigating to: {page_url}")

        try:
            await self.page.goto(page_url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"  [!] Page navigation error: {e}")

        # Wait for Akamai
        await self.wait_for_akamai()

        # Fetch reviews
        reviews = await self.get_all_reviews(product_id)

        # Save
        output_file = OUTPUT_DIR / f"reviews_{product_id}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "product_id": product_id,
                    "product_name": product["name"],
                    "total": len(reviews),
                    "reviews": reviews,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"  [OK] Saved {len(reviews)} reviews -> {output_file}")
        return reviews

    async def run(self, products: list = None):
        """Run the scraper"""
        if products is None:
            products = PRODUCTS

        try:
            await self.start()
            for product in products:
                await self.scrape_product(product)
        finally:
            await self.stop()


# ============================================================
# Main
# ============================================================


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="M.Video Reviews Scraper")
    parser.add_argument(
        "--visible", action="store_true", help="Show browser window (for debugging)"
    )
    parser.add_argument(
        "--product-id", type=str, default="400452396", help="Product ID"
    )
    parser.add_argument(
        "--slug",
        type=str,
        default="holodilnik-midea-mdrb472mgf46om-400452396",
        help="Product URL slug",
    )
    args = parser.parse_args()

    scraper = MvideoScraper(headless=not args.visible)
    await scraper.run(
        [{"id": args.product_id, "slug": args.slug, "name": f"Product {args.product_id}"}]
    )


if __name__ == "__main__":
    asyncio.run(main())
