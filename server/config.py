class Config(object):
    # 文件位置
    FILEPATH = 'file'

    # 密钥
    SECRET_KEY = 'QHQJ'
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/graduation_project'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
