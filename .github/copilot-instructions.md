# Flow Farm - 社交平台自动化获客系统

## 项目概述

Flow Farm 是一个专业的社交平台自动化获客管理系统，支持小红书、抖音等主流社交媒体平台的用户关注、监控和精准获客操作。

### 核心特性

- **三角色权限架构**: 系统管理员（一级）、用户管理员（二级）、员工（脚本用户）
- **多平台支持**: 小红书（优先）、抖音（次要），未来扩展快手、B站等
- **设备管理**: 每个员工最多连接10台设备，支持ADB自动化控制
- **任务管理**: 通讯录导入、同行监控、精准获客、关注统计
- **计费系统**: 基于成功关注的实时扣费机制，余额不足时禁止任务提交
- **数据防重**: 管理员名下所有用户和设备共享关注记录，确保不重复关注

### 技术架构

- **服务器后端**: Rust + Axum + SQLx + SQLite（处理数据存储、权限管理、扣费规则）
- **服务器前端**: React.js + TypeScript + Vite（管理员操作界面）
- **员工客户端**: Rust + Tauri 2.0 + HTML/CSS/JS（原生桌面GUI应用，支持ADB自动化控制）

## 业务需求和功能模块

### 设备管理要求
- 每个员工用户最多管理10台设备
- GUI中直观显示设备连接状态和设备名
- 支持连接/断开设备操作
- 任务只分配给已连接的设备

### 任务管理核心功能
1. **通讯录管理**（通讯录导入任务）
   - 支持CSV或文本格式文件导入
   - 平台区分：小红书、抖音子模块
   - 自动均匀分配任务到已连接设备
   - 显示总关注量和每设备任务量

2. **精准获客**（同行监控任务）
   - 监控指定同行账号
   - 基于关键词搜索和爬取评论
   - AI生成长尾词功能
   - 收集触发关键词的用户ID并执行关注

### 计费机制要求
- 基于成功关注的实时扣费
- 余额不足时禁止任务提交
- 管理员名下所有用户/设备共享关注记录防重复
- 仅成功关注后扣费并同步数据库

### 平台支持优先级
1. 小红书（优先开发完成）
2. 抖音（次要优先级）
3. 未来扩展：快手、B站等（模块化设计）

### GUI界面要求
- 明确区分平台操作（选项卡或下拉菜单）
- 实时显示任务进度和余额状态
- 支持多设备任务分配可视化
- 关键词导入支持手动输入和内置示例

## GUI框架指导原则

### Tauri 桌面应用架构

基于 Tauri 2.0 框架的现代化桌面应用开发：

#### 核心技术栈
- **应用框架**: Tauri 2.0 (原生桌面应用)
- **后端语言**: Rust (Edition 2021)
- **前端技术**: HTML/CSS/JavaScript (最小化，仅用于UI渲染)
- **构建系统**: Cargo + Tauri CLI
- **平台支持**: Windows (主要) + 跨平台支持

#### 开发模式
1. **业务逻辑**: 完全使用Rust实现
2. **GUI渲染**: 通过HTML/CSS定义界面
3. **通信机制**: Tauri命令和事件系统
4. **安全模式**: Tauri提供安全的API访问和沙盒化

#### Tauri 应用架构示例

