import requests
import time
import json
import hashlib
import re
from urllib.parse import quote_from_bytes


def make_sign(token, t, app_key, data):
    s = f"{token}&{t}&{app_key}&{data}"
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def parse_jsonp(text):
    match = re.search(r"^[^(]+\((.*)\)$", text.strip())
    if not match:
        return None
    return json.loads(match.group(1))


def make_data(keyword, page, page_id):
    encoded_keyword = quote_from_bytes(keyword.encode("gbk"))

    inner_params = {
        "beginPage": page,
        "pageSize": 60,
        "method": "getOfferList",
        "pageId": page_id,
        "verticalProductFlag": "pcmarket",
        "searchScene": "pcOfferSearch",
        "charset": "GBK",
        "spm": "a260k.home2025.searchbox.0",
        "keywords": encoded_keyword,
    }

    inner_str = json.dumps(inner_params, ensure_ascii=False, separators=(",", ":"))

    outer_data = {"appId": 32517, "params": inner_str}

    return json.dumps(outer_data, ensure_ascii=False, separators=(",", ":"))


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "referer": "https://s.1688.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
}

cookies = {
    # 这里放你自己的 cookies
    "_m_h5_tk": "b4228dfaba0dad71f358f8a1542c2b59_1780395299419",
    "_m_h5_tk_enc": "cfa02086c564b950d107b0b597a30b40",
}

url = "https://h5api.m.1688.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/"

session = requests.Session()
session.headers.update(headers)
session.cookies.update(cookies)

app_key = "12574478"
api = "mtop.relationrecommend.WirelessRecommend.recommend"
page_id = "j0oooCBwfW8Rwx0JCPLOMEuQE0yo3WtQp7BO3xhLTozP9fct"

keyword = "红米手机"

for page in range(1, 11):
    t = str(int(time.time() * 1000))

    data = make_data(keyword, page, page_id)

    token_cookie = session.cookies.get("_m_h5_tk")
    token = token_cookie.split("_")[0]

    sign = make_sign(token, t, app_key, data)

    params = {
        "jsv": "2.7.4",
        "appKey": app_key,
        "t": t,
        "sign": sign,
        "api": api,
        "v": "2.0",
        "jsonpIncPrefix": "reqTppId_32517_getOfferList",
        "excludeKeys": "",
        "type": "jsonp",
        "dataType": "jsonp",
        "callback": f"mtopjsonp{page}",
        "data": data,
    }

    response = session.get(url, params=params, timeout=10)

    print("page:", page)
    print(response.text)

    result = parse_jsonp(response.text)

    if not result:
        print("JSONP 解析失败")
        continue

    ret = result.get("ret", [])
    print("ret:", ret)

    if ret and "FAIL_SYS_TOKEN_EXOIRED" in ret[0]:
        print("token 过期，需要重新请求后再签名")
        continue

    data_obj = result.get("data", {})
    offer_data = data_obj.get("data", {}).get("OFFER", {})
    items = offer_data.get("items", [])

    all_offers = []
    for item in items:
        d = item.get("data", {})
        offer = {
            "offerId": d.get("offerId"),
            "title": re.sub(r"<[^>]+>", "", d.get("title", "")),
            "price": d.get("priceInfo", {}).get("price"),
            "priceType": d.get("priceInfo", {}).get("priceType"),
            "offerPicUrl": d.get("offerPicUrl"),
            "loginId": d.get("loginId"),
            "shopName": d.get("shop", {}).get("text"),
            "shopLink": d.get("shopAddition", {}).get("shopLinkUrl"),
            "province": d.get("province"),
            "city": d.get("city"),
            "linkUrl": d.get("linkUrl"),
            "bookedCount": d.get("bookedCount"),
            "afterPriceText": d.get("afterPrice", {}).get("text"),
            "type": d.get("type"),
            "block": d.get("block"),
            "bizType": d.get("bizType"),
            "offerRepurchaseRate": d.get("offerRepurchaseRate"),
            "memberId": d.get("memberId"),
            "winPortUrl": d.get("winPortUrl"),
            "quantityPrices": d.get("shopAddition", {}).get("quantityPrices"),
        }
        all_offers.append(offer)

    print(f"parsed {len(all_offers)} offers")

    with open("results.jsonl", "a", encoding="utf-8") as f:
        for offer in all_offers:
            f.write(json.dumps(offer, ensure_ascii=False) + "\n")

    time.sleep(1)
