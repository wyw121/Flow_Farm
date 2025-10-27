# Flow Farm 员工客户端 - 架构文档

## 架构概述

**技术栈**: Rust + Tauri 2.0 + 纯 Web 前端 (HTML/CSS/JavaScript)

### 核心设计原则

1. **前后端分离**: Rust后端处理所有业务逻辑，Web前端仅负责UI渲染和用户交互
2. **单一真理源**: 所有Rust代码集中在 `src-tauri/src/`，避免代码重复
3. **原生性能**: 利用Tauri的原生窗口系统，避免使用重量级Web框架
4. **安全通信**: 通过Tauri的`invoke`机制进行前后端通信

---

## 项目结构

```
employee-client/
├── src-tauri/                  # Rust 后端 (唯一的Rust代码位置)
│   ├── src/
│   │   ├── main.rs            # 应用入口，Tauri命令注册
│   │   ├── models.rs          # 数据模型
│   │   ├── device.rs          # 设备管理 (ADB)
│   │   ├── api.rs             # 服务器API通信
│   │   ├── auth_service.rs    # 认证服务
│   │   ├── contact_manager.rs # 通讯录管理
│   │   ├── xiaohongshu_automator.rs # 小红书自动化
│   │   └── adb_manager.rs     # ADB管理器
│   ├── Cargo.toml             # Rust依赖
│   ├── tauri.conf.json        # Tauri配置
│   └── build.rs               # 构建脚本
│
├── src-web/                    # Web 前端 (纯HTML/CSS/JS)
│   ├── index.html             # 主HTML文件
│   ├── app.js                 # 应用逻辑和Tauri通信
│   ├── styles.css             # 全局样式
│   └── device-styles.css      # 设备管理样式
│
├── public/                     # 静态资源
├── Cargo.toml                 # 工作空间配置 (如果为空则删除)
├── README.md                  # 项目说明
└── ARCHITECTURE.md            # 本文档
```

### ⚠️ 重要规则

- **禁止在 `src/` 目录创建Rust文件** - 已删除，不再使用
- **所有Rust代码必须在 `src-tauri/src/`** - 唯一的后端代码位置
- **Web前端仅使用HTML/CSS/JS** - 不引入React/Vue等框架
- **前端文件统一放在 `src-web/`** - 避免目录混乱

---

## 架构层次

### 1. Rust 后端层 (`src-tauri/src/`)

**职责**:
- 业务逻辑处理 (设备管理、任务调度、数据处理)
- ADB设备控制和自动化
- 服务器API通信 (HTTP请求)
- 本地数据持久化 (SQLite)
- 认证和会话管理

**关键模块**:

#### `main.rs` - 应用入口
```rust
#[tauri::command]
async fn login(username: String, password: String, state: State<'_, AppState>) 
    -> Result<UserSession, String>

#[tauri::command]
async fn scan_adb_devices(state: State<'_, AppState>) 
    -> Result<Vec<AdbDevice>, String>

#[tauri::command]
async fn get_devices(state: State<'_, AppState>) 
    -> Result<Vec<DeviceInfo>, String>
```

#### `device.rs` / `adb_manager.rs` - 设备管理
- ADB设备扫描和连接
- 设备状态监控
- 任务分配到设备 (最多10台)

#### `auth_service.rs` - 认证服务
- 用户登录/登出
- Token验证
- 会话管理

#### `contact_manager.rs` - 通讯录管理
- CSV/TXT文件解析
- 联系人导入
- 任务创建

#### `xiaohongshu_automator.rs` - 小红书自动化
- UI自动化操作
- 关注用户
- 数据爬取

#### `api.rs` - 服务器通信
- HTTP客户端封装
- API请求和响应处理
- 错误处理

### 2. Web 前端层 (`src-web/`)

**职责**:
- UI渲染和用户交互
- 调用Rust后端的Tauri命令
- 状态显示和更新

**文件说明**:

#### `index.html` - 主UI结构
包含所有页面和组件:
- 登录页面
- 主应用 (导航栏、侧边栏、内容区)
- 工作台、设备管理、任务中心、统计数据等视图

#### `app.js` - 应用逻辑
```javascript
const { invoke } = window.__TAURI__.core;

// 调用Rust命令
const devices = await invoke('scan_adb_devices');
const session = await invoke('login', { username, password });
```

核心功能:
- 应用初始化和状态管理
- 事件监听和处理
- Tauri命令调用
- UI更新逻辑

#### `styles.css` - 全局样式
- 布局样式 (页面、导航、侧边栏)
- 组件样式 (按钮、卡片、表单)
- 响应式设计

---

## 前后端通信机制

### Tauri Command 模式

**前端调用**:
```javascript
// app.js
const result = await invoke('command_name', { param1: value1, param2: value2 });
```

**后端定义**:
```rust
// main.rs
#[tauri::command]
async fn command_name(param1: String, param2: i32, state: State<'_, AppState>) 
    -> Result<ReturnType, String> {
    // 业务逻辑
    Ok(result)
}
```

### 已实现的 Tauri 命令

