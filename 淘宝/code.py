import hashlib
import json
import re
import time
import random
import urllib.parse
import requests
import pandas as pd

# ================= 1. 基础配置（已填入你 curl 中的真实凭证） =================
COOKIE_STR = (
    't=6878bc5521b1a890bc9175e0cc65a788; thw=xx; tracknick=tb975336787; '
    'havana_lgc2_0=eyJoaWQiOjIyMDkzOTQyMjA5NDYsInNnIjoiN2JkN2VlOWI3OTJlMWIyNmRhOWZhYjAzMGZhYWIwNWYiLCJzaXRlIjowLCJ0b2tlbiI6IjFYbTRwYUI3TzJZZEMxRVJ2Qzh6UTBnIn0; '
    '_hvn_lgc_=0; xlly_s=1; cookie2=128eb07d7af624c211ad2eb1b8e8663d; _tb_token_=eee93393053e5; '
    'unb=2209394220946; uc1=cookie14=UoYXL7mtBBkeNg%3D%3D&cookie15=UtASsssmOIJ0bQ%3D%3D&pas=0&cookie21=UIHiLt3xTIkz&existShop=false&cookie16=V32FPkk%2FxXMk5UvIbNtImtMfJQ%3D%3D; '
    'sn=; uc3=vt3=F8dD1fHoMMVnBcZ3Qa4%3D&nk2=F5RMHl%2F297M0iBI%3D&lg2=V32FPkk%2Fw0dUvg%3D%3D&id2=UUphw2ZQNahEaWo%2FnA%3D%3D; '
    'csg=c3333e41; lgc=tb975336787; cancelledSubSites=empty; cookie17=UUphw2ZQNahEaWo%2FnA%3D%3D; '
    'dnk=tb975336787; skt=b92a58bbcdecc15a; existShop=MTc5MzQ1MTY1OA%3D%3D; '
    'uc4=nk4=0%40FY4HWyoAUY1pHUtsE%2FafsKhsR4xT9g%3D%3D&id4=0%40U2grGNnTItmXNBbFQzVjcGEef19IrWFs; '
    '_cc_=V32FPkk%2Fhw%3D%3D; _l_g_=Ug%3D%3D; sg=765; _nk_=tb975336787; '
    'cookie1=AiPMjv1hZo%2F57GGgm%2BFAgIDTfI7P9Gs9DRgz5RJrrm0%3D; wk_cookie2=187b82c052c6bd3e094462f9751a7989; '
    'wk_unb=UUphw2ZQNahEaWo%2FnA%3D%3D; sgcookie=E100Gx4SlW5wileyCldX1FA%2BRpcSO0uCxOV%2FKrsQMFizoTgIShIq7f5uQl4h3nRGgiuUy%2FMCzS%2BHjiOA3jlLdYd6VFFD3w%2FeMfcssR7Viw4pdi4%3D; '
    'aui=2209394220946; cna=h9dxItxF4UYCAbz9BOOXFEJX; mtop_partitioned_detect=1; '
    '_m_h5_tk=7468aa0da89ba2746d4f0e6fe915ab13_1793534205573; _m_h5_tk_enc=3a7f7a106868aaede72839d1fe4fe148; '
    'sca=284f980a; _samesite_flag_=true; havana_sdkSilent=1793554727079; havana_lgc_exp=1824629952843; '
    'sdkSilent=1793554752842; _3dtid=OkKpyTfSQzlyU+pAFws1UW+VKkBXR/38MPmAUi2zlJ7b66I5RU9aD8jItYkEilTA; '
    'bxuab=0; tfstk=hP7HuYwTpWzQo5ETj0pWCOFOElUYpbffgL3K4eWMUdf4OpE7ATjGUOtpLpFBr3WPL5eYkg5g7sTWUzLrK68ITUyYHPnt_HwdpOLht35asQdWT2Wy4VkwCQcezp-rQcR2QL8yzT8ZbQAmz48r81owCQ8yUT8zs1J6ZUJPUUPG_ZYOtPSxmTjj4K1eI4uP8ztHnr9iz47GjHvqkdyhP-P9b_tlPbglx6SfFIWEL-KCaGXMtU4tYE5G4tA6YOioqH51wNcYkMef6OWNb02UHPWF66soWfwYTQ6hMNc_h-4ydE1PM0ruHwpdogXaJvr3xgYdC_aqnoZCwsQh1mE5JN_N6Cvv5piL84ecpKPgsmZBYCOLH5ViV0te1CvYs5mjdHR69-C..; '
    'isg=BJ2doECMq9tAk0z6Jmvm5yCprHmXutEMacrMx19i3vQjFr1IJwnj3faAQAoQ1unE'
)

