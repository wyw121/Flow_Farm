// Flow Farm 员工客户端 - 主应用逻辑
// 使用 Tauri API 与 Rust 后端通信

const { invoke } = window.__TAURI__.core;

// ==================== 应用状态管理 ====================
const AppState = {
  currentUser: null,
  currentView: 'dashboard',
  devices: [],
  tasks: [],
  statistics: {
    connectedDevices: 0,
    todayTasks: 0,
    totalFollows: 0,
    accountBalance: 0
  }
};

// ==================== 初始化应用 ====================
document.addEventListener('DOMContentLoaded', async () => {
  console.log('Flow Farm 员工客户端启动...');
  
  // 检查登录状态
  const isLoggedIn = await checkLoginStatus();
  
  if (isLoggedIn) {
    showAppPage();
    await loadDashboard();
  } else {
    showLoginPage();
  }
  
  // 绑定事件监听器
  bindEventListeners();
});

// ==================== 页面切换 ====================
function showLoginPage() {
  document.getElementById('login-page').classList.add('active');
  document.getElementById('app-page').classList.remove('active');
}

function showAppPage() {
  document.getElementById('login-page').classList.remove('active');
  document.getElementById('app-page').classList.add('active');
}

// ==================== 认证功能 ====================
async function checkLoginStatus() {
  try {
    const loggedIn = await invoke('is_logged_in');
    if (loggedIn) {
      AppState.currentUser = await invoke('get_current_user');
      if (AppState.currentUser) {
        updateUserInfo();
      }
    }
    return loggedIn;
  } catch (error) {
    console.error('检查登录状态失败:', error);
    return false;
  }
}

async function login(username, password) {
  try {
    const session = await invoke('login', { username, password });
    AppState.currentUser = session.user;
    return { success: true };
  } catch (error) {
    console.error('登录失败:', error);
    return { success: false, error: error.toString() };
  }
}

async function logout() {
  try {
    await invoke('logout');
    AppState.currentUser = null;
    showLoginPage();
  } catch (error) {
    console.error('退出登录失败:', error);
  }
}

function updateUserInfo() {
  if (AppState.currentUser) {
    document.getElementById('user-info').textContent = 
      `欢迎, ${AppState.currentUser.username}`;
  }
}

// ==================== 事件监听器 ====================
function bindEventListeners() {
  // 登录表单
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', handleLogin);
  }
  
  // 退出登录
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }
  
  // 侧边栏菜单
  const menuItems = document.querySelectorAll('.menu-item');
  menuItems.forEach(item => {
    item.addEventListener('click', () => {
      const page = item.getAttribute('data-page');
      switchView(page);
    });
  });
  
  // 设备管理按钮
  const scanDevicesBtn = document.getElementById('scan-devices-btn');
  if (scanDevicesBtn) {
    scanDevicesBtn.addEventListener('click', scanDevices);
  }
  
  const refreshDevicesBtn = document.getElementById('refresh-devices-btn');
  if (refreshDevicesBtn) {
    refreshDevicesBtn.addEventListener('click', loadDevices);
  }
  
  // 任务标签
  const taskTabs = document.querySelectorAll('.tab-btn');
  taskTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      switchTaskTab(tab.getAttribute('data-tab'));
    });
  });
}

async function handleLogin(event) {
  event.preventDefault();
  
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const errorDiv = document.getElementById('login-error');
  
  const result = await login(username, password);
  
  if (result.success) {
    errorDiv.classList.remove('show');
    showAppPage();
    await loadDashboard();
  } else {
    errorDiv.textContent = result.error || '登录失败，请检查用户名和密码';
    errorDiv.classList.add('show');
  }
}

// ==================== 视图切换 ====================
function switchView(viewName) {
  // 更新侧边栏激活状态
  document.querySelectorAll('.menu-item').forEach(item => {
    item.classList.remove('active');
    if (item.getAttribute('data-page') === viewName) {
      item.classList.add('active');
    }
  });
  
  // 更新内容视图
  document.querySelectorAll('.content-view').forEach(view => {
    view.classList.remove('active');
  });
  
  const targetView = document.getElementById(`${viewName}-view`);
  if (targetView) {
    targetView.classList.add('active');
    AppState.currentView = viewName;
    
    // 加载对应视图的数据
    loadViewData(viewName);
  }
}

async function loadViewData(viewName) {
  switch (viewName) {
    case 'dashboard':
      await loadDashboard();
      break;
    case 'devices':
      await loadDevices();
      break;
    case 'tasks':
      await loadTasks();
      break;
    case 'statistics':
      await loadStatistics();
      break;
    default:
      console.log(`加载 ${viewName} 视图数据`);
  }
}

// ==================== 工作台数据加载 ====================
async function loadDashboard() {
  try {
    // 加载设备数量
    const devices = await invoke('get_devices');
    AppState.devices = devices;
    const connectedCount = devices.filter(d => d.status === 'connected').length;
    document.getElementById('connected-devices').textContent = connectedCount;
    
    // 加载任务数量
    const tasks = await invoke('get_tasks');
    AppState.tasks = tasks;
    const todayTasks = tasks.filter(t => isToday(t.created_at)).length;
    document.getElementById('today-tasks').textContent = todayTasks;
    
    // 加载统计数据
    const stats = await invoke('get_statistics');
    document.getElementById('total-follows').textContent = stats.total_follows || 0;
    document.getElementById('account-balance').textContent = `¥${(stats.balance || 0).toFixed(2)}`;
    
    AppState.statistics = {
      connectedDevices: connectedCount,
      todayTasks,
      totalFollows: stats.total_follows || 0,
      accountBalance: stats.balance || 0
    };
  } catch (error) {
    console.error('加载工作台数据失败:', error);
  }
}

