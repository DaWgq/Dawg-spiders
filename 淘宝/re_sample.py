import re
import pandas as pd


def clean_and_deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    print(f"📊 原始抓取总条数: {len(df)}")

    # 1. 剔除二手/翻新/配件/耗材 + 假头戴（骨传导/挂耳/入耳/耳夹）
    exclude_keywords = [
        "二手", "翻新", "9成新", "95新", "99新", "闲置", "官翻",
        "耳罩", "海绵套", "耳垫", "保护套", "耳机套", "横梁套", "头梁垫", "头梁套", "替换",
        "耳机线", "升级线", "音频线", "延长线", "转接线", "转接头",
        "支架", "挂架", "底座", "收纳包", "收纳盒", "硬壳包",
        "维修", "寄修", "换电池", "换皮", "外壳", "配件", "仅配件", "单卖", "空盒",
        "骨传导", "挂耳式", "耳挂式", "颈挂", "挂脖", "入耳式", "半入耳", "耳夹式"
    ]
    pattern = "|".join(exclude_keywords)
    df = df[~df["title"].str.contains(pattern, case=False, na=False)]
    df = df[df["price"] >= 25.0]
    print(f"✅ 剔除二手/配件/非头戴后剩余: {len(df)} 条")

    # 2. 同商品 ID 去重
    df = df.drop_duplicates(subset=["item_id"], keep="first")
    print(f"✅ 按 item_id 去重后剩余: {len(df)} 条")

    # 3. 精准同商家同款去重（排除 ANC/USB/PRO 等通用词干扰，必须包含字母+数字才算型号）
    ignore_words = {"ANC", "USB", "HIFI", "PRO", "MAX", "PLUS", "FPS", "RGB", "TWS", "2024", "2025", "2026", "5.3",
                    "5.4", "7.1", "2.4G"}

    def make_model_fingerprint(row):
        title = str(row["title"]).upper()
        # 优先匹配同时含字母和数字的真实型号（如 WH-1000XM5, W820NB, G733, Q45）
        models = re.findall(r"[A-Z]+[\-]?[0-9]+[A-Z0-9]*|[0-9]+[\-]?[A-Z]+[A-Z0-9]*", title)
        valid_models = [m for m in models if m not in ignore_words and len(m) >= 2]
        if valid_models:
            model_key = valid_models[0]
        else:
            # 若无英文数字型号，取去除标点后的前12个字符
            clean_t = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", title)
            model_key = clean_t[:12]
        return f"{row['shop_id']}_{model_key}"

    df["fingerprint"] = df.apply(make_model_fingerprint, axis=1)
    df = df.sort_values(by="sales_count", ascending=False)
    df = df.drop_duplicates(subset=["fingerprint"], keep="first").drop(columns=["fingerprint"])
    print(f"✅ 同商家同款去重后剩余: {len(df)} 条")

    return df.reset_index(drop=True)


def stratified_sample(df: pd.DataFrame, target_total: int = 330) -> pd.DataFrame:
    """高、中、低销量分层抽样，默认抽取 330 条（300 条正式 + 30 条防失效递补）"""
    df = df.sort_values(by="sales_count", ascending=False).reset_index(drop=True)
    n = len(df)
    if n < 300:
        print(f"⚠️ 警告：去重后池子仅剩 {n} 条，不足 300 条！将全部输出，建议增加翻页页数。")

    high_end = int(n * 0.3)
    mid_end = int(n * 0.7)

    df.loc[:high_end, "sales_tier"] = "High (高销量)"
    df.loc[high_end:mid_end, "sales_tier"] = "Medium (中销量)"
    df.loc[mid_end:, "sales_tier"] = "Low (低销量)"

    per_tier = target_total // 3  # 每层 110 条
    sampled_list = []
    for tier in ["High (高销量)", "Medium (中销量)", "Low (低销量)"]:
        sub_df = df[df["sales_tier"] == tier]
        take_n = min(len(sub_df), per_tier)
        sampled_list.append(sub_df.sample(n=take_n, random_state=42))

    result = pd.concat(sampled_list, ignore_index=True)
    result["html_filename"] = [f"item_{i + 1:03d}.html" for i in range(len(result))]
    return result


if __name__ == "__main__":
    raw_df = pd.read_csv("taobao_raw_pool.csv")
    clean_df = clean_and_deduplicate(raw_df)
    final_df = stratified_sample(clean_df, target_total=330)
    final_df.to_csv("taobao_target_queue.csv", index=False, encoding="utf-8-sig")
    print(f"\n🎉 重新筛选完成！当前队列共 {len(final_df)} 条有效商品，已覆盖保存至 taobao_target_queue.csv")