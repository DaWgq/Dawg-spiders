import requests
import base64
import json
import struct
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ==================== 1. 配置信息 ====================
API_URL = 'https://api.mars-coder.cn/api/learning-record/list'
PARAMS = {
    "type": "project_chapter",
    "page": "1",
    "size": "500"
}

# 密钥（来自你之前成功解密的配置）
AES_KEY_HEX = "4b215c5fa35b982a670b7576f06fe1b5c946aaebea42431622969b423e9fb385"

HEADERS = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,zh-TW;q=0.8",
    "authorization": "Bearer 93a9037f-5f73-4a03-ac21-b3d723cddec5",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "origin": "https://mars-coder.cn",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Google Chrome\";v=\"153\", \"Not_A Brand\";v=\"8\", \"Chromium\";v=\"153\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36",
    "x-crypto-session": "4b10b07781904ad7aa2f24c7fb539dce"
}


# ==================== 2. Protobuf 解析工具 ====================
def read_varint(data, offset):
    result = 0
    shift = 0
    while True:
        byte = data[offset]
        offset += 1
        result |= (byte & 0x7f) << shift
        if not (byte & 0x80):
            break
        shift += 7
    return result, offset


def parse_protobuf(data):
    """解析 Protobuf 格式的密文，提取 iv 和 ciphertext"""
    result = {'iv': b'', 'ciphertext': b''}
    offset = 0
    while offset < len(data):
        tag, offset = read_varint(data, offset)
        field_num = tag >> 3
        if field_num == 1:  # iv
            length, offset = read_varint(data, offset)
            result['iv'] = data[offset:offset + length]
            offset += length
        elif field_num == 2:  # ciphertext
            length, offset = read_varint(data, offset)
            result['ciphertext'] = data[offset:offset + length]
            offset += length
        else:
            # 跳过其他字段
            if (tag & 7) == 2:  # Length-delimited
                length, offset = read_varint(data, offset)
                offset += length
            elif (tag & 7) == 0:  # Varint
                _, offset = read_varint(data, offset)
    return result


# ==================== 3. 新版解密 (AES-GCM) ====================
def hz_decrypt(base64_data, aes_key: bytes):
    base64_data = base64_data.strip().replace("\n", "").replace(" ", "")
    raw_data = base64.b64decode(base64_data)
    parsed = parse_protobuf(raw_data)

    iv = parsed['iv']
    ciphertext = parsed['ciphertext']

    if len(aes_key) != 32:
        raise ValueError(f"AES密钥长度错误，需32字节，当前{len(aes_key)}字节")

    aesgcm = AESGCM(aes_key)
    decrypted_bytes = aesgcm.decrypt(iv, ciphertext, None)
    return json.loads(decrypted_bytes.decode('utf-8'))


# ==================== 4. 主流程 ====================
def main():
    print("正在请求接口...")
    response = requests.get(API_URL, headers=HEADERS, params=PARAMS, timeout=15)

    print(f"HTTP 状态码: {response.status_code}")
    print(f"响应头 x-encrypted: {response.headers.get('x-encrypted', '未设置')}")

    resp_json = response.json()
    print(f"\n原始响应: {json.dumps(resp_json, ensure_ascii=False, indent=2)}")

    if 'data' not in resp_json or not resp_json['data']:
        print("响应中没有 data 字段或为空。")
        return

    encrypted_data = resp_json['data']
    encrypted_version = response.headers.get('x-encrypted', '')

    try:
        if encrypted_version == '2':
            print("\n检测到新版加密 (AES-GCM)，开始解密...")
            aes_key = bytes.fromhex(AES_KEY_HEX.replace(" ", "").replace("\n", ""))
            decrypted = hz_decrypt(encrypted_data, aes_key)
        else:
            print(f"\n未知加密版本 ({encrypted_version})，尝试使用 AES-GCM 解密...")
            aes_key = bytes.fromhex(AES_KEY_HEX.replace(" ", "").replace("\n", ""))
            decrypted = hz_decrypt(encrypted_data, aes_key)

        print("\n" + "=" * 60)
        print("解密成功！解密后的数据：")
        print("=" * 60)

        # 格式化打印
        if isinstance(decrypted, (dict, list)):
            print(json.dumps(decrypted, ensure_ascii=False, indent=2))
        else:
            print(decrypted)

    except Exception as e:
        print(f"\n解密失败: {e}")
        print("请检查密钥是否正确，或确认 x-crypto-session 是否已过期。")


if __name__ == '__main__':
    main()