// ==================== 设备管理 ====================
async function scanDevices() {
  try {
    console.log('扫描设备中...');
    const devices = await invoke('scan_adb_devices');
    AppState.devices = devices;
    renderDevices(devices);
  } catch (error) {
    console.error('扫描设备失败:', error);
    alert('扫描设备失败: ' + error);
  }
}

async function loadDevices() {
  try {
    const devices = await invoke('get_devices');
    AppState.devices = devices;
    renderDevices(devices);
  } catch (error) {
    console.error('加载设备失败:', error);
  }
}

function renderDevices(devices) {
  const devicesGrid = document.getElementById('devices-list');
  if (!devicesGrid) return;
  
  if (devices.length === 0) {
    devicesGrid.innerHTML = '<p class="placeholder">暂无设备，请点击"扫描设备"</p>';
    return;
  }
  
  devicesGrid.innerHTML = devices.map((device, index) => `
    <div class="device-card ${device.status}">
      <div class="device-header">
        <span class="device-name">设备 ${index + 1}: ${device.name || device.id}</span>
        <span class="device-status ${device.status}">${device.status === 'connected' ? '已连接' : '未连接'}</span>
      </div>
      <div class="device-info">ID: ${device.id}</div>
      <div class="device-info">型号: ${device.model || '未知'}</div>
      <div class="device-actions">
        ${device.status === 'connected' 
          ? `<button class="btn-danger" onclick="disconnectDevice('${device.id}')">断开连接</button>`
          : `<button class="btn-primary" onclick="connectDevice('${device.id}')">连接</button>`
        }
      </div>
    </div>
  `).join('');
}

async function connectDevice(deviceId) {
  try {
    await invoke('connect_device', { deviceId });
    await loadDevices();
  } catch (error) {
    console.error('连接设备失败:', error);
    alert('连接设备失败: ' + error);
  }
}

async function disconnectDevice(deviceId) {
  try {
    await invoke('disconnect_device', { deviceId });
    await loadDevices();
  } catch (error) {
    console.error('断开设备失败:', error);
  }
}

// ==================== 任务管理 ====================
function switchTaskTab(tabName) {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.getAttribute('data-tab') === tabName) {
      btn.classList.add('active');
    }
  });
  
  renderTaskContent(tabName);
}

function renderTaskContent(tabName) {
  const taskContent = document.getElementById('task-content');
  
  if (tabName === 'contact') {
    taskContent.innerHTML = `
      <h4>通讯录导入</h4>
      <div class="form-group">
        <label>上传通讯录文件 (CSV/TXT)</label>
        <input type="file" id="contact-file" accept=".csv,.txt">
      </div>
      <button class="btn-primary" onclick="uploadContactFile()">导入并开始任务</button>
    `;
  } else if (tabName === 'monitor') {
    taskContent.innerHTML = `
      <h4>精准获客 (同行监控)</h4>
      <div class="form-group">
        <label>监控账号</label>
        <input type="text" id="monitor-account" placeholder="输入同行账号ID">
      </div>
      <div class="form-group">
        <label>关键词</label>
        <textarea id="monitor-keywords" rows="4" placeholder="输入关键词，每行一个"></textarea>
      </div>
      <button class="btn-primary" onclick="startMonitorTask()">开始监控</button>
    `;
  }
}

async function loadTasks() {
  try {
    const tasks = await invoke('get_tasks');
    AppState.tasks = tasks;
    renderTaskContent('contact');
  } catch (error) {
    console.error('加载任务失败:', error);
  }
}

async function loadStatistics() {
  try {
    const stats = await invoke('get_statistics');
    const statsContent = document.getElementById('statistics-content');
    statsContent.innerHTML = `
      <div class="dashboard-cards">
        <div class="stat-card">
          <h4>总关注数</h4>
          <p class="stat-value">${stats.total_follows || 0}</p>
        </div>
        <div class="stat-card">
          <h4>今日关注</h4>
          <p class="stat-value">${stats.today_follows || 0}</p>
        </div>
        <div class="stat-card">
          <h4>账户余额</h4>
          <p class="stat-value">¥${(stats.balance || 0).toFixed(2)}</p>
        </div>
        <div class="stat-card">
          <h4>任务完成率</h4>
          <p class="stat-value">${stats.completion_rate || 0}%</p>
        </div>
      </div>
    `;
  } catch (error) {
    console.error('加载统计数据失败:', error);
  }
}

// ==================== 工具函数 ====================
function isToday(dateString) {
  const date = new Date(dateString);
  const today = new Date();
  return date.toDateString() === today.toDateString();
}

// 全局暴露函数供HTML调用
window.connectDevice = connectDevice;
window.disconnectDevice = disconnectDevice;
window.uploadContactFile = async function() {
  alert('通讯录导入功能开发中...');
};
window.startMonitorTask = async function() {
  alert('精准获客功能开发中...');
};

console.log('Flow Farm 员工客户端初始化完成');
