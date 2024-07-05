function myFetchApi(url, method, data) {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errResp => {
                    const error = new Error(errResp.error || '未知错误');
                    error.errorCode = errResp.error_code; // 将 error_code 添加到错误对象中
                    throw error;
                });
            }
            return response.json();
        });
}

// 获取密钥
function getBase64Key() {
    const base_key = localStorage.getItem('base_key');
    return base_key ? base_key : '';
}


// async function myFetchApi(url, method, data) {
//     // 检查是否需要加密
//     if (data.hasOwnProperty('session_id')) {
//         try {
//             // 获取加密密钥
//             const base64Key = getbase64Key();
//             // 将整个data对象转换为字符串，然后加密
//             const encryptedData = await encryptString(JSON.stringify(data), base64Key);
//             // 重新构造data对象，包含session_id和加密后的数据
//             data = {
//                 "session_id": data.session_id,
//                 "data": encryptedData
//             };
//         } catch (error) {
//             console.error("加密失败:", error);
//             throw new Error('请求加密失败');
//         }
//     }
//
//     // 发送请求
//     return fetch(url, {
//         method: method,
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify(data)
//     })
//     .then(response => {
//         if (!response.ok) {
//             return response.json().then(errResp => {
//                 const error = new Error(errResp.error || '未知错误');
//                 error.errorCode = errResp.error_code; // 将 error_code 添加到错误对象中
//                 throw error;
//             });
//         }
//         return response.json();
//     });
// }

function getUsername() {
    const username = localStorage.getItem('username');
    return username ? username : '';
}

function getGroupname() {
    const groupname = localStorage.getItem('groupname');
    return groupname ? groupname : '';
}

function getGroupId() {
    const groupId = localStorage.getItem('groupId');
    return groupId ? groupId : '';
}


function getSessionId() {
    const session_id = localStorage.getItem('session_id');
    return session_id ? session_id : '';
}


// 定时刷新登录状态
function refreshLoginStatus() {
    const loginData = {username: getUsername(), session_id: getSessionId()};

    myFetchApi('/check_login', 'POST', loginData)
        .then(data => {
            // 成功后的处理
            console.log('登录状态刷新成功');
        })
        .catch(error => {
            // 处理错误响应
            console.error('登录状态刷新失败:', error);
            myHandleErrorCode(error.errorCode);
        });
}

function myHandleErrorCode(errorCode) {
    console.log('错误码：', errorCode);
    switch (errorCode) {
        case 1001:
            alert('提交的表单数据不完整，请确保填写所有必填项后再次提交。');
            break;
        case 1002:
            alert('密码与确认密码不匹配，请重新确认密码。');
            break;
        case 1003:
            alert('登录状态已过期，请重新登录。');
            window.location.href = '/login';
            break;
        case 2001:
            alert('该手机号已被注册。');
            break;
        case 2002:
            alert('该用户名已被使用，请尝试其他用户名。');
            break;
        case 2003:
            alert('邀请码无效，请确认后重新输入。');
            break;
        case 2004:
            alert('用户不存在，请检查用户名或注册一个新用户。');
            break;
        case 2005:
            alert('密码错误，请确认密码后重新登录。');
            break;
        case 2006:
            alert('不能将自己添加为好友。');
            break;
        case 2007:
            alert('对方已经是您的好友。');
            break;
        case 2008:
            alert('好友请求不存在。');
            break;
        case 2009:
            alert('无效操作，可能涉及好友关系，请确认后重试。');
            break;
        case 2010:
            alert('已存在好友请求。');
            break;
        case 3001:
            alert('聊天对象不存在或没有权限进行操作。');
            break;
        case 3002:
            alert('接收者名称错误，请检查后重试。');
            break;
        case 3003:
            alert('发送者和接收者不能是同一个人。');
            break;
        case 3004:
            alert('会话或用户不存在或已被删除。');
            break;
        case 4001:
            alert('没有选择文件，请选择文件后重新上传。');
            break;
        case 4002:
            alert('接收者不存在或没有权限发送文件给目标用户。');
            break;
        case 8001:
            alert('写入数据库发生错误!')
        case 9999:
            alert('服务器发生错误!');
            break;
        default:
            alert('发生未知错误，请稍后再试或联系客服。');
            console.log(errorCode)
    }
}

