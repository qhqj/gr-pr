from flask import jsonify, request

from server.myUtil import handle_error_code, check_login, check_friendship, get_user_id, get_messages_query, \
    get_avatar_link, get_group_id, is_user_in_group, save_message


def get_info(data):
    username = data.get("username")
    session_id = data.get("session_id")
    target_type = data.get("target_type")
    target_name = data.get("target_name")
    print(username, session_id, target_type, target_name)
    return username, session_id, target_type, target_name


def get_messages(user_id, target_id, target_type):
    # 查询数据库以获取消息
    messages_query = get_messages_query(target_type, user_id, target_id)
    messages_list = []
    for message in messages_query:
        sender_avatar = get_avatar_link(message.sender.username)
        message_dict = {
            "message_id": message.message_id,
            "sender": message.sender.username,
            "avatar": sender_avatar,
            "content": message.content,
            "sent_at": message.sent_at.strftime("%Y-%m-%d %H:%M:%S"),
            "is_read": message.is_read,
            "content_type": message.content_type
        }

        messages_list.append(message_dict)
    print(messages_list)
    return messages_list


def get_messages_for_user(username, target_name):
    print('get_messages_for_user')
    # 查看是否有权限,即是否是好友关系
    user_id = get_user_id(username)
    target_id = get_user_id(target_name)
    friendship = check_friendship(user_id, target_id)
    print(friendship)
    if friendship != "accepted":
        print("friendship:", friendship)
        return handle_error_code(3001)

    messages_list = get_messages(user_id, target_id, 'user')

    return jsonify(messages_list), 200


def get_messages_for_group(user_id, target_name):
    # 查看是否有权限,即是否是群组成员
    print('get_messages_for_group')
    target_id = get_group_id(target_name)
    if not target_id:
        return handle_error_code(3002)
    if not is_user_in_group(user_id, target_id):
        print(22222)
        return handle_error_code(3001)

    messages_list = get_messages(user_id, target_id, 'group')

    return jsonify(messages_list), 200


def get_message_info():
    data = request.get_json()
    print(data)
    # 解析数据
    username, session_id, target_type, target_name = get_info(data)
    # 验证是否登录
    sender_user_id = check_login(username, session_id)
    if not sender_user_id:
        return handle_error_code(1003)
    # 验证是否有权限
    if target_type == 'user':
        return get_messages_for_user(username, target_name)
    elif target_type == 'group':
        return get_messages_for_group(sender_user_id, target_name)
    else:
        return handle_error_code(9998)


# 保存消息，包括文件、图片、文字等


def send_message_ms():
    data = request.get_json()
    print("send_message_ms")
    print(data)

    # 解析数据
    username = data.get("username")
    session_id = data.get("session_id")
    target_type = data.get("target_type")
    target_name = data.get("target_name")
    message = data.get("message")

    # 打印所有的数据
    print(username, session_id, target_type, target_name, message)

    # 验证是否登录
    sender_user_id = check_login(username, session_id)
    if not sender_user_id:
        return handle_error_code(1003)

    # 验证是否有权限
    if target_type == 'user':
        target_id = get_user_id(target_name)
        if not target_id:
            return handle_error_code(1006)
        friendship = check_friendship(sender_user_id, target_id)
        if friendship != 'accepted':
            print('friendship:', friendship)
            return handle_error_code(3001)
    elif target_type == 'group':
        target_id = get_group_id(target_name)
        print("target_id:", target_id)
        if not target_id:
            return handle_error_code(3002)

        if not is_user_in_group(sender_user_id, target_id):
            print(111)
            return handle_error_code(3001)
    else:
        return handle_error_code(9998)  # 考虑以后在错误码中加入的其他类型
    # 这里是通过验证的，可以直接保存消息

    is_read = target_type != 'user'

    if save_message(sender_user_id, target_id, target_type, message, "text", is_read):
        return jsonify({'message': 'Message sent successfully'}), 200
    return handle_error_code(8001)
