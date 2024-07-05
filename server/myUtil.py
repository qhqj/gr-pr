import hashlib
import os
from datetime import datetime

from flask import jsonify
from flask import session
from sqlalchemy import or_, asc

from models import User, Group, GroupUser, FriendRequest, Message, db, File, InvitationCode



def handle_error_code(error_code):
    error_messages = {
        1001: '提交的表单数据不完整，请确保填写所有必填项后再次提交。',
        1002: '密码与确认密码不匹配，请重新确认密码。',
        1003: '登录状态已过期，请重新登录。',
        1004: '权限不足。',
        2001: '该手机号已被注册。',
        2002: '该用户名已被使用，请尝试其他用户名。',
        2003: '邀请码无效，请确认后重新输入。',
        2004: '用户不存在，请检查用户名或手机号。',
        2005: '密码错误，请确认密码后重新登录。',
        2006: '不能将自己添加为好友。',
        2007: '对方已经是您的好友。',
        2008: '好友请求不存在。',
        2009: '无效操作，可能涉及好友关系，请确认后重试。',
        2010: '已存在好友请求。',
        2011: '群名已存在。',
        3001: '聊天对象不存在或没有权限进行操作。',
        3002: '接收者名称错误，请检查后重试。',
        3003: '发送者和接收者不能是同一个人。',
        3004: '会话或用户不存在或已被删除。',
        3005: '不能和自己聊天。',
        4001: '没有选择文件，请选择文件后重新上传。',
        4002: '接收者不存在或没有权限发送文件给目标用户。',
        8001: '写入数据库出现错误',
        9998: '找不到对象。',
        9999: '未知错误'
    }

    error_message = error_messages.get(error_code)
    print(f"Error code: {error_code}, message: {error_message}")
    return jsonify({'error': error_message, 'error_code': error_code}), 400


# 更新会话时间
def update_session_expiry():
    session.modified = True


def register_ms(username, password, phone, invite_code):
    # 检查手机号是否已被注册
    if User.query.filter_by(phone=phone).first():
        return 2001

    # 检查用户名是否已被使用
    if User.query.filter_by(username=username).first():
        return 2002

    # 检查邀请码是否存在且未被使用
    invitation_code = InvitationCode.query.filter_by(code=invite_code, is_available=True).first()
    if not invitation_code:
        return 2003

    # 创建新用户
    new_user = User(username=username, phone=phone, password_hash=string_to_sha256(password), created_at=datetime.now())

    # 更新邀请码状态
    invitation_code.is_available = False
    invitation_code.used_at = datetime.now()
    print("邀请码状态更新成功")

    # 将新用户添加到数据库中
    db.session.add(new_user)
    db.session.commit()
    return 0
def string_to_sha256(password):
    password = password.encode('utf-8')
    sha256 = hashlib.sha256()
    sha256.update(password)
    return sha256.hexdigest()

# 检查用户是否登录，是则返回用户 ID，否则返回 False
def check_login(username, session_id):
    user = User.query.filter_by(username=username).first()
    if not user:
        return False
    if session.get('user_id') == user.user_id and session.get('session_id') == session_id:
        update_session_expiry()
        print(f"User {username} is logged in")
        return user.user_id
    return False


