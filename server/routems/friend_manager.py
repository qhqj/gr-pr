from flask import jsonify
from flask import request

from server.myUtil import check_login, get_user_by_id, search_user_all, check_friendship, handle_error_code, \
    add_friend_request, search_related_friends, get_user_name, get_user_id, change_friend_request


def friend_manager(method_name):
    data = request.json
    if method_name == 'search_friend':
        return search_friend(data)
    if method_name == 'send_friend_request':
        return send_friend_request(data)
    if method_name == 'search_friend_request':
        return search_friend_request(data)
    if method_name == 'change_friend':
        return change_friend(data)
    return handle_error_code(9999)


# 检测请求数据是否合理：
def check_requested_for_friend(username, session_id, search_input):
    if not (username and session_id and search_input):
        return False, 1001

    user_id = check_login(username, session_id)
    if not user_id:
        return False, 1003

    if username == search_input or get_user_by_id(user_id).phone == search_input:
        return False, 2006

    return True, user_id


def search_friend(data):
    # 解析请求数据
    username = data.get('username')
    session_id = data.get('session_id')
    search_input = data.get('search_input')

    is_success, code = check_requested_for_friend(username, session_id, search_input)
    if not is_success:
        return handle_error_code(code)
    user_id = code

    search_users = search_user_all(search_input)

    search_results = []
    for search_user in search_users:
        if search_user.user_id != user_id:
            status = check_friendship(user_id, search_user.user_id)
            search_results.append({
                'username': search_user.username,
                'status': status
            })
    return jsonify(search_results), 200


#
# # 发送好友请求
def send_friend_request(data):
    print(data)

    sender_name = data.get('sender_name')
    session_id = data.get('session_id')
    receiver_name = data.get('receiver_name')
    print(sender_name, session_id, receiver_name)
    is_success, code = check_requested_for_friend(sender_name, session_id, receiver_name)
    if not is_success:
        return handle_error_code(code)
    user_id = code
    print(user_id)
    # 检测好友是否存在
    receiver_id = get_user_id(receiver_name)
    if not receiver_id:
        return handle_error_code(2004)

    # 检测是否已经有好友关系
    is_friend = check_friendship(user_id, receiver_id)
    if is_friend:
        return handle_error_code(2010)

    # 发送好友请求，即写入数据库
    add_friend_request(user_id, receiver_id)

    # 返回成功信息
    return jsonify({'message': '添加成功'}), 200


def search_friend_request(data):
    print(data)
    username = data.get('username')
    session_id = data.get('session_id')
    method = data.get('method')
    # 检查是否登录
    user_id = check_login(username, session_id)
    if not user_id:
        return False, 1003
    # 搜所所有有关系的好友
    all_friends_request = search_related_friends(user_id)
    search_friends = []
    for friend_request in all_friends_request:
        is_accepter = friend_request.accepter_id == user_id
        other_name = get_user_name(friend_request.requester_id if is_accepter else friend_request.accepter_id)
        search_friends.append({
            'username': other_name,
            'is_accepter': is_accepter,
            'status': friend_request.status
        })
    return jsonify(search_friends), 200


def change_friend(data):
    print(data)
    username = data.get('username')
    session_id = data.get('session_id')
    friend_name = data.get('friend_name')
    action = data.get('action')
    is_success, code = check_requested_for_friend(username, session_id, friend_name)
    if not is_success:
        return handle_error_code(code)
    user_id = code
    friend_id = get_user_id(friend_name)

    if not change_friend_request(user_id, friend_id, action):
        return handle_error_code(2008)

    return jsonify({'message': '操作成功'}), 200

