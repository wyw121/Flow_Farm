// Flow Farm 员工客户端 - 客户拜访管理 JavaScript

// Tauri API 引用
const { invoke } = window.__TAURI__.core;

// 全局状态
let currentUser = null;
let activeVisit = null;
let isGpsTracking = false;
let isRecording = false;

// 页面元素引用
const loginPage = document.getElementById('login-page');
const mainPage = document.getElementById('main-page');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');

// 初始化应用
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Flow Farm 员工客户端启动');
    
    // 检查是否已登录
    try {
        const isLoggedIn = await invoke('is_logged_in');
        if (isLoggedIn) {
            await showMainPage();
        } else {
            showLoginPage();
        }
    } catch (error) {
        console.error('检查登录状态失败:', error);
        showLoginPage();
    }
    
    // 绑定事件监听器
    bindEventListeners();
});

// 显示登录页面
function showLoginPage() {
    loginPage.classList.add('active');
    mainPage.classList.remove('active');
}

// 显示主页面
async function showMainPage() {
    try {
        // 获取当前用户信息
        currentUser = await invoke('get_current_user');
        document.getElementById('current-user').textContent = currentUser.username || '用户';
        
        loginPage.classList.remove('active');
        mainPage.classList.add('active');
        
        // 初始化各个模块
        await initVisitsModule();
        await initGpsModule();
        await initMediaModule();
        
        // 开始定期更新数据
        startDataRefresh();
        
    } catch (error) {
        console.error('显示主页面失败:', error);
        showMessage('获取用户信息失败', 'error');
    }
}

// 绑定事件监听器
function bindEventListeners() {
    // 登录表单
    loginForm.addEventListener('submit', handleLogin);
    
    // 退出按钮
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    
    // 标签切换
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => switchTab(e.target.dataset.tab));
    });
    
    // GPS 控制按钮
    document.getElementById('request-permission-btn').addEventListener('click', requestGpsPermission);
    document.getElementById('start-tracking-btn').addEventListener('click', startGpsTracking);
    document.getElementById('stop-tracking-btn').addEventListener('click', stopGpsTracking);
    document.getElementById('get-location-btn').addEventListener('click', getCurrentLocation);
    
    // 多媒体控制按钮
    document.getElementById('take-photo-btn').addEventListener('click', takePhoto);
    document.getElementById('start-audio-btn').addEventListener('click', startAudioRecording);
    document.getElementById('stop-audio-btn').addEventListener('click', stopAudioRecording);
    document.getElementById('start-video-btn').addEventListener('click', startVideoRecording);
    document.getElementById('stop-video-btn').addEventListener('click', stopVideoRecording);
    
    // 拜访控制按钮
    document.getElementById('start-visit-btn').addEventListener('click', startSelectedVisit);
    document.getElementById('end-visit-btn').addEventListener('click', endCurrentVisit);
    document.getElementById('cancel-visit-btn').addEventListener('click', cancelCurrentVisit);
    
    // 模态框关闭
    document.querySelector('.close').addEventListener('click', closeModal);
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('visit-modal');
        if (e.target === modal) {
            closeModal();
        }
    });
}

// 处理登录
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        await invoke('login', { username, password });
        await showMainPage();
        showMessage('登录成功', 'success');
    } catch (error) {
        console.error('登录失败:', error);
        loginError.textContent = '登录失败: ' + error;
        loginError.style.display = 'block';
    }
}

// 处理退出
async function handleLogout() {
    try {
        await invoke('logout');
        currentUser = null;
        activeVisit = null;
        showLoginPage();
        showMessage('已退出登录', 'info');
    } catch (error) {
        console.error('退出失败:', error);
        showMessage('退出失败', 'error');
    }
}

