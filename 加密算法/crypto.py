"""爬虫 JS 逆向常见密码学算法示例（仅用于合法授权的调试与学习）。
安装依赖：python -m pip install -r crypto_requirements.txt
运行：python crypto_reverse_examples.py
注意：哈希/HMAC不可逆；Base64等编码不是加密；DES/3DES/MD5/SHA1不适合新安全系统。
"""
import base64
import hashlib
import hmac
import secrets
from urllib.parse import quote, unquote

from Crypto.Cipher import AES, DES, DES3, PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA, ECC
from Crypto.Signature import DSS
from Crypto.Util.Padding import pad, unpad
from gmssl import sm2, sm4

TEXT = 'Hello 爬虫逆向'
DATA = TEXT.encode('utf-8')  # 密码学库通常接受 bytes；字符串先转 UTF-8


def show(title, result):
    print(f'\n[{title}]')
    for key, value in result.items():
        print(f'{key}: {value}')


# 1. 哈希摘要：只有计算摘要，没有“解密”操作

def hashes():
    return {
        'MD5': hashlib.md5(DATA).hexdigest(),  # 32个十六进制字符；不建议用于安全签名
        'SHA-1': hashlib.sha1(DATA).hexdigest(),  # 40个十六进制字符；不建议用于新安全系统
        'SHA-256': hashlib.sha256(DATA).hexdigest(),  # 64个十六进制字符
        'SHA-512': hashlib.sha512(DATA).hexdigest(),  # 128个十六进制字符
    }


# 2. 对称加密：相同密钥加密/解密；示例使用随机IV，并打印Base64方便比对前端

def aes_example():
    key = secrets.token_bytes(16)  # 16字节=AES-128，也可24/32字节
    iv = secrets.token_bytes(16)  # CBC模式IV必须16字节
    ciphertext = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(DATA, AES.block_size))
    plaintext = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ciphertext), AES.block_size)
    return {'模式': 'AES-CBC + PKCS7填充', 'key_hex': key.hex(), 'iv_hex': iv.hex(),
            '密文_base64': base64.b64encode(ciphertext).decode(), '解密': plaintext.decode()}


def des_example():
    key = secrets.token_bytes(8)  # DES密钥8字节（实际有效密钥仅56位）
    iv = secrets.token_bytes(8)  # DES的分组/IV大小是8字节
    ciphertext = DES.new(key, DES.MODE_CBC, iv).encrypt(pad(DATA, DES.block_size))
    plaintext = unpad(DES.new(key, DES.MODE_CBC, iv).decrypt(ciphertext), DES.block_size)
    return {'模式': 'DES-CBC（仅兼容旧系统）', 'key_hex': key.hex(), 'iv_hex': iv.hex(),
            '密文_base64': base64.b64encode(ciphertext).decode(), '解密': plaintext.decode()}


def triple_des_example():
    # 3DES使用24字节的三密钥形式；adjust_key_parity设置DES奇偶校验位
    key = DES3.adjust_key_parity(secrets.token_bytes(24))
    iv = secrets.token_bytes(8)
    ciphertext = DES3.new(key, DES3.MODE_CBC, iv).encrypt(pad(DATA, DES3.block_size))
    plaintext = unpad(DES3.new(key, DES3.MODE_CBC, iv).decrypt(ciphertext), DES3.block_size)
    return {'模式': '3DES-CBC（仅兼容旧系统）', 'key_hex': key.hex(), 'iv_hex': iv.hex(),
            '密文_base64': base64.b64encode(ciphertext).decode(), '解密': plaintext.decode()}


def sm4_example():
    key = secrets.token_bytes(16)  # SM4密钥固定16字节
    iv = secrets.token_bytes(16)  # CBC的IV固定16字节
    en = sm4.CryptSM4()
    en.set_key(key, sm4.SM4_ENCRYPT)
    ciphertext = en.crypt_cbc(iv, DATA)  # gmssl会做PKCS7填充
    de = sm4.CryptSM4()
    de.set_key(key, sm4.SM4_DECRYPT)
    plaintext = de.crypt_cbc(iv, ciphertext)  # gmssl会移除填充
    return {'模式': 'SM4-CBC', 'key_hex': key.hex(), 'iv_hex': iv.hex(),
            '密文_base64': base64.b64encode(ciphertext).decode(), '解密': plaintext.decode()}


# 3. 非对称密码：RSA/SM2展示公钥加密+私钥解密；ECC展示签名验签

def rsa_example():
    private_key = RSA.generate(2048)  # 生成2048位RSA密钥对
    public_key = private_key.publickey()
    ciphertext = PKCS1_OAEP.new(public_key, hashAlgo=SHA256).encrypt(DATA)  # OAEP-SHA256
    plaintext = PKCS1_OAEP.new(private_key, hashAlgo=SHA256).decrypt(ciphertext)
    return {'方案': 'RSA-OAEP-SHA256', '密文_base64': base64.b64encode(ciphertext).decode(),
            '解密': plaintext.decode(), '公钥PEM预览': public_key.export_key().decode()[:75] + '...'}