#   """已废弃"""
#     # 检查用户是否登录
#     user_id = check_session_validity(sender_name, session_id)
#     if not user_id:
#         return jsonify({'error': 'Invalid session or user', 'error_code': 1}), 400  # 登录失效
#     # 检查是否为同一人
#     if sender_name == receiver_name:
#         return jsonify({'error': 'Cannot add self as friend', 'error_code': 2}), 400  # 不能添加自己为好友
#     # 检查好友是否存在
#     receiver = User.query.filter_by(username=receiver_name).first()
#     if not receiver:
#         return jsonify({'error': 'User not found', 'error_code': 3}), 400  # 用户不存在
#
#     receiver_user_id = receiver.user_id
#     # 检查是否已在好友列表中
#     friend_request = FriendRequest.query.filter(
#         or_(
#             (FriendRequest.requester_id == user_id) & (FriendRequest.accepter_id == receiver_user_id),
#             (FriendRequest.accepter_id == user_id) & (FriendRequest.requester_id == receiver_user_id)
#         )
#     ).first()
#     if friend_request:
#         return jsonify({'error': 'Already friends', 'error_code': 4}), 400  # 已经是好友
#
#     # 创建好友请求
#     # 将请求写入数据库
#     new_request = FriendRequest(
#         requester_id=user_id,
#         accepter_id=receiver.user_id,
#         created_at=datetime.now()
#     )
#
#     db.session.add(new_request)
#     db.session.commit()
#     # 错误码：1表示会话无效，2表示不能添加自己为好友，3表示用户不存在，4表示已经是好友
#     return jsonify({'message': 'success', 'code': 0}), 200
#
#
# # 添加好友
# def add_friend(data):
#     data = request.json
#     print(data)  # 打印请求数据
#     # json格式示例
#     # {
#     #   "sender_name": "", # 发送者用户名
#     #   "session_id": "", # 会话ID
#     #   "receiver_name": "", # 接收者用户名
#     #   "action": "" # 操作，取值为"accept"、"decline"或"detect"
#     # }
#     # 解析请求数据
#
#     sender_name = data.get('sender_name')
#     session_id = data.get('session_id')
#     receiver_name = data.get('receiver_name')
#     action = data.get('action')
#
#     # 检查用户是否登录
#     user_id = check_session_validity(sender_name, session_id)
#     if not user_id:
#         return jsonify({'error': 'Invalid session or user', 'error_code': 1}), 400  # 会话无效
#     # 检查好友请求是否存在,这里处理pending的user_id应该是接受者的id，即accepter_id
#     friend_request = FriendRequest.query.filter_by(accepter_id=user_id).first()
#     if not friend_request:
#         # 这里进一步细分，处理非pending的情况，即user_id是requester_id，且status是accepted。
#         friend_request = FriendRequest.query.filter_by(requester_id=user_id, status='accepted').first()
#         if not friend_request:
#             return jsonify({'error': 'Friend request not found', 'error_code': 2}), 400
#
#     # 检查是否为同一人
#     if sender_name == receiver_name:
#         return jsonify({'error': 'Cannot add self as friend', 'error_code': 3}), 400  # 不能添加自己为好友
#
#     # 处理好友请求
#     print(action)
#     if action == 'accept':
#         print('action is accept')
#         friend_request.status = 'accepted'
#         friend_request.updated_at = datetime.now()
#     elif action == 'decline':
#         friend_request.status = 'declined'
#         friend_request.updated_at = datetime.now()
#     elif action == 'delete':
#         print('action is detect')
#         # 删除好友请求
#         db.session.delete(friend_request)
#     else:
#         return jsonify({'error': 'Invalid action', 'error_code': 4}), 400  # 无效操作
#
#     db.session.commit()
#
#     # 错误码：1表示会话无效，2表示好友请求不存在，3表示不能添加自己为好友，4表示无效操作
#     return jsonify({'message': 'success', 'code': 0}), 200  # 成功
#
#
# # 列出好友请求
# def list_friend_request(data):
#     # 解析请求数据
#     username = data.get('sender_name')
#     session_id = data.get('session_id')
#     # 检查用户是否登录
#     user_id = check_session_validity(username, session_id)
#     if not user_id:
#         return jsonify({'error': 'Invalid session or user', 'error_code': 1}), 400  # 会话无效
#
#     # 查询所有好友请求，写入数组
#     request_query = get_request_query(user_id)
#     request_list = []
#
#     for request_item in request_query:
#         if request_item.requester_id == user_id:  # 如果请求者是当前用户
#             is_request_user = True
#             other_user_id = request_item.accepter_id
#         else:
#             is_request_user = False
#             other_user_id = request_item.requester_id
#
#         other_user = User.query.get(other_user_id)
#
#         request_dict = {
#             "other_username": other_user.username,
#             "other_phone": other_user.phone,
#             "is_request_user": is_request_user,
#             "status": request_item.status,
#             "created_at": request_item.created_at.strftime("%Y-%m-%d %H:%M:%S")
#         }
#
#         request_list.append(request_dict)
#
#     return jsonify(request_list), 200
#
#
# def get_request_query(user_id):
#     request_query = FriendRequest.query.filter(
#         or_(FriendRequest.requester_id == user_id, FriendRequest.accepter_id == user_id)
#     )
#
#     return request_query
#
#
# # 创建一个方法，输入两个用户名，返回是否为好友关系
# def is_friend(username1, username2):
#     print('is_friend:开始检查是否为好友')
#     print(username1, username2)
#     if not username1 or not username2:
#         print('is_friend:用户不存在')
#         return False  # 用户不存在
#
#     if username1 == username2:
#         print('is_friend:自己不是自己的好友')
#         return False  # 自己不是自己的好友
#
#     user1 = User.query.filter_by(username=username1).first()
#     user2 = User.query.filter_by(username=username2).first()
#
#     if not user1 or not user2:
#         print('is_friend：用户不存在')
#         return False
#
#     friend_request = FriendRequest.query.filter(
#         or_(
#             (FriendRequest.requester_id == user1.user_id) & (FriendRequest.accepter_id == user2.user_id),
#             (FriendRequest.accepter_id == user1.user_id) & (FriendRequest.requester_id == user2.user_id)
#         )
#     ).first()
#
#     if friend_request and friend_request.status == 'accepted':
#         print('is_friend：是好友')
#         return True
#     else:
#         print('is_friend:不是好友')
#         return False
