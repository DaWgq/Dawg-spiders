"""
闲鱼商品搜索 - 批量爬取 (签名逆向 + CSV保存)
"""
import requests
import hashlib
import time
import json
import csv
import os


# ============================================================
# 签名算法逆向
# ============================================================

class XianyuAPI:
    """
    闲鱼 MTOP API 封装
    签名算法: md5(token + "&" + t + "&" + appKey + "&" + dataJson)
    """

    APP_KEY = "34839810"
    BASE_URL = "https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "application/json",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://www.goofish.com",
            "referer": "https://www.goofish.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        })
        self._setup_cookies()

    def _setup_cookies(self):
        """设置Cookie（从浏览器或抓包获取）"""
        cookies = {
            "cna": "Gm5/In55snoCAbz9BOPVXW4C",
            "t": "dd5e21f58f5f44183bf0d6615ff5f601",
            "tracknick": "tb975336787",
            "_m_h5_tk": "a4c727fa2e7fd0fe4543a5d236f698f9_1778603357824",
            "_m_h5_tk_enc": "7be034ae13cd73988d57e2a1b287ce13",
            "cookie2": "1a4332ed29ddae83c74e2d67f63674df",
            "_tb_token_": "ee43eb13561ee",
            "sgcookie": "E1003ts3yqOvV66YQCNVOQsa9k%2BaAnUsDtnVa8%2FVzI4hsx68e8RNfmfk9XYQ5VDRSAUlyFeUuDJTl7TcMU%2FuRGeXAc58wa0eyd5VDpJ6m1yj2RQ%3D",
            "csg": "c19ed2fa",
        }
        for k, v in cookies.items():
            self.session.cookies.set(k, v)

    @property
    def _token(self) -> str:
        """从cookie中提取token（_m_h5_tk 在'_'之前的部分）"""
        tk = self.session.cookies.get("_m_h5_tk", "")
        return tk.split("_")[0] if "_" in tk else tk

    def _sign(self, t: str, data_json: str) -> str:
        """
        生成MTOP签名
        sign = md5(token + "&" + t + "&" + appKey + "&" + dataJson)
        """
        raw = f"{self._token}&{t}&{self.APP_KEY}&{data_json}"
        return hashlib.md5(raw.encode()).hexdigest()

    def search(self, keyword: str, page: int = 1, rows_per_page: int = 30,
               sort_field: str = "", sort_value: str = "") -> dict:
        """
        搜索商品

        Args:
            keyword: 搜索关键词
            page: 页码
            rows_per_page: 每页条数 (最大30)
            sort_field: 排序字段 (如 "price")
            sort_value: 排序值 (如 "asc"/"desc")

        Returns:
            dict: API响应
        """
        data_payload = {
            "pageNumber": page,
            "keyword": keyword,
            "fromFilter": False,
            "rowsPerPage": rows_per_page,
            "sortValue": sort_value,
            "sortField": sort_field,
            "customDistance": "",
            "gps": "",
            "propValueStr": {},
            "customGps": "",
            "searchReqFromPage": "pcSearch",
            "extraFilterValue": "{}",
            "userPositionJson": "{}",
        }
        data_json = json.dumps(data_payload, ensure_ascii=False, separators=(",", ":"))

        t = str(int(time.time() * 1000))
        sign = self._sign(t, data_json)

        params = {
            "jsv": "2.7.2",
            "appKey": self.APP_KEY,
            "t": t,
            "sign": sign,
            "v": "1.0",
            "type": "originaljson",
            "accountSite": "xianyu",
            "dataType": "json",
            "timeout": "20000",
            "api": "mtop.taobao.idlemtopsearch.pc.search",
            "sessionOption": "AutoLoginOnly",
        }

        resp = self.session.post(
            self.BASE_URL,
            params=params,
            data={"data": data_json},
        )
        return resp.json()

    def search_all(self, keyword: str, max_pages: int = 999,
                   sort_field: str = "", sort_value: str = "") -> list[dict]:
        """
        批量搜索所有页

        Returns:
            list[dict]: 所有商品信息
        """
        all_items = []
        page = 1

        while page <= max_pages:
            print(f"[第{page}页] 搜索 \"{keyword}\"...", end=" ")

            result = self.search(keyword, page=page, sort_field=sort_field, sort_value=sort_value)

            ret = result.get("ret", [])
            if not ret or "SUCCESS" not in str(ret):
                msg = result.get("ret", ["未知错误"])
                print(f"失败: {msg}")
                break

            result_list = result.get("data", {}).get("resultList", [])
            if not result_list:
                print("没有更多结果")
                break

            items = self._extract_items(result_list)
            all_items.extend(items)
            print(f"获取 {len(items)} 条, 累计 {len(all_items)} 条")

            # 检查是否有下一页
            has_next = result.get("data", {}).get("resultInfo", {}).get("hasNextPage", False)
            if not has_next:
                print("已到达最后一页")
                break

            page += 1
            time.sleep(1.5)

        return all_items

    @staticmethod
    def _extract_items(result_list: list) -> list[dict]:
        """从API响应中提取商品关键信息"""
        items = []
        for item_data in result_list:
            try:
                item = item_data.get("data", {}).get("item", {})
                main = item.get("main", {})
                click_args = main.get("clickParam", {}).get("args", {})
                ex_content = main.get("exContent", {})
                detail = ex_content.get("detailParams", {})

                items.append({
                    "itemId": detail.get("itemId", ""),
                    "title": (detail.get("title", "") or "").replace("\n", " "),
                    "price": click_args.get("price", ""),
                    "displayPrice": click_args.get("displayPrice", ""),
                    "seller": detail.get("userNick", ""),
                    "sellerId": click_args.get("seller_id", ""),
                    "location": ex_content.get("area", ""),
                    "publishTime": click_args.get("publishTime", ""),
                    "wantNum": click_args.get("wantNum", "0"),
                    "bizType": click_args.get("biz_type", ""),
                    "tag": click_args.get("tag", ""),
                    "tagname": click_args.get("tagname", ""),
                })
            except Exception as e:
                continue
        return items


