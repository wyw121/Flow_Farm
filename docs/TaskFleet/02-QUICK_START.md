# TaskFleet - 快速启动指南

**目的**: 帮助你在 30 分钟内从 Flow_Farm 创建 TaskFleet 新项目

**创建日期**: 2025年10月28日

---

## 🎯 第一步: 创建新项目 (5分钟)

### 1. 创建 GitHub 仓库

```bash
# 在 GitHub 上创建新仓库
# 仓库名: TaskFleet
# 描述: 专注任务执行的开源项目管理系统
# 公开仓库,添加 MIT License
```

### 2. 克隆 Flow_Farm 并清理

```bash
# 克隆 Flow_Farm 到新目录
cd d:/repositories
git clone https://github.com/wyw121/Flow_Farm.git TaskFleet
cd TaskFleet

# 删除 .git 目录
Remove-Item -Recurse -Force .git

# 初始化新的 Git 仓库
git init
git remote add origin https://github.com/wyw121/TaskFleet.git
```

### 3. 清理不需要的模块

```bash
# 删除不需要的目录
Remove-Item -Recurse -Force adb_xml_reader
Remove-Item -Recurse -Force employee-client  # 稍后重新创建简化版
Remove-Item -Recurse -Force deploy
Remove-Item -Recurse -Force scripts

# 保留目录
# - server-backend (重命名为 backend)
# - server-frontend (重命名为 frontend)
# - docs
```

---

## 🔧 第二步: 重构后端 (10分钟)

### 1. 重命名和清理

```bash
# 重命名目录
Rename-Item server-backend backend
cd backend

# 更新 Cargo.toml
```

**backend/Cargo.toml**:
```toml
[package]
name = "taskfleet-backend"
version = "0.1.0"
edition = "2021"

# 保留核心依赖
[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
sqlx = { version = "0.7", features = ["runtime-tokio-native-tls", "postgres", "uuid", "chrono"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
jsonwebtoken = "9.2"
uuid = { version = "1.6", features = ["serde", "v4"] }
chrono = { version = "0.4", features = ["serde"] }
# ... 其他必要依赖
```

### 2. 清理数据模型

**需要保留的模型**:
- `models/user.rs` - 用户模型
- `models/project.rs` - 项目模型 (新建)
- `models/task.rs` - 任务模型 (新建)

**需要删除的模型**:
- 所有与"用户管理员"相关的代码
- 所有与"设备管理"相关的代码
- 所有与"平台自动化"相关的代码
- 所有与"余额/计费"相关的代码

### 3. 简化权限系统

**src/models/user.rs**:
```rust
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "user_role", rename_all = "lowercase")]
pub enum UserRole {
    Manager,   // 项目经理
    Employee,  // 员工
}

// 删除: SystemAdmin, UserAdmin 等
```

### 4. 创建核心表结构

**migrations/001_init.sql**:
```sql
-- 用户表 (简化)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 项目表
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 项目成员表
CREATE TABLE project_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, user_id)
);

-- 任务表
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    assigned_to UUID REFERENCES users(id),
    created_by UUID NOT NULL REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'todo',
    priority VARCHAR(20) DEFAULT 'medium',
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
```

---

## 🎨 第三步: 重构前端 (10分钟)

### 1. 重命名和清理

```bash
cd ..
Rename-Item server-frontend frontend
cd frontend

# 更新 package.json
```

**frontend/package.json**:
```json
{
  "name": "taskfleet-frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "antd": "^5.12.0",
    "@ant-design/icons": "^5.2.6",
    "axios": "^1.6.0",
    "zustand": "^4.4.7",
    "echarts": "^5.4.3",
    "echarts-for-react": "^3.0.2",
    "dayjs": "^1.11.10"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.8"
  }
}
```

### 2. 删除不需要的页面

**需要删除**:
- 所有系统管理员相关页面
- 所有设备管理页面
- 所有计费相关页面

**需要保留和新建**:
- `pages/Login.tsx` - 登录页 (简化)
- `pages/Dashboard.tsx` - 仪表盘 (新建)
- `pages/Projects.tsx` - 项目列表 (新建)
- `pages/Tasks.tsx` - 任务管理 (新建)
- `pages/Statistics.tsx` - 统计报表 (新建)

### 3. 简化路由

**src/App.tsx**:
```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Projects } from './pages/Projects';
import { Tasks } from './pages/Tasks';
import { Statistics } from './pages/Statistics';
import { ProtectedRoute } from './components/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/statistics" element={<Statistics />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

---

## 💻 第四步: 创建桌面客户端 (5分钟)

### 1. 初始化 Tauri 项目

```bash
cd ..
mkdir desktop-client
cd desktop-client

