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
TARGET_COUNT = 300                    # 目标有效 HTML 采集总数
ROLLBACK_START_NUM = 103               # 强制从第 n 个起清理并重爬（保留前 n 个）

EXTRA_EXCLUDE_WORDS = ["骨传导", "挂耳式", "耳挂式", "颈挂", "挂脖", "入耳式", "半入耳", "耳夹式"]

# 黑名单：所有属于风控/验证码/异常降级的特征词[cite: 3, 4, 5]
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

# 白名单：正常淘宝/天猫商品详情页必须至少包含其中一个核心交易词
VALID_ITEM_MARKERS = [
    "加入购物车",
    "立即购买",
    "领券购买",
    "宝贝详情",
    "商品详情",
    "累计评价",
    "图文详情",
]

# 注入浏览器的 JS：固化懒加载图 + 内联CSS + 清除预发环境拦截遮罩 + 移除所有<script>[cite: 1]
INLINE_DOM_JS = """
async () => {
    // 1. 固化所有懒加载图片的真实地址并限制最大宽度
    document.querySelectorAll('img').forEach(img => {
        const realSrc = img.getAttribute('data-src') || img.getAttribute('data-ks-lazyload') || img.src;
        if (realSrc && !realSrc.startsWith('data:')) {
            img.src = realSrc.startsWith('//') ? 'https:' + realSrc : realSrc;
            img.removeAttribute('loading');
            img.removeAttribute('data-src');
        }
        img.style.maxWidth = '100%';
    });

    // 2. 将外部 CSS 样式表内联为 <style> 标签
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

    // 3. 补全所有以 // 开头的相对协议链接
    document.querySelectorAll('[src^="//"], [href^="//"]').forEach(el => {
        if (el.src && el.getAttribute('src').startsWith('//')) el.src = 'https:' + el.getAttribute('src');
        if (el.href && el.getAttribute('href').startsWith('//')) el.href = 'https:' + el.getAttribute('href');
    });

    // 4. 清除“外网访问预发环境拦截 / 一键加白”弹窗及遮罩层[cite: 1]
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

    // 5. 移除所有 <script> 和 iframe，防止离线双击打开 HTML 时报错弹窗[cite: 1]
    document.querySelectorAll('script, link[as="script"], link[rel="preload"], iframe').forEach(el => el.remove());

    return "<!DOCTYPE html>\\n" + document.documentElement.outerHTML;
}
"""


