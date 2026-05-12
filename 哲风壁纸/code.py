import requests
import json
import time
import base64
import os
import sqlite3
from typing import Any, Dict, List
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


AES_KEY = b"68zhehao2O776519"
AES_IV = b"aa176b7519e84710"


def aes_encrypt_value(plain_text: str) -> str:
    """
    对应前端 b().encryptValue(...)
    AES/CBC/Pkcs7，加密后 Base64
    """
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain_text.encode("utf-8")) + padder.finalize()

    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(AES_IV))
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded_data) + encryptor.finalize()

    return base64.b64encode(encrypted).decode("utf-8")


def aes_decrypt_value(cipher_text: str) -> str:
    """
    对应前端 w(G)
    Base64 -> AES/CBC/Pkcs7 解密 -> UTF-8
    """
    try:
        encrypted_data = base64.b64decode(cipher_text)

        cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(AES_IV))
        decryptor = cipher.decryptor()
        padded_plain = decryptor.update(encrypted_data) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        plain_data = unpadder.update(padded_plain) + unpadder.finalize()

        return plain_data.decode("utf-8").replace("\x00", "")
    except Exception as e:
        print(f"[解密失败] {e}")
        return ""


# =========================
# 请求配置
# =========================

headers = {
    "accept": "application/json",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "priority": "u=1, i",
    "referer": "https://haowallpaper.com/?page=1",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "token": "ack:_177815338814510041274704340",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
}

cookies = {
    "askId": "ack%3A_177815338814510041274704340",
    "downEdit": "%22true%22",
    "popUpLogin": "ok",
    "_ga": "GA1.1.684562016.1778153404",
    "server_name_session": "6cb280cda0f73c18b8fe003cf952d514",
    "_clsk": "1xho8b9%5E1778415444454%5E1%5E1%5En.clarity.ms%2Fcollect",
    "isShowElNotice": "ok",
    "isWebsiteLog": "ok",
    "_clck": "1a3q6pg%5E2%5Eg5x%5E0%5E2318",
    "Hm_lvt_3c3619543a455fffe6917f75aba0e02b": "1778153402,1778222203,1778334032,1778416197",
    "Hm_lpvt_3c3619543a455fffe6917f75aba0e02b": "1778416197",
    "HMACCOUNT": "45FC6488ADA4CC26",
    "_ga_XT96CDMYZB": "GS2.1.s1778416197$o6$g1$t1778416619$j60$l0$h0"
}

url = "https://haowallpaper.com/link/pc/wallpaper/wallpaperList"


# =========================
# 数据处理函数
# =========================

def build_encrypted_params(page: int) -> Dict[str, str]:
    """
    构造每一页的加密 data 参数
    """
    payload = {
        "page": str(page),
        "sortType": 3,
        "rows": 12,
        "isFavorites": False,
        "wpType": "1,3,4"
    }

    plain_text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    encrypted_data = aes_encrypt_value(plain_text)

    return {
        "data": encrypted_data
    }


def parse_response_text(text: str) -> Any:
    """
    尝试解析返回结果：
    1. 如果整个 response.text 是密文，就直接解密；
    2. 如果 response.text 是 JSON，且里面某个 data 字段是密文，也尝试解密 data。
    """
    text = text.strip()

    # 情况1：返回本身就是 JSON
    try:
        obj = json.loads(text)

        # 如果返回是字符串，可能是 JSON 字符串形式的密文
        if isinstance(obj, str):
            decrypted = aes_decrypt_value(obj)
            if decrypted:
                try:
                    return json.loads(decrypted)
                except Exception:
                    return decrypted

        # 如果返回是 dict，并且 data 是加密字符串
        if isinstance(obj, dict):
            for key in ["data", "result", "rows"]:
                if key in obj and isinstance(obj[key], str):
                    decrypted = aes_decrypt_value(obj[key])
                    if decrypted:
                        try:
                            obj[key] = json.loads(decrypted)
                        except Exception:
                            obj[key] = decrypted
            return obj

        return obj

    except Exception:
        pass

    # 情况2：返回整体是加密字符串
    decrypted = aes_decrypt_value(text)
    if decrypted:
        try:
            return json.loads(decrypted)
        except Exception:
            return decrypted

    return text


def find_image_urls(obj: Any) -> List[str]:
    """
    递归提取 JSON 里的图片链接。
    因为不知道接口字段名，这里通用提取包含 http 且像图片的字段。
    """
    urls = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            urls.extend(find_image_urls(value))

    elif isinstance(obj, list):
        for item in obj:
            urls.extend(find_image_urls(item))

    elif isinstance(obj, str):
        lower = obj.lower()
        if (
            obj.startswith("http")
            and any(ext in lower for ext in [".jpg", ".jpeg", ".png", ".webp"])
        ):
            urls.append(obj)

    return list(set(urls))


