"""
Klei 奖励页面数据采集
从 accounts.klei.com/account/rewards 提取所有卡片数据，保存到 SQLite + CSV

card 结构:
  <div class="card reward [too-expensive|card-claimed]">
    <div class="card-header">
      <div class="game-info wide game-icon DST-icon"></div>
      <div class="cost-info">
        <span class="label">物品需要</span>
        <span class="value points"><span>1200</span><span class="icon"></span></span>
      </div>
    </div>
    <div class="card-body">
      <img src="https://items.kleientertainment.com/images/DST/XXX/small">
    </div>
    <div class="card-footer">
      <div class="item-info">
        <span class="collection">Nautical Collection</span>
        <h1 class="card-title">Leviathan Chest</h1>
        <span class="reskins">外观重置： Scaled Chest</span>
      </div>
      <!-- 可兑换: <a class="btn">兑换</a> -->
      <!-- 已兑换: <span class="status-success">成功兑换！</span> -->
    </div>
  </div>
"""

from DrissionPage import ChromiumPage
import sqlite3
import csv
import re
import os
from urllib.parse import urlparse

DB_PATH = os.path.join(os.path.dirname(__file__), "rewards.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "rewards.csv")


def extract_image_name(url: str) -> str:
    """从图片 URL 提取物品标识名"""
    if not url:
        return ""
    # URL: https://items.kleientertainment.com/images/DST/DRAGONFLYCHEST_KRAKEN/small
    # 取倒数第二段: DRAGONFLYCHEST_KRAKEN
    parsed = urlparse(url)
    parts = parsed.path.rstrip("/").split("/")
    return parts[-2] if len(parts) >= 2 else ""


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS rewards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game TEXT,
        cost INTEGER,
        cost_type TEXT,
        image_url TEXT,
        image_name TEXT,
        collection TEXT,
        title TEXT,
        reskins TEXT,
        is_expensive INTEGER DEFAULT 0,
        is_owned INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    csv_file = open(CSV_PATH, "w", newline="", encoding="utf-8-sig")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        "game", "cost", "cost_type", "image_url", "image_name",
        "collection", "title", "reskins", "is_expensive", "is_owned",
    ])

    print("正在启动浏览器...")
    dp = ChromiumPage()

    print("正在打开 https://accounts.klei.com/account/rewards")
    dp.get("https://accounts.klei.com/account/rewards")

    print("\n" + "=" * 50)
    print("请在浏览器中手动登录 Klei 账号")
    print("登录完成后回到终端，按 Enter 继续爬取")
    print("=" * 50)
    input(">>> 按 Enter 继续... ")

    # 等待页面稳定
    dp.wait.doc_loaded()
    dp.wait(2)

    reward_deck = dp.ele(".rewards-deck", timeout=15)
    if not reward_deck:
        print("错误: 未找到 .rewards-deck，页面可能未加载成功")
        dp.quit()
        return

    cards = reward_deck.eles("xpath:./div")
    print(f"共找到 {len(cards)} 个卡片\n")

    count = 0
    for i, card in enumerate(cards, 1):
        try:
            class_str = card.attr("class") or ""
            is_expensive = 1 if "too-expensive" in class_str else 0
            is_owned = 1 if "card-claimed" in class_str else 0

            # ----- game （从 game-icon 的 class 中提取） -----
            game_icon_ele = card.ele(".game-icon", timeout=0)
            game = ""
            if game_icon_ele:
                cls = game_icon_ele.attr("class") or ""
                m = re.search(
                    r"(DST|DS|ROG|SW|HAM|GROTTO|TURN_OF_SEASONS"
                    r"|WANDA|WURT|WORMWOOD|WALTER|WX78|WINONA"
                            r"|WICKERBOTTOM|WEBBER|WOLFGANG|WOODIE"
                    r"|WENDY|WILLOW|WILSON|MAXWELL|MISSING_PERSON"
                    r"|WORTOX|WOODLEGS|WARLY|WATHGRITHR|WES)_?icon",
                    cls,
                    re.I,
                )
                if m:
                    game = m.group(1).upper()

            # ----- cost -----
            cost = 0
            cost_info = card.ele(".cost-info")
            if cost_info:
                points_wrapper = cost_info.ele(".value.points")
                if points_wrapper:
                    m = re.search(r"\d+", points_wrapper.text.strip())
                    if m:
                        cost = int(m.group())

            # ----- image (分两步查: 先 .card-body, 再 img) -----
            image_url = ""
            image_name = ""
            body = card.ele(".card-body")
            if body:
                img = body.ele("tag:img")
                if img:
                    image_url = img.attr("src") or ""
                    image_name = extract_image_name(image_url)

            # ----- collection / title / reskins -----
            collection_ele = card.ele(".collection", timeout=0)
            collection = collection_ele.text.strip() if collection_ele else ""

            title_ele = card.ele(".card-title", timeout=0)
            title = title_ele.text.strip() if title_ele else ""

            reskins_ele = card.ele(".reskins", timeout=0)
            reskins = ""
            if reskins_ele:
                raw = reskins_ele.text.strip()
                m = re.match(r"外观重置[：:]\s*(.*)", raw)
                if m:
                    reskins = m.group(1).strip()

            # ----- 已兑换状态（兜底判断：卡面上有 status-success 也是已兑换） -----
            if not is_owned:
                status = card.ele(".status-success", timeout=0)
                if status:
                    is_owned = 1

            row = (
                game, cost, "points", image_url, image_name,
                collection, title, reskins, is_expensive, is_owned,
            )
            conn.execute(
                """INSERT INTO rewards
                   (game, cost, cost_type, image_url, image_name,
                    collection, title, reskins, is_expensive, is_owned)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                row,
            )
            csv_writer.writerow(row)
            count += 1

            tag = "✓已兑换" if is_owned else ("✗太贵" if is_expensive else "可兑换")
            print(f"  [{i:>3}] {title or '?':<28s} | {cost:>4}点 | {image_name:<30s} | {tag}")

        except Exception as e:
            print(f"  [{i:>3}] 解析失败: {e}")

    conn.commit()
    conn.close()
    csv_file.close()
    dp.quit()

    print(f"\n完成！共保存 {count} 条记录")
    print(f"  DB:  {DB_PATH}")
    print(f"  CSV: {CSV_PATH}")


if __name__ == "__main__":
    main()