| 命令名称              | 参数                          | 返回类型                | 功能描述         |
| --------------------- | ----------------------------- | ----------------------- | ---------------- |
| `login`               | `username`, `password`        | `UserSession`           | 用户登录         |
| `logout`              | -                             | `()`                    | 退出登录         |
| `is_logged_in`        | -                             | `bool`                  | 检查登录状态     |
| `get_current_user`    | -                             | `Option<UserInfo>`      | 获取当前用户信息 |
| `scan_adb_devices`    | -                             | `Vec<AdbDevice>`        | 扫描ADB设备      |
| `get_devices`         | -                             | `Vec<DeviceInfo>`       | 获取设备列表     |
| `connect_device`      | `deviceId`                    | `()`                    | 连接设备         |
| `disconnect_device`   | `deviceId`                    | `()`                    | 断开设备         |
| `get_tasks`           | -                             | `Vec<TaskInfo>`         | 获取任务列表     |
| `get_statistics`      | -                             | `Statistics`            | 获取统计数据     |
| `upload_contacts`     | `filePath`, `platform`        | `TaskInfo`              | 上传通讯录       |
| `start_monitor_task`  | `account`, `keywords`         | `TaskInfo`              | 开始监控任务     |

---

## 开发工作流

### 1. 添加新功能

**后端 (Rust)**:
1. 在 `src-tauri/src/` 中创建或编辑模块
2. 定义 `#[tauri::command]` 函数
3. 在 `main.rs` 中注册命令:
   ```rust
   tauri::Builder::default()
       .invoke_handler(tauri::generate_handler![
           login, logout, scan_adb_devices, new_command
       ])
   ```

**前端 (JavaScript)**:
1. 在 `src-web/app.js` 中添加调用函数:
   ```javascript
   async function newFeature() {
       const result = await invoke('new_command', { param: value });
       // 更新UI
   }
   ```
2. 在 `src-web/index.html` 中添加UI元素
3. 在 `src-web/styles.css` 中添加样式

### 2. 构建和测试

**开发模式** (带热重载):
```bash
cd employee-client
cargo tauri dev
```

**生产构建**:
```bash
cargo tauri build
```

**代码检查**:
```bash
cargo check
cargo clippy --all-targets --all-features
cargo fmt
```

### 3. 调试

- **后端日志**: 使用 `tracing` crate，日志输出到控制台
- **前端调试**: 打开开发者工具 (Ctrl+Shift+I)，查看Console

---

## API 调用规范

### 服务器API地址

- **开发环境**: `http://localhost:8000`
- **生产环境**: 配置在 `tauri.conf.json` 或应用设置中

### API 通信流程

1. 前端用户操作 → `app.js` 调用 `invoke()`
2. Tauri命令 → Rust后端处理
3. Rust后端 → `api.rs` 发送HTTP请求到服务器
4. 服务器响应 → Rust处理结果
5. Rust返回数据 → 前端更新UI

### 错误处理

```javascript
// 前端
try {
    const result = await invoke('some_command', { param: value });
    // 成功处理
} catch (error) {
    console.error('操作失败:', error);
    alert('操作失败: ' + error);
}
```

```rust
// 后端
#[tauri::command]
async fn some_command(param: String) -> Result<Data, String> {
    match perform_operation(param).await {
        Ok(data) => Ok(data),
        Err(e) => {
            tracing::error!("操作失败: {}", e);
            Err(format!("操作失败: {}", e))
        }
    }
}
```

---

## 性能优化建议

1. **减少前后端通信**: 批量操作而非频繁单次调用
2. **异步处理**: 使用 `async/await` 避免阻塞UI
3. **状态缓存**: 在AppState中缓存常用数据
4. **懒加载**: 按需加载视图数据

---

## 安全考虑

1. **API访问控制**: 在 `tauri.conf.json` 中限制HTTP访问域名
2. **Token管理**: 敏感Token存储在Rust后端，不暴露给前端
3. **输入验证**: 前后端都进行数据验证
4. **ADB安全**: 仅连接授权的设备

---

## 常见问题

### Q: 为什么不使用React/Vue?
A: Tauri强调轻量化，纯HTML/CSS/JS足以满足需求，避免引入额外复杂度和打包体积。

### Q: 如何在前端访问Tauri API?
A: 使用 `window.__TAURI__.core.invoke()` 调用Rust命令。

### Q: 设备管理如何实现?
A: 通过 `adb_manager.rs` 调用ADB命令，Rust后端负责设备状态跟踪。

### Q: 数据如何持久化?
A: 使用SQLite数据库，通过 `sqlx` crate进行类型安全操作。

---

## 下一步计划

- [ ] 完善设备自动化功能
- [ ] 实现通讯录导入和任务分配
- [ ] 集成小红书/抖音自动化脚本
- [ ] 添加实时进度显示
- [ ] 优化UI/UX设计

---

## 参考资料

- [Tauri 2.0 官方文档](https://tauri.app/v2/)
- [Tauri Commands 指南](https://tauri.app/v2/develop/calling-rust/)
- [Rust async/await 教程](https://rust-lang.github.io/async-book/)

---

**文档版本**: v1.0  
**最后更新**: 2025年10月27日  
**维护者**: Flow Farm Team
