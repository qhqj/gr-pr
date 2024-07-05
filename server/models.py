# models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# 用户表模型类
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)


# 消息表模型类
class Message(db.Model):
    __tablename__ = 'messages'
    message_id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    target_id = db.Column(db.Integer)
    target_type = db.Column(db.String(255))
    content = db.Column(db.Text)
    content_type = db.Column(db.String(255))
    thumbnail = db.Column(db.String(255))
    sent_at = db.Column(db.DateTime)
    is_read = db.Column(db.Boolean)
    sender = db.relationship('User', foreign_keys=[sender_id])


# 文件表模型类
class File(db.Model):
    __tablename__ = 'files'
    file_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False)
    user = db.relationship('User', foreign_keys=[user_id])


# 群组表模型类
class Group(db.Model):
    __tablename__ = 'u_groups'
    group_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    is_department = db.Column(db.Boolean)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    creator = db.relationship('User', backref=db.backref('created_groups', lazy=True))


# 群组用户表模型类
class GroupUser(db.Model):
    __tablename__ = 'group_users'
    group_id = db.Column(db.Integer, db.ForeignKey('u_groups.group_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)


# 通知表模型类#废弃
# class Notification(db.Model):
#     __tablename__ = 'notifications'
#     notification_id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
#     group_id = db.Column(db.Integer, db.ForeignKey('u_groups.group_id'))
#     message = db.Column(db.Text)
#     user = db.relationship('User', foreign_keys=[user_id])
#     group = db.relationship('Group', foreign_keys=[group_id])


# 邀请码表模型类
class InvitationCode(db.Model):
    __tablename__ = 'Invitation_code'
    Invitation_code_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(16), nullable=False)
    is_available = db.Column(db.Boolean, nullable=False)
    used_at = db.Column(db.DateTime)


# 好友请求模型类
class FriendRequest(db.Model):
    __tablename__ = 'friend_requests'
    request_id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    accepter_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    status = db.Column(db.Enum('pending', 'accepted', 'declined', 'blocked'), nullable=False, default='pending')
    #                           “待定”、   “接受”、    “拒绝”、   “阻止”
