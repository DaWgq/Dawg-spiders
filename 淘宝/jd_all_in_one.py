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

TOTAL_PROJECT_TARGET = 300                # 最终总样本硬性目标（item_001 ~ item_300）
JD_MAX_CAPTURE = 300                      # 放开京东采集上限，直接补齐到总样本满 300 个为止！

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

        const nameEl = card.querySelector('.p-name em, .p-name a, [class*="goods_title"], [class*="title"]');
        let title = nameEl ? nameEl.innerText.replace(/\\s+/g, ' ').trim() : '';
        if (!title) return;

        const priceEl = card.querySelector('.p-price i, .p-price strong, [class*="price"]');
        const price_str = priceEl ? priceEl.innerText.trim() : '0';

        const commitEl = card.querySelector('.p-commit a, .p-commit strong, [class*="comment"], [class*="commit"]');
        const sales_raw = commitEl ? commitEl.innerText.trim() : '0';

        let shop_name = '';
        const shopEl = card.querySelector('.p-shop a, .hd-shopname, a[href*="mall.jd.com"], a[title*="旗舰店"], a[title*="专卖店"], a[title*="专营店"], a[title*="自营"], [class*="shopName"], [class*="shop"]');
        if (shopEl) {
            shop_name = (shopEl.getAttribute('title') || shopEl.innerText || '').trim();
        }
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


# ================= 2. 阶段一：扩充更多细分词与深层页码，确保未抓候选数远超剩余缺口 =================
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


def clean_and_sample_jd(df: pd.DataFrame, target_total: int = 350) -> pd.DataFrame:
    """清洗并输出大容量候选池（默认保留最多 350 条有效京东商品）"""
    if df.empty:
        return df

    def fix_shop_name(row):
        sname = str(row.get("shop_name", ""))
        if not sname or sname in ["京东自营/官方店", "京东自营/第三方店", "京东店"]:
            return "JD_" + re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", str(row["title"]))[:6]
        return sname

    df["shop_name"] = df.apply(fix_shop_name, axis=1)
    df["shop_id"] = df["shop_name"]

    pattern = "|".join(EXCLUDE_KEYWORDS)
    df = df[~df["title"].str.contains(pattern, case=False, na=False)]
    df = df[df["price"] >= 25.0]

    df = df.sort_values(by="sales_count", ascending=False)
    df = df.drop_duplicates(subset=["item_id"], keep="first")
    if "spu_id" in df.columns:
        df = df.drop_duplicates(subset=["spu_id"], keep="first")

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
    return result


