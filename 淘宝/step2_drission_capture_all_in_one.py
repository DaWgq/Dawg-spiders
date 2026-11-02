import os
import re
import time
import random
import pandas as pd
from datetime import datetime
from DrissionPage import ChromiumPage, ChromiumOptions

# ================= 1. 全局配置 =================
INPUT_CSV = "taobao_target_queue.csv"
OUTPUT_DIR = "captured_html"          # HTML 保存文件夹
INDEX_CSV = "index_table.csv"         # 实时更新的 CSV 索引表
INDEX_XLSX = "index_table.xlsx"       # 实时更新的 Excel 索引表
TARGET_COUNT = 300                    # 目标采集总数（如果淘宝只采150个、剩下150个采京东，这里改成 150 即可）
ROLLBACK_START_NUM = 999              # 设为 999 表示保留目前已爬好的所有正常文件；若仍想强制删掉61及之后的重来，改为 61

EXTRA_EXCLUDE_WORDS = ["骨传导", "挂耳式", "耳挂式", "颈挂", "挂脖", "入耳式", "半入耳", "耳夹式"]

# 黑名单：风控/验证码/软拦截特征词[cite: 3, 4, 5, 6]
BAD_PAGE_MARKERS = [
    "验证码拦截",
    "安全验证",
    "captchacappuzzle",
    "captchacapslide",
    "将满足描述的所有图片",
    "访问异常提示",
    "系统检测到当前访问存在异常",
    "baxia-dialog",
    "通过验证以确保正常访问",
    "rgv587_flag",
    "sec.taobao.com",
]

# 白名单：正常商品详情页核心词
VALID_ITEM_MARKERS = [
    "加入购物车", "立即购买", "领券购买", "宝贝详情", "商品详情", "累计评价", "图文详情"
]

# 注入浏览器的 JS：固化懒加载图 + 内联CSS + 移除<script>防离线弹窗[cite: 1]
INLINE_DOM_JS = """
async () => {
    document.querySelectorAll('img').forEach(img => {
        const realSrc = img.getAttribute('data-src') || img.getAttribute('data-ks-lazyload') || img.src;
        if (realSrc && !realSrc.startsWith('data:')) {
            img.src = realSrc.startsWith('//') ? 'https:' + realSrc : realSrc;
            img.removeAttribute('loading');
            img.removeAttribute('data-src');
        }
        img.style.maxWidth = '100%';
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

    document.querySelectorAll('div, section, iframe').forEach(el => {
        const text = el.innerText || '';
        if (text.includes('外网访问预发环境拦截') || text.includes('一键加白')) {
            let target = el;
            while (target.parentElement && target.parentElement !== document.body) {
                const pos = window.getComputedStyle(target.parentElement).position;
                if (pos === 'fixed' || pos === 'absolute') {
                    target = target.parentElement;
                } else {
                    break;
                }
            }
            target.remove();
        }
    });

    document.body.style.overflow = 'auto';
    document.documentElement.style.overflow = 'auto';
    document.querySelectorAll('script, link[as="script"], link[rel="preload"], iframe').forEach(el => el.remove());

    return "<!DOCTYPE html>\\n" + document.documentElement.outerHTML;
}
"""


# ================= 2. 启动自检与脏文件清理 =================
def rollback_and_clean(start_num: int = 999):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    deleted_files = []

    for fname in os.listdir(OUTPUT_DIR):
        match = re.match(r"item_(\d+)\.(html|mhtml)$", fname)
        if match and int(match.group(1)) >= start_num:
            os.remove(os.path.join(OUTPUT_DIR, fname))
            deleted_files.append(fname)

    if not os.path.exists(INDEX_CSV):
        return set(), []

    df_idx = pd.read_csv(INDEX_CSV)
    valid_records = []

    for _, row in df_idx.iterrows():
        fname = str(row["html_filename"])
        match = re.match(r"item_(\d+)\.html$", fname)
        if not match or int(match.group(1)) >= start_num:
            continue

        fpath = os.path.join(OUTPUT_DIR, fname)
        if not os.path.exists(fpath):
            continue

        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if any(m in content for m in BAD_PAGE_MARKERS) or len(content) < 25000:
            print(f"🗑️ 自动剔除含验证码/访问异常的坏文件: {fname}")
            os.remove(fpath)
            continue

        valid_records.append(row.to_dict())

    for i, rec in enumerate(valid_records, 1):
        expected_fname = f"item_{i:03d}.html"
        old_path = os.path.join(OUTPUT_DIR, rec["html_filename"])
        new_path = os.path.join(OUTPUT_DIR, expected_fname)
        if old_path != new_path and os.path.exists(old_path):
            os.rename(old_path, new_path)
        rec["html_filename"] = expected_fname

    if valid_records:
        new_df = pd.DataFrame(valid_records)
        new_df.to_csv(INDEX_CSV, index=False, encoding="utf-8-sig")
        new_df.to_excel(INDEX_XLSX, index=False)
    elif os.path.exists(INDEX_CSV):
        os.remove(INDEX_CSV)

    captured_ids = {str(r["item_id"]) for r in valid_records}
    print(f"✅ 自检完毕！当前保留 100% 正常文件: {len(valid_records)} 个，将从 item_{len(valid_records)+1:03d}.html 继续！")
    return captured_ids, valid_records


