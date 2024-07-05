# 语音转文字
import os
from datetime import datetime

import whisper
from flask import request, jsonify
from opencc import OpenCC
from werkzeug.utils import secure_filename

# 加载 Whisper 模型
model = whisper.load_model("base")


def convert_to_simplified(text):
    cc = OpenCC('t2s')  # 从繁体转换到简体
    converted_text = cc.convert(text)
    return converted_text


def recognize_ms_1():
    print("recognize_ms_1")
    if 'video' not in request.files:
        return jsonify({'error': '没有文件部分'}), 400
    file = request.files['video']
    remove_file = request.form.get('remove_file', 'no')

    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    try:
        # 使用当前时间戳作为文件名
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = secure_filename(f"{timestamp}.webm")
        filepath = os.path.join("uploads", filename)
        file.save(filepath)

        # 使用 Whisper 模型进行语音识别
        text = model.transcribe(filepath)
        recognized_text = convert_to_simplified(text["text"])

        # 打印当前的时间
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        print("当前时间为：", formatted_time)

        # 考虑删除文件
        if remove_file == 'yes':
            os.remove(filepath)

        # 返回识别的文本内容
        return jsonify({'message': '文件上传成功', 'transcribedText': recognized_text})

    except Exception as e:
        print(f"识别失败：{e}")
        return jsonify({'error': '语音识别失败'}), 500