```rust
// src-tauri/src/main.rs
use tauri::command;

#[command]
fn connect_device(device_id: String) -> Result<String, String> {
    // 设备连接逻辑
    Ok("Device connected".to_string())
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![connect_device])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

## 构建指令 (BuildInstructions)

### 环境要求

- **Rust**: 1.75+ (server-backend + employee-client)
- **Node.js**: 18+ (server-frontend)
- **Tauri CLI**: 2.0+ (employee-client)
- **Android SDK**: Platform Tools (ADB)

### 快速启动 (推荐顺序)

#### 1. 服务器后端 (Rust)

```bash
cd server-backend
cargo build --release
cargo run --release
# API访问: http://localhost:8000
# API文档: http://localhost:8000/docs
```

#### 2. 服务器前端 (React)

```bash
cd server-frontend
npm install
npm run dev
# Web界面: http://localhost:3000
```

#### 3. 员工客户端 (Rust + Tauri)

```bash
cd employee-client
cargo tauri dev  # 开发模式
# 或
cargo tauri build  # 生产构建
# GUI界面: 原生桌面应用自动启动
```

## 项目结构和模块化指令

本项目使用模块化的指令系统，每个模块都有专门的指令文件：

| 模块/路径模式                          | 指令文件                                                                                        | 描述                  |
| -------------------------------------- | ----------------------------------------------------------------------------------------------- | --------------------- |
| `server-backend/src/**/*.rs`           | [server-backend.instructions.md](.github/instructions/server-backend.instructions.md)           | Rust 后端开发指令     |
| `server-frontend/**/*.{tsx,ts,jsx,js}` | [server-frontend.instructions.md](.github/instructions/server-frontend.instructions.md)         | React.js 前端开发指令 |
| `employee-client/src-tauri/**/*.rs`    | [employee-client.instructions.md](.github/instructions/employee-client.instructions.md)         | Rust + Tauri 客户端开发指令 |
| `src/auth/**/*.py`                     | [auth-system.instructions.md](.github/instructions/auth-system.instructions.md)                 | 认证系统指令          |
| `src/core/**/*.py`                     | [core-modules.instructions.md](.github/instructions/core-modules.instructions.md)               | 核心模块指令          |
| `src/gui/**/*.py`                      | [gui-development.instructions.md](.github/instructions/gui-development.instructions.md)         | GUI 开发指令          |
| `src/platforms/**/*.py`                | [platform-automation.instructions.md](.github/instructions/platform-automation.instructions.md) | 平台自动化指令        |
| `scripts/**/*.py`                      | [build-scripts.instructions.md](.github/instructions/build-scripts.instructions.md)             | 构建脚本指令          |

## 专用 Prompt 文件

项目还提供了专门的 prompt 文件，用于特定的开发任务：

| Prompt 文件                                                                    | 用途               | 使用方法                        |
| ------------------------------------------------------------------------------ | ------------------ | ------------------------------- |
| [server-optimization.prompt.md](.github/prompts/server-optimization.prompt.md) | 服务器端重构和优化 | 在 Copilot Chat 中附加此 prompt |
| [api-development.prompt.md](.github/prompts/api-development.prompt.md)         | API 开发和文档生成 | 用于设计和实现 REST API         |
| [rbac-system.prompt.md](.github/prompts/rbac-system.prompt.md)                 | 权限系统开发       | 实现三角色权限控制              |
| [device-automation.prompt.md](.github/prompts/device-automation.prompt.md)     | 设备自动化开发     | 员工客户端自动化功能            |

## 三角色系统架构指导

### 系统管理员（一级管理员，服务器端）

- 开通用户管理员权限
- 查看所有员工工作信息和统计数据
- 设置收费规则和计费标准
- 系统配置和监控

### 用户管理员（二级管理员，服务器端）

- 开通员工权限（最多 10 个用户）
- 查看本公司员工工作信息
- 查看结算界面，调整关注数量
- 扣费计划管理

### 员工（脚本用户，桌面客户端）

- 多设备自动化控制
- 抖音、小红书关注引流操作
- 工作数据上传和同步
- 任务执行和状态汇报

## 项目结构和模块化指令

本项目使用模块化的指令系统，每个模块都有专门的指令文件：

| 模块/路径模式                      | 指令文件                                                                                        | 描述                  |
| ---------------------------------- | ----------------------------------------------------------------------------------------------- | --------------------- |
| `server-backend/src/**/*.rs`       | [server-backend.instructions.md](.github/instructions/server-backend.instructions.md)           | Rust 后端开发指令     |
| `server-frontend/**/*.{vue,ts,js}` | [server-frontend.instructions.md](.github/instructions/server-frontend.instructions.md)         | Vue.js 前端开发指令   |
| `employee-client/src-tauri/**/*.rs`    | [employee-client.instructions.md](.github/instructions/employee-client.instructions.md)         | Rust + Tauri 客户端开发指令 |
| `src/auth/**/*.py`                 | [auth-system.instructions.md](.github/instructions/auth-system.instructions.md)                 | 认证系统指令          |
| `src/core/**/*.py`                 | [core-modules.instructions.md](.github/instructions/core-modules.instructions.md)               | 核心模块指令          |
| `src/gui/**/*.py`                  | [gui-development.instructions.md](.github/instructions/gui-development.instructions.md)         | GUI 开发指令          |
| `src/platforms/**/*.py`            | [platform-automation.instructions.md](.github/instructions/platform-automation.instructions.md) | 平台自动化指令        |
| `scripts/**/*.py`                  | [build-scripts.instructions.md](.github/instructions/build-scripts.instructions.md)             | 构建脚本指令          |

## 三角色系统架构指导

### 系统管理员（一级管理员，服务器端）

- 开通用户管理员权限
- 查看所有员工工作信息和统计数据
- 设置收费规则和计费标准
- 系统配置和监控

### 用户管理员（二级管理员，服务器端）

- 开通员工权限（最多 10 个用户）
- 查看本公司员工工作信息
- 查看结算界面，调整关注数量
- 扣费计划管理

### 员工（脚本用户，桌面客户端）

- 多设备自动化控制
- 抖音、小红书关注引流操作
- 工作数据上传和同步
- 任务执行和状态汇报

## 开发工作流

### 1. 代码生成和修改

当需要生成或修改代码时：

- 首先阅读相应的模块指令文件
- 确保理解该模块的特定要求和约定
- 生成的代码必须符合项目的架构模式和编码规范
- 包含适当的错误处理和日志记录

### 2. API 开发

- 遵循 RESTful API 设计原则
- 使用 OpenAPI 3.0 规范生成文档
- 实现适当的认证和授权
- 包含输入验证和错误响应

### 3. 数据库设计

- 使用 SQLx 进行类型安全的数据库操作
- 实现适当的索引和查询优化
- 遵循数据库规范化原则
- 包含迁移脚本

### 4. 前端开发

- 使用 Vue 3 组合式 API
- 实现响应式设计
- 遵循组件化开发模式
- 包含类型定义和错误处理

## 安全和性能指导

### 安全要求

- 所有 API 端点必须实现适当的认证和授权
- 敏感数据必须加密存储
- 输入数据必须验证和清理
- 实现适当的审计日志

### 性能要求

- 数据库查询必须优化
- 实现适当的缓存策略
- 异步操作使用 Tokio
- 前端实现懒加载和代码分割

## 测试策略

### 单元测试

- Rust: 使用内置的测试框架
- 前端: 使用 Vitest 进行单元测试
- Python: 使用 pytest 框架
- 目标覆盖率: 80%+

### 集成测试

- API 端点测试
- 数据库集成测试
- 前后端集成测试

### 性能测试

- 负载测试
- 并发测试
- 内存泄漏检测

## 部署和 DevOps

### 构建流程

- Rust: `cargo build --release`
- 前端: `npm run build`
- Python: PyInstaller 打包

### 监控和日志

- 使用结构化日志
- 实现健康检查端点
- 监控系统性能指标

## 重要提醒

1. **始终遵循相关平台的使用条款和法律法规**
2. **合理控制操作频率，避免被平台检测为异常行为**
3. **定期备份重要数据和配置**
4. **监控设备状态，避免过度使用导致设备损坏**
5. **保护用户隐私，严格控制数据访问权限**

## 获取更多帮助

在使用 Copilot 时，可以使用以下提示：

- `@workspace` 或 `#codebase` 来引用整个代码库
- `#<filename>` 来引用特定文件
- 明确指定你要修改的模块和功能
- 参考相应的指令文件获取模块特定的指导

