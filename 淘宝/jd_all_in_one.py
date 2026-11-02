import os
import re
import time
import random
import urllib.parse
import pandas as pd
from datetime import datetime
from DrissionPage import ChromiumPage, ChromiumOptions

# ================= 1. 全局配置 =================
JD_RAW_CSV = "jd_raw_pool.csv"            # 京东原始候选池
JD_QUEUE_CSV = "jd_target_queue.csv"      # 京东清洗分层后的待抓队列
OUTPUT_DIR = "captured_html"              # 与淘宝共用的 HTML 保存文件夹
INDEX_CSV = "index_table.csv"             # 与淘宝共用的总索引表 (CSV)
INDEX_XLSX = "index_table.xlsx"           # 与淘宝共用的总索引表 (Excel)

TOTAL_PROJECT_TARGET = 300                # 淘宝+京东最终总样本目标（item_001 ~ item_300）
JD_QUEUE_MIN_REQUIRED = 180               # 京东待抓队列最少需要条数（不足则自动扩充列表）
JD_MAX_CAPTURE = 200                      # 京东最多采集详情页数量

# 剔除二手/翻新/配件/耗材 + 假头戴（骨传导/挂耳/入耳/耳夹）
EXCLUDE_KEYWORDS = [
    "二手", "翻新", "9成新", "95新", "99新", "闲置", "官翻", "拍拍",
    "耳罩", "海绵套", "耳垫", "保护套", "耳机套", "横梁套", "头梁垫", "头梁套", "替换",
    "耳机线", "升级线", "音频线", "延长线", "转接线", "转接头",
    "支架", "挂架", "底座", "收纳包", "收纳盒", "硬壳包",
    "维修", "寄修", "换电池", "换皮", "外壳", "配件", "仅配件", "单卖", "空盒",
    "骨传导", "挂耳式", "耳挂式", "颈挂", "挂脖", "入耳式", "半入耳", "耳夹式"
]

JD_BAD_MARKERS = [
    "访问受限", "安全验证", "京东-欢迎登录", "passport.jd.com",
    "cfe.m.jd.com", "verify.jd.com", "风险检测",
]

JD_VALID_MARKERS = [
    "加入购物车", "商品介绍", "规格与包装", "售后保障", "商品评价", "预约抢购", "立即购买"
]

# 详情页固化懒加载图片 + 内联 CSS + 移除 <script>
JD_INLINE_DOM_JS = """
return (async () => {
    document.querySelectorAll('img').forEach(img => {
        const realSrc = img.getAttribute('data-lazyload') || img.getAttribute('data-src') || img.src;
        if (realSrc && !realSrc.startsWith('data:')) {
            img.src = realSrc.startsWith('//') ? 'https:' + realSrc : realSrc;
            img.removeAttribute('data-lazyload');
            img.removeAttribute('data-src');
            img.removeAttribute('loading');
        }
        img.style.maxWidth = '100%';
    });

    document.querySelectorAll('[style*="url(//"]').forEach(el => {
        el.style.backgroundImage = el.style.backgroundImage.replace(/url\\(["']?\\/\\//g, 'url("https://');
    });

    const links = Array.from(document.querySelectorAll('link[rel="stylesheet"]'));
    for (const link of links) {
        try {
            const href = link.href.startsWith('//') ? 'https:' + link.href : link.href;
            if (!href) continue;
            const resp = await fetch(href);
            if (resp.ok) {
                const cssText = await resp.text();
                const style = document.createElement('style');
                style.textContent = cssText;
                link.parentNode.replaceChild(style, link);
            }
        } catch (e) {
            if (link.getAttribute('href') && link.getAttribute('href').startsWith('//')) {
                link.href = 'https:' + link.getAttribute('href');
            }
        }
    }

    document.querySelectorAll('[src^="//"], [href^="//"]').forEach(el => {
        if (el.src && el.getAttribute('src').startsWith('//')) el.src = 'https:' + el.getAttribute('src');
        if (el.href && el.getAttribute('href').startsWith('//')) el.href = 'https:' + el.getAttribute('href');
    });

    document.body.style.overflow = 'auto';
    document.documentElement.style.overflow = 'auto';
    document.querySelectorAll('script, link[as="script"], link[rel="preload"], iframe').forEach(el => el.remove());

    return "<!DOCTYPE html>\\n" + document.documentElement.outerHTML;
})();
"""