// 切换标签
function switchTab(tabName) {
    // 更新标签按钮状态
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // 更新标签内容
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

// ============= 拜访管理模块 =============

// 初始化拜访模块
async function initVisitsModule() {
    await loadTodayVisits();
    await checkActiveVisit();
}

// 加载今日拜访
async function loadTodayVisits() {
    try {
        const visits = await invoke('get_today_visits');
        displayVisits(visits);
        updateVisitsStats(visits);
    } catch (error) {
        console.error('加载拜访数据失败:', error);
        showMessage('加载拜访数据失败', 'error');
    }
}

// 显示拜访列表
function displayVisits(visits) {
    const visitsList = document.getElementById('visits-list');
    visitsList.innerHTML = '';
    
    visits.forEach(visit => {
        const visitItem = document.createElement('div');
        visitItem.className = `visit-item ${visit.status}`;
        visitItem.innerHTML = `
            <div class="visit-customer">
                <strong>${visit.customer_name}</strong>
            </div>
            <div class="visit-address">${visit.customer_address}</div>
            <div class="visit-time">
                计划时间: ${formatDateTime(visit.planned_start_time)}
                ${visit.actual_start_time ? `<br>开始时间: ${formatDateTime(visit.actual_start_time)}` : ''}
                ${visit.actual_end_time ? `<br>结束时间: ${formatDateTime(visit.actual_end_time)}` : ''}
            </div>
        `;
        
        visitItem.addEventListener('click', () => showVisitDetails(visit));
        visitsList.appendChild(visitItem);
    });
}

// 更新拜访统计
function updateVisitsStats(visits) {
    const planned = visits.length;
    const completed = visits.filter(v => v.status === 'completed').length;
    const active = visits.filter(v => v.status === 'active').length;
    
    document.getElementById('planned-visits').textContent = planned;
    document.getElementById('completed-visits').textContent = completed;
    document.getElementById('active-visits').textContent = active;
}

// 检查活动拜访
async function checkActiveVisit() {
    try {
        activeVisit = await invoke('get_active_visit');
        if (activeVisit) {
            showActiveVisit(activeVisit);
        } else {
            hideActiveVisit();
        }
    } catch (error) {
        console.error('检查活动拜访失败:', error);
        hideActiveVisit();
    }
}

// 显示活动拜访
function showActiveVisit(visit) {
    const activeVisitDiv = document.getElementById('active-visit');
    document.getElementById('active-customer-name').textContent = visit.customer_name;
    document.getElementById('active-customer-address').textContent = visit.customer_address;
    document.getElementById('active-visit-start').textContent = formatTime(visit.actual_start_time);
    activeVisitDiv.style.display = 'block';
}

// 隐藏活动拜访
function hideActiveVisit() {
    document.getElementById('active-visit').style.display = 'none';
}

// 显示拜访详情
function showVisitDetails(visit) {
    const modal = document.getElementById('visit-modal');
    const details = document.getElementById('visit-details');
    
    details.innerHTML = `
        <div class="visit-detail-item">
            <strong>客户名称:</strong> ${visit.customer_name}
        </div>
        <div class="visit-detail-item">
            <strong>客户地址:</strong> ${visit.customer_address}
        </div>
        <div class="visit-detail-item">
            <strong>联系电话:</strong> ${visit.customer_phone || '未提供'}
        </div>
        <div class="visit-detail-item">
            <strong>计划时间:</strong> ${formatDateTime(visit.planned_start_time)}
        </div>
        <div class="visit-detail-item">
            <strong>拜访状态:</strong> ${getStatusText(visit.status)}
        </div>
        <div class="visit-detail-item">
            <strong>拜访目的:</strong> ${visit.purpose || '常规拜访'}
        </div>
    `;
    
    // 设置选中的拜访
    window.selectedVisit = visit;
    
    // 控制开始拜访按钮
    const startBtn = document.getElementById('start-visit-btn');
    startBtn.style.display = visit.status === 'pending' ? 'inline-block' : 'none';
    
    modal.style.display = 'block';
}

// 开始选中的拜访
async function startSelectedVisit() {
    if (!window.selectedVisit) return;
    
    try {
        await invoke('start_visit', { 
            visitId: window.selectedVisit.id,
            latitude: 0.0,  // 实际应用中从GPS获取
            longitude: 0.0
        });
        
        showMessage('拜访已开始', 'success');
        closeModal();
        await initVisitsModule(); // 刷新拜访数据
    } catch (error) {
        console.error('开始拜访失败:', error);
        showMessage('开始拜访失败: ' + error, 'error');
    }
}

// 结束当前拜访
async function endCurrentVisit() {
    if (!activeVisit) return;
    
    try {
        await invoke('end_visit', { 
            visitId: activeVisit.id,
            latitude: 0.0,  // 实际应用中从GPS获取
            longitude: 0.0
        });
        
        showMessage('拜访已结束', 'success');
        await initVisitsModule(); // 刷新拜访数据
    } catch (error) {
        console.error('结束拜访失败:', error);
        showMessage('结束拜访失败: ' + error, 'error');
    }
}

// 取消当前拜访
async function cancelCurrentVisit() {
    if (!activeVisit) return;
    
    try {
        await invoke('cancel_visit', { visitId: activeVisit.id });
        showMessage('拜访已取消', 'info');
        await initVisitsModule(); // 刷新拜访数据
    } catch (error) {
        console.error('取消拜访失败:', error);
        showMessage('取消拜访失败: ' + error, 'error');
    }
}

// ============= GPS模块 =============

// 初始化GPS模块
async function initGpsModule() {
    await updateGpsStatus();
}

// 更新GPS状态
async function updateGpsStatus() {
    try {
        const status = await invoke('get_gps_status');
        
        document.getElementById('gps-status').textContent = status.is_tracking ? '正在定位' : '未启动';
        document.getElementById('gps-permission').textContent = status.permissions_granted ? '已授权' : '未授权';
        
        if (status.current_location) {
            document.getElementById('current-latitude').textContent = status.current_location.latitude.toFixed(6);
            document.getElementById('current-longitude').textContent = status.current_location.longitude.toFixed(6);
            document.getElementById('location-timestamp').textContent = formatDateTime(status.current_location.timestamp);
            document.getElementById('gps-accuracy').textContent = status.current_location.accuracy + 'm';
        }
        
        isGpsTracking = status.is_tracking;
        updateGpsButtons();
        
    } catch (error) {
        console.error('更新GPS状态失败:', error);
    }
}

// 更新GPS按钮状态
function updateGpsButtons() {
    document.getElementById('start-tracking-btn').disabled = isGpsTracking;
    document.getElementById('stop-tracking-btn').disabled = !isGpsTracking;
}

// 请求GPS权限
async function requestGpsPermission() {
    try {
        await invoke('request_gps_permission');
        showMessage('GPS权限已授权', 'success');
        await updateGpsStatus();
    } catch (error) {
        console.error('GPS权限请求失败:', error);
        showMessage('GPS权限请求失败: ' + error, 'error');
    }
}

// 开始GPS跟踪
async function startGpsTracking() {
    try {
        await invoke('start_gps_tracking');
        showMessage('GPS定位已开始', 'success');
        await updateGpsStatus();
    } catch (error) {
        console.error('开始GPS跟踪失败:', error);
        showMessage('开始GPS跟踪失败: ' + error, 'error');
    }
}

// 停止GPS跟踪
async function stopGpsTracking() {
    try {
        await invoke('stop_gps_tracking');
        showMessage('GPS定位已停止', 'info');
        await updateGpsStatus();
    } catch (error) {
        console.error('停止GPS跟踪失败:', error);
        showMessage('停止GPS跟踪失败: ' + error, 'error');
    }
}

// 获取当前位置
async function getCurrentLocation() {
    try {
        const location = await invoke('get_current_location');
        document.getElementById('current-latitude').textContent = location.latitude.toFixed(6);
        document.getElementById('current-longitude').textContent = location.longitude.toFixed(6);
        document.getElementById('location-timestamp').textContent = formatDateTime(location.timestamp);
        document.getElementById('gps-accuracy').textContent = location.accuracy + 'm';
        showMessage('位置已更新', 'success');
    } catch (error) {
        console.error('获取位置失败:', error);
        showMessage('获取位置失败: ' + error, 'error');
    }
}

// ============= 多媒体模块 =============

// 初始化多媒体模块
async function initMediaModule() {
    await updateRecordingStatus();
}

// 更新录制状态
async function updateRecordingStatus() {
    try {
        const status = await invoke('get_recording_status');
        const statusText = document.getElementById('recording-status-text');
        const indicator = document.getElementById('recording-indicator');
        
        if (status === 'Recording') {
            statusText.textContent = '录制中';
            indicator.classList.add('recording');
            isRecording = true;
        } else {
            statusText.textContent = '就绪';
            indicator.classList.remove('recording');
            isRecording = false;
        }
        
        updateMediaButtons();
        
    } catch (error) {
        console.error('更新录制状态失败:', error);
    }
}

// 更新多媒体按钮状态
function updateMediaButtons() {
    document.getElementById('start-audio-btn').disabled = isRecording;
    document.getElementById('stop-audio-btn').disabled = !isRecording;
    document.getElementById('start-video-btn').disabled = isRecording;
    document.getElementById('stop-video-btn').disabled = !isRecording;
    document.getElementById('take-photo-btn').disabled = isRecording;
}

// 拍照
async function takePhoto() {
    try {
        const photo = await invoke('take_photo', { 
            visitId: activeVisit ? activeVisit.id : null 
        });
        showMessage('照片已保存: ' + photo.file_name, 'success');
        // 这里可以添加上传到服务器的逻辑
    } catch (error) {
        console.error('拍照失败:', error);
        showMessage('拍照失败: ' + error, 'error');
    }
}

// 开始录音
async function startAudioRecording() {
    try {
        await invoke('start_audio_recording', { 
            visitId: activeVisit ? activeVisit.id : null 
        });
        showMessage('录音已开始', 'success');
        await updateRecordingStatus();
    } catch (error) {
        console.error('开始录音失败:', error);
        showMessage('开始录音失败: ' + error, 'error');
    }
}

// 停止录音
async function stopAudioRecording() {
    try {
        const audio = await invoke('stop_audio_recording');
        showMessage('录音已保存: ' + audio.file_name, 'success');
        await updateRecordingStatus();
    } catch (error) {
        console.error('停止录音失败:', error);
        showMessage('停止录音失败: ' + error, 'error');
    }
}

// 开始录像
async function startVideoRecording() {
    try {
        await invoke('start_video_recording', { 
            visitId: activeVisit ? activeVisit.id : null 
        });
        showMessage('录像已开始', 'success');
        await updateRecordingStatus();
    } catch (error) {
        console.error('开始录像失败:', error);
        showMessage('开始录像失败: ' + error, 'error');
    }
}

// 停止录像
async function stopVideoRecording() {
    try {
        const video = await invoke('stop_video_recording');
        showMessage('录像已保存: ' + video.file_name, 'success');
        await updateRecordingStatus();
    } catch (error) {
        console.error('停止录像失败:', error);
        showMessage('停止录像失败: ' + error, 'error');
    }
}

// ============= 工具函数 =============

// 关闭模态框
function closeModal() {
    document.getElementById('visit-modal').style.display = 'none';
}

// 显示消息
function showMessage(text, type = 'info') {
    const container = document.getElementById('message-container');
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.textContent = text;
    
    container.appendChild(message);
    
    // 3秒后自动删除
    setTimeout(() => {
        if (message.parentNode) {
            message.parentNode.removeChild(message);
        }
    }, 3000);
}

// 格式化日期时间
function formatDateTime(dateString) {
    if (!dateString) return '--';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 格式化时间
function formatTime(dateString) {
    if (!dateString) return '--:--';
    const date = new Date(dateString);
    return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 获取状态文本
function getStatusText(status) {
    const statusMap = {
        'pending': '待开始',
        'active': '进行中',
        'completed': '已完成',
        'cancelled': '已取消'
    };
    return statusMap[status] || status;
}

// 开始数据刷新
function startDataRefresh() {
    // 每30秒刷新拜访数据
    setInterval(async () => {
        if (currentUser) {
            await initVisitsModule();
        }
    }, 30000);
    
    // 每5秒刷新GPS状态
    setInterval(async () => {
        if (currentUser) {
            await updateGpsStatus();
        }
    }, 5000);
    
    // 每2秒刷新录制状态
    setInterval(async () => {
        if (currentUser) {
            await updateRecordingStatus();
        }
    }, 2000);
}

// 导出到全局作用域供HTML调用
window.closeModal = closeModal;