当创建 pull request 时，请在描述的第一行添加：
_This pull request was created as a result of the following prompt in Copilot Chat._

## 项目架构 (ProjectLayout)

### 目录结构详解

```
Flow_Farm/                          # 项目根目录
├── .github/                        # GitHub配置和CI/CD
│   ├── copilot-instructions.md     # 主要Copilot指令文件
│   ├── instructions/               # 模块化指令目录
│   ├── prompts/                    # 提示文件目录
│   └── workflows/                  # GitHub Actions工作流
├── server-backend/                 # 服务器后端 (FastAPI)
│   ├── app/                       # 应用程序代码
│   │   ├── main.py               # FastAPI应用入口
│   │   ├── config.py             # 配置管理
│   │   ├── database.py           # 数据库连接
│   │   ├── api/                  # API路由
│   │   ├── models/               # 数据模型
│   │   ├── schemas/              # Pydantic模式
│   │   └── services/             # 业务逻辑
│   ├── requirements.txt          # Python依赖
│   └── data/                     # 数据库文件
├── server-frontend/                # 服务器前端 (Vue.js)
│   ├── src/                      # 源代码
│   │   ├── main.ts              # 应用入口
│   │   ├── App.vue              # 根组件
│   │   ├── components/          # Vue组件
│   │   ├── views/               # 页面视图
│   │   ├── router/              # 路由配置
│   │   └── stores/              # Pinia状态管理
│   ├── package.json             # Node.js依赖
│   └── vite.config.ts           # Vite配置
├── employee-client/                # 员工客户端 (Rust + Tauri)
│   ├── src-tauri/              # Rust 后端代码
│   │   ├── src/                # Rust 源代码
│   │   │   ├── main.rs        # 应用程序入口点
│   │   │   ├── api.rs         # API 通信模块
│   │   │   ├── device.rs      # 设备管理 (ADB连接和控制)
│   │   │   ├── models.rs      # 数据模型
│   │   │   └── utils.rs       # 工具函数
│   │   ├── Cargo.toml         # Rust 依赖
│   │   └── tauri.conf.json    # Tauri 配置
│   ├── src/                   # 前端资源 (HTML/CSS/JS)
│   ├── logs/                  # 日志文件
│   └── target/                # 构建产物
├── config/                        # 全局配置文件目录
├── docs/                         # 项目文档
├── tests/                        # 测试文件目录
├── scripts/                      # 构建和部署脚本
└── Flow_Farm.code-workspace      # VS Code工作区配置
```