# ============================================================
# CSV 保存
# ============================================================

def save_to_csv(items: list[dict], filename: str):
    """保存为CSV"""
    if not items:
        print("没有数据可保存")
        return

    fields = ["itemId", "title", "price", "displayPrice", "seller", "sellerId",
              "location", "publishTime", "wantNum", "bizType", "tag", "tagname"]

    with open(filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(items)

    print(f"\n已保存 {len(items)} 条数据到 {filename}")


def save_to_json(items: list[dict], filename: str):
    """保存为JSON"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"已保存 {len(items)} 条数据到 {filename}")


# ============================================================
# 批量爬取多个关键词
# ============================================================

def batch_search(keywords: list[str], max_pages_per_keyword: int = 5,
                 sort_field: str = "", sort_value: str = ""):
    """
    批量搜索多个关键词

    Args:
        keywords: 关键词列表
        max_pages_per_keyword: 每个关键词最多爬取页数
        sort_field: 排序字段
        sort_value: 排序值 (asc/desc)
    """
    api = XianyuAPI()

    for keyword in keywords:
        print(f"\n{'='*50}")
        print(f"搜索关键词: {keyword}")
        print(f"{'='*50}")

        items = api.search_all(keyword, max_pages=max_pages_per_keyword,
                               sort_field=sort_field, sort_value=sort_value)

        if items:
            safe_name = keyword.replace("/", "_").replace("\\", "_").replace("?", "")
            filename = f"xianyu_{safe_name}.csv"
            save_to_csv(items, filename)
            save_to_json(items, filename.replace(".csv", ".json"))
        else:
            print(f"关键词 \"{keyword}\" 无结果")

        time.sleep(2)


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    # ========== 配置 ==========
    KEYWORD = "手机"
    MAX_PAGES = 5   # 最多爬几页 (每页30条)
    SORT_FIELD = ""  # 排序: "" 综合, "price" 价格
    SORT_VALUE = ""  # 排序值: "asc" 升序, "desc" 降序
    # ==========================

    api = XianyuAPI()

    # 单关键词搜索
    items = api.search_all(KEYWORD, max_pages=MAX_PAGES,
                           sort_field=SORT_FIELD, sort_value=SORT_VALUE)

    if items:
        save_to_csv(items, f"xianyu_{KEYWORD}.csv")
        save_to_json(items, f"xianyu_{KEYWORD}.json")

        # 打印前5条
        print(f"\n=== 前5条结果 ===")
        for item in items[:5]:
            print(f"[{item['price']}元] {item['title'][:60]}")
            print(f"    卖家: {item['seller']} | 地点: {item['location']} | 想要: {item['wantNum']}")
            print()
    else:
        print("没有获取到数据")

    # ========== 批量搜索示例 ==========
    # batch_search(["手机", "笔记本电脑", "相机"], max_pages_per_keyword=3)
