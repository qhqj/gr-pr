import os
import os
import time
from base64 import b64encode

from flask import request, jsonify
from flask import session

from server.config import keys, Check_password  # 导入全局字典
from server.myUtil import handle_error_code, get_user_by_id, check_login, get_user_id_or_phone, register_ms, \
    string_to_sha256


def generate_key():
    key = os.urandom(32)
    return b64encode(key).decode('utf-8')


def register_login(method_name):
    data = request.json

    if method_name == 'login':
        return login(data)
    elif method_name == 'register':
        return register(data)
    elif method_name == 'check_login':
        return check_login_status(data)
    else:
        return handle_error_code(9999)


def check_login_status(data):
    session_id = data.get('session_id')
    username = data.get('username')
    if not (session_id and username):
        return handle_error_code(1003)
    user_id = check_login(username, session_id)
    if not user_id:
        return handle_error_code(1003)
    return jsonify({'message': '已经登录'}), 200


def register(data):
    # 解析 JSON 数据
    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    phone = data.get('phone')
    invite_code = data.get('invite_code')
    print(f"Received data: {username}, {password}, {confirm_password}, {phone}, {invite_code}")

    # 检查 JSON 数据是否符合规则
    if not (username and password and confirm_password and phone and invite_code):
        return handle_error_code(1001)

    # 检查密码和确认密码是否匹配
    if password != confirm_password:
        return handle_error_code(1002)

    code = register_ms(username, password, phone, invite_code)
    if code == 0:
        return jsonify({'message': '用户注册成功'}), 200
    else:
        return handle_error_code(code)

    # return jsonify({'message': '用户注册成功'}), 200
    # return handle_error_code(9999)
    #
    # # 检查手机号是否已被注册
    # if User.query.filter_by(phone=phone).first():
    #     return handle_error_code(2001)
    #
    # # 检查用户名是否已被使用
    # if User.query.filter_by(username=username).first():
    #     return handle_error_code(2002)
    #
    # # 检查邀请码是否存在且未被使用
    # invitation_code = InvitationCode.query.filter_by(code=invite_code, is_available=True).first()
    # if not invitation_code:
    #     return handle_error_code(2003)
    #
    # # 创建新用户
    # new_user = User(username=username, phone=phone, password_hash=string_to_sha256(password), created_at=datetime.now())
    #
    # # 更新邀请码状态
    # invitation_code.is_available = False
    # invitation_code.used_at = datetime.now()
    # print("邀请码状态更新成功")
    #
    # # 将新用户添加到数据库中
    # db.session.add(new_user)
    # db.session.commit()


def login(data):  # 登录的具体逻辑
    username_or_phone = data.get('username_or_phone')
    password = data.get('password')
    key_client = data.get('key')

    # 检查用户名和密码是否存在
    if not (username_or_phone and password):
        return handle_error_code(1001)

    # 检查用户名或电话号码是否存在
    user_id = get_user_id_or_phone(username_or_phone)

    if not user_id:
        return handle_error_code(2004)

    user = get_user_by_id(user_id)
    password_hash = string_to_sha256(password)
    # 检查密码是否匹配
    if user.password_hash != password_hash:
        return handle_error_code(2005)

    username = user.username
    # 记录登录信息
    timestamp = str(int(time.time()))
    session_id = string_to_sha256(f"{user_id}{timestamp}")
    session['user_id'] = user_id
    session['session_id'] = session_id

    if key_client != Check_password:
        # 错误则不返回密钥, 聊天逻辑切换为不进行加密的默认模式
        print("无key")
        return jsonify(
            {'message': 'Login successful', 'session_id': session_id, 'username': username}), 200
    else:
        # 生成并存储密钥
        key = generate_key()
        keys[session_id] = key

        # 返回给客户端
        print("有key")
        return jsonify(
            {'message': 'Login successful', 'session_id': session_id, 'username': username, 'key': key}), 200