### 架构模式说明

- **微服务架构**: server-backend 和 server-frontend 分离
- **C/S 架构**: 服务器端 Web 应用 + 桌面客户端
- **分层架构**: core(业务逻辑) → gui(表示层) → platforms(平台层)
- **MVP 模式**: Model(数据) + View(GUI) + Presenter(控制器)
- **模块化设计**: 每个功能模块独立，便于维护和扩展
- **插件化平台**: 新平台可通过继承 base_platform 轻松添加

### 关键配置文件

- `server-backend/src/main.rs`: Rust 后端应用入口，包含 Axum 服务器
- `server-frontend/src/main.tsx`: React.js 应用入口
- `employee-client/src-tauri/src/main.rs`: Tauri 应用入口
- `config/app_config.json`: 主要配置文件，包含所有系统设置
- `Flow_Farm.code-workspace`: VS Code 工作区配置

### 数据流向

1. **管理员操作** → Web 前端 → API → 数据库 → 权限验证
2. **员工操作** → 桌面客户端 → API → 数据库 → 任务分发
3. **设备操作** → 平台模块 → 自动化引擎 → ADB → 数据上报

### 开发时文件位置规则

- 新增 API 接口: `server-backend/src/handlers/`
- 新增 Web 页面: `server-frontend/src/views/`
- 新增设备管理功能: `employee-client/src-tauri/src/device.rs`
- 新增 GUI 组件: `employee-client/src/` (HTML/CSS/JS 前端资源)
- 新增平台支持: `employee-client/src-tauri/src/` (Rust 模块)
- 新增权限功能: `employee-client/src-tauri/src/` (Rust 认证模块)
  │ │ ├── windows/ # 独立窗口
  │ │ │ ├── admin_panel.py # 管理员控制面板
  │ │ │ ├── user_panel.py # 用户操作面板
  │ │ │ └── settings_window.py # 设置窗口
  │ │ └── dialogs/ # 对话框
  │ │ ├── login_dialog.py # 登录对话框
  │ │ └── device_dialog.py # 设备配置对话框
  │ ├── platforms/ # 平台特定自动化模块
  │ │ ├── **init**.py
  │ │ ├── base_platform.py # 平台基类 (抽象接口)
  │ │ ├── xiaohongshu/ # 小红书自动化
  │ │ │ ├── **init**.py
  │ │ │ ├── automation.py # 小红书自动化逻辑
  │ │ │ ├── ui_elements.py # UI 元素定义
  │ │ │ └── strategies.py # 操作策略
  │ │ └── douyin/ # 抖音自动化
  │ │ ├── **init**.py
  │ │ ├── automation.py # 抖音自动化逻辑
  │ │ ├── ui_elements.py # UI 元素定义
  │ │ └── strategies.py # 操作策略
  │ ├── auth/ # 权限认证系统
  │ │ ├── **init**.py
  │ │ ├── user_manager.py # 用户管理 (CRUD 操作)
  │ │ ├── permission.py # 权限控制 (RBAC 实现)
  │ │ ├── session.py # 会话管理
  │ │ └── crypto.py # 加密工具
  │ └── utils/ # 工具类和帮助函数
  │ ├── **init**.py
  │ ├── logger.py # 日志配置
  │ ├── adb_helper.py # ADB 命令封装
  │ ├── ui_parser.py # UI XML 解析
  │ └── validator.py # 数据验证
  ├── config/ # 配置文件目录
  │ ├── app_config.json # 应用程序配置
  │ ├── device_config.json # 设备配置模板
  │ ├── platform_config.json # 平台特定配置
  │ └── logging.conf # 日志配置
  ├── data/ # 数据文件目录
  │ ├── database.db # SQLite 数据库
  │ ├── cache/ # 缓存文件
  │ └── exports/ # 导出数据
  ├── logs/ # 日志文件目录
  │ ├── app.log # 应用程序日志
  │ ├── device.log # 设备操作日志
  │ └── error.log # 错误日志
  ├── tests/ # 测试文件目录
  │ ├── **init**.py
  │ ├── unit/ # 单元测试
  │ ├── integration/ # 集成测试
  │ └── gui/ # GUI 测试
  ├── scripts/ # 构建和部署脚本
  │ ├── build.py # 构建脚本 (PyInstaller 配置)
  │ ├── encrypt.py # 加密脚本
  │ ├── package.py # 打包脚本
  │ └── validate_build.py # 构建验证
  ├── docs/ # 项目文档
  │ ├── README.md # 项目说明
  │ ├── API.md # API 文档
  │ ├── USER_GUIDE.md # 用户指南
  │ └── DEVELOPER.md # 开发者文档
  ├── requirements.txt # Python 依赖列表
  ├── requirements-dev.txt # 开发依赖列表
  ├── .gitignore # Git 忽略文件
  ├── .env.example # 环境变量模板
  └── Flow_Farm.code-workspace # VS Code 工作区配置

