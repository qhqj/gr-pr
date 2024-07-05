const toggleBtn = document.querySelector(".toggleBtn");
const intervalSelect = document.querySelector('#interval');//确定几秒一断
const previewVideoElement = document.getElementById('previewVideo');//预览框
const waitingMessage = document.getElementById('waitingMessage');//等待直播开始的提示信息
const showTimeCheckbox = document.getElementById('showTimeCheckbox');//显示或者隐藏时间的勾选框
const socket = io('/start_live');

let liveStream; // 用于直播的流
let recordStream; // 用于录制的流
let liveRecorder;
let recordRecorder;

let intervalId;


let mediaSource = new MediaSource();
let sourceBuffer;
let queue = [];

previewVideoElement.src = URL.createObjectURL(mediaSource);
previewVideoElement.muted = true;

mediaSource.addEventListener('sourceopen', function () {
    sourceBuffer = mediaSource.addSourceBuffer('video/webm; codecs="vp9,opus"');
    sourceBuffer.mode = 'sequence';

    sourceBuffer.addEventListener('updateend', () => {
        if (queue.length > 0 && !sourceBuffer.updating) {
            sourceBuffer.appendBuffer(queue.shift());
        }
    });
});

socket.on('live_data', function (data) {
    let arrayBuffer = new Uint8Array(data).buffer;

    if (sourceBuffer && !sourceBuffer.updating) {
        sourceBuffer.appendBuffer(arrayBuffer);
    } else {
        queue.push(arrayBuffer);
    }

    if (previewVideoElement.paused) {
        previewVideoElement.play().catch(err => console.error("播放失败:", err));
    }

    waitingMessage.style.display = 'none';
    previewVideoElement.style.display = 'block';
});


checkLiveStatusWin();
// 定时器检查是否有直播正在进行
setInterval(() => {
    checkLiveStatusWin();
}, 10000); // 每 10 秒检查一次直播状态

// 处理直播状态变化
function checkLiveStatusWin() {
    socket.emit('is_live', 'check', (response) => {
        if (response) {//有正在进行的直播
            waitingMessage.style.display = 'none';
            previewVideoElement.style.display = 'block';
        } else {//没有正在进行的直播
            waitingMessage.style.display = 'block';
            previewVideoElement.style.display = 'none';
            previewVideoElement.pause();
        }
    });
}


async function getMedia() {
    const selectedValue = document.getElementById('selectAudio').value;
    try {
        const audioStream = await navigator.mediaDevices.getUserMedia({audio: true});
        const screenStream = await navigator.mediaDevices.getDisplayMedia({
            video: {
                width: {ideal: 1280}, // 720p 分辨率
                height: {ideal: 720}
            },
            audio: selectedValue === 'inside' // 是否包括系统音频
        });

        // 为直播和录制分别创建流
        liveStream = new MediaStream([...screenStream.getTracks(), ...audioStream.getTracks()]);
        recordStream = new MediaStream([...screenStream.getTracks(), ...audioStream.getTracks()]);

        // 创建用于直播的 liveRecorder
        liveRecorder = new MediaRecorder(liveStream, {mimeType: 'video/webm; codecs=vp9,opus'});
        liveRecorder.ondataavailable = e => {

            if (e.data.size > 0) {
                sendDataViaSocket(e.data);
                console.log("直播数据已发送")
            }
        };

        // 创建用于录制的 recordRecorder
        recordRecorder = new MediaRecorder(recordStream, {mimeType: 'video/webm; codecs=vp9,opus'});
        recordRecorder.ondataavailable = e => {
            if (e.data.size > 0) {
                sendToServer([e.data]);
            }
        };

        startBtn.disabled = false;

    } catch (error) {
        console.error("授权失败！", error);
    }
}

function sendDataViaSocket(data) {
    data.arrayBuffer().then(arrayBuffer => {
        const uint8Array = new Uint8Array(arrayBuffer);
        socket.emit('live_data', uint8Array.buffer);
    }).catch(error => console.error("转换Blob时出错：", error));
}

function startLive() {
    if (liveRecorder && liveRecorder.state !== 'recording') {
        liveRecorder.start(500); // 每X毫秒生成一次数据块
        console.log("直播开始");
    }
}


function startRecording() {
    if (recordRecorder && recordRecorder.state !== 'recording') {
        recordRecorder.start();
        console.log("录制开始");
    }
}

function stopRecording() {
    if (recordRecorder && recordRecorder.state === "recording") {
        recordRecorder.stop();
        console.log("录制停止");
    }
}