def expand_jd_pool_until_enough(page: ChromiumPage, captured_ids: set, needed_more: int) -> pd.DataFrame:
    """
    智能检测当前未抓的候选商品是否够填满剩余缺口（如还差 55 个，则至少准备 80 个未抓过的新候选商品）
    不够则自动启用第 2 批、第 3 批新关键词往深页抓取！
    """
    existing_raw = pd.read_csv(JD_RAW_CSV) if os.path.exists(JD_RAW_CSV) else pd.DataFrame()
    if not existing_raw.empty:
        clean_df = clean_and_sample_jd(existing_raw.copy(), target_total=360)
        uncaptured_df = clean_df[~clean_df["item_id"].astype(str).isin(captured_ids)]
        print(f"📊 当前京东队列共有 {len(clean_df)} 条有效商品，其中尚未采集的有 {len(uncaptured_df)} 条（还需采集 {needed_more} 条）。")
        if len(uncaptured_df) >= needed_more + 15:
            return clean_df
    else:
        uncaptured_df = pd.DataFrame()

    print(f"\n🚀 未采集候选商品不足 {needed_more + 15} 条！开始用新细分词扩充京东商品池...")
    all_items = existing_raw.to_dict("records") if not existing_raw.empty else []
    seen_skus = {str(r["item_id"]) for r in all_items}

    # 新增一批之前没搜过的细分词与排序，确保抓出来的全是新鲜未重复的头戴式耳机！
    search_tasks = [
        ("头戴式有线耳机", "", 5, "有线细分"),
        ("头戴式监听耳机", "", 4, "HiFi监听细分"),
        ("电脑耳麦头戴式", "", 5, "电脑耳麦细分"),
        ("头戴式音乐耳机", "4", 4, "评论数排序"),
        ("头戴式降噪耳机", "", 5, "降噪综合"),
        ("头戴式耳机", "", 8, "主词深翻页"),
    ]

    for kw, psort, max_pages, desc in search_tasks:
        kw_enc = urllib.parse.quote(kw)
        url = f"https://search.jd.com/Search?keyword={kw_enc}&enc=utf-8"
        if psort:
            url += f"&psort={psort}"

        page.get(url)
        time.sleep(random.uniform(2.5, 4.0))

        for p in range(1, max_pages + 1):
            while (
                "passport.jd.com" in page.url
                or "safe.jd.com" in page.url
                or "verify.jd.com" in page.url
                or "欢迎登录" in (page.title or "")
            ):
                print("\n🚨 请先在 Chrome 窗口中完成京东登录或验证！")
                input("👉 看到商品搜索列表后，按【回车键】继续...")
                time.sleep(2)

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

            raw_df = pd.DataFrame(all_items)
            raw_df.to_csv(JD_RAW_CSV, index=False, encoding="utf-8-sig")

            # 实时测算清洗后未抓的商品够不够填满缺口
            clean_df = clean_and_sample_jd(raw_df.copy(), target_total=360)
            uncaptured_cnt = len(clean_df[~clean_df["item_id"].astype(str).isin(captured_ids)])
            print(f"⏳ [{kw}-{desc}] 第 {p}/{max_pages} 页 -> 新增 SKU: {new_added} 个 | 当前可用未抓有效商品: {uncaptured_cnt}/{needed_more + 15} 个")

            if uncaptured_cnt >= needed_more + 15:
                print(f"✅ 补货完成！已备妥 {uncaptured_cnt} 个全新有效京东商品，立即开始采集剩余的 {needed_more} 个详情页！")
                return clean_df

            if p < max_pages:
                clicked_next = page.run_js("""
                return (() => {
                    const nextBtn = document.querySelector('a.pn-next, .pn-next, [class*="pagination_next"]');
                    if (nextBtn && !nextBtn.className.includes('disabled')) {
                        nextBtn.click();
                        return true;
                    }
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
                    next_url = f"https://search.jd.com/Search?keyword={kw_enc}&enc=utf-8&page={(p+1)*2-1}&s={p*60+1}"
                    if psort:
                        next_url += f"&psort={psort}"
                    page.get(next_url)
                time.sleep(random.uniform(3.0, 5.0))

    return clean_and_sample_jd(pd.DataFrame(all_items), target_total=360)


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

    # 1. 先读取现有的 index_table.csv，算出还差多少个满 300 个
    if os.path.exists(INDEX_CSV):
        idx_df = pd.read_csv(INDEX_CSV)
        index_records = idx_df.to_dict("records")
        captured_ids = {str(r["item_id"]) for r in index_records}
        jd_captured_count = sum(1 for r in index_records if r.get("platform") == "jd")
    else:
        index_records = []
        captured_ids = set()
        jd_captured_count = 0

    needed_more = TOTAL_PROJECT_TARGET - len(index_records)
    if needed_more <= 0:
        print(f"🎉 当前已有 {len(index_records)} 个文件，已达到 {TOTAL_PROJECT_TARGET} 个目标！")
        return

    # 2. 自动扩充京东候选队列，确保【未采集过】的有效商品数量足够填满剩余的 55 个缺口
    jd_df = expand_jd_pool_until_enough(page, captured_ids, needed_more)

    next_file_num = len(index_records) + 1
    print("\n" + "=" * 65)
    print(f"🔄 【断点补齐已就绪】")
    print(f"   - 当前已完成总样本数: {len(index_records)} 个 (还差 {needed_more} 个满 {TOTAL_PROJECT_TARGET} 个)")
    print(f"   - 本次将直接从 `item_{next_file_num:03d}.html` 采到 `item_{TOTAL_PROJECT_TARGET:03d}.html`！")
    print("=" * 65)

    page.get("https://search.jd.com/Search?keyword=%E5%A4%B4%E6%88%B4%E5%BC%8F%E8%80%B3%E6%9C%BA&enc=utf-8")
    time.sleep(3)

    session_counter = 0
    next_break = random.randint(15, 25)

    for _, row in jd_df.iterrows():
        if len(index_records) >= TOTAL_PROJECT_TARGET or jd_captured_count >= JD_MAX_CAPTURE:
            print(f"\n🎯 已达到采集目标上限（总计 {len(index_records)} 条，京东 {jd_captured_count} 条），圆满收工！")
            break

        item_id = str(row["item_id"])
        title = str(row["title"])
        url = f"https://item.jd.com/{item_id}.html"

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

    print(f"\n🎉 京东采集任务圆满结束！当前 `captured_html/` 共归档 {len(index_records)} 个文件，总索引表 `{INDEX_XLSX}` 已同步更新。")


if __name__ == "__main__":
    main()