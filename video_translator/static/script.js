let currentTaskId = null;
let currentFilePath = null;
let pollInterval = null;

const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const configSection = document.getElementById('configSection');
const progressSection = document.getElementById('progressSection');
const translationSection = document.getElementById('translationSection');
const completeSection = document.getElementById('completeSection');
const errorSection = document.getElementById('errorSection');
const startBtn = document.getElementById('startBtn');
const downloadBtn = document.getElementById('downloadBtn');
const newVideoBtn = document.getElementById('newVideoBtn');
const newVideoBtn2 = document.getElementById('newVideoBtn2');
const retryBtn = document.getElementById('retryBtn');

function initEventListeners() {
    uploadBox.addEventListener('click', () => fileInput.click());
    uploadBox.addEventListener('dragover', handleDragOver);
    uploadBox.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);
    
    startBtn.addEventListener('click', startProcessing);
    downloadBtn.addEventListener('click', downloadResult);
    newVideoBtn.addEventListener('click', resetUI);
    newVideoBtn2.addEventListener('click', resetUI);
    retryBtn.addEventListener('click', () => location.reload());
    
    const translationUploadBox = document.getElementById('translationUploadBox');
    const translationFileInput = document.getElementById('translationFileInput');
    
    translationUploadBox.addEventListener('click', () => translationFileInput.click());
    translationUploadBox.addEventListener('dragover', handleDragOver);
    translationUploadBox.addEventListener('drop', (e) => handleTranslationDrop(e, translationFileInput));
    translationFileInput.addEventListener('change', handleTranslationSelect);
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.style.borderColor = '#764ba2';
    e.currentTarget.style.background = '#f0f2ff';
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.style.borderColor = '#667eea';
    e.currentTarget.style.background = '#f8f9ff';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        handleFileSelect();
    }
}

function handleFileSelect() {
    const file = fileInput.files[0];
    if (file) {
        uploadVideo(file);
    }
}

function handleTranslationDrop(e, input) {
    e.preventDefault();
    e.currentTarget.style.borderColor = '#667eea';
    e.currentTarget.style.background = '#f8f9ff';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        input.files = files;
        handleTranslationSelect();
    }
}

function handleTranslationSelect() {
    const translationFileInput = document.getElementById('translationFileInput');
    const file = translationFileInput.files[0];
    if (file) {
        uploadTranslation(file);
    }
}

// 上传视频
async function uploadVideo(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    document.getElementById('uploadProgress').style.display = 'block';
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentFilePath = data.filepath;
            document.getElementById('uploadStatus').textContent = '上传成功！';
            setTimeout(() => {
                document.getElementById('uploadProgress').style.display = 'none';
                uploadBox.style.display = 'none';
                configSection.style.display = 'block';
            }, 1500);
        } else {
            alert('上传失败：' + (data.error || '未知错误'));
            resetUI();
        }
    } catch (error) {
        alert('上传出错：' + error.message);
        resetUI();
    }
}

// 开始处理
async function startProcessing() {
    const modelSize = document.getElementById('modelSelect').value;
    const device = document.getElementById('deviceSelect').value;
    const manualTranslate = document.getElementById('manualTranslate').checked;
    
    startBtn.disabled = true;
    
    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filepath: currentFilePath,
                model_size: modelSize,
                device: device,
                manual_translate: manualTranslate
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentTaskId = data.task_id;
            configSection.style.display = 'none';
            progressSection.style.display = 'block';
            pollTaskStatus();
        } else {
            alert('处理失败：' + (data.error || '未知错误'));
            startBtn.disabled = false;
        }
    } catch (error) {
        alert('请求出错：' + error.message);
        startBtn.disabled = false;
    }
}

// 轮询任务状态
function pollTaskStatus() {
    if (pollInterval) clearInterval(pollInterval);
    
    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/task/${currentTaskId}`);
            const task = await response.json();
            
            if (response.ok) {
                updateProgress(task);
                
                if (task.status === 'completed') {
                    clearInterval(pollInterval);
                    showComplete(task);
                } else if (task.status === 'failed') {
                    clearInterval(pollInterval);
                    showError(task.error || '处理失败');
                } else if (task.status === 'waiting_translation') {
                    clearInterval(pollInterval);
                    showTranslationWaiting(task);
                }
            }
        } catch (error) {
            console.error('状态查询失败：' + error.message);
        }
    }, 1000);
}

// 更新进度
function updateProgress(task) {
    const progressFill = document.getElementById('processProgressFill');
    const progressText = document.getElementById('progressText');
    const statusMessage = document.getElementById('statusMessage');
    
    progressFill.style.width = task.progress + '%';
    progressText.textContent = task.progress + '%';
    statusMessage.textContent = task.message || '处理中...';
}

// 显示完成
function showComplete(task) {
    progressSection.style.display = 'none';
    completeSection.style.display = 'block';
    
    const completeMessage = document.getElementById('completeMessage');
    completeMessage.textContent = '视频处理完成！\n字幕文件已压制到视频中。';
}

// 显示翻译等待状态
function showTranslationWaiting(task) {
    progressSection.style.display = 'none';
    translationSection.style.display = 'block';
    
    const translationLink = document.querySelector('.translation-section p');
    if (task.translation_file) {
        translationLink.textContent = `转录文件已生成：${task.translation_file}，请进行翻译后上传。`;
    }
}

// 上传翻译文件
async function uploadTranslation(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    document.getElementById('translationUploadProgress').style.display = 'block';
    
    try {
        const response = await fetch(`/api/upload-translation/${currentTaskId}`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('translationUploadStatus').textContent = '上传成功！处理中...';
            translationSection.style.display = 'none';
            progressSection.style.display = 'block';
            pollTaskStatus();
        } else {
            alert('上传失败：' + (data.error || '未知错误'));
            document.getElementById('translationUploadProgress').style.display = 'none';
        }
    } catch (error) {
        alert('上传出错：' + error.message);
        document.getElementById('translationUploadProgress').style.display = 'none';
    }
}

// 显示错误
function showError(errorMessage) {
    progressSection.style.display = 'none';
    errorSection.style.display = 'block';
    
    const errorMsg = document.getElementById('errorMessage');
    errorMsg.textContent = '处理过程中出现错误：\n' + errorMessage;
}

// 下载结果
function downloadResult() {
    // 这里应该获取实际的输出文件路径
    alert('结果已生成。请在输出文件夹中查看。');
}

// 重置 UI
function resetUI() {
    // 重新加载页面
    location.reload();
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initEventListeners);
