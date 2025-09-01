# Flow Farm - 计费自动化流量农场系统

## 项目概述

Flow Farm 是一个企业级计费自动化流量农场系统，专为多角色权限管理和社交媒体自动化操作而设计。

### 核心特性

- **三角色架构**: 系统管理员、用户管理员、员工
- **多平台支持**: 抖音、小红书等主流社交媒体平台
- **自动化引流**: 智能设备控制和任务调度
- **计费管理**: 精确的使用统计和费用计算

### 技术架构

- **服务器后端**: Rust + Axum + SQLx + SQLite
- **服务器前端**: React.js + TypeScript + Vite
- **员工客户端**: Python + PySide6 + qfluentwidgets + ADB

## GUI框架指导原则

### 现代化UI框架迁移计划

基于 OneDragon 项目的成功实践，员工客户端正在从原生 PySide6 迁移到 PySide6 + qfluentwidgets 架构：

#### 目标框架
- **基础框架**: PySide6 6.8.0+ (Qt6)
- **UI组件库**: qfluentwidgets 1.7.0+ (Microsoft Fluent Design)
- **图标系统**: FluentIcon (内置) + qtawesome (兼容)
- **主题系统**: 自动深色/浅色主题切换
- **布局系统**: VerticalScrollInterface + 组件化设计

#### 迁移策略
1. **渐进式重构**: 保持现有 `ComponentFactory` 和 `ModernTheme`
2. **组件替换**: 逐步替换 QPushButton → PrimaryPushButton
3. **界面继承**: 从 VerticalScrollInterface 继承主界面
4. **设置卡片**: 使用 SettingCard 系列组件替换自定义设置界面

#### OneDragon GUI架构借鉴

```python
# 推荐的新组件使用模式
from qfluentwidgets import (
    VerticalScrollInterface, PrimaryPushButton,
    SettingCardGroup, ComboBoxSettingCard, FluentIcon,
    InfoBar, MessageBox, Theme
)

class ModernInterface(VerticalScrollInterface):
    def __init__(self):
        super().__init__(
            object_name="modern_interface",
            nav_text_cn="现代界面",
            nav_icon=FluentIcon.HOME
        )
```

## 构建指令 (BuildInstructions)

### 环境要求

- **Rust**: 1.75+ (server-backend)
- **Node.js**: 18+ (server-frontend)
- **Python**: 3.8+ (employee-client)
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

#### 3. 员工客户端 (Python)

```bash
cd employee-client
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python src/main.py --gui --debug
```

## 项目结构和模块化指令

本项目使用模块化的指令系统，每个模块都有专门的指令文件：

| 模块/路径模式                          | 指令文件                                                                                        | 描述                  |
| -------------------------------------- | ----------------------------------------------------------------------------------------------- | --------------------- |
| `server-backend/src/**/*.rs`           | [server-backend.instructions.md](.github/instructions/server-backend.instructions.md)           | Rust 后端开发指令     |
| `server-frontend/**/*.{tsx,ts,jsx,js}` | [server-frontend.instructions.md](.github/instructions/server-frontend.instructions.md)         | React.js 前端开发指令 |
| `employee-client/**/*.py`              | [employee-client.instructions.md](.github/instructions/employee-client.instructions.md)         | Python 客户端开发指令 |
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
| `employee-client/**/*.py`          | [employee-client.instructions.md](.github/instructions/employee-client.instructions.md)         | Python 客户端开发指令 |
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
├── employee-client/                # 员工客户端 (Python GUI)
│   ├── src/                     # 源代码目录
│   │   ├── main.py              # 应用程序入口点
│   │   ├── core/                # 核心业务逻辑模块
│   │   │   ├── device_manager.py    # 设备管理 (ADB连接和控制)
│   │   │   ├── automation_engine.py # 自动化引擎 (UI操作核心)
│   │   │   ├── task_scheduler.py    # 任务调度器 (多任务管理)
│   │   │   └── config_manager.py    # 配置管理器
│   │   ├── gui/                 # GUI界面模块 (用户交互)
│   │   │   ├── main_window.py   # 主窗口 (应用程序主界面)
│   │   │   ├── components/      # 可复用组件
│   │   │   ├── windows/         # 独立窗口
│   │   │   └── dialogs/         # 对话框
│   │   ├── platforms/           # 平台特定自动化模块
│   │   │   ├── base_platform.py     # 平台基类
│   │   │   ├── xiaohongshu/     # 小红书自动化
│   │   │   └── douyin/          # 抖音自动化
│   │   ├── auth/                # 权限认证系统
│   │   └── utils/               # 工具类和帮助函数
│   ├── requirements.txt         # Python依赖
│   └── config/                  # 配置文件目录
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

- `server-backend/app/main.py`: FastAPI 应用入口，包含 API 路由
- `server-frontend/src/main.ts`: Vue.js 应用入口
- `employee-client/src/main.py`: 员工客户端入口
- `config/app_config.json`: 主要配置文件，包含所有系统设置
- `Flow_Farm.code-workspace`: VS Code 工作区配置

### 数据流向

1. **管理员操作** → Web 前端 → API → 数据库 → 权限验证
2. **员工操作** → 桌面客户端 → API → 数据库 → 任务分发
3. **设备操作** → 平台模块 → 自动化引擎 → ADB → 数据上报

### 开发时文件位置规则

- 新增 API 接口: `server-backend/app/api/`
- 新增 Web 页面: `server-frontend/src/views/`
- 新增设备管理功能: `employee-client/src/core/device_manager.py`
- 新增 GUI 组件: `employee-client/src/gui/components/`
- 新增平台支持: `employee-client/src/platforms/新平台名/`
- 新增权限功能: `employee-client/src/auth/`
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
