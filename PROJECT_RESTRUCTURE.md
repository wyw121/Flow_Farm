# Flow Farm 项目重构说明

## 重构概述

原Flow Farm单体项目已重构为三个独立模块的企业级架构：

### 🏗️ 新架构模块

#### 1. 🖥️ 服务器后端 (`server-backend/`)
**功能**: 管理员用于记录和管理员工工作信息的后端服务
- **技术栈**: FastAPI + SQLAlchemy + PostgreSQL
- **主要功能**:
  - 员工账号管理和授权
  - 工作量KPI数据记录和统计
  - 设备使用情况监控
  - RESTful API服务
- **运行环境**: 服务器 (Linux/Windows)
- **端口**: 8000

#### 2. 🌐 服务器前端 (`server-frontend/`)
**功能**: 管理员用于展示员工工作信息的Web界面
- **技术栈**: React.js + TypeScript + Ant Design
- **主要功能**:
  - 管理员登录和权限控制
  - 员工工作量仪表盘
  - KPI数据可视化
  - 设备状态监控面板
- **运行环境**: 与后端同服务器
- **端口**: 3000 (开发) / 80 (生产)

#### 3. 💻 员工客户端 (`employee-client/`)
**功能**: 员工工作程序，需要管理员授权账号
- **技术栈**: Python + tkinter + ADB
- **主要功能**:
  - 员工登录认证 (JWT Token)
  - 设备自动化操作
  - 工作量实时上传
  - 离线工作支持
- **运行环境**: 员工电脑 (Windows)

### 🔄 数据流架构

```
[员工客户端] --HTTPS API--> [服务器后端] <--API--> [服务器前端]
     ↓                           ↓                      ↑
[设备操作]                  [数据库存储]            [管理员查看]
     ↓                           ↓                      ↑
[KPI上传] -----------------> [统计分析] -----------> [可视化展示]
```

### 🚀 快速启动指南

#### 1. 初始化整个项目
```bash
# VS Code中运行任务: "🏗️ 初始化整个项目"
# 或手动执行:
cd server-backend && python -m venv venv && pip install -r requirements.txt
cd ../server-frontend && npm install
cd ../employee-client && python -m venv venv && pip install -r requirements.txt
```

#### 2. 启动服务器后端
```bash
# VS Code任务: "🚀 启动服务器后端"
cd server-backend
./venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
```

#### 3. 启动服务器前端
```bash
# VS Code任务: "🌐 启动服务器前端开发"
cd server-frontend
npm run dev
```

#### 4. 启动员工客户端
```bash
# VS Code任务: "💻 启动员工客户端GUI"
cd employee-client
./venv/Scripts/python.exe src/main.py --mode gui --debug
```

### 📁 工作区文件夹说明

- **🏢 Flow Farm - 完整项目**: 项目根目录，包含全局配置和原有文件
- **🖥️ 服务器后端 (管理员)**: 后端API服务，独立的Python环境
- **🌐 服务器前端 (管理员)**: 前端Web应用，独立的Node.js环境
- **💻 员工客户端**: 桌面客户端程序，独立的Python环境

### 🔧 开发环境配置

每个模块都有独立的虚拟环境和依赖管理：

- `server-backend/venv/` - 后端Python环境
- `server-frontend/node_modules/` - 前端Node.js环境
- `employee-client/venv/` - 客户端Python环境
- `venv/` - 原项目兼容环境

### 🧪 测试策略

- **后端测试**: `pytest server-backend/tests/`
- **前端测试**: `npm test` (在server-frontend目录)
- **客户端测试**: `pytest employee-client/tests/`
- **集成测试**: 跨模块API测试

### 🔐 安全和权限

1. **服务器端**: 管理员拥有完全控制权
   - 创建和管理员工账号
   - 查看所有工作数据
   - 设置KPI目标和权限

2. **客户端**: 员工需要授权账号
   - JWT Token认证
   - 只能访问自己的数据
   - 工作量自动上传到服务器

### 📊 数据库设计

主要数据表：
- `users` - 用户账号信息
- `kpi_records` - KPI工作量记录
- `devices` - 设备信息
- `work_sessions` - 工作会话
- `platforms` - 平台操作记录

### 🚀 部署建议

#### 开发环境
- 服务器后端: 本地运行 (localhost:8000)
- 服务器前端: 本地开发服务器 (localhost:3000)
- 员工客户端: 开发机器运行

#### 生产环境
- 服务器: Docker容器 + Nginx反向代理
- 客户端: PyInstaller打包的exe文件
- 数据库: PostgreSQL或MySQL

### 🔄 迁移现有代码

原有代码位置映射：
- `src/core/` → `server-backend/app/` + `employee-client/src/automation/`
- `src/gui/` → `employee-client/src/gui/` + `server-frontend/src/`
- `src/auth/` → `server-backend/app/auth/` + `employee-client/src/auth/`
- `src/platforms/` → `employee-client/src/automation/platforms/`

### 💡 开发建议

1. **并行开发**: 三个模块可以独立开发和测试
2. **API优先**: 先定义API接口，再实现前后端
3. **测试驱动**: 每个模块都要有完整的测试覆盖
4. **文档同步**: 及时更新各模块的README文档
5. **版本控制**: 使用Git分支管理不同模块的开发

### ⚠️ 注意事项

1. **网络依赖**: 员工客户端需要网络连接服务器
2. **权限管理**: 严格控制员工账号的权限范围
3. **数据安全**: 敏感信息加密存储和传输
4. **性能监控**: 监控服务器负载和客户端性能
5. **备份策略**: 定期备份数据库和配置文件
