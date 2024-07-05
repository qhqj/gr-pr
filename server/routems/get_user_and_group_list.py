from flask import jsonify, request

from server.myUtil import check_login, handle_error_code, search_related_friends, get_user_name, get_group_name, \
    search_group_join_all, get_avatar_link, get_group_user_count


def get_left_list():
    data = request.get_json()
    username = data.get("username")
    session_id = data.get("session_id")

    user_id = check_login(username, session_id)
    if not user_id:
        return handle_error_code(1003)
    # 尝试获取用户的好友和群组列表
    friend_list = []
    search_friends = search_related_friends(user_id)
    for friend_member in search_friends:
        if friend_member.status == 'accepted':
            friend_id = friend_member.accepter_id if friend_member.requester_id == user_id else friend_member.requester_id
            friend_name = get_user_name(friend_id)
            avatar = get_avatar_link(friend_name)
            link = '/chat/' + friend_name
            unread = 0  # 以后再说
            friend_list.append({
                'username': friend_name,
                'avatar': avatar,
                'link': link,
                'unread': unread
            })
    print("friend_list:", friend_list)
    group_list = []
    # 查询用户所在的所有
    search_groups = search_group_join_all(user_id)
    for group in search_groups:
        # group是GroupUser对象
        # 取出群组的id
        group_id = group.group_id
        # 获取群组的名字
        group_name = get_group_name(group_id)
        # 查询组中的用户人数
        group_count = get_group_user_count(group_id)
        result = group_name + '(' + str(group_count) + ')'

        # avatar = '../../static/images/avatar/' + group_name + '.jpg' # 群组暂时没有设置头像
        avatar = "../../static/images/demo.png"  # 以后再说
        link = '/groupchat/' + group_name
        unread = 0  # 以后再说
        group_list.append({
            'groupname': result,
            'avatar': avatar,
            'link': link,
            'unread': unread
        })
    print("group_list:", group_list)
    data = {
        'friends': friend_list,
        'groups': group_list
    }
    return jsonify(data), 200