````

### 架构模式说明
- **分层架构**: core(业务逻辑) → gui(表示层) → platforms(平台层)
- **MVP模式**: Model(数据) + View(GUI) + Presenter(控制器)
- **模块化设计**: 每个功能模块独立，便于维护和扩展
- **插件化平台**: 新平台可通过继承base_platform轻松添加

### 关键配置文件
- `src/main.py`: 应用程序入口，包含启动逻辑
- `config/app_config.json`: 主要配置文件，包含所有系统设置
- `requirements.txt`: 生产环境依赖，构建时必须安装
- `.github/copilot-instructions.md`: 本文件，Copilot工作指南

### 数据流向
1. **用户操作** → GUI组件 → 核心模块 → 平台模块 → 设备执行
2. **设备反馈** → 平台模块 → 核心模块 → GUI更新 → 用户可见

### 开发时文件位置规则
- 新增设备管理功能: `src/core/device_manager.py`
- 新增GUI组件: `src/gui/components/`
- 新增平台支持: `src/platforms/新平台名/`
- 新增权限功能: `src/auth/`
- 新增工具函数: `src/utils/`

## 开发规范

### 代码规范
- 使用PEP 8编码规范
- 函数名使用下划线命名法（snake_case）
- 类名使用驼峰命名法（PascalCase）
- 常量使用全大写（UPPER_CASE）
- 所有函数和类必须包含docstring文档

### 注释规范
- 中文注释，便于国内团队理解
- 关键业务逻辑必须添加详细注释
- API接口必须包含参数说明和返回值说明

### 安全规范
- 敏感信息（API密钥、数据库密码）必须加密存储
- 用户权限验证在每个关键操作前进行
- 设备连接信息加密传输

## 构建指令 (BuildInstructions)

### 环境设置 (必须按顺序执行)