# ================= 3. 拟人化导航、真鼠标轨迹与风控死锁拦截 =================
def open_item_from_search_mother_tab(page: ChromiumPage, raw_url: str, item_idx: int):
    """
    模拟真人行为：
    保持主标签页始终在 s.taobao.com 搜索列表页，每次从中点击带随机 spm 的链接打开新标签页，
    彻底消除『详情页跳详情页』的爬虫轨迹！
    """
    if "s.taobao.com" not in page.url:
        page.get("https://s.taobao.com/search?q=%E5%A4%B4%E6%88%B4%E5%BC%8F%E8%80%B3%E6%9C%BA")
        time.sleep(random.uniform(3.0, 5.0))

    # 在搜索母页随便滚一下鼠标，制造母页活跃痕迹
    page.scroll.down(random.randint(150, 450))
    time.sleep(random.uniform(0.6, 1.5))

    # 构造高度拟真的动态 spm 参数（每次序号不同）
    rand_pos = (item_idx % 48) + 1
    rand_spm = f"a21bo.jianhua.201876.d{rand_pos}.{random.randint(1000,9999)}ac"
    sep = "&" if "?" in raw_url else "?"
    target_url = f"{raw_url}{sep}spm={rand_spm}"

    # 在当前标签页打开（或通过链接跳转），抓完后会退回搜索页
    js_click = f"""
    let a = document.getElementById('__human_link');
    if (!a) {{
        a = document.createElement('a');
        a.id = '__human_link';
        a.rel = 'opener';
        document.body.appendChild(a);
    }}
    a.href = "{target_url}";
    a.click();
    """
    page.run_js(js_click)
    time.sleep(random.uniform(2.8, 4.5))
    page.wait.doc_loaded(timeout=15)


def is_item_invalid(page: ChromiumPage) -> bool:
    invalid_markers = [
        "此商品已下架", "商品已下架", "很抱歉，您查看的商品找不到了",
        "商品不存在", "非常抱歉，您查看的商品不存在", "柜台已撤",
    ]
    body_text = page.ele("tag:body").text if page.ele("tag:body") else ""
    return any(m in body_text[:1500] for m in invalid_markers)


