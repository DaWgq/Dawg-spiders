import requests
import json
import time
import base64
import os
import re
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


def save_json(page: int, data: Any, folder: str = "haowallpaper_json"):
    """
    每页保存一份原始 JSON，方便后面分析字段
    """
    os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, f"page_{page}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def sanitize_filename(label_list: List[str]) -> str:
    """
    将 labelList 转换为合法的文件名
    移除或替换不合法的字符
    """
    if not label_list:
        return "unknown"
    
    # 用下划线连接所有标签
    filename = "_".join(label_list)
    
    # 移除 Windows 文件名中的非法字符: \ / : * ? " < > |
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    
    # 限制文件名长度（Windows 最大 255 字符）
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename


def download_image(session: requests.Session, file_id: str, label_list: List[str], 
                   save_dir: str = "wallpapers", retry: int = 3) -> bool:
    """
    下载单张壁纸图片
    """
    url = f'https://haowallpaper.com/link/common/file/getCroppingImg/{file_id}'
    filename = sanitize_filename(label_list)
    
    # 确保保存目录存在
    os.makedirs(save_dir, exist_ok=True)
    
    # 构造完整文件路径
    filepath = os.path.join(save_dir, f"{filename}.jpg")
    
    # 如果文件已存在，跳过
    if os.path.exists(filepath):
        print(f"  [跳过] 文件已存在: {filename}")
        return True
    
    for attempt in range(1, retry + 1):
        try:
            response = session.get(url, timeout=30)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"  [成功] 已下载: {filename}")
                return True
            else:
                print(f"  [失败] 状态码 {response.status_code}, 第 {attempt} 次重试")
                time.sleep(2)
                
        except requests.RequestException as e:
            print(f"  [错误] 下载失败: {e}, 第 {attempt} 次重试")
            time.sleep(2)
    
    print(f"  [失败] 无法下载: {filename}")
    return False


def crawl_and_download(start_page: int = 1, end_page: int = 2942, 
                       save_dir: str = "wallpapers"):
    """
    批量爬取并下载壁纸图片
    """
    session = requests.Session()
    
    total_downloaded = 0
    total_failed = 0
    
    for page in range(start_page, end_page + 1):
        print(f"\n========== 正在抓取第 {page}/{end_page} 页 ==========")
        
        data = fetch_page(session, page)
        
        if not data:
            print(f"[第 {page} 页] 没有拿到有效数据")
            continue
        
        # 解析数据结构
        try:
            wallpaper_list = data.get('data', {}).get('list', [])
            
            if not wallpaper_list:
                print(f"[第 {page} 页] 没有壁纸数据")
                continue
            
            print(f"[第 {page} 页] 找到 {len(wallpaper_list)} 张壁纸")
            
            # 遍历当前页的所有壁纸
            for idx, wallpaper in enumerate(wallpaper_list, 1):
                file_id = wallpaper.get('fileId')
                label_list = wallpaper.get('labelList', [])
                
                if not file_id:
                    print(f"  [跳过] 第 {idx} 个壁纸缺少 fileId")
                    continue
                
                print(f"  [{idx}/{len(wallpaper_list)}] 正在下载...")
                
                success = download_image(session, file_id, label_list, save_dir)
                
                if success:
                    total_downloaded += 1
                else:
                    total_failed += 1
                
                # 每张图片之间延迟，控制请求频率
                time.sleep(1.5)
            
            # 每页之间额外延迟
            time.sleep(2)
            
            # 打印进度
            print(f"\n[进度] 已完成 {page}/{end_page} 页 | 已下载: {total_downloaded} | 失败: {total_failed}")
            
        except Exception as e:
            print(f"[第 {page} 页] 解析数据失败: {e}")
            continue
    
    print("\n" + "="*50)
    print("采集完成！")
    print(f"总下载数量: {total_downloaded}")
    print(f"失败数量: {total_failed}")
    print(f"保存目录: {save_dir}")
    print("="*50)


if __name__ == "__main__":
    # 开始爬取并下载壁纸
    # start_page: 起始页码
    # end_page: 结束页码（总共 2942 页）
    # save_dir: 保存图片的文件夹
    crawl_and_download(start_page=1, end_page=2942, save_dir="wallpapers")