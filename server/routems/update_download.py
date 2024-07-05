from datetime import datetime
import io
import os
from datetime import datetime
from urllib.parse import quote

from PIL import Image
from flask import request, jsonify, render_template
from flask import send_from_directory

from server.myUtil import handle_error_code, check_login, save_file_db, get_user_id, get_group_id, save_message, \
    get_file_by_id


def get_target_id(target_type, target_name):
    if target_type == 'user':
        return get_user_id(target_name)
    elif target_type == 'group':
        return get_group_id(target_name)
    else:
        return handle_error_code(9998)


def file_update_ms():
    file = request.files['file']
    file_type = request.form.get('file_type')
    username = request.form.get('username')
    session_id = request.form.get('session_id')
    target_type = request.form.get('target_type')
    target_name = request.form.get('target_name')
    # 验证登录
    sender_user_id = check_login(username, session_id)
    if not sender_user_id:
        return handle_error_code(1003)
    # 检查是否有文件
    if file.filename == '':
        return handle_error_code(4001)
    target_id = get_target_id(target_type, target_name)
    is_read = target_type != 'user'
    # 通了验证
    if file_type == 'file':
        path = os.path.join('file', file.filename)
        base_filename, file_extension = os.path.splitext(file.filename)
        # 修改文件名防止重名
        counter = 0
        while os.path.exists(path):
            counter += 1
            unique_filename = f"{base_filename}_{counter}{file_extension}"
            path = os.path.join('file', unique_filename)
        file.save(path)
        # 将文件信息保存到数据库
        file_id = save_file_db(base_filename + file_extension, path, sender_user_id)
        if not file_id:
            return handle_error_code(8001)
        # 将其写入消息表
        file_path = '/start_download/' + str(file_id)
        if not save_message(sender_user_id, target_id, target_type, file_path, base_filename + file_extension, is_read):
            return handle_error_code(8001)
        return jsonify({'message': 'File uploaded successfully', 'file_id': file_id}), 200

    elif file_type == 'picture':
        file_extension = os.path.splitext(file.filename)[1]
        filename = str(int(datetime.now().timestamp())) + file_extension
        path = os.path.join('server/static/images', filename)
        file.save(path)
        file_path = '../../static/images/' + filename
        if not save_message(sender_user_id, target_id, target_type, file_path, 'image', is_read):
            return handle_error_code(8001)
        return jsonify({'message': 'File uploaded successfully'}), 200
    else:
        return handle_error_code(9999)


def file_download_ms(file_id):
    file = get_file_by_id(file_id)
    if file is None:
        return render_template('file_not_found.html')

    absolute_path = os.path.join(os.getcwd(), file.file_path)
    directory = os.path.dirname(absolute_path)
    filename = os.path.basename(file.file_path)

    response = send_from_directory(directory, filename, as_attachment=True)

    safe_filename = quote(file.filename.encode('utf-8'))
    response.headers['X-Filename'] = safe_filename

    return response


def upload_avatar_ms():
    file = request.files['file']
    username = request.form.get('username')
    session_id = request.form.get('session_id')
    sender_user_id = check_login(username, session_id)
    if not sender_user_id:
        return handle_error_code(1003)
    if file.filename == '':
        return handle_error_code(4001)
    # 处理头像文件：
    # 读取图像数据
    image_stream = io.BytesIO()
    file.save(image_stream)
    image_stream.seek(0)

    # 打开图像并转换为 JPG 格式
    try:
        image = Image.open(image_stream)
        if image.format != 'JPEG':
            # 如果不是 JPG 格式，则转换为 JPG
            image = image.convert('RGB')
    except Exception as e:
        print("无法处理图像:", e)
        return jsonify({'error': 'Invalid image file'}), 400

    # 设置图像文件名为用户名，后缀为 jpg，路径为 avatar 文件夹下
    path = os.path.join('server/static/images/avatar', username + '.jpg')

    # 检查是否存在同名文件，如果存在则先删除
    if os.path.exists(path):
        os.remove(path)

    # 保存图像
    image.save(path, 'JPEG')
    return jsonify({'message': 'successful'}), 200