# 检查用户是否存在，是则返回用户 ID，否则返回 False
def get_user_id(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return user.user_id
    return False


def get_user_name(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if user:
        return user.username
    return False


# 检查手机号是否存在，是则返回用户 ID，否则返回 False
def check_phone(phone):
    user = User.query.filter_by(phone=phone).first()
    if user:
        return user.user_id
    return False


def get_user_id_or_phone(username_or_phone):
    user = User.query.filter((User.username == username_or_phone) | (User.phone == username_or_phone)).first()
    if user:
        return user.user_id
    return False


# 根据用户 ID 获取用户对象
def get_user_by_id(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    return user


# 检查是否为群组成员
def check_group_user(groupname, username):
    group = Group.query.filter_by(name=groupname).first()
    user = User.query.filter_by(username=username).first()
    if group and user:
        group_user = GroupUser.query.filter_by(group_id=group.group_id, user_id=user.user_id).first()
        if group_user:
            return True
    return False


# 模糊搜索用户
def search_user_all(search_input):
    search_users = User.query.filter(
        or_(User.username.like(f'%{search_input}%'), User.phone.like(f'%{search_input}%'))).all()
    return search_users


# 搜索所有有关系的好友
def search_related_friends(user_id):
    search_friends = FriendRequest.query.filter(
        or_((FriendRequest.requester_id == user_id), (FriendRequest.accepter_id == user_id))).all()
    return search_friends


# 检查好友关系是否存在
def check_friendship(user_id, friend_id):
    friend_request = FriendRequest.query.filter(
        or_(
            (FriendRequest.requester_id == user_id) & (FriendRequest.accepter_id == friend_id),
            (FriendRequest.accepter_id == user_id) & (FriendRequest.requester_id == friend_id)
        )
    ).first()
    if friend_request:
        return friend_request.status
    return False


# 构造一个方法，传入两个user_id，在好友关系表中创建一个记录：
def add_friend_request(requester_id, accepter_id):
    status = 'pending'
    new_friend_request = FriendRequest(
        requester_id=requester_id,
        accepter_id=accepter_id,
        status=status,
        created_at=datetime.now()
    )
    db.session.add(new_friend_request)
    db.session.commit()
    return True


def change_friend_request(accepter_id, requester_id, action):
    friend_request = FriendRequest.query.filter(
        (FriendRequest.requester_id == requester_id) & (FriendRequest.accepter_id == accepter_id)).first()

    if action == 'delete':
        db.session.delete(friend_request)  # 删除好友请求记录
        db.session.commit()  # 提交数据库更改

    friend_request.status = action
    friend_request.updated_at = datetime.now()
    db.session.commit()  # 提交数据库更改
    return True


# 查询自己创建的所有的群组
def search_group_create_all(creator_id):
    search_group = Group.query.filter(Group.creator_id == creator_id).all()
    return search_group


# 查询自己加入的所有的群组
def search_group_join_all(user_id):
    search_group = GroupUser.query.filter(GroupUser.user_id == user_id).all()
    return search_group


# 查询组中的用户人数
def get_group_user_count(group_id):
    count = GroupUser.query.filter(GroupUser.group_id == group_id).count()
    return count


# 查询群组id
def get_group_id(groupname):
    group = Group.query.filter_by(name=groupname).first()
    if group:
        return group.group_id
    return False


# 查询群组名
def get_group_name(group_id):
    group = Group.query.filter_by(group_id=group_id).first()
    if group:
        return group.name
    return False


# 查询群组成员列表
def search_member_all(group_id):
    search_member = GroupUser.query.filter(GroupUser.group_id == group_id).all()
    return search_member


# 判断用户是否在群组中
def is_user_in_group(user_id, group_id):
    print(user_id)
    print(group_id)
    group_user = GroupUser.query.filter_by(user_id=user_id, group_id=group_id).first()
    if group_user:
        print("用户在群组中")
        return True
    print("用户不在群组中")
    return False


# 从群组中删除用户
def delete_user_from_group(user_id, group_id):
    group_user = GroupUser.query.filter_by(user_id=user_id, group_id=group_id).first()
    db.session.delete(group_user)
    db.session.commit()
    return True


# 添加用户到群组
def add_user_to_group(user_id, group_id):
    new_group_user = GroupUser(
        user_id=user_id,
        group_id=group_id,
    )
    db.session.add(new_group_user)
    db.session.commit()
    return True


# 查询是否是群组创建者
def check_group_creator(group_id, user_id):
    print(group_id)
    group = Group.query.filter_by(group_id=group_id).first()
    if not group:
        print("没有群组")
        return False
    if group.creator_id == user_id:
        print("是群组创建者")
        return True
    return False


def check_groupname_just_name(group_name):
    group = Group.query.filter_by(name=group_name).first()
    return group


# 查询群名是否可用
def check_groupname(groupname, group_id):
    group = Group.query.filter_by(name=groupname).first()
    if group:
        return group.group_id == group_id
    return False


# 更新群组信息
def update_group_info_ms(group_id, groupname, description):
    group = Group.query.filter_by(group_id=group_id).first()
    group.name = groupname
    group.description = description
    db.session.commit()
    return True


# 查询用户间的聊天记录
def get_messages_query(target_type, sender_user_id, target_id):
    if target_type == 'user':
        messages_query = Message.query.filter(
            Message.target_type == target_type,
            or_(
                (Message.sender_id == sender_user_id) & (Message.target_id == target_id),
                (Message.sender_id == target_id) & (Message.target_id == sender_user_id)
            )
        ).order_by(asc(Message.sent_at)).all()
    else:
        messages_query = Message.query.filter_by(target_id=target_id, target_type=target_type).order_by(
            asc(Message.sent_at)).all()

    return messages_query


def get_avatar_link(username):
    # 检查用户是否有头像，如果有则返回头像链接，否则返回默认头像链接
    path = os.path.join('server/static/images/avatar', username + '.jpg')
    if os.path.exists(path):
        return '../../static/images/avatar/' + username + '.jpg'
    else:
        return '../../static/images/avatar/default.jpg'


def save_message(sender_user_id, target_id, target_type, content, content_type, is_read):
    # 将消息保存到数据库
    new_message = Message(
        sender_id=sender_user_id,
        target_id=target_id,
        target_type=target_type,
        content=content,
        content_type=content_type,
        sent_at=datetime.now(),
        is_read=is_read
    )
    db.session.add(new_message)
    db.session.commit()
    return True


# 将文件信息保存到数据库
def save_file_db(filename, file_path, user_id):
    new_file = File(
        filename=filename,
        file_path=file_path,
        uploaded_at=datetime.now(),
        user_id=user_id
    )
    db.session.add(new_file)
    db.session.commit()
    print("save_file_db")

    print('file_id:')
    print(new_file.file_id)

    return new_file.file_id


def check_file_existence(file_id):
    print(file_id)
    file = File.query.filter_by(file_id=file_id).first()
    if file:
        return True
    return False


def get_file_by_id(file_id):
    file = File.query.get(file_id)
    return file


def create_group(groupname, description, is_department, creator_id):
    new_group = Group(
        name=groupname,
        description=description,
        is_department=is_department,
        creator_id=creator_id
    )
    db.session.add(new_group)
    db.session.commit()
    return True
