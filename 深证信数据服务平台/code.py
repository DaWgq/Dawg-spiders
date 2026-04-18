import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
import time


def get_res_code():
    """生成Accept-EncKey的值,与JS代码逻辑一致"""
    key = b"1234567887654321"
    iv = b"1234567887654321"
    
    # 获取当前时间戳(秒)
    timestamp = str(int(time.time()))
    
    # AES-CBC加密
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(timestamp.encode('utf-8'), AES.block_size))
    
    # Base64编码
    return base64.b64encode(encrypted).decode('utf-8')


headers = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://webapi.cninfo.com.cn",
    "Referer": "https://webapi.cninfo.com.cn/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}

# 动态生成Accept-EncKey
enc_key = get_res_code()
headers["Accept-EncKey"] = enc_key
print(f"生成的Accept-EncKey: {enc_key}")

cookies = {
    "Hm_lvt_489bd07e99fbfc5f12cbb4145adb0a9b": "1776493709",
    "HMACCOUNT": "45FC6488ADA4CC26",
    "MALLSSID": "3067362F3063514C58562B54634D7950797A4154675561664D3552485642722F66356772656F30464B2F55487774586336565770314D522B49345658414C4454",
    "Hm_lpvt_489bd07e99fbfc5f12cbb4145adb0a9b": "1776501628"
}
url = "https://webapi.cninfo.com.cn/api/sysapi/p_sysapi1007"
data = {
    "tdate": "2026-04-14",
    "market": "SZE"
}
response = requests.post(url, headers=headers, cookies=cookies, data=data)

print(response.text)
print(response)