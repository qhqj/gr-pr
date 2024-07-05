from flask import jsonify, request

from server.myUtil import check_login, search_group_create_all, handle_error_code, search_member_all, get_user_name, \
    search_user_all, is_user_in_group, get_user_id, delete_user_from_group, add_user_to_group, check_group_creator, \
    check_groupname, update_group_info_ms, create_group, check_groupname_just_name, get_group_id


def get_list(method):
    data = request.json
    if method == 'group':
        return get_list_group(data)
    elif method == 'members':
        return get_list_members(data)
    else:
        return handle_error_code(9999)


# 获取管理的群组列表
def get_list_group(data):
    print("get_list_group，data=", data)
    # 验证是否登录
    username = data.get("username")
    session_id = data.get("session_id")

    user_id = check_login(username, session_id)
    if not user_id:
        return handle_error_code(1003)

    # 查询管理着的群组列表：
    print("查询管理着的群组列表")
    search_group = search_group_create_all(user_id)
    print(search_group)
    search_results = []
    for group in search_group:
        search_results.append({
            'id': group.group_id,
            'name': group.name,
            'description': group.description
        })
    print("search_results:", search_results)
    return jsonify(search_results), 200


# 获取群成员列表
def get_list_members(data):
    print(data)
    username = data.get("username")
    session_id = data.get("session_id")
    group_id = data.get("groupId")
    print(group_id)
    # 验证是否登录
    user_id = check_login(username, session_id)
    if not user_id:
        return handle_error_code(1003)

    # # 查询群组成员列表
    search_member = search_member_all(group_id)
    search_results = []
    for member in search_member:
        is_creator = member.user_id == user_id

        search_results.append({
            "username": get_user_name(member.user_id),
            "is_creator": is_creator
        })
    print(search_results)

    return jsonify(search_results), 200


def update_info(method):
    data = request.json
    if method == 'group':
        return update_info_group(data)
    elif method == 'members':
        return update_info_members(data)
    else:
        return handle_error_code(9999)


# 更新群组信息
def update_info_group(data):
    print("update_info_group")
    print(data)
    # 获取数据
    username = data.get("username")
    session_id = data.get("session_id")
    groupname = data.get("groupname")
    description = data.get("description")
    group_id = data.get("group_id")

    # 检查完整性
    if not (username and session_id and groupname and description):
        return handle_error_code(1001)
    # 验证是否登录
    user_id = check_login(username, session_id)
    if not user_id:
        return handle_error_code(1003)
    # 查询是否是群组创建者
    if not check_group_creator(group_id, user_id):
        return handle_error_code(1004)
    # 查询群名是否可用

    if check_groupname(groupname, group_id):
        return handle_error_code(2011)

    print("update_group_info_ms")

    # 更新群组信息
    if update_group_info_ms(group_id, groupname, description):
        return jsonify({})  # 添加默认返回
    else:
        return handle_error_code(8001)


# 增加或删除群组与用户的关系
def update_info_members(data):
    print(data)
    username = data.get("username")
    session_id = data.get("session_id")
    operand = data.get("operand")
    action = data.get("action")
    group_id = data.get("group_id")

    # 检查完整性
    if not (username and session_id and operand and action and group_id):
        return handle_error_code(1001)
    # 验证是否登录
    user_id = check_login(username, session_id)
    if not user_id:
        return handle_error_code(1003)
    # 查询对象是否存在
    operand_id = get_user_id(operand)
    if not operand_id:
        return handle_error_code(2004)

    if action == "delete":
        print(action)
        # 删除相关方法
        # 查询是否在群组中
        if not is_user_in_group(operand_id, group_id):
            return handle_error_code(3004)
        if delete_user_from_group(operand_id, group_id):
            # 返回删除成功
            return jsonify({}), 200
        else:
            return handle_error_code(8001)
    elif action == "add":
        print(action)
        # 添加相关方法
        # 查询是否在群组中
        if is_user_in_group(operand_id, group_id):
            return handle_error_code(3004)
        # 添加到群组
        if add_user_to_group(operand_id, group_id):
            return jsonify({}), 200
        else:
            return handle_error_code(8001)


def search_users_group():
    data = request.json
    username = data.get("username")
    session_id = data.get("session_id")
    group_id = data.get("group_id")
    search_input = data.get("searchInput")

    # 检查完整性
    if not (username and session_id and group_id and search_input):
        return handle_error_code(1001)

    user_id = check_login(username, session_id)
    if not user_id:
        return handle_error_code(1003)

    users = search_user_all(search_input)
    search_results = []
    for user in users:
        in_group = is_user_in_group(user.user_id, group_id)
        search_results.append({
            "username": user.username,
            "in_group": in_group
        })
    print(search_results)
    return jsonify(search_results), 200


def check_group_name_ms():
    data = request.json
    username = data.get("username")
    session_id = data.get("session_id")
    group_name = data.get("group_name")
    print(data)
    print(username)
    print(session_id)
    print(group_name)

    # 检查完整性
    if not (username and session_id and group_name):
        return handle_error_code(1001)

    user_id = check_login(username, session_id)
    if not user_id:
        return handle_error_code(1003)

    # 查询群名是否可用
    if not check_groupname_just_name(group_name):
        return jsonify({"message": "群名可用"}), 200

    else:
        return handle_error_code(2011)


def creat_a_group_ms():
    data = request.json
    username = data.get("username")
    session_id = data.get("session_id")
    group_name = data.get("group_name")
    description = data.get("description")
    is_department = data.get("is_department")

    # 检查完整性
    if not (username and session_id and group_name and description and is_department):
        return handle_error_code(1001)

    user_id = check_login(username, session_id)
    if not user_id:
        return handle_error_code(1003)

    if check_groupname_just_name(group_name):
        return handle_error_code(2011)

    is_department_bool = True if is_department == "true" else False

    if create_group(group_name, description, is_department_bool, user_id):
        # 写入群组关系表

        group_id = get_group_id(group_name)
        if add_user_to_group(user_id, group_id):
            return jsonify({}), 200
    else:
        return handle_error_code(8001)