# 使用 Tauri CLI 创建项目
cargo install tauri-cli
cargo tauri init
```

### 2. 配置 Tauri

按照之前的技术指南配置 `tauri.conf.json`

### 3. 创建简单的 UI

**src/index.html**:
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>TaskFleet - 员工客户端</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="app">
        <div id="login-page" class="page">
            <h1>TaskFleet 员工客户端</h1>
            <form id="login-form">
                <input type="text" id="username" placeholder="用户名" required>
                <input type="password" id="password" placeholder="密码" required>
                <button type="submit">登录</button>
            </form>
        </div>
        
        <div id="tasks-page" class="page hidden">
            <h1>我的任务</h1>
            <div id="task-list"></div>
        </div>
    </div>
    
    <script src="app.js"></script>
</body>
</html>
```

---

## 📝 第五步: 更新文档

### 1. 更新 README.md

**README.md**:
```markdown
# TaskFleet - 任务执行专家

![Logo](docs/logo.png)

> 专注于任务分发、进度监控和数据统计的开源项目管理系统

## 特性

- 🚀 **智能任务分发** - 批量导入,自动均衡分配
- 📊 **实时进度监控** - 一目了然的执行状态
- 📈 **深度数据统计** - 员工效率分析,趋势预测
- 💻 **多端协同** - Web管理端 + 桌面员工端
- ⚡ **高性能** - Rust后端,极速响应
- 🎯 **简单易用** - 扁平化权限,开箱即用

## 快速开始

### 后端

```bash
cd backend
cargo run
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

### 桌面客户端

```bash
cd desktop-client
cargo tauri dev
```

## 技术栈

- **后端**: Rust + Axum + PostgreSQL
- **前端**: React + TypeScript + Ant Design
- **桌面**: Tauri + Rust

## 文档

- [项目概述](docs/TaskFleet/00-PROJECT_OVERVIEW.md)
- [技术指南](docs/TaskFleet/01-TECHNICAL_GUIDE.md)
- [API 文档](docs/TaskFleet/API.md)

## 贡献

欢迎贡献!请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License
```

### 2. 创建 .gitignore

**.gitignore**:
```gitignore
# Rust
target/
Cargo.lock

# Node
node_modules/
dist/
.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite

# Logs
logs/
*.log
```

---

## ✅ 第六步: 提交到 GitHub

### 1. 初始提交

```bash
cd ..  # 回到项目根目录

# 添加所有文件
git add .

# 初始提交
git commit -m "feat: initial commit - TaskFleet v0.1.0

- 从 Flow_Farm 提取核心功能
- 简化权限架构 (项目经理-员工)
- 专注任务执行管理
- 移除不需要的模块 (设备管理/计费等)"

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 2. 创建分支保护

在 GitHub 仓库设置中:
- 启用分支保护
- 要求 PR review
- 启用 CI/CD

---

## 🎯 第七步: 验证和测试

### 1. 启动后端

```bash
cd backend

# 设置环境变量
cp .env.example .env
# 编辑 .env 文件

# 运行迁移
sqlx database create
sqlx migrate run

# 启动服务
cargo run
```

### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 3. 测试功能

- [ ] 用户注册和登录
- [ ] 创建项目
- [ ] 添加任务
- [ ] 分配任务
- [ ] 更新状态

---

## 📋 检查清单

在完成以上步骤后,确认:

### 代码清理
- [ ] 删除了所有设备管理相关代码
- [ ] 删除了所有计费相关代码
- [ ] 删除了所有系统管理员功能
- [ ] 简化了用户权限系统

### 功能验证
- [ ] 后端 API 正常启动
- [ ] 前端页面正常显示
- [ ] 用户认证正常工作
- [ ] 数据库迁移成功

### 文档完善
- [ ] README.md 更新
- [ ] 技术文档创建
- [ ] API 文档编写
- [ ] 贡献指南添加

### Git 管理
- [ ] .gitignore 配置正确
- [ ] 代码已提交到 GitHub
- [ ] 分支保护已设置

---

## 🚀 下一步计划

### 本周 (Week 1)
- [ ] 完成项目管理 API
- [ ] 完成任务管理 API
- [ ] 创建基础 Web 页面

### 下周 (Week 2)
- [ ] 实现任务分发功能
- [ ] 实现进度监控
- [ ] 开发桌面客户端

### 第三周 (Week 3)
- [ ] 添加统计功能
- [ ] 集成 WebSocket 实时推送
- [ ] UI/UX 优化

### 第四周 (Week 4)
- [ ] 完整测试
- [ ] 文档完善
- [ ] 准备 MVP 发布

---

## 💡 重要提示

### 保持专注
- ✅ 只做任务执行相关功能
- ❌ 不要添加即时通讯
- ❌ 不要添加文档协作
- ❌ 不要添加复杂权限

### 快速迭代
- 每周发布一个小版本
- 及时收集用户反馈
- 持续优化核心功能

### 社区建设
- 在开发过程中记录博客
- 在社交媒体分享进度
- 积极回应 GitHub Issues

---

## 📞 需要帮助?

如果在创建过程中遇到问题:

1. 查看详细文档: `docs/TaskFleet/`
2. 查看原项目代码作为参考
3. 搜索相关技术问题
4. 在 GitHub 创建 Issue

---

**祝你顺利创建 TaskFleet! 🚀**

**记住**: 简洁 > 复杂,执行 > 计划,迭代 > 完美