// 改变指定元素的内容
const updateElementContentById = (id, str) => {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = str;
    } else {
        console.error(`Element with id '${id}' not found.`);
    }
};

// 为指定输入框添加显示/隐藏密码的功能
function togglePasswordVisibility(inputId) {
    const inputField = document.getElementById(inputId);

    inputField.addEventListener('mouseenter', () => {
        inputField.type = "text";
        inputField.dataset.password = "隐藏密码";
    });

    inputField.addEventListener('mouseleave', () => {
        inputField.type = "password";
        inputField.dataset.password = "显示密码";
    });
}

// 将HTML字符串追加到指定容器中
function appendHtmlToContainer(data, targetId) {
    const container = document.getElementById(targetId);
    if (!container) return;
    container.innerHTML += data;
}

function replaceLinks(messageContent) {
    const linkRegex = /(\[([^\]]+)\]\(([^)]+)\))/g;
    return messageContent.replace(linkRegex, '<a href="$3" target="_blank">$2</a>');
}

async function base64ToCryptoKey(base64Key) {
    const rawKey = window.atob(base64Key);
    const keyBuffer = new Uint8Array(new ArrayBuffer(rawKey.length));
    for (let i = 0; i < rawKey.length; i++) {
        keyBuffer[i] = rawKey.charCodeAt(i);
    }
    return window.crypto.subtle.importKey(
        "raw",
        keyBuffer,
        {name: "AES-CBC", length: 256},
        true,
        ["encrypt", "decrypt"]
    );
}

// 加密方法，调用：encryptString("明文","编码后的密钥")
async function encryptString(str, base64Key) {
    console.log("加密前：", str);
    try {
        const cryptoKey = await base64ToCryptoKey(base64Key);
        const iv = window.crypto.getRandomValues(new Uint8Array(16));
        const encoded = new TextEncoder().encode(str);

        const encrypted = await window.crypto.subtle.encrypt(
            {name: "AES-CBC", iv},
            cryptoKey,
            encoded
        );

        const ivAndEncrypted = new Uint8Array(iv.length + encrypted.byteLength);
        ivAndEncrypted.set(iv, 0);
        ivAndEncrypted.set(new Uint8Array(encrypted), iv.length);

        return window.btoa(String.fromCharCode.apply(null, ivAndEncrypted));
    } catch (error) {
        throw new Error('加密过程中发生错误');
    }
}


// 解密方法，调用：decryptString("编码后的密文","编码后的密钥")
// async function decryptString(encryptedBase64Str, base64Key) {
//     try {
//         const cryptoKey = await base64ToCryptoKey(base64Key);
//         const ivAndEncrypted = Uint8Array.from(atob(encryptedBase64Str), c => c.charCodeAt(0));
//         const iv = ivAndEncrypted.slice(0, 16);
//         const encrypted = ivAndEncrypted.slice(16);
//
//         const decrypted = await window.crypto.subtle.decrypt(
//             {name: "AES-CBC", iv},
//             cryptoKey,
//             encrypted
//         );
//
//         return new TextDecoder().decode(decrypted);
//     } catch (error) {
//         throw new Error('解密过程中发生错误');
//     }
// }
// 解密方法，调用：decryptString("编码后的密文","编码后的密钥")
async function decryptString(encryptedBase64Str, base64Key) {
    try {
        const cryptoKey = await base64ToCryptoKey(base64Key);
        const ivAndEncrypted = Uint8Array.from(atob(encryptedBase64Str), c => c.charCodeAt(0));
        const iv = ivAndEncrypted.slice(0, 16);
        const encrypted = ivAndEncrypted.slice(16);

        const decrypted = await window.crypto.subtle.decrypt(
            {name: "AES-CBC", iv},
            cryptoKey,
            encrypted
        );

        const decodedText = new TextDecoder().decode(decrypted);

        // 尝试解析为 JSON 对象，如果失败则返回原始文本
        try {
            return JSON.parse(decodedText);
        } catch (e) {
            return decodedText;
        }
    } catch (error) {
        throw new Error('解密过程中发生错误');
    }
}