# ================= 2. 强制回滚至第 60 个，删除 61 及之后的全部脏数据 =================
def rollback_and_clean(start_num: int = 61):
    """
    1. 强制删除 item_061.html 及之后的所有 HTML 文件；
    2. 同时检查前 60 个文件里有没有漏网的验证码页，确保前 60 个 100% 纯净；
    3. 截断并同步更新 index_table.csv 和 index_table.xlsx。
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 第一步：直接物理删除文件夹里编号 >= 61 的所有 html 文件
    deleted_files = []
    for fname in os.listdir(OUTPUT_DIR):
        match = re.match(r"item_(\d+)\.(html|mhtml)$", fname)
        if match and int(match.group(1)) >= start_num:
            fpath = os.path.join(OUTPUT_DIR, fname)
            os.remove(fpath)
            deleted_files.append(fname)

    if deleted_files:
        print(f"🗑️ 已强制删除第 {start_num} 号及之后的脏 HTML 文件共 {len(deleted_files)} 个（{deleted_files[0]} ~ {deleted_files[-1]}）。")

    if not os.path.exists(INDEX_CSV):
        return set(), []

    # 第二步：截取索引表前 60 条，并二次校验这前 60 个文件是否 100% 正常
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

        # 如果前 60 个里面也有残留验证码页，一并剔除
        if any(m in content for m in BAD_PAGE_MARKERS):
            print(f"⚠️ 发现前 60 个中 {fname} 也含有异常/验证码特征，已一并删除！")
            os.remove(fpath)
            continue

        valid_records.append(row.to_dict())

    # 重新对齐编号（正常情况下就是 item_001.html ~ item_060.html）
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
    print(f"✅ 索引表回滚完毕！当前保留有效存量: {len(valid_records)} 条，接下来将严格从 item_{len(valid_records)+1:03d}.html 重新开始爬！")
    return captured_ids, valid_records


# ================= 3. 浏览器导航与【正反双重死锁】验证码拦截 =================
def navigate_with_referer(page: ChromiumPage, target_url: str):
    if "taobao.com" not in page.url and "tmall.com" not in page.url:
        page.get("https://s.taobao.com/search?q=%E5%A4%B4%E6%88%B4%E5%BC%8F%E8%80%B3%E6%9C%BA")
        time.sleep(3)

    if "spm=" not in target_url:
        sep = "&" if "?" in target_url else "?"
        target_url = f"{target_url}{sep}spm=a21bo.jianhua.201876.d1"

    js_jump = f"""
    let a = document.getElementById('__sim_click_link');
    if (!a) {{
        a = document.createElement('a');
        a.id = '__sim_click_link';
        a.rel = 'opener';
        document.body.appendChild(a);
    }}
    a.href = "{target_url}";
    a.click();
    """
    page.run_js(js_jump)
    time.sleep(2.5)
    page.wait.doc_loaded(timeout=15)


def is_item_invalid(page: ChromiumPage) -> bool:
    invalid_markers = [
        "此商品已下架", "商品已下架", "很抱歉，您查看的商品找不到了",
        "商品不存在", "非常抱歉，您查看的商品不存在", "柜台已撤",
    ]
    body_text = page.ele("tag:body").text if page.ele("tag:body") else ""
    return any(m in body_text[:1500] for m in invalid_markers)


def strict_guard_check(page: ChromiumPage, target_url: str):
    """
    【核心死锁拦截器】
    只要触发以下任一条件，立刻发出警报并死锁暂停脚本，绝不往下执行，也绝不保存文件：
    1. 命中黑名单（验证码拦截、captchacappuzzle、将满足描述的所有图片、访问异常提示、punish 等）[cite: 3, 4, 5]
    2. 未命中白名单（页面既不是下架商品，也找不到“加入购物车/立即购买/宝贝详情”等正常商品元素）
    """
    while True:
        try:
            url = page.url.lower()
            title = page.title or ""
            body_text = page.ele("tag:body").text if page.ele("tag:body") else ""
            full_html = page.html or ""
        except Exception:
            time.sleep(2)
            continue

        # 如果是明确的商品下架页，放行交给外层 is_item_invalid 跳过
        if is_item_invalid(page):
            return

        # 1. 检查是否命中黑名单（九宫格验证码 / 滑块 / 访问异常 / 登录）
        hit_bad = [m for m in BAD_PAGE_MARKERS if (m in title or m in body_text or m in full_html[:15000] or m in url)]
        is_login_or_punish = any(k in url for k in ["login.taobao", "login.tmall", "punish", "sec.taobao", "alisec"])

        # 2. 检查是否具备正常商品页的白名单特征（防止新型未知验证码漏网）
        has_valid_item_feature = any(v in body_text or v in full_html for v in VALID_ITEM_MARKERS)

        if hit_bad or is_login_or_punish or not has_valid_item_feature:
            print("\a")  # 终端蜂鸣提示音
            print("\n" + "=" * 65)
            if "访问异常提示" in body_text or "系统检测到当前访问存在异常" in body_text:
                print("🛑 【紧急停止！触发淘宝软风控：访问异常提示】")
                print("👉 解决步骤：")
                print("   1. 电脑切换连接【手机个人热点】（或重启光猫换IP），或者原地休息 10~15 分钟。")
                print("   2. 在 Chrome 浏览器里手动刷新当前商品页，确保看到正常价格和『加入购物车』。")
            else:
                reason = f"检测到特征 {hit_bad}" if hit_bad else f"页面缺少正常商品特征 (当前标题: {title})"
                print(f"🚨 【紧急停止！触发验证码拦截】原因: {reason}")
                print("👉 解决步骤：")
                print("   1. 请立即切换到 Chrome 浏览器窗口，手动完成【九宫格拖放拼图】或【滑块验证】！")
                print("   2. 验证通过后，确认浏览器已显示正常的耳机商品详情页。")
            print("=" * 65)

            input("⏳ 处理完成后，请按【回车键】重新检测当前页面...")
            time.sleep(2.5)

            # 如果验证完跳到了淘宝首页或空白页，自动重新打开刚才那个目标商品
            if "item.htm" not in page.url and "detail.tmall" not in page.url:
                print("   🔄 正在重新打开当前目标商品页...")
                navigate_with_referer(page, target_url)
                time.sleep(3.5)

            # 继续下一轮 while 循环严格复检，直到真正看到正常商品页才放行！
            continue

        # 通过黑名单+白名单双重检验，确认是 100% 正常的商品详情页
        break


def smooth_scroll_to_load_details(page: ChromiumPage, target_url: str):
    """平滑分段滚动，每滚一步都实时监测是否突然跳出验证码"""
    print("   ⏬ 正在分段滚动加载详情大图与规格表...")
    for step in range(1, 10):
        strict_guard_check(page, target_url)
        scroll_y = step * 950 + random.randint(-80, 80)
        try:
            page.run_js(f"window.scrollTo({{top: {scroll_y}, behavior: 'smooth'}});")
        except Exception:
            time.sleep(2)
            strict_guard_check(page, target_url)
        time.sleep(random.uniform(1.0, 1.5))

    time.sleep(random.uniform(2.0, 10.0))
    try:
        page.run_js("window.scrollTo({top: 0, behavior: 'smooth'});")
    except Exception:
        pass
    time.sleep(random.uniform(0.8, 1.2))


# ================= 4. 主执行入口 =================
def main():
    if not os.path.exists(INPUT_CSV):
        print(f"❌ 找不到 `{INPUT_CSV}`，请先确认队列文件存在！")
        return

    # 启动时先强制清理第 61 号及之后的脏数据，锁定从 item_061.html 开始
    captured_ids, index_records = rollback_and_clean(start_num=ROLLBACK_START_NUM)
    next_file_num = len(index_records) + 1

    df = pd.read_csv(INPUT_CSV)
    print(f"📂 已加载候选队列 `{INPUT_CSV}`（共 {len(df)} 条），现在从 item_{next_file_num:03d}.html 开始采集！")

    co = ChromiumOptions()
    co.set_local_port(9222)
    page = ChromiumPage(co)
    print("🌐 已连接 Chrome 浏览器！")

    session_counter = 0

    for idx, row in df.iterrows():
        if len(index_records) >= TARGET_COUNT:
            print(f"\n🎯 已达到目标采集数量 ({TARGET_COUNT} 条)，任务圆满结束！")
            break

        item_id = str(row["item_id"])
        title = str(row["title"])
        url = str(row["item_url"])

        # 跳过前 60 个已经成功保存的商品 ID
        if item_id in captured_ids:
            continue

        if any(w in title for w in EXTRA_EXCLUDE_WORDS):
            print(f"⏭️ [跳过非头戴式] {item_id} | {title}")
            continue

        file_name = f"item_{next_file_num:03d}.html"
        file_path = os.path.join(OUTPUT_DIR, file_name)
        print(f"\n[{len(index_records)+1}/{TARGET_COUNT}] 正在采集 -> {file_name} | ID: {item_id} | {title[:25]}...")

        try:
            navigate_with_referer(page, url)
            time.sleep(random.uniform(3.5, 5.0))

            # 第一道拦截：刚打开页面时立刻检查是否跳了九宫格验证码
            strict_guard_check(page, url)

            if is_item_invalid(page):
                print("   ❌ 商品已下架或失效，自动跳过并由下一条递补！")
                continue

            # 第二道拦截：滚动加载途中实时检查
            smooth_scroll_to_load_details(page, url)

            # 第三道拦截：导出 HTML 前最后一次复核
            strict_guard_check(page, url)

            full_html = page.run_js(INLINE_DOM_JS)

            # 写入硬盘前终极校验：如果导出的源码里有验证码字样，或文件体积过小（<30KB），死锁重来
            if any(m in full_html for m in BAD_PAGE_MARKERS) or len(full_html) < 30000:
                print("   🚨 导出源码校验未通过（疑似验证码页或空白页），已拦截写入！")
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

            # 每采满 30 个商品自动长休眠 90~120 秒，避免连续请求在第 60 个左右触发九宫格验证码
            if session_counter % 30 == 0:
                long_break = random.uniform(90.0, 125.0)
                print(f"   ☕ 已连续采集 {session_counter} 个，自动中场休息 {long_break:.0f} 秒冷却风控...")
                time.sleep(long_break)
            else:
                sleep_sec = random.uniform(14.0, 22.0)
                print(f"   💤 休眠 {sleep_sec:.1f} 秒...")
                time.sleep(sleep_sec)

        except Exception as e:
            print(f"   ⚠️ 采集 {item_id} 异常: {e}")
            time.sleep(5)

    print(f"\n🎉 全部采集完成！共保存 {len(index_records)} 个完整 HTML 至 `{OUTPUT_DIR}/`，索引表 `{INDEX_XLSX}` 已生成。")


if __name__ == "__main__":
    main()