import requests
import hashlib
import math
import struct
import json
import os
import time


# ========== 1. 自定义 xooo，注意不是标准 md5 ==========
def left_rotate(x, c):
    x &= 0xffffffff
    return ((x << c) | (x >> (32 - c))) & 0xffffffff


def xooo(text):
    """
    JS 里的自定义 MD5 变种：
    初始值顺序被改过：
    D = 0x10325476
    C = 0x98badcfe
    B = 0xefcdab89
    A = 0x67452301

    所以不能直接 hashlib.md5()
    """
    data = text.encode("utf-8")
    bit_len = (len(data) * 8) & 0xffffffffffffffff

    data += b"\x80"
    while len(data) % 64 != 56:
        data += b"\x00"

    data += struct.pack("<Q", bit_len)

    # 改过顺序的初始值
    a0 = 0x10325476
    b0 = 0x98badcfe
    c0 = 0xefcdab89
    d0 = 0x67452301

    s = (
        [7, 12, 17, 22] * 4
        + [5, 9, 14, 20] * 4
        + [4, 11, 16, 23] * 4
        + [6, 10, 15, 21] * 4
    )

    k = [
        int(abs(math.sin(i + 1)) * (2 ** 32)) & 0xffffffff
        for i in range(64)
    ]

    for offset in range(0, len(data), 64):
        block = data[offset:offset + 64]
        m = list(struct.unpack("<16I", block))

        a, b, c, d = a0, b0, c0, d0

        for i in range(64):
            if 0 <= i <= 15:
                f = (b & c) | ((~b) & d)
                g = i
            elif 16 <= i <= 31:
                f = (b & d) | (c & (~d))
                g = (5 * i + 1) % 16
            elif 32 <= i <= 47:
                f = b ^ c ^ d
                g = (3 * i + 5) % 16
            else:
                f = c ^ (b | (~d))
                g = (7 * i) % 16

            f = (f + a + k[i] + m[g]) & 0xffffffff
            a, d, c, b = d, c, b, (b + left_rotate(f, s[i])) & 0xffffffff

        a0 = (a0 + a) & 0xffffffff
        b0 = (b0 + b) & 0xffffffff
        c0 = (c0 + c) & 0xffffffff
        d0 = (d0 + d) & 0xffffffff

    return struct.pack("<4I", a0, b0, c0, d0).hex()


# ========== 2. 生成 t 参数 ==========
def generate_t(page):
    salt = "b|s|b|s|b|s|b|s|b|l"

    # 注意：这里不要带域名，只用 path + query
    api_path = f"/api/problem-detail/10/data/?page={page}"

    first_hash = xooo(api_path + salt)
    t = hashlib.sha256(first_hash.encode("utf-8")).hexdigest()

    return t


# ========== 3. 请求头和 Cookie ==========
headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.mashangpa.com/problem-detail/10/",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}

cookies = {
    "sessionid": "cltgpy5soaoykvyavu7q8jagr2bv6g1e",
    "Hm_lvt_0d2227abf9548feda3b9cb6fddee26c0": "1777381181,1777448593,1777628901,1777723369",
    "HMACCOUNT": "45FC6488ADA4CC26",
    "Hm_lpvt_0d2227abf9548feda3b9cb6fddee26c0": "1777724366",
}


# ========== 4. 断点续爬 ==========
PROGRESS_FILE = "mashangpa_10_progress.json"
RESULT_FILE = "mashangpa_10_result.json"


def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return {"completed_pages": [], "total_array": [0] * 10}
    
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"completed_pages": [], "total_array": [0] * 10}


def save_progress(progress_data):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=4)


# ========== 5. 单页请求 ==========
def fetch_page(page, retry=3):
    url = "https://www.mashangpa.com/api/problem-detail/10/data/"

    params = {
        "page": str(page),
        "t": generate_t(page)
    }

    for i in range(retry):
        try:
            response = requests.get(
                url,
                headers=headers,
                cookies=cookies,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                current_array = result.get("current_array", [])
                
                # 验证数据有效性
                if len(current_array) == 10:
                    print(f"第 {page} 页状态码：{response.status_code}，获取到有效数据")
                    return current_array
                else:
                    print(f"第 {page} 页数据异常（数组长度:{len(current_array)}），将重试...")
                    time.sleep(2)
            else:
                print(f"第 {page} 页第 {i + 1} 次请求失败，状态码: {response.status_code}，将重试...")
                time.sleep(2)

        except Exception as e:
            print(f"第 {page} 页第 {i + 1} 次请求异常：{e}，将重试...")
            time.sleep(2)
    
    return None


# ========== 6. 批量爬取 ==========
def main():
    # 加载进度
    progress = load_progress()
    total_array = progress.get("total_array", [0] * 10)
    completed_pages = set(progress.get("completed_pages", []))
    
    print(f"已完成的页数: {sorted(completed_pages)}")
    print(f"当前累加数组: {total_array}")
    print()
    
    start_page = 1
    end_page = 20

    print(f"开始爬取第 {start_page} 到 {end_page} 页")
    print("="*50)

    for page in range(start_page, end_page + 1):
        # 跳过已完成的页面
        if page in completed_pages:
            print(f"第 {page} 页已完成，跳过")
            continue
        
        print(f"正在爬取第 {page} 页...")

        current_array = fetch_page(page)

        if current_array is None:
            print(f"⚠️ 第 {page} 页经过3次重试后仍然失败，请稍后重新运行程序继续爬取")
            break

        # 累加当前页的数组值
        for i in range(len(current_array)):
            total_array[i] += current_array[i]
        
        print(f"第 {page} 页爬取成功，current_array: {current_array}")
        
        # 标记该页已完成并保存进度
        completed_pages.add(page)
        progress["completed_pages"] = sorted(list(completed_pages))
        progress["total_array"] = total_array
        save_progress(progress)

        print(f"第 {page} 页保存完成")
        print()

        time.sleep(1)
    
    # 输出最终结果
    print("\n" + "="*50)
    print(f"20页数据累加结果 (已完成{len(completed_pages)}页):")
    print(f"total_array: {total_array}")
    print(f"数组总和: {sum(total_array)}")
    print("="*50)
    
    # 保存结果到文件（只有全部完成才保存最终结果）
    if len(completed_pages) == 20:
        result_data = {
            "total_pages": 20,
            "total_array": total_array,
            "sum": sum(total_array)
        }
        
        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=4)
        
        print("\n✅ 所有页面爬取完成！结果已保存到", RESULT_FILE)
        
        # 清理进度文件
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
            print("进度文件已清理")
    else:
        print(f"\n⚠️ 还有 {20 - len(completed_pages)} 页未完成，请重新运行程序继续爬取")
        print("进度已保存，下次运行将从断点继续")


if __name__ == "__main__":
    # 验证 page=2 的 t，应该等于你抓包里的值
    test_t = generate_t(2)
    print("page=2 测试 t =", test_t)

    # 正式爬取
    main()