import requests
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64


def decrypt_data(encrypted_data):
    """
    解密AES加密的数据
    :param encrypted_data: Base64编码的加密字符串
    :return: 解密后的JSON对象
    """
    # 密钥
    key = b"DXZWdxUZ5jgsUFPF"
    
    # Base64解码
    encrypted_bytes = base64.b64decode(encrypted_data)
    
    # 创建AES解密器（ECB模式）
    cipher = AES.new(key, AES.MODE_ECB)
    
    # 解密并去除填充
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    decrypted_padded = unpad(decrypted_bytes, AES.block_size)
    
    # 转换为字符串并解析JSON
    decrypted_str = decrypted_padded.decode('utf-8')
    return json.loads(decrypted_str)


headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.jinglingshuju.com",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
}
url = "https://vapi.jinglingshuju.com/Data/getNewsList"
data = {
    "page": "2",
    "num": "20",
    "uid": "undefined"
}
response = requests.post(url, headers=headers, data=data)

# 解析响应JSON
response_json = response.json()

# 检查是否有加密数据
if response_json.get('code') == 0 and response_json.get('data'):
    encrypted_data = response_json['data']
    try:
        # 解密数据
        decrypted_data = decrypt_data(encrypted_data)
        print("解密后的数据：")
        print(json.dumps(decrypted_data, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"解密失败：{e}")
        print("原始响应：")
        print(response.text)
else:
    print("响应数据：")
    print(json.dumps(response_json, ensure_ascii=False, indent=2))