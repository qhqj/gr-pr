import hashlib
import time
from datetime import datetime

from flask import request, jsonify
from flask import session

from server.models import User, InvitationCode, db
from server.myUtil import handle_error_code, get_user_by_id, check_login, get_user_id_or_phone


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

    # 检查手机号是否已被注册
    if User.query.filter_by(phone=phone).first():
        return handle_error_code(2001)

    # 检查用户名是否已被使用
    if User.query.filter_by(username=username).first():
        return handle_error_code(2002)

    # 检查邀请码是否存在且未被使用
    invitation_code = InvitationCode.query.filter_by(code=invite_code, is_available=True).first()
    if not invitation_code:
        return handle_error_code(2003)

    # 创建新用户
    new_user = User(username=username, phone=phone, password_hash=string_to_sha256(password), created_at=datetime.now())

    # 更新邀请码状态
    invitation_code.is_available = False
    invitation_code.used_at = datetime.now()
    print("邀请码状态更新成功")

    # 将新用户添加到数据库中
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '用户注册成功'}), 200


def login(data):
    username_or_phone = data.get('username_or_phone')
    password = data.get('password')

    print(f"Received data: {username_or_phone}, {password}")

    # 检查用户名和密码是否存在
    if not (username_or_phone and password):
        return handle_error_code(1001)
    print(data)
    print(username_or_phone)

    # 检查用户名或电话号码是否存在
    user_id = get_user_id_or_phone(username_or_phone)
    print(user_id)
    if not user_id:
        print(2004)
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
    print("user_id:", user_id, 'session_id', session_id)

    # 返回给客户端
    return jsonify(
        {'message': 'Login successful', 'session_id': session_id, 'username': username}), 200


def string_to_sha256(password):
    password = password.encode('utf-8')
    sha256 = hashlib.sha256()
    sha256.update(password)
    return sha256.hexdigest()
