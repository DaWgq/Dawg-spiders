import os
import time
import json
import hashlib
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


# =========================
# 基础配置
# =========================

BASE_URL = "https://www.mashangpa.com/api/problem-detail/7/data/"

TOTAL_PAGE = 20

SAVE_FILE = "mashangpa_7_result.json"

FAILED_FILE = "mashangpa_7_failed_pages.json"

SESSION_ID = "cltgpy5soaoykvyavu7q8jagr2bv6g1e"


# =========================
# 生成请求参数
# =========================

def get_sign():
    """
    生成 ts、m、x

    ts = 当前13位时间戳
    m  = MD5("xialuo" + ts)
    x  = SHA256(m + "xxoo")
    """
    ts = str(int(time.time() * 1000))

    m = hashlib.md5(("xialuo" + ts).encode("utf-8")).hexdigest()

    x = hashlib.sha256((m + "xxoo").encode("utf-8")).hexdigest()

    return ts, m, x


# =========================
# 解密 r
# =========================

def decrypt_r(r_hex):
    """
    r 是 AES-CBC-Pkcs7 加密后的 hex 字符串
    """
    key = b"xxxxxxxxoooooooo"
    iv = b"0123456789ABCDEF"

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(bytes.fromhex(r_hex))
    plain = unpad(decrypted, AES.block_size).decode("utf-8")

    return json.loads(plain)


# =========================
# 读取已保存数据
# =========================

def load_saved_data():
    """
    读取已经爬过的数据，用于断点续爬
    """
    if not os.path.exists(SAVE_FILE):
        return {}

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 保证 key 是字符串形式
        return {str(k): v for k, v in data.items()}

    except Exception:
        return {}


# =========================
# 保存数据
# =========================

def save_data(data):
    """
    每成功一页就保存一次
    """
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_failed_pages(failed_pages):
    """
    保存失败页码
    """
    with open(FAILED_FILE, "w", encoding="utf-8") as f:
        json.dump(failed_pages, f, ensure_ascii=False, indent=2)


# =========================
# 请求单页
# =========================

def fetch_page(page, max_retry=3):
    """
    爬取单页数据，失败自动重试
    """
    for retry in range(1, max_retry + 1):
        try:
            ts, m, x = get_sign()

            headers = {
                "accept": "application/json, text/javascript, */*; q=0.01",
                "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
                "cache-control": "no-cache",
                "m": m,
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": "https://www.mashangpa.com/problem-detail/7/",
                "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "ts":ts,
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
                "x-requested-with": "XMLHttpRequest"
            }

            cookies = {
                "sessionid": SESSION_ID
            }

            params = {
                "page": str(page),
                "x": x
            }

            response = requests.get(
                BASE_URL,
                headers=headers,
                cookies=cookies,
                params=params,
                timeout=20
            )

            print(f"第 {page} 页状态码：{response.status_code}")
            print()

            response.raise_for_status()

            result = response.json()

            if "r" not in result:
                print("接口未返回 r，原始返回：")
                print(result)
                return result

            data = decrypt_r(result["r"])

            return data

        except Exception as e:
            print(f"第 {page} 页第 {retry} 次请求失败：{e}")

            if retry < max_retry:
                sleep_time = retry * 2
                print(f"等待 {sleep_time} 秒后重试...")
                time.sleep(sleep_time)
            else:
                print(f"第 {page} 页重试失败，跳过。")
                return None


def calculate_sum(data):
    """
    计算所有 current_array 的累加值
    """
    total_sum = 0
    page_details = []

    for page_key in sorted(data.keys(), key=lambda x: int(x)):
        page_data = data[page_key]
        current_array = page_data['current_array']
        page_sum = sum(current_array)
        total_sum += page_sum
        page_details.append({
            'page': page_key,
            'sum': page_sum,
            'count': len(current_array)
        })

    # 打印每页详情
    print("\n" + "=" * 50)
    print("每页 current_array 求和详情:")
    print("=" * 50)
    for detail in page_details:
        print(f"第 {detail['page']:>2} 页: {detail['sum']:>6} (共 {detail['count']} 个数字)")

    # 打印总计
    print("=" * 50)
    print(f"所有页面总和: {total_sum}")
    print(f"总页数: {len(data)}")
    print(f"总数字个数: {sum(d['count'] for d in page_details)}")
    print("=" * 50)

    return total_sum


# =========================
# 主程序：批量爬取 + 断点续爬
# =========================

def main():
    saved_data = load_saved_data()

    failed_pages = []

    print("已完成页码：", list(saved_data.keys()))

    for page in range(1, TOTAL_PAGE + 1):
        page_key = str(page)

        # 断点续爬：已经成功的页直接跳过
        if page_key in saved_data:
            print(f"第 {page} 页已存在，跳过。")
            continue

        print(f"\n开始爬取第 {page} 页...")

        data = fetch_page(page)

        if data is not None:
            saved_data[page_key] = data
            save_data(saved_data)
            print(f"第 {page} 页保存成功。")
        else:
            failed_pages.append(page)
            save_failed_pages(failed_pages)
            print(f"第 {page} 页保存到失败列表。")

        # 降低请求频率，避免太快
        time.sleep(1)

    print("\n全部任务结束。")
    print(f"成功页数：{len(saved_data)}")
    print(f"失败页码：{failed_pages}")

    if failed_pages:
        save_failed_pages(failed_pages)

    print(f"\n结果文件：{SAVE_FILE}")
    print(f"失败页文件：{FAILED_FILE}")

    # 自动计算累加结果
    if saved_data:
        print("\n正在计算累加结果...")
        total = calculate_sum(saved_data)
        print(f"\n最终结果: {total}")


if __name__ == "__main__":
    main()