def strict_guard_check(page: ChromiumPage, target_url: str):
    """正反双重死锁检测：一旦发现验证码或左下角『访问异常提示』，立即停止等待人工解除[cite: 3, 4, 5, 6]"""
    while True:
        try:
            url = page.url.lower()
            title = page.title or ""
            body_text = page.ele("tag:body").text if page.ele("tag:body") else ""
            full_html = page.html or ""
        except Exception:
            time.sleep(2)
            continue

        if is_item_invalid(page):
            return

        hit_bad = [m for m in BAD_PAGE_MARKERS if (m in title or m in body_text or m in full_html[:20000] or m in url)]
        is_login_or_punish = any(k in url for k in ["login.taobao", "login.tmall", "punish", "sec.taobao", "alisec"])
        has_valid_item_feature = any(v in body_text or v in full_html for v in VALID_ITEM_MARKERS)

        if hit_bad or is_login_or_punish or not has_valid_item_feature:
            print("\a")
            print("\n" + "=" * 68)
            if "访问异常提示" in body_text or "系统检测到当前访问存在异常" in body_text:
                print("🛑 【死锁停止！检测到左下角『访问异常提示』软风控】[cite: 6]")
                print("💡 为什么会越封越快：当前账号/IP 已被打上短期惩罚标记，继续硬刷会每 5 个封一次！")
                print("👉 彻底解除办法：")
                print("   1. 手机热点开关一次飞行模式换个新 IP（最快）或换另一个淘宝号登录；")
                print("   2. 若不换号，请让浏览器静止休息 15~20 分钟等信誉分恢复；")
                print("   3. 在浏览器手动刷新当前页，往下拉确认左下角不再出现『访问异常提示』且详情长图正常显示。")
            else:
                reason = f"命中风控特征 {hit_bad}" if hit_bad else f"缺少商品交易按钮 (标题: {title})"
                print(f"🚨 【死锁停止！检测到验证码/登录拦截】原因: {reason}")
                print("👉 请在 Chrome 中手动完成九宫格/滑块验证，并确认看到正常的耳机商品详情页！")
            print("=" * 68)

            input("⏳ 确认浏览器中商品与详情长图已 100% 恢复正常后，按【回车键】继续...")
            time.sleep(2.5)

            if "item.htm" not in page.url and "detail.tmall" not in page.url:
                page.get(target_url)
                time.sleep(3.5)
            continue

        break


def human_like_mouse_and_scroll(page: ChromiumPage, target_url: str):
    """
    【核心反规律升级】
    摒弃死板的 window.scrollTo 循环！
    改用 DrissionPage 原生真实鼠标移动 (actions.move) + 不规则物理滚轮 (page.scroll) + 偶尔往回倒滚，
    向淘宝 baxia 传感器灌入大量真实的 mousemove 与 wheel 人类行为熵！
    """
    print("   🖱️ 正在模拟真人鼠标移动与不规则滚轮阅读详情...")

    # 1. 首屏随机晃动鼠标（模拟看主图和看价格/SKU）
    try:
        for _ in range(random.randint(2, 4)):
            dx = random.randint(-180, 220)
            dy = random.randint(-100, 180)
            page.actions.move(dx, dy, duration=random.uniform(0.2, 0.6))
            time.sleep(random.uniform(0.3, 0.8))
    except Exception:
        pass

    # 2. 不规则次数（7 ~ 13 次）、不规则步长向下滚动，中间夹杂鼠标微移与回滚
    total_steps = random.randint(8, 13)
    for step in range(total_steps):
        strict_guard_check(page, target_url)

        # 随机滚动距离（有时滚得快 800px，有时仔细看滚 350px）
        scroll_dist = random.randint(420, 880)
        page.scroll.down(scroll_dist)

        # 25% 的概率稍微往回滚一点点（人类看长图常有的回看动作）
        if random.random() < 0.25 and step > 2:
            time.sleep(random.uniform(0.4, 0.8))
            page.scroll.up(random.randint(100, 260))

        # 滚动间隙随机动一下鼠标，喂给淘宝前端风控传感器真实坐标流
        if random.random() < 0.5:
            try:
                page.actions.move(random.randint(-80, 80), random.randint(-50, 50), duration=0.3)
            except Exception:
                pass

        # 停顿时间服从人类对数正态感（有时0.7秒略过，有时停2.5秒细看）
        time.sleep(random.uniform(0.8, 2.2))

    # 3. 到底部后再停顿 2 秒等待最后的长图渲染，并检查一次左下角有没有刷出“访问异常提示”[cite: 6]
    time.sleep(2.0)
    strict_guard_check(page, target_url)


