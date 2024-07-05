# 测试解密

from flask import jsonify, request

from server.routems.my_aes import encrypt_aes_cbc, decrypt_aes_cbc


def test_encrypt_ms():
    # data =
    data = request.json
    print(data)
    # 解析请求数据
    # plaintext = data['plaintext']
    plaintext = data.get('plaintext')  # 明文
    key_base64 = data.get('key')  # 密钥
    output = data.get('output')  # 密文
    # 打印一下
    print("plaintext：", plaintext, "key_base64：", key_base64, "output：", output)
    # 现在尝试进行解密
    ciphertext = decrypt_aes_cbc(output, key_base64)
    print("客户端的：", plaintext)
    print("服务器的：", ciphertext)
    # return jsonify({'message': '操作成功'}), 200
    # 尝试进行加密，让前端解密

    ciphertext1 = ciphertext + '123123123'
    ciphertext2 = encrypt_aes_cbc(ciphertext1, key_base64)
    return jsonify({'message': ciphertext2})