def fetch_page(session: requests.Session, page: int, retry: int = 3) -> Any:
    """
    抓取单页
    """
    params = build_encrypted_params(page)

    page_headers = headers.copy()
    page_headers["referer"] = f"https://haowallpaper.com/?page={page}"

    for attempt in range(1, retry + 1):
        try:
            response = session.get(
                url,
                headers=page_headers,
                cookies=cookies,
                params=params,
                timeout=15
            )

            print(f"[第 {page} 页] 状态码：{response.status_code}")

            if response.status_code != 200:
                print(response.text[:300])
                time.sleep(2)
                continue

            return parse_response_text(response.text)

        except requests.RequestException as e:
            print(f"[第 {page} 页] 请求失败，第 {attempt} 次重试：{e}")
            time.sleep(2)

    return None


# =========================
# SQLite 数据库操作
# =========================

DB_PATH = "haowallpaper.db"


def init_db(db_path: str = DB_PATH):
    """初始化数据库，创建壁纸表"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallpapers (
            wtId TEXT PRIMARY KEY,
            type INTEGER,
            userId TEXT,
            fileId TEXT,
            fileMb TEXT,
            typeId TEXT,
            colorId TEXT,
            sort TEXT,
            showStatus INTEGER,
            rlevel INTEGER,
            rw TEXT,
            rh TEXT,
            createTime TEXT,
            labelList TEXT,
            downCount TEXT,
            favorCount TEXT,
            page INTEGER,
            crawlTime TEXT
        )
    """)
    conn.commit()
    conn.close()
    print(f"[数据库] 初始化完成: {db_path}")


def insert_wallpaper(conn: sqlite3.Connection, wallpaper: dict, page: int):
    """插入一条壁纸数据（重复则忽略）"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO wallpapers (
            wtId, type, userId, fileId, fileMb, typeId, colorId,
            sort, showStatus, rlevel, rw, rh, createTime,
            labelList, downCount, favorCount, page, crawlTime
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        wallpaper.get("wtId"),
        wallpaper.get("type"),
        wallpaper.get("userId"),
        wallpaper.get("fileId"),
        wallpaper.get("fileMb"),
        wallpaper.get("typeId"),
        wallpaper.get("colorId"),
        wallpaper.get("sort"),
        1 if wallpaper.get("showStatus") else 0,
        wallpaper.get("rlevel"),
        wallpaper.get("rw"),
        wallpaper.get("rh"),
        wallpaper.get("createTime"),
        json.dumps(wallpaper.get("labelList", []), ensure_ascii=False),
        wallpaper.get("downCount"),
        wallpaper.get("favorCount"),
        page,
        time.strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()


def crawl_and_save(start_page: int = 1, end_page: int = 2942):
    """
    批量爬取壁纸数据并保存到 SQLite
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    session = requests.Session()

    total_saved = 0

    for page in range(start_page, end_page + 1):
        print(f"\n========== 正在抓取第 {page}/{end_page} 页 ==========")

        data = fetch_page(session, page)

        if not data:
            print(f"[第 {page} 页] 没有拿到有效数据")
            continue

        try:
            wallpaper_list = data.get('data', {}).get('list', [])

            if not wallpaper_list:
                print(f"[第 {page} 页] 没有壁纸数据")
                continue

            print(f"[第 {page} 页] 找到 {len(wallpaper_list)} 张壁纸")

            for idx, wallpaper in enumerate(wallpaper_list, 1):
                file_id = wallpaper.get('fileId')
                if not file_id:
                    print(f"  [跳过] 第 {idx} 个壁纸缺少 fileId")
                    continue

                insert_wallpaper(conn, wallpaper, page)
                total_saved += 1
                print(f"  [{idx}/{len(wallpaper_list)}] 已保存: {wallpaper.get('wtId')}")

            # 每页之间延迟
            time.sleep(2)

            print(f"\n[进度] 已完成 {page}/{end_page} 页 | 已保存: {total_saved} 条")

        except Exception as e:
            print(f"[第 {page} 页] 解析数据失败: {e}")
            continue

    conn.close()
    print("\n" + "=" * 50)
    print("采集完成！")
    print(f"总共保存: {total_saved} 条壁纸数据")
    print(f"数据库: {DB_PATH}")
    print("=" * 50)


if __name__ == "__main__":
    # 开始爬取，数据保存到 SQLite
    # start_page: 起始页码
    # end_page: 结束页码（总共 2942 页）
    crawl_and_save(start_page=1, end_page=2942)