APP_KEY = "12574478"
API_URL = "https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/"

HEADERS = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,zh-TW;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "referer": "https://s.taobao.com/",
    "sec-ch-ua": '"Not:A-Brand";v="8", "Chromium";v="156", "Google Chrome";v="156"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "script",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36",
    "cookie": COOKIE_STR,
}


# ================= 2. 签名与参数构造函数 =================
def extract_token(cookie_str: str) -> str:
    """从 Cookie 的 _m_h5_tk 中提取签名所需的 token"""
    match = re.search(r"_m_h5_tk=([^;_]+)", cookie_str)
    if not match:
        raise ValueError("Cookie 中未找到 _m_h5_tk，请检查！")
    return match.group(1)


def generate_sign(token: str, t: str, app_key: str, data_str: str) -> str:
    """淘宝 MTOP 标准 MD5 签名生成"""
    raw = f"{token}&{t}&{app_key}&{data_str}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def build_data_str(keyword: str, page: int, sort_mode: str = "_coefp") -> str:
    """
    构造请求中的 data 字符串
    sort_mode:
      - "_coefp": 综合排序（涵盖高中低各类自然流量商品）
      - "_sale": 销量从高到低（确保抓够高销量头部商品）
      - "price-asc": 价格从低到高
    """
    inner_params = {
        "device": "HMA-AL00",
        "isBeta": "false",
        "grayHair": "false",
        "from": "nt_history",
        "brand": "HUAWEI",
        "info": "wifi",
        "index": "4",
        "rainbow": "",
        "schemaType": "auction",
        "elderHome": "false",
        "isEnterSrpSearch": "true",
        "newSearch": "false",
        "network": "wifi",
        "subtype": "",
        "hasPreposeFilter": "false",
        "prepositionVersion": "v2",
        "client_os": "Android",
        "gpsEnabled": "false",
        "searchDoorFrom": "srp",
        "debug_rerankNewOpenCard": "false",
        "homePageVersion": "v7",
        "searchElderHomeOpen": "false",
        "search_action": "initiative",
        "sugg": "_4_1",
        "sversion": "13.6",
        "style": "list",
        "ttid": "600000@taobao_pc_10.7.0",
        "needTabs": "true",
        "areaCode": "CN",
        "vm": "nw",
        "countryNum": "156",
        "m": "pc",
        "page": page,
        "n": 48,
        "q": urllib.parse.quote(keyword),  # 与你原请求一致，内层 URL 编码一次
        "qSource": "url",
        "pageSource": "a21bo.jianhua/a.search_manual.0",
        "channelSrp": "",
        "tab": "all",
        "pageSize": 48,
        "totalPage": 100,
        "totalResults": 4800,
        "sourceS": "0",
        "sort": sort_mode,
        "bcoffset": "",
        "ntoffset": "",
        "filterTag": "",
        "service": "",
        "prop": "",
        "loc": "",
        "start_price": None,
        "end_price": None,
        "startPrice": None,
        "endPrice": None,
        "itemIds": None,
        "p4pIds": None,
        "p4pS": None,
        "categoryp": "",
        "ha3Kvpairs": None,
        "myCNA": "h9dxItxF4UYCAbz9BOOXFEJX",
        "screenResolution": "1920x1080",
        "viewResolution": "1905x956",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36",
        "couponUnikey": "",
        "subTabId": "",
        "np": "",
        "clientType": "h5",
        "isNewDomainAb": "false",
        "forceOldDomain": "false",
    }
    outer_data = {
        "appId": "34385",
        "params": json.dumps(inner_params, separators=(",", ":"), ensure_ascii=False),
    }
    return json.dumps(outer_data, separators=(",", ":"), ensure_ascii=False)


