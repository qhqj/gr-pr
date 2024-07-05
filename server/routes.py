from flask import Blueprint
from flask import redirect, url_for
from flask import render_template
from sqlalchemy.event import api  # pip install SQLAlchemy

from routems.register_login import register_login
from server.myUtil import check_file_existence
from server.routems.friend_manager import friend_manager
from server.routems.get_user_and_group_list import get_left_list
from server.routems.group_manager import get_list, update_info, search_users_group, check_group_name_ms, \
    creat_a_group_ms
from server.routems.message_manager import get_message_info, send_message_ms
from server.routems.my_test import test_encrypt_ms
from server.routems.negotiate_key import negotiate_key_ms
from server.routems.recognize import recognize_ms_1
from server.routems.update_download import file_update_ms, file_download_ms, upload_avatar_ms

api = Blueprint('api', __name__)


class LiveStatus:
    is_live = False  # 初始化直播状态为False（没有直播）


def init_api(socketio):
    live_status = LiveStatus()

    @socketio.on('live_data', namespace='/start_live')
    def handle_live(data):
        socketio.emit('live_data', data, namespace='/start_live')

    @socketio.on('is_live', namespace='/start_live')
    def handle_is_live(method):
        print(method)
        if method == 'start':
            if live_status.is_live:
                # 直接回应给请求的客户端
                return False  # 因为有正在进行的直播，所以返回假，即失败
            else:
                live_status.is_live = True  # 标记为直播中
                return True
        elif method == 'end':
            # 如果方法是end，没有正在进行的直播，则返回假（即发生了逻辑错误）
            if not live_status.is_live:
                return False
            # 如果方法是end，有正在进行的直播，则返回真，即关闭了直播
            else:
                live_status.is_live = False
                print("直播状态:", live_status.is_live)
                return True
        else:
            # 这里统一处理为查询状态
            print("直播状态:", live_status.is_live)
            return live_status.is_live

    return api


# GET
@api.route('/', methods=['GET'])  # 跳转到'/login'
def index_to_login():
    return redirect(url_for('api.show_login_page'))


@api.route('/login', methods=['GET'])
def show_login_page():
    return render_template('login.html')


@api.route('/register', methods=['GET'])
def show_register_page():
    return render_template('register.html')


@api.route('/home', methods=['GET'])
def show_home_page():
    return render_template('home.html')


@api.route('/chat', methods=['GET'])
@api.route('/chat/<username>', methods=['GET'])
def chat(username=None):
    if username:
        return render_template('user/chat.html', username=username)
    else:
        return render_template('user/chat_init.html')


@api.route('/groupchat/<groupname>', methods=['GET'])
def groupchat(groupname):
    return render_template('group/chat_group.html', groupname="groupname")


@api.route('/friend_management', methods=['GET'])
def show_friend_management_page():
    return render_template('friend_management.html')


@api.route('/group_management', methods=['GET'])
def show_group_management_page():
    return render_template('group_management.html')


@api.route('/avatar_setting', methods=['GET'])
def show_avatar_setting_page():
    return render_template('avatar_setting.html')


@api.route('/create_group', methods=['GET'])
def show_create_group_page():
    return render_template('create_group.html')


@api.route('/live', methods=['GET'])
def show_live_page():
    return render_template('live.html')


@api.route('/start_live', methods=['GET'])
def show_start_live_page():
    return render_template('start_live.html')


@api.route('/start_download/<file_id>', methods=['GET'])
def start_download(file_id):
    if check_file_existence(file_id):
        return render_template('downloading.html')
    else:
        return render_template('file_not_found.html')


@api.route('/download_file/<file_id>', methods=['GET'])
def download_file(file_id):
    # 实际的文件下载逻辑
    return file_download_ms(file_id)


# POST
@api.route('/login', methods=['POST'])
def login():
    return register_login('login')


@api.route('/register', methods=['POST'])
def register():
    return register_login('register')


# 检查登录状态
@api.route('/check_login', methods=['POST'])
def check_login():
    return register_login('check_login')


# 查询好友
@api.route('/search_friend', methods=['POST'])
def search_friend():
    return friend_manager('search_friend')


# 发送添加好友请求
@api.route('/send_friend_request', methods=['POST'])
def send_friend_request():
    return friend_manager('send_friend_request')


@api.route('/search_friend_request', methods=['POST'])
def search_friend_request():
    return friend_manager('search_friend_request')


@api.route('/change_friend', methods=['POST'])
def change_friend():
    return friend_manager('change_friend')


# 群组相关操作
# get_group_list 获取管理的群组列表
@api.route('/get_group_list', methods=['POST'])
def get_group_list():
    return get_list('group')


# get_members_list 获取群成员列表
@api.route('/get_members_list', methods=['POST'])
def get_members_list():
    return get_list('members')


# update_group_info 更新群组信息
@api.route('/update_group_info', methods=['POST'])
def update_group_info():
    return update_info('group')


# change_member 增加或删除群组与用户的关系
@api.route('/change_member', methods=['POST'])
def change_member():
    return update_info('members')


# search_users_in_group 查询用户
@api.route('/search_users_in_group', methods=['POST'])
def search_users_in_group():
    return search_users_group()


# 聊天相关
# get_message
@api.route('/get_message', methods=['POST'])
def get_message():
    return get_message_info()


# send_message
@api.route('/send_message', methods=['POST'])
def send_message():
    return send_message_ms()


# file_update
@api.route('/file_update', methods=['POST'])
def file_update():
    return file_update_ms()


@api.route('/get_user_list', methods=['POST'])  # 获取用户列表
def get_user_list():
    return get_left_list()


# 上传头像
@api.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    return upload_avatar_ms()


# 检查是否可用
@api.route('/check_group_name', methods=['POST'])
def check_group_name():
    return check_group_name_ms()


# 创建群组
@api.route('/creat_a_group', methods=['POST'])
def creat_a_group():
    return creat_a_group_ms()


"""下面的正在测试"""


# transcribe
@api.route('/transcribe', methods=['GET'])
def transcribe():
    return render_template('init.html')


@api.route('/upload', methods=['POST'])
async def upload():
    return recognize_ms_1()


"""加密部分"""


@api.route('/negotiate_key', methods=['POST'])
def negotiate_key():
    return negotiate_key_ms()


@api.route('/negotiate_key', methods=['GET'])
def get_negotiate_key():
    return render_template('test_encryption.html')


# 测试用
@api.route('/test_encrypt', methods=['GET'])
def show_test_encrypt():
    return render_template('test/mytest.html')


@api.route('/test_encrypt', methods=['POST'])
def test_encrypt():
    return test_encrypt_ms()
