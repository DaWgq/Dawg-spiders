"""
京东商品评论批量爬取工具
使用 DrissionPage 浏览器自动化，绕过 h5st 签名限制
支持多商品批量爬取，自动翻页至最后一页

使用方法：
  1. 修改下方 PRODUCTS 配置，填入商品 SKU
  2. 运行脚本 -> 自动打开浏览器 -> 手动登录京东
  3. 在原终端按 Enter 确认登录完成 -> 自动批量爬取
  4. 结果保存在 OUTPUT_DIR 目录 (JSON + CSV)

注意事项：
  - 首次运行会自动打开 Chrome 浏览器，请确保网络通畅
  - 爬取过程中不要手动关闭浏览器 / 不要操作浏览器
  - 登录后可以看到更多评论（非必须，不登录也能爬到一部分）
"""

from DrissionPage import ChromiumPage
import time
import json
import csv
import os
from datetime import datetime

# ====================================================================
# 配置区 - 修改这里
# ====================================================================

PRODUCTS = [
    # 格式: {"sku": "商品ID", "name": "备注名"}
    {"sku": "100310496358", "name": "测试商品"},
    # 可以添加更多:
    # {"sku": "10096961713154", "name": "另一个商品"},
]

MAX_SCROLL = 500          # 单商品最大滚动次数 (约10条/页)
OUTPUT_DIR = "jd_reviews"  # 输出目录

# ====================================================================
# 核心代码 - 无需修改
# ====================================================================


def extract_comments(packet) -> list:
    """从京东API响应包中提取评论列表"""
    comments = []
    try:
        data = packet.response.body
        floors = data.get("result", {}).get("floors", [])
        for floor in floors:
            if floor.get("mId") != "commentlist-list":
                continue
            for item in floor.get("data", []):
                info = item.get("commentInfo", {})
                comments.append({
                    "评论ID": info.get("commentId", ""),
                    "用户昵称": info.get("userNickName", ""),
                    "评论日期": info.get("commentDate", ""),
                    "评分": info.get("commentScore", ""),
                    "评分文本": info.get("commentScoreText", ""),
                    "评论内容": info.get("commentData", "").replace("\n", " "),
                    "点赞数": info.get("praiseCnt", ""),
                    "回复数": info.get("replyCnt", ""),
                    "产品规格": info.get("productSpecifications", ""),
                    "购买次数": info.get("buyCount", ""),
                    "用户等级": info.get("userLevel", ""),
                    "图片数量": len(info.get("pictureInfoList", []) or []),
                    "是否有图": "是" if info.get("pictureInfoList") else "否",
                    "是否追评": "是" if info.get("afterDays") else "否",
                })
    except Exception as e:
        print(f"    [!] 解析数据包失败: {e}")
    return comments