# ================= 3. 数据解析与过滤清洗 =================
def parse_sales(sales_str: str) -> int:
    """将 '1万+人付款'、'500+人收货' 转换为整数"""
    if not sales_str:
        return 0
    s = str(sales_str)
    num_match = re.search(r"(\d+(?:\.\d+)?)", s)
    if not num_match:
        return 0
    val = float(num_match.group(1))
    if "万" in s:
        val *= 10000
    return int(val)


def fetch_one_page(keyword: str, page: int, sort_mode: str, token: str) -> list:
    """请求单页并提取商品数组"""
    t = str(int(time.time() * 1000))
    data_str = build_data_str(keyword, page, sort_mode)
    sign = generate_sign(token, t, APP_KEY, data_str)

    params = {
        "jsv": "2.7.4",
        "appKey": APP_KEY,
        "t": t,
        "sign": sign,
        "api": "mtop.relationrecommend.wirelessrecommend.recommend",
        "v": "2.0",
        "timeout": "10000",
        "type": "jsonp",
        "dataType": "jsonp",
        "callback": "mtopjsonp6",
        "data": data_str,
        "bx-ua": "fast-load",
    }

    resp = requests.get(API_URL, headers=HEADERS, params=params, timeout=12)
    text = resp.text.strip()

    # 剥离外层 mtopjsonp6(...)
    match = re.search(r"mtopjsonp\d+\((.*)\)$", text, re.S)
    json_data = json.loads(match.group(1)) if match else json.loads(text)

    ret_msg = json_data.get("ret", [""])[0]
    if "SUCCESS" not in ret_msg:
        print(f"⚠️ 第 {page} 页请求异常: {ret_msg}")
        if "RGV587_ERROR" in ret_msg or "FAIL_SYS_USER_VALIDATE" in ret_msg:
            print("❌ 触发了霸王龙滑块 (bx-ua/tfstk)，请在浏览器刷新一次搜索页并替换脚本中的 COOKIE_STR！")
        return []

    items_raw = json_data.get("data", {}).get("itemsArray", [])
    parsed_items = []

    for item in items_raw:
        item_id = item.get("item_id") or item.get("itemId")
        if not item_id:
            continue

        # 清理标题中的 <span class=H> 高亮标签
        raw_title = item.get("title", "")
        clean_title = re.sub(r"<[^>]+>", "", raw_title).strip()

        price = item.get("priceWap") or item.get("price") or "0"
        try:
            price_val = float(re.findall(r"\d+(?:\.\d+)?", str(price))[0])
        except IndexError:
            price_val = 0.0

        sales_raw = item.get("realSales") or item.get("procity") or ""
        sales_num = parse_sales(sales_raw)

        shop_name = item.get("nick") or item.get("shopInfo", {}).get("title", "")
        user_id = item.get("userId") or item.get("sellerId") or shop_name

        # 规范化商品详情页 URL
        raw_url = item.get("auctionURL") or item.get("clickUrl") or ""
        if raw_url.startswith("//"):
            item_url = "https:" + raw_url
        elif not raw_url.startswith("http"):
            item_url = f"https://item.taobao.com/item.htm?id={item_id}"
        else:
            item_url = raw_url

        parsed_items.append({
            "platform": "taobao",
            "item_id": str(item_id),
            "shop_id": str(user_id),
            "shop_name": shop_name,
            "title": clean_title,
            "price": price_val,
            "sales_raw": sales_raw,
            "sales_count": sales_num,
            "item_url": f"https://item.taobao.com/item.htm?id={item_id}",
            "raw_url": item_url
        })

    return parsed_items


