import requests
import time
import hashlib
import json
import csv
import os


def get_taobao_sign(token, t, app_key, data_str):
    """根据淘宝 mtop 接口规则动态生成 sign"""
    sign_str = f"{token}&{t}&{app_key}&{data_str}"
    md5 = hashlib.md5()
    md5.update(sign_str.encode('utf-8'))
    return md5.hexdigest()


def extract_item_info(item):
    """从商品数据中提取关键信息"""
    # 提取标题（去除HTML标签）
    title = item.get('title', '')
    import re
    title_clean = re.sub(r'<[^>]+>', '', title)
    
    # 提取价格
    price_show = item.get('priceShow', {})
    price = price_show.get('price', item.get('price', ''))
    price_unit = price_show.get('unit', '¥')
    price_desc = price_show.get('priceDesc', '')
    
    # 提取店铺信息
    shop_info = item.get('shopInfo', {})
    shop_name = shop_info.get('title', '')
    shop_tag = item.get('shopTag', '')
    
    # 提取销量
    real_sales = item.get('realSales', '')
    
    # 提取地区
    procity = item.get('procity', '')
    
    # 提取商品ID和链接
    item_id = item.get('item_id', '')
    auction_url = item.get('auctionURL', '')
    if auction_url and not auction_url.startswith('http'):
        auction_url = 'https:' + auction_url
    
    # 提取图片链接
    pic_path = item.get('pic_path', '')
    
    # 提取商品属性
    structured_usp = item.get('structuredUSPInfo', [])
    properties = {}
    for usp in structured_usp:
        prop_name = usp.get('propertyName', '')
        prop_value = usp.get('propertyValueName', '')
        if prop_name and prop_value:
            properties[prop_name] = prop_value
    
    # 提取图标/标签
    icons = item.get('icons', [])
    icon_texts = []
    for icon in icons:
        text = icon.get('text', '')
        if text:
            icon_texts.append(text)
    
    return {
        '商品ID': item_id,
        '标题': title_clean,
        '价格': f"{price_unit}{price}",
        '价格说明': price_desc,
        '店铺名称': shop_name,
        '店铺标签': shop_tag,
        '销量': real_sales,
        '地区': procity,
        '商品链接': auction_url,
        '图片链接': pic_path,
        '品牌': properties.get('品牌', ''),
        '型号': properties.get('型号', ''),
        '屏幕尺寸': properties.get('屏幕尺寸', ''),
        '刷新率': properties.get('刷新率', ''),
        '电池容量': properties.get('电池容量', ''),
        '像素': properties.get('像素', ''),
        '机身内存': properties.get('机身内存ROM', ''),
        '充电功率': properties.get('充电功率', ''),
        '标签': '; '.join(icon_texts)
    }