# 【升级版】精准提取京东店铺名（解决全部变成“京东自营/官方店”的问题）+ 提取商品卡片
EXTRACT_JD_SEARCH_JS = """
return (() => {
    const results = [];
    const seen = new Set();
    const cards = document.querySelectorAll('li.gl-item, div[data-sku], div.plugin_goodsCardWrapper');

    cards.forEach(card => {
        let sku = card.getAttribute('data-sku') || '';
        if (!sku) {
            const innerSkuEl = card.querySelector('[data-sku]');
            if (innerSkuEl) sku = innerSkuEl.getAttribute('data-sku') || '';
        }
        if (!sku) {
            const linkEl = card.querySelector('a[href*="item.jd.com/"]');
            if (linkEl) {
                const m = linkEl.href.match(/item\\.jd\\.com\\/(\\d+)\\.html/);
                if (m) sku = m[1];
            }
        }
        if (!sku || seen.has(sku)) return;

        const spu = card.getAttribute('data-spu') || sku;

        // 提取标题
        const nameEl = card.querySelector('.p-name em, .p-name a, [class*="goods_title"], [class*="title"]');
        let title = nameEl ? nameEl.innerText.replace(/\\s+/g, ' ').trim() : '';
        if (!title) return;

        // 提取价格
        const priceEl = card.querySelector('.p-price i, .p-price strong, [class*="price"]');
        const price_str = priceEl ? priceEl.innerText.trim() : '0';

        // 提取评价数/销量
        const commitEl = card.querySelector('.p-commit a, .p-commit strong, [class*="comment"], [class*="commit"]');
        const sales_raw = commitEl ? commitEl.innerText.trim() : '0';

        // 精准提取真实店铺名（支持新版京东 مال/shop 链接与 title 属性）
        let shop_name = '';
        const shopEl = card.querySelector('.p-shop a, .hd-shopname, a[href*="mall.jd.com"], a[title*="旗舰店"], a[title*="专卖店"], a[title*="专营店"], a[title*="自营"], [class*="shopName"], [class*="shop"]');
        if (shopEl) {
            shop_name = (shopEl.getAttribute('title') || shopEl.innerText || '').trim();
        }
        // 如果还是没提取到，用标题里的品牌前缀区分店铺，绝不让所有商品共用同一个假店名导致被误删！
        if (!shop_name) {
            shop_name = '京东店_' + title.slice(0, 6);
        }

        seen.add(sku);
        results.push({
            item_id: sku.trim(),
            spu_id: spu.trim(),
            title: title,
            price_str: price_str,
            sales_raw: sales_raw,
            shop_name: shop_name
        });
    });
    return results;
})();
"""


# ================= 2. 阶段一：多词 + 真实点击翻页扩充京东商品池 =================
def parse_jd_commit(commit_str: str) -> int:
    if not commit_str:
        return 0
    s = str(commit_str).replace(",", "")
    m = re.search(r"(\d+(?:\.\d+)?)", s)
    if not m:
        return 0
    val = float(m.group(1))
    if "万" in s:
        val *= 10000
    return int(val)


