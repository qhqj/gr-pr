# 待定
运行以安装依赖
```pip install -r requirements.txt```

数据库配置（直接运行这段查询就可以了！）:
```sql

-- 创建用户表
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    phone VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL
);

-- 创建消息表
CREATE TABLE messages (
    message_id INT PRIMARY KEY,
    sender_id INT,
    target_id INT,
    target_type VARCHAR(255),
    content TEXT,
    content_type VARCHAR(255),
    thumbnail VARCHAR(255),
    sent_at DATETIME,
    is_read BOOLEAN,
    FOREIGN KEY (sender_id) REFERENCES users(user_id)
);

-- 创建文件表
CREATE TABLE files (
    file_id INT PRIMARY KEY,
    user_id INT,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    uploaded_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 创建群组表
CREATE TABLE u_groups (
    group_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_department BOOLEAN,
    creator_id INT,
    FOREIGN KEY (creator_id) REFERENCES users(user_id)
);

-- 创建群组用户表
CREATE TABLE group_users (
    group_id INT,
    user_id INT,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES u_groups(group_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 创建邀请码表
CREATE TABLE Invitation_code (
    Invitation_code_id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(16) NOT NULL,
    is_available BOOLEAN NOT NULL,
    used_at DATETIME
);

-- 创建好友请求表
CREATE TABLE friend_requests (
    request_id INT PRIMARY KEY,
    requester_id INT NOT NULL,
    accepter_id INT NOT NULL,
    created_at DATETIME,
    updated_at DATETIME,
    status ENUM('pending', 'accepted', 'declined', 'blocked') NOT NULL DEFAULT 'pending',
    FOREIGN KEY (requester_id) REFERENCES users(user_id),
    FOREIGN KEY (accepter_id) REFERENCES users(user_id)
);
```


运行方法：将`creat_invitation_code.py`的运行结果复制出来，在数据库上查询添加邀请码

# 就这样吧
 联系方式：3115759842@qq.com

https://github.com/qhqj

项目地址：https://github.com/qhqj/gr-pr （旧）

