# 加密函数，明文和密钥为 Base64 编码，返回将 IV 和密文连接在一起并进行 Base64 编码的结果
import json
from base64 import b64decode, b64encode
from os import urandom

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


# 加密函数
def encrypt_aes_cbc(plaintext, base64_key):
    print('encrypt_aes_cbc is working')
    # 解码密钥
    key = b64decode(base64_key)

    iv = urandom(16)

    # 使用密钥和 IV 创建 AES-CBC 加密对象
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # 如果输入是列表，将其转换为 JSON 字符串
    if isinstance(plaintext, list):
        plaintext = json.dumps(plaintext)

    # 对明文进行填充
    pad_length = 16 - len(plaintext) % 16
    padded_plaintext = plaintext + chr(pad_length) * pad_length

    # 加密
    ciphertext = encryptor.update(padded_plaintext.encode()) + encryptor.finalize()

    # 将 IV 和密文连接在一起并进行 Base64 编码
    iv_and_ciphertext = iv + ciphertext
    base64_iv_and_ciphertext = b64encode(iv_and_ciphertext).decode('utf-8')

    return base64_iv_and_ciphertext


# 解密函数, 密文和密钥为 Base64 编码，返回解密后的明文
def decrypt_aes_cbc(ciphertext, base64_key):
    print("密文", ciphertext)
    print("密钥", base64_key)

    # 解码密钥
    key = b64decode(base64_key)
    print("解码后的密钥：", key)

    # Base64 解码密文
    iv_and_ciphertext = b64decode(ciphertext)
    print("解码后的密文：", iv_and_ciphertext)

    # 提取 IV 和密文
    iv = iv_and_ciphertext[:16]
    ciphertext = iv_and_ciphertext[16:]

    # 使用密钥和 IV 创建 AES-CBC 解密对象
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # 解密
    decrypted_padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # 去除填充
    pad_length = decrypted_padded_plaintext[-1]
    decrypted_plaintext = decrypted_padded_plaintext[:-pad_length]
    print("解密后的明文：", decrypted_plaintext)

    return decrypted_plaintext.decode('utf-8')
