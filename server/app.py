# app.py

import os

from flask import Flask
from flask_socketio import SocketIO

from config import Config
from models import db
from routes import init_api

socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    # 导入配置
    app.config.from_object(Config)
    # 初始化数据库
    db.init_app(app)
    # 初始化SocketIO
    socketio.init_app(app)
    # 注册蓝图
    api = init_api(socketio)
    app.register_blueprint(api, url_prefix='/')
    return app


if __name__ == "__main__":
    save_directory = '../file'  # 创建目录
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    app = create_app()
    # socketio.run(app, debug=True, port=80, host='0.0.0.0')
    socketio.run(app, debug=True, port=80, host='0.0.0.0', allow_unsafe_werkzeug=True)