function sendToServer(chunks) {
    const blob = new Blob(chunks, {type: "video/webm; codecs=vp9,opus"});
    const formData = new FormData();
    formData.append('video', blob);

    // 检查 isRemove 复选框的状态
    const isRemoveChecked = document.getElementById('isRemove').checked;

    // 根据复选框的状态添加 remove_file 键值对
    if (isRemoveChecked) {
        formData.append('remove_file', 'yes');
    } else {
        formData.append('remove_file', 'no');
    }

    const textOutput = document.getElementById('textOutput');

    // 记录发送的时间
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const sentTime = `${hours}:${minutes}:${seconds}`;

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('服务器返回错误');
            }
            return response.json();
        })
        .then(data => {
            // 创建新的 <p> 元素
            const newParagraph = document.createElement('p');

            // 在段落中添加时间的 <div> 元素
            const timeDiv = document.createElement('div');
            timeDiv.className = 'timeSend';
            timeDiv.textContent = sentTime;

            // 将时间 <div> 元素插入到段落中
            newParagraph.appendChild(timeDiv);

            // 将返回的文本内容添加到段落中
            const transcribedText = data.transcribedText || "未获取到服务器响应";
            newParagraph.appendChild(document.createTextNode(transcribedText));

            // 将新的段落添加到 textOutput 中
            textOutput.appendChild(newParagraph);
            console.log("视频片段成功发送到服务器");
        })
        .catch(error => {
            console.error("发送过程中出现错误：", error);
            const errorParagraph = document.createElement('p');
            errorParagraph.style.color = 'red';
            errorParagraph.textContent = `错误：${error.message}`;
            textOutput.appendChild(errorParagraph);
        });
}


showTimeCheckbox.addEventListener('change', function () {
    // 获取所有具有类名 'timeSend' 的元素
    const timeDivs = document.querySelectorAll('.timeSend');

    // 根据勾选框的状态决定显示或隐藏这些元素
    const displayStyle = showTimeCheckbox.checked ? 'block' : 'none';

    // 遍历所有 timeDivs 元素，并设置其显示样式
    timeDivs.forEach(function (timeDiv) {
        timeDiv.style.display = displayStyle;
    });
});


function stopMediaStreams() {
    if (liveStream) {
        liveStream.getTracks().forEach(track => track.stop());
    }
    if (recordStream) {
        recordStream.getTracks().forEach(track => track.stop());
    }

    liveStream = null;
    recordStream = null;
}


// 让服务器关闭直播标识
function endLive() {
    socket.emit('is_live', 'end', (response) => {
        if (response) {
            console.log("直播已结束");
        } else {
            console.log("未知错误，请刷新页面");
            alert("未知错误，请刷新页面重试")
            window.location.reload();
        }
    });
}

function startLiveServer() {
    // 通知服务器开始直播
    socket.emit('is_live', 'start', (response) => {

        if (response) {
            console.log("直播已开始");
        } else {
            console.log(response);
            alert("未知错误，请刷新页面重试");
            window.location.reload();

        }
    })
}


toggleBtn.addEventListener('click', () => {
    // 首先查询当前直播状态
    checkLiveStatus(() => {
        if (toggleBtn.textContent === '开始录制') {
            startLiveServer();

            getMedia().then(() => {
                startLive(); // 启动直播
                startRecording(); // 启动录制

                intervalId = setInterval(() => {
                    stopRecording(); // 停止当前录制
                    startRecording(); // 启动新的录制
                }, parseInt(intervalSelect.value));

                // 切换按钮标签为"结束录制"
                toggleBtn.textContent = '结束录制';
            }).catch(error => {
                console.error("错误：", error);
            });

        } else if (toggleBtn.textContent === '结束录制') {
            // 停止录制和直播的逻辑

            clearInterval(intervalId);
            stopRecording();
            stopMediaStreams();

            // 停止直播
            if (liveRecorder && liveRecorder.state === 'recording') {
                liveRecorder.stop();
                console.log("直播结束");
            }

            // 通知服务器直播结束
            endLive();

            // 切换按钮标签为"开始录制"，结束逻辑
            toggleBtn.textContent = '开始录制';
        } else {
            console.log("未知状态");
            alert("未知状态，请刷新页面重试");
            window.location.reload();
        }
    });
});

function checkLiveStatus(callback) {
    socket.emit('is_live', 'check', (response) => {
        console.log(response)
        if (response) {
            toggleBtn.textContent = '结束录制';
        } else {
            toggleBtn.textContent = '开始录制';
        }
        callback(); // 调用回调函数
    });
}