def clean_and_deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """执行你要求的 3 大清洗规则：剔除二手配件、同ID去重、同商家同款去重"""
    print(f"\n📊 原始抓取总条数: {len(df)}")

    # 1. 剔除二手/翻新/配件/耗材/维修及低于20元的引流配件
    exclude_keywords = [
        "二手", "翻新", "9成新", "95新", "99新", "闲置", "官翻",
        "耳罩", "海绵套", "耳垫", "保护套", "耳机套", "横梁套", "头梁垫", "头梁套", "替换",
        "耳机线", "升级线", "音频线", "延长线", "转接线", "转接头",
        "支架", "挂架", "底座", "收纳包", "收纳盒", "硬壳包",
        "维修", "寄修", "换电池", "换皮", "外壳", "配件", "仅配件", "单卖", "空盒"
    ]
    pattern = "|".join(exclude_keywords)
    df = df[~df["title"].str.contains(pattern, case=False, na=False)]
    df = df[df["price"] >= 25.0]  # 剔除25元以下的纯配件或假价格链接
    print(f"✅ 剔除二手/配件/异常低价后剩余: {len(df)} 条")

    # 2. 同商品 ID 严格去重（保留第1条）
    df = df.drop_duplicates(subset=["item_id"], keep="first")
    print(f"✅ 按 item_id 去重后剩余: {len(df)} 条")

    # 3. 同商家同款去重（提取标题中的英文字母+数字型号，结合前8个中文字符作为同款指纹）
    def make_model_fingerprint(row):
        title = row["title"]
        # 提取英文+数字的型号（如 WH1000XM5, Q45, H2, G733）
        models = re.findall(r"[A-Za-z0-9\-]{3,}", title.upper())
        model_key = models[0] if models else title[:10]
        return f"{row['shop_id']}_{model_key}"

    df["fingerprint"] = df.apply(make_model_fingerprint, axis=1)
    # 按销量降序排列，同商家同款优先保留销量最高的那条
    df = df.sort_values(by="sales_count", ascending=False)
    df = df.drop_duplicates(subset=["fingerprint"], keep="first").drop(columns=["fingerprint"])
    print(f"✅ 同商家同款去重后剩余: {len(df)} 条")

    return df.reset_index(drop=True)


def stratified_sample(df: pd.DataFrame, target_total: int = 200) -> pd.DataFrame:
    """按高、中、低销量分层抽样"""
    if len(df) == 0:
        return df

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
        take_n = min(len(sub_df), per_tier + 10)  # 多留10条作为失效页递补
        sampled_list.append(sub_df.sample(n=take_n, random_state=42))

    result = pd.concat(sampled_list, ignore_index=True)
    # 编号 item_001.html 起
    result["html_filename"] = [f"item_{i+1:03d}.html" for i in range(len(result))]
    return result


# ================= 4. 主程序入口 =================
if __name__ == "__main__":
    token = extract_token(COOKIE_STR)
    print(f"🔑 成功提取 _m_h5_tk Token: {token}")

    all_items = []
    keyword = "头戴式耳机"

    # 策略：抓 5 页销量排序（保障头部爆款） + 10 页综合排序（覆盖中长尾与低销量）
    crawl_plan = [("_sale", 5), ("_coefp", 10)]

    for sort_mode, max_pages in crawl_plan:
        mode_name = "销量排序" if sort_mode == "_sale" else "综合排序"
        for page in range(1, max_pages + 1):
            print(f"⏳ 正在抓取 [{mode_name}] 第 {page}/{max_pages} 页...")
            items = fetch_one_page(keyword, page, sort_mode, token)
            print(f"   -> 本页获取到 {len(items)} 个商品")

            if not items:
                print("⚠️ 当前排序页未返回数据，停止当前模式翻页。")
                break

            all_items.extend(items)
            # 随机停顿 3.5 ~ 6.5 秒，避免触发 MTOP 频率限制
            time.sleep(random.uniform(3.5, 6.5))

    if all_items:
        raw_df = pd.DataFrame(all_items)
        raw_df.to_csv("taobao_raw_pool.csv", index=False, encoding="utf-8-sig")

        clean_df = clean_and_deduplicate(raw_df)
        final_df = stratified_sample(clean_df, target_total=180)

        final_df.to_csv("taobao_target_queue.csv", index=False, encoding="utf-8-sig")
        print(f"\n🎉 采集与分层抽样完成！最终生成 {len(final_df)} 条淘宝待归档队列，已保存至 taobao_target_queue.csv")