# ================= 4. 主执行入口 =================
def main():
    if not os.path.exists(INPUT_CSV):
        print(f"❌ 找不到 `{INPUT_CSV}`，请先确认队列文件存在！")
        return

    captured_ids, index_records = rollback_and_clean(start_num=ROLLBACK_START_NUM)
    next_file_num = len(index_records) + 1

    df = pd.read_csv(INPUT_CSV)
    print(f"📂 已加载队列 `{INPUT_CSV}`（共 {len(df)} 条），将从 item_{next_file_num:03d}.html 继续采集！")

    co = ChromiumOptions()
    co.set_local_port(9222)
    page = ChromiumPage(co)
    print("🌐 已连接 Chrome！先打开淘宝搜索母页预热...")
    page.get("https://s.taobao.com/search?q=%E5%A4%B4%E6%88%B4%E5%BC%8F%E8%80%B3%E6%9C%BA")
    time.sleep(3)

    session_counter = 0
    # 动态随机设定下一次喝水休息的间隔（比如抓 14 个休一次，下次抓 21 个休一次，绝不固定 30 个！）
    next_break_threshold = random.randint(12, 22)

    for idx, row in df.iterrows():
        if len(index_records) >= TARGET_COUNT:
            print(f"\n🎯 已达到目标采集数量 ({TARGET_COUNT} 条)，任务圆满结束！")
            break

        item_id = str(row["item_id"])
        title = str(row["title"])
        url = str(row["item_url"])

        if item_id in captured_ids:
            continue

        if any(w in title for w in EXTRA_EXCLUDE_WORDS):
            print(f"⏭️ [跳过非头戴式] {item_id} | {title}")
            continue

        file_name = f"item_{next_file_num:03d}.html"
        file_path = os.path.join(OUTPUT_DIR, file_name)
        print(f"\n[{len(index_records)+1}/{TARGET_COUNT}] 正在采集 -> {file_name} | ID: {item_id} | {title[:25]}...")

        try:
            # 1. 从搜索母页模拟点击进入商品页
            open_item_from_search_mother_tab(page, url, next_file_num)

            # 2. 首屏死锁检测
            strict_guard_check(page, url)

            if is_item_invalid(page):
                print("   ❌ 商品已下架或失效，自动退回搜索页并跳过！")
                page.back()
                time.sleep(2)
                continue

            # 3. 真人鼠标轨迹 + 不规则滚轮阅读（触发详情长图并检测左下角『访问异常提示』[cite: 6]）
            human_like_mouse_and_scroll(page, url)

            # 4. 导出完整 HTML
            full_html = page.run_js(INLINE_DOM_JS)

            if any(m in full_html for m in BAD_PAGE_MARKERS) or len(full_html) < 30000:
                print("   🚨 导出源码中检测到『访问异常提示』或验证码特征，已拦截保存！")
                strict_guard_check(page, url)
                full_html = page.run_js(INLINE_DOM_JS)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(full_html)

            record = {
                "html_filename": file_name,
                "platform": row["platform"],
                "item_id": item_id,
                "shop_id": row["shop_id"],
                "shop_name": row["shop_name"],
                "title": title,
                "price": row["price"],
                "sales_raw": row["sales_raw"],
                "sales_count": row["sales_count"],
                "sales_tier": row["sales_tier"],
                "item_url": f"https://item.taobao.com/item.htm?id={item_id}",
                "capture_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "file_size_kb": round(os.path.getsize(file_path) / 1024, 1),
            }
            index_records.append(record)
            captured_ids.add(item_id)
            next_file_num += 1
            session_counter += 1

            out_df = pd.DataFrame(index_records)
            out_df.to_csv(INDEX_CSV, index=False, encoding="utf-8-sig")
            out_df.to_excel(INDEX_XLSX, index=False)

            print(f"   ✅ 保存成功: {file_name} ({record['file_size_kb']} KB)")

            # 5. 看完商品后模拟真人按返回键退回搜索列表页，准备看下一个
            page.back()

            # 6. 非线性随机休眠（彻底打破固定周期规律）
            if session_counter >= next_break_threshold:
                long_break = random.uniform(75.0, 140.0)
                print(f"   ☕ 已连续浏览 {session_counter} 个商品，模拟真人离开电脑休息 {long_break:.0f} 秒...")
                time.sleep(long_break)
                session_counter = 0
                next_break_threshold = random.randint(12, 22)
            else:
                # 80% 概率正常停顿 15~26 秒，20% 概率模拟停下来发呆 30~45 秒
                if random.random() < 0.8:
                    sleep_sec = random.uniform(15.0, 26.0)
                else:
                    sleep_sec = random.uniform(30.0, 48.0)
                print(f"   💤 拟人随机停顿 {sleep_sec:.1f} 秒...")
                time.sleep(sleep_sec)

        except Exception as e:
            print(f"   ⚠️ 采集 {item_id} 异常: {e}")
            time.sleep(5)

    print(f"\n🎉 全部采集完成！共保存 {len(index_records)} 个完整 HTML 至 `{OUTPUT_DIR}/`，索引表 `{INDEX_XLSX}` 已生成。")


if __name__ == "__main__":
    main()