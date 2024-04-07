// 获取消息
function getMessage(target_type, target_name) {
    //构造请求参数
    const requestData = {
        "username": getUsername(),
        "session_id": getSessionId(),
        "target_type": target_type,
        "target_name": target_name

    }
    myFetchApi('/get_message', 'POST', requestData)
        .then(data => {
            // 成功后的处理
            console.log('获取消息成功');
            processMessages(data);
        })
        .catch(error => {
            // 处理错误响应
            console.log(error)
            myHandleErrorCode(error.errorCode);
        });
}


function processMessages(messages) {
    const chatMessages = document.getElementById("chat-messages");
    // 清空聊天消息容器
    chatMessages.innerHTML = '';
    const currentUser = getUsername();
    messages.forEach(message => {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");
        messageElement.dataset.messageId = message.message_id;

        if (message.sender === currentUser) {
            messageElement.classList.add("sent-by-me");
        }

        let contentHTML = '';

        if (message.content_type === "image") {
            contentHTML = `<img src="${message.content}" alt="Image">`;
        } else if (message.content_type === "text") {
            const messageContent = replaceLinks(message.content);
            contentHTML = `<p>${messageContent}</p>`;
        } else {
            const filename = message.content_type;
            const filePath = message.content;
            contentHTML = `
        <div class="file-message">
            <a href="${filePath}" target="_blank" class="file-link">
                <span class="file-icon">📄</span> 
                <span class="file-name">${filename}</a>
            </a>
        </div>`;
        }


        messageElement.innerHTML = `
            <div class="message-info">
                <div class="avatar">
                    <img src="${message.avatar}" alt="Avatar">
                </div>
                <div class="message-content">
                    <div class="sender">${message.sender}</div>
                    <div class="bubble">
                        ${contentHTML}
                    </div>
                    <div class="meta">
                        <div class="sent-at">${message.sent_at}</div>
                        <div class="read-status ${message.is_read ? 'read' : 'unread'}">${message.is_read ? "已读" : "未读"}</div>
                    </div>
                </div>
            </div>
        `;

        chatMessages.appendChild(messageElement);
    });
}

//发送消息
function sendMessage(message, target_type, target_name) {
    console.log(message, target_type, target_name)
    //构造请求体
    const requestData = {
        "username": getUsername(),
        "session_id": getSessionId(),
        "target_type": target_type,
        "target_name": target_name,
        "message": message
    }

    myFetchApi('/send_message', 'POST', requestData)
        .then(data => {
            // 成功后的处理
            console.log("发送消息成功！")
            //更新聊天界面
            getMessage(target_type, target_name);
        })
        .catch(error => {
            // 处理错误响应
            console.log(error)
            alert("发送消息失败！")
        });
}

function uploadFile(file, file_type, target_type, target_name) {
    //构造请求体
    const requestData = new FormData();
    requestData.append('file', file);
    requestData.append('file_type', file_type);
    requestData.append('username', getUsername());
    requestData.append('session_id', getSessionId());
    requestData.append('target_type', target_type);
    requestData.append('target_name', target_name);

    fetch('/file_update', {
        method: 'POST',
        body: requestData,
    })
        .then(response => {
            if (response.ok) {
                return response.json(); // 或者其他处理响应的方式
            }
            throw new Error('网络错误');
        })
        .then(data => {
            //更新聊天界面
            getMessage(target_type, target_name);
        })
        .catch(error => {
            console.error('出现问题：', error);
        });
}

//显示左侧列表
function showUserList() {

    //构造请求体
    const requestData = {
        "username": getUsername(),
        "session_id": getSessionId()
    }
    myFetchApi('/get_user_list', 'POST', requestData)
        .then(data => {
            // 成功后的处理
            console.log('获取用户列表成功');
            console.log(data);
            //更新左侧列表
            processUserList(data);
        })
        .catch(error => {
            // 处理错误响应
            console.log(error)
            myHandleErrorCode(error.errorCode);
        });
}

// 更新左侧列表
function processUserList(userList) {
    const friendsList = document.querySelector('.contacts');
    const groupsList = document.querySelector('.groups');
    // 填充好友列表：
    userList.friends.forEach(friend => {
        const listItem = document.createElement('li');
        listItem.innerHTML = `
                <!-- 好友列表项 -->
                <div class="list-item">
                    <a href="${friend.link}" class="friend-link">
                        <div class="avatar">
                            <img src="${friend.avatar}" alt="${friend.username}">
                        </div>
                        <div class="info">
                            <h4>${friend.username}</h4>
                           <span class="${friend.unread > 0 ? 'unread-message' : ''}">
                                ${friend.unread > 0 ? `未读消息: ${friend.unread}` : '暂无未读消息'}
                           </span>
                        </div>
                    </a>
                </div>
            `;
        friendsList.appendChild(listItem);
    });
    // 填充群组列表
    userList.groups.forEach(group => {
        const listItem = document.createElement('li');
        listItem.innerHTML = `
                <!-- 群组列表项 -->
                <div class="list-item">
                    <a href="${group.link}" class="group-link">
                        <div class="avatar">
                            <img src="${group.avatar}" alt="${group.groupname}">
                        </div>
                        <div class="info">
                            <h4>${group.groupname}</h4>
                            <span class="${group.unread > 0 ? 'unread-message' : ''}">
                                ${group.unread > 0 ? `未读消息: ${group.unread}` : '暂无未读消息'}
                            </span>
                        </div>
                    </a>
                </div>
            `;
        groupsList.appendChild(listItem);
    });
}