def crawl_product(page: ChromiumPage, sku: str, name: str, max_scroll: int) -> list:
    """爬取单个商品的全部评论"""
    url = f"https://item.jd.com/{sku}.html"
    print(f"\n{'='*60}")
    print(f"  商品: {name}")
    print(f"  SKU:  {sku}")
    print(f"  链接: {url}")
    print(f"{'='*60}")

    page.get(url)
    page.wait.doc_loaded()
    time.sleep(1)

    # 点击"全部评价"标签，触发评论加载
    try:
        btn = page.ele("tag:a@@text():全部评价", timeout=8)
        btn.click()
        print("  [OK] 已点击'全部评价'")
        time.sleep(2)
    except Exception as e:
        print(f"  [!] 点击'全部评价'失败 (可能已自动加载): {e}")

    # 等待评论容器出现
    try:
        container = page.ele("._rateListContainer_1ygkr_45", timeout=10)
    except Exception:
        print("  [!] 未找到评论容器，页面结构可能已变更")
        return []

    collected = []
    seen_ids = set()
    scroll_count = 0
    empty_rounds = 0  # 连续无新数据的轮数

    while scroll_count < max_scroll and empty_rounds < 10:
        scroll_count += 1

        # 向下滚动，触发加载更多
        container.scroll.down(800)
        time.sleep(1.5)

        # 尝试展开"展开更多评论"
        try:
            expand_btn = page.ele("._hoverContent_1ygkr_111", timeout=0.5)
            if expand_btn and expand_btn.states.is_displayed:
                expand_btn.click()
                print("    [展开] 点击了展开更多评论")
                time.sleep(1.5)
        except Exception:
            pass

        # 等待拦截API响应
        packet = page.listen.wait(timeout=4)
        if not packet or not packet.response:
            empty_rounds += 1
            continue

        comments = extract_comments(packet)
        new_count = 0
        for c in comments:
            cid = c["评论ID"]
            if cid and cid not in seen_ids:
                seen_ids.add(cid)
                collected.append(c)
                new_count += 1

        if new_count > 0:
            empty_rounds = 0
            print(f"  [第{scroll_count:>3}页] +{new_count:>3} 条 → 累计 {len(collected):>4} 条")
        else:
            empty_rounds += 1
            print(f"  [第{scroll_count:>3}页] 无新数据 (连续{empty_rounds}轮, {empty_rounds*2}s)")

        # 检测是否滚动到底部
        try:
            st = container.run_js("return this.scrollTop")
            sh = container.run_js("return this.scrollHeight")
            ch = container.run_js("return this.clientHeight")
            if st + ch >= sh - 10:
                print("  [结束] 已滚动至底部，无更多评论")
                break
        except Exception:
            pass

    print(f"  {'='*60}")
    print(f"  完成! {name} => 共 {len(collected)} 条不重复评论")
    return collected


def save_json(comments: list, filepath: str):
    """保存为JSON"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)


def save_csv(comments: list, filepath: str):
    """保存为CSV (UTF-8 BOM, Excel可直接打开)"""
    if not comments:
        return
    keys = list(comments[0].keys())
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(comments)


def save_results(comments: list, sku: str, name: str):
    """保存爬取结果"""
    if not comments:
        print(f"  [!] {name} 无数据，跳过保存")
        return

    safe_name = name.replace("/", "_").replace("\\", "_").replace(":", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{safe_name}_{sku}_{timestamp}"

    json_path = os.path.join(OUTPUT_DIR, f"{base}.json")
    csv_path = os.path.join(OUTPUT_DIR, f"{base}.csv")

    save_json(comments, json_path)
    save_csv(comments, csv_path)

    print(f"  [保存] JSON: {json_path}")
    print(f"  [保存] CSV:  {csv_path}")


def wait_for_login(page: ChromiumPage):
    """打开京东登录页，等待用户在终端按回车确认登录完成"""
    print("\n正在跳转到京东登录页...")
    page.get("https://passport.jd.com/new/login.aspx")
    page.wait.doc_loaded()
    print()
    print("=" * 60)
    print("  请在浏览器中手动登录京东")
    print("  如果已登录或无需登录，直接按 Enter 继续")
    print("=" * 60)
    input("  >>> 登录完成后按 Enter 继续...")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("京东商品评论批量爬取工具")
    print(f"输出目录: {OUTPUT_DIR}/")
    print(f"待爬商品: {len(PRODUCTS)} 个")
    print("正在启动浏览器...")

    page = ChromiumPage()
    page.listen.start("client.action")

    try:
        wait_for_login(page)

        for i, product in enumerate(PRODUCTS, 1):
            print(f"\n[{i}/{len(PRODUCTS)}]")
            comments = crawl_product(page, product["sku"], product["name"], MAX_SCROLL)
            save_results(comments, product["sku"], product["name"])
            if i < len(PRODUCTS):
                print("  准备爬取下一个商品...")
                time.sleep(2)
    finally:
        page.quit()

    print(f"\n全部完成! 共处理 {len(PRODUCTS)} 个商品")
    print(f"结果保存在 '{OUTPUT_DIR}/' 目录下")