def crawl_jd_search_pool(page: ChromiumPage, existing_raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    通过多个头戴式耳机细分搜索词 + 页面真实点击『下一页』按钮，快速凑够 800+ 原始商品，
    彻底解决单一词 URL 翻页重复导致去重后只有 62 条的问题！
    """
    print("\n🚀 [阶段一] 正在扩充京东『头戴式耳机』候选池（目标清洗后 >= 210 条）...")
    all_items = existing_raw_df.to_dict("records") if not existing_raw_df.empty else []
    seen_skus = {str(r["item_id"]) for r in all_items}

    # 采用 4 个核心词 × 不同排序，并通过点击页面上的“下一页”按钮真实翻页
    search_tasks = [
        ("头戴式耳机", "", 5, "综合排序"),
        ("头戴式耳机", "3", 4, "销量排序"),
        ("头戴式蓝牙耳机", "", 4, "蓝牙细分"),
        ("头戴式游戏耳机", "", 4, "电竞细分"),
        ("头戴式降噪耳机", "1", 3, "价格/长尾细分"),
    ]

    for kw, psort, max_pages, desc in search_tasks:
        kw_enc = urllib.parse.quote(kw)
        url = f"https://search.jd.com/Search?keyword={kw_enc}&enc=utf-8"
        if psort:
            url += f"&psort={psort}"

        page.get(url)
        time.sleep(random.uniform(2.5, 4.0))

        for p in range(1, max_pages + 1):
            # 检查登录或验证
            while (
                "passport.jd.com" in page.url
                or "safe.jd.com" in page.url
                or "verify.jd.com" in page.url
                or "欢迎登录" in (page.title or "")
            ):
                print("\n🚨 请先在 Chrome 窗口中完成京东登录或滑块验证！")
                input("👉 看到商品搜索列表后，按【回车键】继续...")
                time.sleep(2)

            # 滚动到底部加载本页全部 60 个商品
            for _ in range(6):
                page.scroll.down(random.randint(650, 950))
                time.sleep(random.uniform(0.5, 0.9))
            time.sleep(1.2)

            items_on_page = page.run_js(EXTRACT_JD_SEARCH_JS) or []
            new_added = 0
            for it in items_on_page:
                sku = str(it["item_id"])
                if sku in seen_skus:
                    continue
                seen_skus.add(sku)
                new_added += 1

                try:
                    price_val = float(re.findall(r"\d+(?:\.\d+)?", str(it.get("price_str", "0")))[0])
                except IndexError:
                    price_val = 0.0

                sales_num = parse_jd_commit(it.get("sales_raw", "0"))
                all_items.append({
                    "platform": "jd",
                    "item_id": sku,
                    "spu_id": str(it.get("spu_id") or sku),
                    "shop_id": it.get("shop_name", f"京东店_{sku[:4]}"),
                    "shop_name": it.get("shop_name", f"京东店_{sku[:4]}"),
                    "title": it.get("title", ""),
                    "price": price_val,
                    "sales_raw": it.get("sales_raw", "0"),
                    "sales_count": sales_num,
                    "item_url": f"https://item.jd.com/{sku}.html",
                })

            print(f"⏳ [{kw}-{desc}] 第 {p}/{max_pages} 页 -> 提取 {len(items_on_page)} 个，新增不重复 SKU: {new_added} 个（池子累计: {len(all_items)}）")

            # 实时保存一次原始池，防中断丢失
            raw_df = pd.DataFrame(all_items)
            raw_df.to_csv(JD_RAW_CSV, index=False, encoding="utf-8-sig")

            # 如果不重复的原始商品已经超过 650 个，足够洗出 220+ 条，提前结束列表抓取！
            if len(all_items) >= 650:
                print("✅ 京东原始候选池已满 650 条不重复商品，列表扩充完成！")
                return raw_df

            # 模拟点击页面上的“下一页”按钮（兼容旧版 a.pn-next 和新版分页按钮）
            if p < max_pages:
                clicked_next = page.run_js("""
                return (() => {
                    const nextBtn = document.querySelector('a.pn-next, .pn-next, [class*="pagination_next"], a[title="使用方向键右键也可翻到下一页哦！"]');
                    if (nextBtn && !nextBtn.className.includes('disabled')) {
                        nextBtn.click();
                        return true;
                    }
                    // 备用：找包含“下一页”文字的按钮
                    const els = Array.from(document.querySelectorAll('a, button, span'));
                    const target = els.find(el => el.innerText.trim() === '下一页' || el.innerText.trim() === '下一页>');
                    if (target) {
                        target.click();
                        return true;
                    }
                    return false;
                })();
                """)
                if not clicked_next:
                    # 如果没找到按钮，用 URL 强跳下一页
                    next_url = f"https://search.jd.com/Search?keyword={kw_enc}&enc=utf-8&page={(p+1)*2-1}&s={p*60+1}"
                    if psort:
                        next_url += f"&psort={psort}"
                    page.get(next_url)
                time.sleep(random.uniform(3.0, 5.0))

    return pd.DataFrame(all_items)


def clean_and_sample_jd(df: pd.DataFrame, target_total: int = 210) -> pd.DataFrame:
    """修复因为默认店名导致的误删问题，输出 210 条分层队列"""
    print(f"\n📊 京东原始池总条数: {len(df)}")

    # 修复旧数据中全部叫“京东自营/官方店”的字段，用标题前6个字区分不同品牌商，防止跨品牌误删
    def fix_shop_name(row):
        sname = str(row.get("shop_name", ""))
        if not sname or sname in ["京东自营/官方店", "京东自营/第三方店", "京东店"]:
            return "JD_" + re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", str(row["title"]))[:6]
        return sname

    df["shop_name"] = df.apply(fix_shop_name, axis=1)
    df["shop_id"] = df["shop_name"]

    # 1. 剔除二手拍拍、配件耗材、非头戴式及低价引流项
    pattern = "|".join(EXCLUDE_KEYWORDS)
    df = df[~df["title"].str.contains(pattern, case=False, na=False)]
    df = df[df["price"] >= 25.0]
    print(f"✅ 剔除二手/配件/非头戴后剩余: {len(df)} 条")

    # 2. 按 item_id (SKU) 去重 + 按 spu_id 去重
    df = df.sort_values(by="sales_count", ascending=False)
    df = df.drop_duplicates(subset=["item_id"], keep="first")
    if "spu_id" in df.columns:
        df = df.drop_duplicates(subset=["spu_id"], keep="first")
    print(f"✅ 按 SKU 与 SPU 去重后剩余: {len(df)} 条")

    # 3. 同店铺同型号去重
    ignore_words = {
        "ANC", "USB", "HIFI", "PRO", "MAX", "PLUS", "FPS", "RGB", "TWS",
        "2024", "2025", "2026", "5.3", "5.4", "7.1", "2.4G", "3.5MM", "TYPEC"
    }

    def make_model_fingerprint(row):
        title = str(row["title"]).upper()
        models = re.findall(r"[A-Z]+[\-]?[0-9]+[A-Z0-9]*|[0-9]+[\-]?[A-Z]+[A-Z0-9]*", title)
        valid_models = [m for m in models if m not in ignore_words and len(m) >= 2]
        if valid_models:
            model_key = valid_models[0]
        else:
            clean_t = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", title)
            model_key = clean_t[:14]
        return f"{row['shop_name']}_{model_key}"

    df["fingerprint"] = df.apply(make_model_fingerprint, axis=1)
    df = df.drop_duplicates(subset=["fingerprint"], keep="first").drop(columns=["fingerprint"])
    print(f"✅ 同商家同款去重后剩余: {len(df)} 条")

    # 4. 高、中、低销量分层抽样
    df = df.sort_values(by="sales_count", ascending=False).reset_index(drop=True)
    n = len(df)
    high_end = int(n * 0.3)
    mid_end = int(n * 0.7)

    df.loc[:high_end, "sales_tier"] = "High (高销量)"
    df.loc[high_end:mid_end, "sales_tier"] = "Medium (中销量)"
    df.loc[mid_end:, "sales_tier"] = "Low (低销量)"

    per_tier = target_total // 3
    sampled_list = []
    for tier in ["High (高销量)", "Medium (中销量)", "Low (低销量)"]:
        sub_df = df[df["sales_tier"] == tier]
        take_n = min(len(sub_df), per_tier)
        if take_n > 0:
            sampled_list.append(sub_df.sample(n=take_n, random_state=42))

    result = pd.concat(sampled_list, ignore_index=True)
    result.to_csv(JD_QUEUE_CSV, index=False, encoding="utf-8-sig")
    print(f"🎉 京东分层队列已更新至 `{JD_QUEUE_CSV}`，当前共 {len(result)} 条有效候选商品！")
    return result


# ================= 3. 阶段二：京东详情页断点续传与 HTML 归档 =================
def is_jd_item_invalid(page: ChromiumPage) -> bool:
    if "www.jd.com" in page.url and "item.jd.com" not in page.url:
        return True
    invalid_markers = [
        "该商品已下柜", "非常抱歉，您查看的商品不存在", "此商品已下架", "商品已下柜"
    ]
    body_text = page.ele("tag:body").text if page.ele("tag:body") else ""
    return any(m in body_text[:1500] for m in invalid_markers)


def strict_jd_guard_check(page: ChromiumPage, target_url: str):
    while True:
        try:
            url = page.url.lower()
            title = page.title or ""
            body_text = page.ele("tag:body").text if page.ele("tag:body") else ""
            full_html = page.html or ""
        except Exception:
            time.sleep(2)
            continue

        if is_jd_item_invalid(page):
            return

        hit_bad = [m for m in JD_BAD_MARKERS if (m in title or m in body_text[:2000] or m in url)]
        has_valid = any(v in body_text or v in full_html for v in JD_VALID_MARKERS)

        if hit_bad or not has_valid:
            print("\a")
            print("\n" + "=" * 65)
            print(f"🚨 【京东安全拦截暂停】原因: {hit_bad if hit_bad else '未检测到正常商品按钮'}")
            print("👉 请切换到 Chrome 窗口，完成京东滑块验证或扫码登录，确认看到正常商品详情页！")
            print("=" * 65)
            input("⏳ 确认页面正常显示后，按【回车键】继续...")
            time.sleep(2.5)
            if "item.jd.com" not in page.url:
                page.get(target_url)
                time.sleep(3)
            continue
        break


def jd_human_scroll_and_load(page: ChromiumPage, target_url: str):
    print("   🖱️ 正在模拟真人滚轮触发京东详情长图加载...")
    try:
        page.actions.move(random.randint(50, 200), random.randint(50, 150), duration=0.3)
    except Exception:
        pass

    total_steps = random.randint(8, 12)
    for step in range(total_steps):
        strict_jd_guard_check(page, target_url)
        page.scroll.down(random.randint(450, 850))
        if random.random() < 0.2 and step > 2:
            time.sleep(0.4)
            page.scroll.up(random.randint(100, 220))
        time.sleep(random.uniform(0.8, 1.6))

    time.sleep(2.0)
    strict_jd_guard_check(page, target_url)


# ================= 4. 主执行入口 =================
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    co = ChromiumOptions()
    co.set_local_port(9222)
    page = ChromiumPage(co)
    print("🌐 已连接 Chrome 浏览器！")

    # 1. 检查本地 jd_target_queue.csv 数量是否够用（少于 180 条则自动扩充！）
    existing_raw = pd.read_csv(JD_RAW_CSV) if os.path.exists(JD_RAW_CSV) else pd.DataFrame()
    need_crawl_more = True

    if not existing_raw.empty:
        test_clean = clean_and_sample_jd(existing_raw.copy(), target_total=210)
        if len(test_clean) >= JD_QUEUE_MIN_REQUIRED:
            jd_df = test_clean
            need_crawl_more = False
            print(f"✅ 现有京东池重筛后已有 {len(jd_df)} 条，无需重新翻页！")

    if need_crawl_more:
        raw_df = crawl_jd_search_pool(page, existing_raw)
        jd_df = clean_and_sample_jd(raw_df, target_total=210)

    # 2. 【断点续传核心】读取 index_table.csv，自动跳过已抓商品，并从最后一个编号+1继续（如 item_125.html）[cite: 7]
    if os.path.exists(INDEX_CSV):
        idx_df = pd.read_csv(INDEX_CSV)
        index_records = idx_df.to_dict("records")
        captured_ids = {str(r["item_id"]) for r in index_records}
        jd_captured_count = sum(1 for r in index_records if r.get("platform") == "jd")
    else:
        index_records = []
        captured_ids = set()
        jd_captured_count = 0

    next_file_num = len(index_records) + 1
    print("\n" + "=" * 65)
    print(f"🔄 【断点续传已就绪】")
    print(f"   - 当前已完成总样本数: {len(index_records)} 个 (其中京东已采: {jd_captured_count} 个)")
    print(f"   - 本次将直接从 `item_{next_file_num:03d}.html` 接着往下采集，自动跳过前面已采过的 SKU！")
    print("=" * 65)

    page.get("https://search.jd.com/Search?keyword=%E5%A4%B4%E6%88%B4%E5%BC%8F%E8%80%B3%E6%9C%BA&enc=utf-8")
    time.sleep(3)

    session_counter = 0
    next_break = random.randint(15, 25)

    for _, row in jd_df.iterrows():
        if len(index_records) >= TOTAL_PROJECT_TARGET or jd_captured_count >= JD_MAX_CAPTURE:
            print(f"\n🎯 已达到采集目标上限（总计 {len(index_records)} 条，京东 {jd_captured_count} 条），全部完成！")
            break

        item_id = str(row["item_id"])
        title = str(row["title"])
        url = f"https://item.jd.com/{item_id}.html"

        # 自动跳过之前已经采过的京东商品 ID
        if item_id in captured_ids:
            continue

        file_name = f"item_{next_file_num:03d}.html"
        file_path = os.path.join(OUTPUT_DIR, file_name)
        print(f"\n[总进度 {len(index_records)+1}/{TOTAL_PROJECT_TARGET} | 京东第 {jd_captured_count+1} 个] 正在采集 -> {file_name} | SKU: {item_id} | {title[:25]}...")

        try:
            js_click = f"""
            let a = document.getElementById('__jd_link');
            if (!a) {{
                a = document.createElement('a');
                a.id = '__jd_link';
                a.rel = 'opener';
                document.body.appendChild(a);
            }}
            a.href = "{url}";
            a.click();
            """
            page.run_js(js_click)
            time.sleep(random.uniform(2.5, 4.0))
            page.wait.doc_loaded(timeout=15)

            strict_jd_guard_check(page, url)

            if is_jd_item_invalid(page):
                print("   ❌ 该京东商品已下柜或失效，自动跳过！")
                continue

            jd_human_scroll_and_load(page, url)

            full_html = page.run_js(JD_INLINE_DOM_JS) or page.html
            if len(full_html) < 25000:
                print("   ⚠️ 导出页面过小，重新检测...")
                strict_jd_guard_check(page, url)
                full_html = page.run_js(JD_INLINE_DOM_JS) or page.html

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(full_html)

            record = {
                "html_filename": file_name,
                "platform": "jd",
                "item_id": item_id,
                "shop_id": row["shop_id"],
                "shop_name": row["shop_name"],
                "title": title,
                "price": row["price"],
                "sales_raw": row["sales_raw"],
                "sales_count": row["sales_count"],
                "sales_tier": row["sales_tier"],
                "item_url": url,
                "capture_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "file_size_kb": round(os.path.getsize(file_path) / 1024, 1),
            }
            index_records.append(record)
            captured_ids.add(item_id)
            next_file_num += 1
            jd_captured_count += 1
            session_counter += 1

            out_df = pd.DataFrame(index_records)
            out_df.to_csv(INDEX_CSV, index=False, encoding="utf-8-sig")
            out_df.to_excel(INDEX_XLSX, index=False)

            print(f"   ✅ 保存成功: {file_name} ({record['file_size_kb']} KB)")

            page.back()
            if session_counter >= next_break:
                rest_t = random.uniform(50.0, 90.0)
                print(f"   ☕ 已连续抓 {session_counter} 个京东商品，小憩 {rest_t:.0f} 秒...")
                time.sleep(rest_t)
                session_counter = 0
                next_break = random.randint(15, 25)
            else:
                sleep_sec = random.uniform(8.0, 15.0)
                print(f"   💤 休眠 {sleep_sec:.1f} 秒...")
                time.sleep(sleep_sec)

        except Exception as e:
            print(f"   ⚠️ 采集京东 SKU {item_id} 异常: {e}")
            time.sleep(4)

    print(f"\n🎉 京东采集任务结束！当前 `captured_html/` 共归档 {len(index_records)} 个文件，总索引表 `{INDEX_XLSX}` 已同步更新。")


if __name__ == "__main__":
    main()