#### 服务器后端环境
```bash
# 进入服务器后端目录
cd server-backend

# 创建Python虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows

# 安装后端依赖
pip install --upgrade pip
pip install -r requirements.txt

# 初始化数据库
python -c "from app.init_db import create_tables; create_tables()"
````

#### 服务器前端环境

```bash
# 进入服务器前端目录
cd server-frontend

# 安装Node.js依赖
npm install

# 验证安装
npm run type-check
```

#### 员工客户端环境

```bash
# 进入员工客户端目录
cd employee-client

# 创建Python虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装客户端依赖
pip install --upgrade pip
pip install -r requirements.txt

# 配置ADB环境 (必需步骤)
# Windows: 下载 Android SDK Platform Tools
# 确保 adb.exe 在 PATH 中

# 验证设备连接 (开发前必须执行)
adb devices
```

### 开发环境启动

#### 启动服务器后端

```bash
cd server-backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
# API文档访问: http://localhost:8000/docs
```

#### 启动服务器前端

```bash
cd server-frontend
npm run dev
# Web界面访问: http://localhost:3000
```

#### 启动员工客户端

```bash
cd employee-client
venv\Scripts\activate
python src/main.py --gui --debug
```

### 构建和打包

#### 构建服务器后端

```bash
cd server-backend
venv\Scripts\activate

# 运行测试
python -m pytest tests/ -v

# 构建Docker镜像 (生产环境)
docker build -t flow-farm-backend:latest .
```

#### 构建服务器前端

```bash
cd server-frontend

# 运行测试
npm run test:unit

# 构建生产版本
npm run build

# 构建结果在 dist/ 目录
```

#### 构建员工客户端

```bash
cd employee-client
venv\Scripts\activate

# 运行测试
python -m pytest tests/ -v

# 构建开发版本 (未加密)
python scripts/build.py --mode development

# 构建生产版本 (加密保护)
python scripts/build.py --mode production --encrypt

# 验证构建结果
python scripts/validate_build.py
```

### 完整项目构建

```bash
# 在项目根目录执行
python scripts/build_all.py --mode production

# 这将依次构建：
# 1. 服务器后端 (Docker镜像)
# 2. 服务器前端 (静态文件)
# 3. 员工客户端 (加密可执行文件)
```

### 测试验证 (必须步骤)

```bash
# 运行完整测试套件 (构建前必须通过)
python -m pytest tests/ -v --cov=src --cov-report=html

# 运行设备连接测试
python tests/integration/test_device_connection.py

# 运行GUI测试 (需要显示器)
python tests/gui/test_main_window.py

