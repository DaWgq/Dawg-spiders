import requests
import time


def fetch_school_info(start_page=1, end_page=3):
    """
    批量爬取学校信息并解析输出到控制台
    :param start_page: 起始页码
    :param end_page: 结束页码
    """
    url = 'https://api.xf985211.com/User/GetSchoolInfoList?com=XF'

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://www.xf985211.com',
        'referer': 'https://www.xf985211.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36'
    }

    # 基础的数据载荷模板
    payload_template = {
        "PageSize": 30,
        "XXType": 10,
        "ZhuTypeId": "",
        "ZhuTypeIdzx": [],
        "ZhuLXIds": [],
        "SchoolInfoTypeIds": [],
        "ProIds": [],
        "SchoolInfoCCIds": [],
        "Sex": -1,
        "SchoolInfoXZIds": [],
        "SCKWC": "",
        "ECKWC": "",
        "SpecialityInfoCode": "",
        "SpecialityInfoName": [],
        "Code": "",
        "Name": [],
        "SchoolInfoCode": "",
        "SearchName": [],
        "ZXZhuType02Name": "",
        "ZXZhuType01Name": ""
    }

    for page in range(start_page, end_page + 1):
        print(f"\n{'=' * 25} 正在抓取第 {page} 页 {'=' * 25}")

        payload = payload_template.copy()
        payload["PageIndex"] = page

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # --- 解析步骤开始 ---

            # 1. 检查接口是否返回成功标识
            if not data.get("Ok"):
                print(f"❌ 接口返回业务错误: {data.get('Msg')}")
                break

            # 2. 提取学校数据列表
            rows = data.get("Data", {}).get("rows", [])

            # 如果当前页没有数据，说明爬取到了最后一页，提前退出
            if not rows:
                print("⚠️ 当前页没有数据，抓取已完成。")
                break

            # 3. 遍历提取所需字段
            for item in rows:
                # 基础信息
                school_name = item.get("Name", "未知")
                school_code = item.get("Code", "未知")
                province = item.get("ProName", "未知")
                city = item.get("CityName", "未知")
                tags = item.get("SchoolInfoCCName") or "普通"  # 如 985/211
                group_name = item.get("ZYZ", "未知")  # 专业组名称，如"101普通组"

                # 选科要求组合 (如：物理+化学)
                zhu_type = item.get("ZhuTypeName", "")
                zx_zhu_type = item.get("ZXZhuType01Name") or ""
                subject_req = f"{zhu_type}+{zx_zhu_type}" if zx_zhu_type else zhu_type

                # 历年投档数据解析
                year_info_list = []
                year_datas = item.get("YearDatas") or []
                for yd in year_datas:
                    year = yd.get("Year")
                    plan = yd.get("jhdata") or "0"  # 计划招生人数
                    score = yd.get("tdxdata") or "-"  # 投档线
                    rank = yd.get("wcdata") or "-"  # 最低位次
                    year_info_list.append(f"[{year}年: 计划{plan}人 | 分数:{score} | 位次:{rank}]")

                year_str = "  ".join(year_info_list)

                # 打印到控制台
                print(f"🏫 【{school_name}】 (代码:{school_code}) | 📍 {province}-{city} | 🏷️ 标签: {tags}")
                print(f"   📘 专业组: {group_name} | 🎯 选科要求: {subject_req}")
                print(f"   📊 录取数据: {year_str}")
                print("-" * 75)

            # --- 解析步骤结束 ---

        except requests.exceptions.RequestException as e:
            print(f"❌ 抓取第 {page} 页时发生网络错误: {e}")
        except ValueError:
            print(f"❌ 第 {page} 页解析 JSON 失败，服务器可能返回了非 JSON 内容。")

        # 爬虫礼仪：每次请求后休眠 2 秒
        time.sleep(2)


if __name__ == '__main__':
    fetch_school_info(start_page=1, end_page=3)