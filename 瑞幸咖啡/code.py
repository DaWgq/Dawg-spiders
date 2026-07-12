import requests
import json
import base64
import hashlib
import struct
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


# ==================== 1. 加密与解密核心函数 ====================

def get_encrypted_q(payload_dict, key_str):
    """AES-ECB 加密 q 参数并进行 URL 安全替换"""
    text = json.dumps(payload_dict, separators=(',', ':'))
    cipher = AES.new(key_str.encode('utf-8'), AES.MODE_ECB)
    padded_text = pad(text.encode('utf-8'), AES.block_size, style='pkcs7')
    encrypted_bytes = cipher.encrypt(padded_text)

    base64_str = base64.b64encode(encrypted_bytes).decode('utf-8')
    return base64_str.replace('+', '-').replace('/', '_')


def get_magic_md5_sign(sign_str):
    """还原 JS 魔改 MD5 生成 sign"""
    md5_bytes = hashlib.md5(sign_str.encode('utf-8')).digest()
    words = struct.unpack('>4i', md5_bytes)
    return "".join(str(abs(w)) for w in words)


def decrypt_response(encrypted_str, key_str):
    """AES-ECB 解密服务端返回的数据"""
    if not encrypted_str:
        return None
    try:
        standard_base64 = encrypted_str.replace('-', '+').replace('_', '/')
        missing_padding = len(standard_base64) % 4
        if missing_padding:
            standard_base64 += '=' * (4 - missing_padding)

        encrypted_bytes = base64.b64decode(standard_base64)
        cipher = AES.new(key_str.encode('utf-8'), AES.MODE_ECB)
        decrypted_padded = cipher.decrypt(encrypted_bytes)

        decrypted_text = unpad(decrypted_padded, AES.block_size, style='pkcs7').decode('utf-8')
        return json.loads(decrypted_text)
    except Exception as e:
        print(f"[-] 解密失败: {e}")
        return encrypted_str


# ==================== 2. 主逻辑 ====================

def main():
    # 基础配置
    AES_KEY = "CJQjAc1hYieC4QYb"
    UID = "a5af2ca2-6f11-47fd-9edc-1a2d9db2dacb1781196463889-918123490-hRmtt4iKRE52nC73QmtK0d5wefmn1jNL98OpS3Y0eqVCXO_.s3eK7AFczTMNVimt"

    # URL 目标 (当前为你抓的收货地址接口)
    # 如果要爬门店，请替换为类似： "https://capi.lkcoffee.com/resource/m/store/list"
    url = "https://capi.lkcoffee.com/resource/m/shop/shopList"

    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://servicewechat.com/wx21c7506e98a2fe75/916/page-frame.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541b18) XWEB/20005",
        "X-LK-AKV": "lk-wxmp-v5.3.22",
        "X-LK-CSID": "c5c857d9-766a-0a1c-4482-c9e6d19f210f",
        "X-LK-MID": "918123490",
        "X-LK-SID": "373922",
        "x-lkwx-ostype": "windows",
        "x-lkwx-sdkversion": "3.16.1",
        "xweb_xhr": "1"
    }

    cookies = {
        "uid": UID
    }

    # 1. 构造明文查询参数
    # 收货地址接口对应的参数通常是空的 {}，如果你请求的是门店列表，请替换为下方的字典
    payload_t = {
        "pageSize": 20,  # 每页请求多少条数据
        "pageNo": 1,  # 请求第几页 (部分接口可能是 pageNum 或 page)
        "longitude": 113.41627,  # 经度
        "latitude": 23.109635,  # 纬度
        "deptId": 373922,  # 城市/区域ID
        "supportTakeout": "0",  # 是否支持外卖，通常带上
        "extendsData": {"algTestGroupId": 12374, "algTestId": 2290, "Flow-30407": 0},
        "miniversion": "5572"
    }

    # 如果你把 url 换成了门店列表，请使用这个 payload_t：
    # payload_t = {
    #     "supportTakeout": "0",
    #     "deptId": 373922,
    #     "longitude": 113.41627,
    #     "latitude": 23.109635,
    #     "extendsData": {"algTestGroupId": 12374, "algTestId": 2290, "Flow-30407": 0},
    #     "miniversion": "5572"
    # }

    cid = "230101"
    dk = "1"

    # 2. 动态生成加密的 q
    print("[*] 正在动态加密请求参数 (q)...")
    q = get_encrypted_q(payload_t, AES_KEY)

    # 3. 动态生成签名的 sign
    print("[*] 正在动态生成签名 (sign)...")
    sign_str = f"cid={cid};dk={dk};q={q};uid={UID}{AES_KEY}"
    sign = get_magic_md5_sign(sign_str)

    data = {
        "cid": cid,
        "q": q,
        "dk": dk,
        "sign": sign
    }

    # 4. 发起请求
    print(f"[*] 正在发送请求 -> {url}")
    response = requests.post(url, headers=headers, cookies=cookies, data=data)
    print(f"[*] 响应状态码: {response.status_code}")

    # 5. 处理和解密返回数据
    if response.status_code == 200:
        try:
            resp_json = response.json()
            # 瑞幸通常把加密字符串放在 'content' 中，有的接口可能是 'data'
            target_encrypted_data = resp_json.get('content') or resp_json.get('data')

            if target_encrypted_data and isinstance(target_encrypted_data, str):
                print("[*] 获取到密文，正在解密...")
                decrypted_data = decrypt_response(target_encrypted_data, AES_KEY)
                print("\n================ [ 解密结果 (JSON) ] ================\n")
                print(json.dumps(decrypted_data, indent=4, ensure_ascii=False))
                print("\n=====================================================\n")
            else:
                print("[-] 响应的 JSON 中未发现加密字符串，服务器返回原文如下：")
                print(json.dumps(resp_json, indent=4, ensure_ascii=False))

        except requests.exceptions.JSONDecodeError:
            # 修改了这里的异常捕获：捕获 requests 抛出的 JSONDecodeError
            print("[*] 返回值为非 JSON 格式，正在尝试直接解密...")

            # 增加风控/报错拦截判断
            if response.text.strip().startswith("<"):
                print("[-] 警告: 服务器返回了 HTML，可能是 Header(CSID) 或 Cookie(uid) 过期，被风控拦截！")
                print("返回内容摘要:", response.text[:500])
            else:
                decrypted_data = decrypt_response(response.text, AES_KEY)
                print("\n================ [ 解密结果 (纯文本) ] ================\n")
                if isinstance(decrypted_data, dict):
                    print(json.dumps(decrypted_data, indent=4, ensure_ascii=False))
                else:
                    print(decrypted_data)
                print("\n=====================================================\n")
    else:
        print(f"[-] 请求异常！状态码: {response.status_code}\n{response.text}")


if __name__ == "__main__":
    main()