# 性能测试 (可选)
python tests/performance/test_multi_device.py
```

### 已验证的构建流程

1. **总是在虚拟环境中工作** - 避免依赖冲突
2. **构建前运行完整测试** - 确保代码质量
3. **验证 ADB 连接** - 构建前确保设备管理正常
4. **分阶段构建** - 先开发版本，测试通过后再生产版本
5. **构建时间**: 开发版本约 2-3 分钟，生产版本约 5-8 分钟

### 常见构建问题和解决方案

- **PyInstaller 导入错误**: 添加 `--hidden-import` 参数
- **ADB 路径问题**: 配置 `config/adb_path.json`
- **权限错误**: 以管理员身份运行构建脚本
- **内存不足**: 构建时关闭其他应用程序

## 核心功能模块

### 设备管理模块 (src/core/device_manager.py)

- 自动发现和连接 Android 设备
- 设备状态监控和健康检查
- 多设备并发控制

### 自动化引擎 (src/core/automation_engine.py)

- 基于 Appium 的 UI 自动化
- 图像识别和 OCR 功能
- 智能等待和重试机制

### 任务调度器 (src/core/task_scheduler.py)

- 任务队列管理
- 定时任务执行
- 任务状态跟踪

### 权限系统 (src/auth/)

- 基于角色的访问控制（RBAC）
- 用户认证和会话管理
- 操作日志记录

## 平台特定操作

### 抖音自动化 (src/platforms/douyin/)

- 自动关注用户
- 视频点赞和评论
- 直播间互动
- 数据收集和分析

### 小红书自动化 (src/platforms/xiaohongshu/)

- 笔记点赞和收藏
- 用户关注操作
- 评论互动
- 热门内容监控

## 错误处理和日志

### 日志配置

- 使用 Python logging 模块
- 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
- 日志文件按日期轮转

### 异常处理

- 网络连接异常重试机制
- 设备离线自动重连
- UI 元素查找失败的降级处理

## 性能优化

### 并发控制

- 使用线程池管理设备操作
- 避免过度并发导致设备负载过高
- 智能任务分配算法

### 资源管理

- 及时释放设备连接
- 内存使用监控
- 临时文件清理

## 安全和加密

### 代码保护

- 使用 PyInstaller 打包
- 添加自定义加密层
- 防逆向工程措施

### 数据安全

- 用户数据加密存储
- 设备标识信息脱敏
- 操作日志安全存储

## 测试策略

### 单元测试

- 核心功能模块 100%覆盖
- 使用 pytest 框架
- Mock 外部依赖

### 集成测试

- 设备连接测试
- 平台操作测试
- 权限系统测试

### 性能测试

- 多设备并发测试
- 长时间运行稳定性测试
- 内存泄漏检测

## 部署说明

### 客户端部署

- 提供一键安装包
- 自动检测和配置 ADB 环境
- 设备驱动自动安装

### 权限配置

- 管理员初始化系统
- 用户权限分配
- 操作审计日志

## 重要提醒

1. **始终遵循相关平台的使用条款和法律法规**
2. **合理控制操作频率，避免被平台检测为异常行为**
3. **定期备份重要数据和配置**
4. **监控设备状态，避免过度使用导致设备损坏**
5. **保护用户隐私，严格控制数据访问权限**

## 开发优先级

1. 设备管理和连接模块
2. 基础自动化引擎
3. 权限认证系统
4. GUI 界面开发
5. 平台特定操作实现
6. 加密和安全功能
7. 测试和优化
8. 部署和分发

当实现新功能时，请优先考虑代码的可维护性、安全性和用户体验。所有涉及设备操作的代码都应该包含适当的错误处理和日志记录。

## 开发工作流

### 1. 代码生成和修改

当需要生成或修改代码时：

- 首先阅读相应的模块指令文件
- 确保理解该模块的特定要求和约定
- 生成的代码必须符合项目的架构模式和编码规范
- 包含适当的错误处理和日志记录

### 2. API 开发

- 遵循 RESTful API 设计原则
- 使用 OpenAPI 3.0 规范生成文档
- 实现适当的认证和授权
- 包含输入验证和错误响应

### 3. 数据库设计

- 使用 SQLx 进行类型安全的数据库操作
- 实现适当的索引和查询优化
- 遵循数据库规范化原则
- 包含迁移脚本

### 4. 前端开发

- 使用 React 18 组合式 API
- 实现响应式设计
- 遵循组件化开发模式
- 包含类型定义和错误处理

## 安全和性能指导

### 安全要求

- 所有 API 端点必须实现适当的认证和授权
- 敏感数据必须加密存储
- 输入数据必须验证和清理
- 实现适当的审计日志

### 性能要求

- 数据库查询必须优化
- 实现适当的缓存策略
- 异步操作使用 Tokio
- 前端实现懒加载和代码分割

## 测试策略

### 单元测试

- Rust: 使用内置的测试框架
- 前端: 使用 Jest/Vitest 进行单元测试
- Python: 使用 pytest 框架
- 目标覆盖率: 80%+

### 集成测试

- API 端点测试
- 数据库集成测试
- 前后端集成测试

### 性能测试

- 负载测试
- 并发测试
- 内存泄漏检测

## 部署和 DevOps

### 构建流程

- Rust: `cargo build --release`
- 前端: `npm run build`
- Python: PyInstaller 打包

### 监控和日志

- 使用结构化日志
- 实现健康检查端点
- 监控系统性能指标

## 获取更多帮助

在使用 Copilot 时，可以使用以下提示：

- `@workspace` 或 `#codebase` 来引用整个代码库
- `#<filename>` 来引用特定文件
- 明确指定你要修改的模块和功能
- 参考相应的指令文件获取模块特定的指导

当创建 pull request 时，请在描述的第一行添加：
_This pull request was created as a result of the following prompt in Copilot Chat._
