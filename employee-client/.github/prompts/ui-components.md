# UI Development Prompts

## Modern Desktop Interface Design

### Device Management UI
```prompt
创建设备管理界面，包含：
1. 设备列表（1-10编号显示）
2. 连接状态指示器（绿色/红色）
3. 设备名称显示
4. 连接/断开按钮
5. 批量操作功能

HTML 结构：
```html
<div class="device-management">
    <h2>设备管理 (Device Management)</h2>
    <div class="device-list">
        <!-- 动态生成设备项 -->
    </div>
    <div class="device-actions">
        <button id="connect-all">全部连接</button>
        <button id="disconnect-all">全部断开</button>
    </div>
</div>
```

CSS 样式要求：
- 现代卡片设计
- 清晰的状态指示
- 响应式布局
```

### Task Management Interface
```prompt
设计任务管理界面：
1. 选项卡切换（通讯录管理、精准获客）
2. 平台选择下拉菜单
3. 文件上传区域
4. 任务进度显示
5. 余额和统计信息

布局结构：
```html
<div class="task-management">
    <div class="platform-selector">
        <select id="platform-select">
            <option value="xiaohongshu">小红书</option>
            <option value="douyin">抖音</option>
        </select>
    </div>

    <div class="task-tabs">
        <div class="tab active" data-tab="contacts">通讯录管理</div>
        <div class="tab" data-tab="acquisition">精准获客</div>
    </div>

    <div class="tab-content">
        <!-- 动态内容 -->
    </div>
</div>
```
```

## Interactive Components

### File Upload Component
```prompt
创建文件上传组件：
1. 拖拽上传支持
2. 文件类型验证（CSV/TXT）
3. 上传进度显示
4. 文件预览功能
5. 错误处理提示

JavaScript 实现：
```javascript
class FileUploadComponent {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.init();
    }

    init() {
        this.createUploadArea();
        this.bindEvents();
    }

    async uploadFile(file) {
        try {
            const result = await window.__TAURI__.invoke('upload_file', {
                filePath: file.path,
                fileType: file.type
            });
            this.handleSuccess(result);
        } catch (error) {
            this.handleError(error);
        }
    }
}
```
```

### Progress Display Component
```prompt
实现进度显示组件：
1. 实时进度条更新
2. 任务状态显示
3. 完成数量统计
4. 错误计数显示
5. 暂停/继续控制

HTML 结构：
```html
<div class="progress-display">
    <div class="progress-header">
        <span class="task-title">任务进行中...</span>
        <span class="progress-percentage">0%</span>
    </div>
    <div class="progress-bar">
        <div class="progress-fill" style="width: 0%"></div>
    </div>
    <div class="progress-stats">
        <span>已完成: <span id="completed">0</span></span>
        <span>总数: <span id="total">0</span></span>
        <span>失败: <span id="failed">0</span></span>
    </div>
    <div class="progress-controls">
        <button id="pause-btn">暂停</button>
        <button id="stop-btn">停止</button>
    </div>
</div>
```
```

## Responsive Layout Patterns

### Grid Layout System
```prompt
创建响应式网格布局：
```css
.app-container {
    display: grid;
    grid-template-areas:
        "sidebar main-content"
        "sidebar status-bar";
    grid-template-columns: 300px 1fr;
    grid-template-rows: 1fr auto;
    height: 100vh;
    gap: 1rem;
}

.sidebar {
    grid-area: sidebar;
    background: #f5f5f5;
    padding: 1rem;
    overflow-y: auto;
}

.main-content {
    grid-area: main-content;
    padding: 1rem;
    overflow-y: auto;
}

.status-bar {
    grid-area: status-bar;
    background: #e0e0e0;
    padding: 0.5rem 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

@media (max-width: 768px) {
    .app-container {
        grid-template-areas:
            "sidebar"
            "main-content"
            "status-bar";
        grid-template-columns: 1fr;
        grid-template-rows: auto 1fr auto;
    }
}
```
```

## Event Handling Patterns

### Tauri Integration
```prompt
实现 Tauri 前后端通信：
```javascript
class TauriService {
    // 调用 Rust 命令
    async invokeCommand(command, payload = {}) {
        try {
            const result = await window.__TAURI__.invoke(command, payload);
            return { success: true, data: result };
        } catch (error) {
            console.error(`Command ${command} failed:`, error);
            return { success: false, error: error };
        }
    }

    // 监听后端事件
    async listen(event, callback) {
        const unlisten = await window.__TAURI__.event.listen(event, callback);
        return unlisten;
    }

    // 发送事件到后端
    async emit(event, payload) {
        await window.__TAURI__.event.emit(event, payload);
    }
}

// 使用示例
const tauriService = new TauriService();

// 获取设备列表
async function getDevices() {
    const result = await tauriService.invokeCommand('get_devices');
    if (result.success) {
        updateDeviceList(result.data);
    } else {
        showError(result.error);
    }
}

// 监听设备状态变化
tauriService.listen('device-status-changed', (event) => {
    updateDeviceStatus(event.payload);
});
```
```