def scrape_taobao_pages(keyword, start_page=1, end_page=3):
    app_key = "12574478"
    url = "https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/"
    
    # 用于存储所有商品数据
    all_items = []

    # ！！！非常重要：请务必去浏览器复制你刚刚刷新产生的最新 Cookie！！！
    # 旧的肯定已经过期了
    cookies = {
        "mtop_partitioned_detect": "1",
        "_m_h5_tk": "df86c2085ed32a1cc02145dc76aa5eae_1777012594987",
        "_m_h5_tk_enc": "b43e91add7dc99aed1f6ab43209a351b",
        "xlly_s": "1",
        "t": "6878bc5521b1a890bc9175e0cc65a788",
        "_tb_token_": "07bf34b97eee",
        "sca": "b8871d5e",
        "thw": "xx",
        "cookie2": "27e4375021d34bb74af7e8b36fc9a1ef",
        "_samesite_flag_": "true",
        "cna": "h9dxItxF4UYCAbz9BOOXFEJX",
        "3PcFlag": "1777002895575",
        "unb": "2209394220946",
        "lgc": "tb975336787",
        "cancelledSubSites": "empty",
        "cookie17": "UUphw2ZQNahEaWo%2FnA%3D%3D",
        "dnk": "tb975336787",
        "tracknick": "tb975336787",
        "_l_g_": "Ug%3D%3D",
        "sg": "765",
        "_nk_": "tb975336787",
        "cookie1": "AiPMjv1hZo%2F57GGgm%2BFAgIDTfI7P9Gs9DRgz5RJrrm0%3D",
        "sgcookie": "E100VWFVhF17mzHG3bCMh4aRF7wyEFzn7irxX6ww7GFfWg0fZK6ZIFFhQHLgW6OzTGLiPXF7cZowlxo53KQOpW7J2y%2BNb39zDqTLsVRmcYMRqGA%3D",
        "havana_lgc2_0": "eyJoaWQiOjIyMDkzOTQyMjA5NDYsInNnIjoiN2JkN2VlOWI3OTJlMWIyNmRhOWZhYjAzMGZhYWIwNWYiLCJzaXRlIjowLCJ0b2tlbiI6IjFYbTRwYUI3TzJZZEMxRVJ2Qzh6UTBnIn0",
        "_hvn_lgc_": "0",
        "cookie3_bak": "27e4375021d34bb74af7e8b36fc9a1ef",
        "cookie3_bak_exp": "1777262122176",
        "wk_cookie2": "16ed12d665ba7a8471e771307594d290",
        "wk_unb": "UUphw2ZQNahEaWo%2FnA%3D%3D",
        "uc1": "pas=0&cookie14=UoYZbYrVSRUuPg%3D%3D&existShop=false&cookie16=VT5L2FSpNgq6fDudInPRgavC%2BQ%3D%3D&cookie15=URm48syIIVrSKA%3D%3D&cookie21=WqG3DMC9FxUx",
        "uc3": "vt3=F8dD29octsCXimHjx7M%3D&id2=UUphw2ZQNahEaWo%2FnA%3D%3D&nk2=F5RMHl%2F297M0iBI%3D&lg2=U%2BGCWk%2F75gdr5Q%3D%3D",
        "csg": "7e3ecd6f",
        "env_bak": "FM%2BgmqK9a2XF76NvndNHX7%2BjLjqp0DtZo8bUc%2BiHXw2L",
        "skt": "6530ca6c6704441b",
        "existShop": "MTc3NzAwMjkyMg%3D%3D",
        "uc4": "id4=0%40U2grGNnTItmXNBbFQzVjcG%2BYlIXKQMGz&nk4=0%40FY4HWyoAUY1pHUtsE%2FaR%2BwN7nDFdog%3D%3D",
        "_cc_": "U%2BGCWk%2F7og%3D%3D",
        "havana_lgc_exp": "1808107081302",
        "sdkSilent": "1777031881301",
        "havana_sdkSilent": "1777031881301",
        "tfstk": "g4r-L1986sfuXNSf63b0xl1ITyWDoZmzU4NWxHmnZZNxGJuBxaooJDFjiucuE0GBvW23qWqLLHHQdWWrtT70U8oEA1fg9G2zUuqu15E-PjgjU-OWPZ05Z8iHU1fGjGbWhDCRs84iI8ujBAiIFbG7htHIdYiIRYwfHvMHNet7O-6xgYLSO4MWhIMrBDGQOD6YhjkKAYNIAtejgvM1f6hXFXxLlp_oEWYhIRygDY3-1-QwAHp_FCc7Fj-BAbCZPfsnMHtQDYwBmwCkXwc_7b0i1SsD2Dejp7c01GtxcVUaKvFR23iulrrrqof9Q4FKMVZmkQTSB0h-5ug2FHwqRrExqu1e7-2xNVn0oZ5o-0F87fu5usPLHbVQ2qORiX4gnugY1sxYT2UaKvFR23N14dqgXqmwsfHHPtBv8euS3c3c2MMYHokxHfXRve8EutkxstBv8euS3xhGe9Le8qWV.",
        "isg": "BKSk2cFmkf3MQeWxh8xPHFE2daKWPcinsllo4r7hZmr1aUkz5kjhN8SPKcHxsQD_"
    }

    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "referer": "https://s.taobao.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
    }

    token = cookies.get("_m_h5_tk", "").split("_")[0]
    if not token:
        print("未找到有效的 _m_h5_tk，请检查 Cookie！")
        return

    for page in range(start_page, end_page + 1):
        print(f"\n--- 正在抓取 [{keyword}] 的第 {page} 页 ---")

        inner_params = {
            "device": "HMA-AL00",
            "search_action": "initiative",
            "style": "list",
            "m": "pc",
            "page": page,
            "n": 48,
            "q": keyword,
            "tab": "all",
            "pageSize": 48
        }

        data_dict = {
            "appId": "34385",
            "params": json.dumps(inner_params, separators=(',', ':'))
        }
        data_str = json.dumps(data_dict, separators=(',', ':'))

        t = str(int(time.time() * 1000))
        sign = get_taobao_sign(token, t, app_key, data_str)

        # 补全了 callback 和 timeout 等参数，尽量拟真
        req_params = {
            "jsv": "2.7.4",
            "appKey": app_key,
            "t": t,
            "sign": sign,
            "api": "mtop.relationrecommend.wirelessrecommend.recommend",
            "v": "2.0",
            "timeout": "10000",
            "type": "jsonp",
            "dataType": "jsonp",
            "callback": "mtopjsonp6",
            "data": "{" + f'"appId":"34385","params":"{json.dumps(inner_params, separators=(",", ":")).replace('"', "\\\"")}"' + "}"
            # 严格按照你的原请求构造转义格式
        }

        # 强制按照原始请求里的转义格式来生成 data，避免字典 dumps 后的顺序或转义差异导致 sign 失效
        raw_data_str = "{\"appId\":\"34385\",\"params\":\"" + json.dumps(inner_params, separators=(',', ':')).replace(
            '"', '\\"') + "\"}"
        req_params['data'] = raw_data_str

        # 重新计算严格匹配的 sign
        req_params['sign'] = get_taobao_sign(token, t, app_key, raw_data_str)

        try:
            response = requests.get(url, headers=headers, cookies=cookies, params=req_params)
            response.raise_for_status()

            # 【关键修复】：去掉首尾的空格和换行符
            text = response.text.strip()

            if not text.startswith('mtopjsonp'):
                print(f"[警告] 服务器返回的不是预期数据，可能是拦截页或登录页！\n返回内容前200个字符: {text[:200]}")
                break

            start_idx = text.find('(') + 1
            end_idx = text.rfind(')')
            clean_text = text[start_idx:end_idx]

            json_data = json.loads(clean_text)

            if "SUCCESS" in str(json_data.get("ret", [])):
                items = json_data.get("data", {}).get("itemsArray", [])
                print(f"成功！第 {page} 页获取到 {len(items)} 条商品数据。")
                
                # 提取并打印商品信息
                page_items = []
                for idx, item in enumerate(items, 1):
                    item_info = extract_item_info(item)
                    page_items.append(item_info)
                    
                    # 打印到控制台
                    print(f"\n  [{idx}] {item_info['标题']}")
                    print(f"      价格: {item_info['价格']} {item_info['价格说明']}")
                    print(f"      店铺: {item_info['店铺名称']} ({item_info['店铺标签']})")
                    print(f"      销量: {item_info['销量']} | 地区: {item_info['地区']}")
                    print(f"      品牌: {item_info['品牌']} | 型号: {item_info['型号']}")
                    if item_info['屏幕尺寸']:
                        print(f"      规格: 屏幕{item_info['屏幕尺寸']} | 刷新率{item_info['刷新率']} | 电池{item_info['电池容量']}")
                    print(f"      标签: {item_info['标签']}")
                    print(f"      链接: {item_info['商品链接']}")
                    print("-" * 80)
                
                all_items.extend(page_items)
                print(f"\n第 {page} 页共处理 {len(page_items)} 条商品数据")
            else:
                print(f"请求失败，接口返回信息: {json_data.get('ret')}")

        except Exception as e:
            print(f"发生异常: {e}")

        # 延长休眠时间，降低被直接封禁的概率
        time.sleep(5)
    
    # 保存为CSV文件
    if all_items:
        save_to_csv(all_items, keyword)
    else:
        print("\n未获取到任何商品数据！")


def save_to_csv(items, keyword):
    """将商品数据保存为CSV文件"""
    # 生成文件名
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"淘宝商品_{keyword}_{timestamp}.csv"
    
    # 确保字段顺序
    fieldnames = [
        '商品ID', '标题', '价格', '价格说明', '店铺名称', '店铺标签',
        '销量', '地区', '商品链接', '图片链接',
        '品牌', '型号', '屏幕尺寸', '刷新率', '电池容量',
        '像素', '机身内存', '充电功率', '标签'
    ]
    
    try:
        with open(filename, 'w', encoding='utf-8-sig', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(items)
        
        print(f"\n{'='*80}")
        print(f"数据保存成功！")
        print(f"文件路径: {os.path.abspath(filename)}")
        print(f"共保存 {len(items)} 条商品数据")
        print(f"{'='*80}")
    except Exception as e:
        print(f"保存CSV文件时出错: {e}")


if __name__ == "__main__":
    # 请先在上方填入最新的 Cookie！！！
    scrape_taobao_pages("手机", start_page=1, end_page=3)