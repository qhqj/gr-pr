import base64

from Crypto.Cipher import AES  # pip install pycryptodome
from Crypto.Random import get_random_bytes
from flask import jsonify
from flask import request

from server.config import Config


def encrypt_aes(data, key):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return base64.b64encode(nonce + tag + ciphertext).decode('utf-8')


def negotiate_key_ms():
    data = request.get_json()
    key = data.get("key")
    if not key:
        return jsonify({"error": "No key provided"}), 400
    # 这里进行和本地存储的校验码进行比较
    if key != Config.Check_password:
        return jsonify({"error": "Wrong password"}), 400

    # 这里开始生成对话用密钥
    key_new = get_random_bytes(32)  # 256位密钥
    key = encrypt_aes(key, key_new)

    # 这里还要把密钥存起来

    return jsonify({"key": key})
