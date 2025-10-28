# Flow Farm 项目文档中心# Flow Farm - 手机流量农场自动化系统



欢迎访问 Flow Farm 项目文档中心。本文档库包含项目的所有技术文档、用户指南、开发指南和报告。## 项目简介



## 📚 文档分类导航Flow Farm 是一个企业级手机流量农场自动化系统，专为批量Android设备管理和社交媒体自动化操作而设计。系统通过Python实现多设备并发控制，支持抖音、小红书等主流平台的智能引流操作，具备完善的权限管理和现代化用户界面。



### 01. 架构文档 (`01-architecture/`)## 核心特性



系统架构设计、技术栈说明和项目结构分析。### 🤖 智能自动化

- **多平台支持**: 抖音、小红书等主流社交媒体平台

- **[架构可视化 2025](./01-architecture/ARCHITECTURE_VISUALIZATION_2025.md)** - 完整的系统架构图和组件说明- **智能操作**: 模拟真实用户行为，避免机器检测

- **[深度项目分析 2025](./01-architecture/PROJECT_DEEP_ANALYSIS_2025.md)** - 项目技术栈深度分析- **任务调度**: 支持定时任务和批量操作执行

- **[员工客户端架构](./01-architecture/employee-client-architecture.md)** - 员工客户端 (Tauri) 架构设计- **故障恢复**: 自动重试和错误恢复机制



### 02. 开发指南 (`02-development/`)### 📱 设备管理

- **多设备控制**: 同时管理数十台Android设备

开发环境配置、构建流程和开发规范。- **实时监控**: 设备状态、性能指标实时监控

- **热插拔支持**: 设备动态连接和断开检测

- **[开发指南](./02-development/DEVELOPMENT_GUIDE.md)** - 完整的开发和部署指南- **远程控制**: 通过ADB实现设备远程操作

- **[安装指南](./02-development/INSTALL.md)** - 项目安装和环境配置

- **[后端开发说明](./02-development/backend-readme.md)** - 服务器后端 (Rust) 开发指南### 🔐 权限管理

- **[前端开发说明](./02-development/frontend-readme.md)** - 服务器前端 (React) 开发指南- **角色分离**: 管理员和普通用户权限分级

- **[员工客户端开发说明](./02-development/employee-client-readme.md)** - 员工客户端开发指南- **安全认证**: 用户登录和会话管理

- **[员工客户端 OneDragon 说明](./02-development/employee-client-onedragon-readme.md)** - OneDragon 集成说明- **操作审计**: 完整的操作日志记录

- **[GUI 迁移指南](./02-development/gui-migration-guide.md)** - GUI 框架迁移指南- **数据加密**: 敏感信息加密存储



### 03. 部署文档 (`03-deployment/`)### 🎨 现代化界面

- **Material Design**: 现代化UI设计风格

生产环境部署、服务器配置和运维指南。- **响应式布局**: 适配不同屏幕尺寸

- **主题切换**: 支持亮色/暗色主题

- **[Ubuntu 部署指南](./03-deployment/ubuntu-deployment.md)** - Ubuntu 服务器部署完整流程- **实时状态**: 设备和任务状态实时更新

- **[部署说明](./03-deployment/deploy-readme.md)** - 通用部署文档

## 技术架构

### 04. 项目报告 (`04-reports/`)

### 核心技术栈

开发进度报告、问题修复记录和完成报告。- **Python 3.8+**: 主要开发语言

- **tkinter/PyQt**: GUI界面框架

- **[项目状态分析](./04-reports/PROJECT_STATUS_ANALYSIS.md)** - 项目当前状态分析- **ADB**: Android设备通信

- **[前端调试报告](./04-reports/FRONTEND_DEBUG_REPORT.md)** - 前端问题调试记录- **SQLite**: 本地数据存储

- **[统一错误处理完成](./04-reports/UNIFIED_ERROR_HANDLING_COMPLETE.md)** - 错误处理机制重构报告- **PyInstaller**: 代码加密打包

- **[优先级 2-3 重构完成](./04-reports/PRIORITY_2_3_REFACTORING_COMPLETE.md)** - 代码重构完成报告

- **[员工创建修复完成](./04-reports/EMPLOYEE_CREATION_FIX_COMPLETE.md)** - 员工创建功能修复报告### 架构设计

- **[后端编译成功报告](./04-reports/backend-compilation-success.md)** - 后端编译测试报告```

- **[后端测试覆盖率报告](./04-reports/backend-test-coverage.md)** - 后端单元测试覆盖率┌─────────────────────────────────────────────────────┐

- **[员工客户端开发总结](./04-reports/employee-client-development-summary.md)** - 员工客户端开发阶段总结│                   GUI Layer                         │

- **[布局优化](./04-reports/layout-optimization.md)** - UI 布局优化记录│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │

- **[项目清理完成报告](./04-reports/project-cleanup-completion.md)** - 代码清理和整理报告│  │Main Window  │ │Admin Panel  │ │User Panel   │   │

- **[设备管理总结](./04-reports/project-device-management-summary.md)** - 设备管理功能开发总结│  └─────────────┘ └─────────────┘ └─────────────┘   │

- **[重构完成报告](./04-reports/refactoring-completion.md)** - 代码重构完成记录└─────────────────┬───────────────────────────────────┘

- **[设备管理完成报告](./04-reports/employee-device-management-completion.md)** - 设备管理模块完成报告                  │

- **[ADB 配置成功](./04-reports/adb-configuration-success.md)** - ADB 配置和测试报告┌─────────────────▼───────────────────────────────────┐

- **[安装完成](./04-reports/setup-complete.md)** - 项目初始化完成报告│                Core Layer                           │

│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │

### 05. 用户指南 (`05-user-guides/`)│  │Device Mgr   │ │Task Sched   │ │Auth System  │   │

│  └─────────────┘ └─────────────┘ └─────────────┘   │

面向最终用户的操作手册和使用指南。└─────────────────┬───────────────────────────────────┘

                  │

- **[用户使用指南](./USER_GUIDE.md)** - 系统整体使用指南┌─────────────────▼───────────────────────────────────┐

- **[设备管理指南](./05-user-guides/device-management-guide.md)** - 设备管理功能使用说明│              Platform Layer                         │

- **[设备管理用户手册](./05-user-guides/device-management-user-guide.md)** - 设备管理详细操作手册│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │

- **[任务管理用户指南](./05-user-guides/task-management-user-guide.md)** - 任务管理功能使用说明│  │Douyin Auto  │ │XHS Auto     │ │Base Platform│   │

│  └─────────────┘ └─────────────┘ └─────────────┘   │

### 06. 需求文档 (`06-requirements/`)└─────────────────────────────────────────────────────┘

```

项目需求规格说明和功能特性文档。

## 快速开始

- **[完整需求文档](./06-requirements/COMPLETE_REQUIREMENTS.md)** - 项目完整需求规格说明书 (1431 行)

- **[功能需求](./FEATURE_REQUIREMENTS.md)** - 详细功能需求列表### 环境要求

- Windows 10/11

### 07. AI 指令文档 (`07-ai-instructions/`)- Python 3.8+

- Android SDK Platform Tools

GitHub Copilot 和 AI 辅助开发的指令和配置。- 支持ADB调试的Android设备



- **[根项目 AI 指令](./07-ai-instructions/root-copilot-instructions.md)** - 项目根目录 Copilot 指令### 安装步骤

- **[项目 AI 代理指令](./07-ai-instructions/AGENTS.md)** - 主项目 AI 代理配置

- **[员工客户端 AI 代理](./07-ai-instructions/employee-client-agents.md)** - 员工客户端 AI 代理配置1. **克隆项目**

- **[员工客户端 Copilot 工作区指南](./07-ai-instructions/employee-copilot-workspace-guide.md)** - 员工客户端 Copilot 配置```bash

git clone https://github.com/wyw121/Flow_Farm.git

### 08. 开发者文档 (`DEVELOPER.md`)cd Flow_Farm

```

开发者参考文档和 API 说明。

2. **设置Python环境**

- **[开发者文档](./DEVELOPER.md)** - API 接口文档和开发规范```bash

python -m venv venv

---venv\Scripts\activate  # Windows

pip install -r requirements.txt

## 🚀 快速开始```



### 新手入门3. **配置ADB环境**

```bash

1. 阅读 **[完整需求文档](./06-requirements/COMPLETE_REQUIREMENTS.md)** 了解项目整体# 下载Android SDK Platform Tools

2. 查看 **[架构可视化](./01-architecture/ARCHITECTURE_VISUALIZATION_2025.md)** 理解系统架构# 配置PATH环境变量或在config/adb_path.json中设置路径

3. 按照 **[安装指南](./02-development/INSTALL.md)** 配置开发环境adb devices  # 验证设备连接

4. 参考 **[开发指南](./02-development/DEVELOPMENT_GUIDE.md)** 开始开发```



### 系统管理员4. **启动应用**

```bash

1. **[Ubuntu 部署指南](./03-deployment/ubuntu-deployment.md)** - 生产环境部署# 开发模式

2. **[用户使用指南](./USER_GUIDE.md)** - 系统操作手册cd employee-client

python src/main.py --debug

### 员工用户

# 生产模式

1. **[设备管理用户手册](./05-user-guides/device-management-user-guide.md)** - 设备连接和管理cd employee-client

2. **[任务管理用户指南](./05-user-guides/task-management-user-guide.md)** - 任务创建和执行python src/main.py

```

---

## 项目结构

## 📁 项目结构概览

```

```Flow_Farm/

Flow_Farm/├── src/                    # 源代码

├── server-backend/          # Rust + Axum 后端服务│   ├── main.py            # 应用入口

├── server-frontend/         # React + TypeScript 前端│   ├── core/              # 核心模块

├── employee-client/         # Rust + Tauri 员工客户端│   ├── gui/               # 界面模块

├── docs/                    # 📚 文档中心（当前目录）│   ├── platforms/         # 平台自动化

│   ├── 01-architecture/     # 架构设计文档│   ├── auth/              # 权限系统

│   ├── 02-development/      # 开发指南│   └── utils/             # 工具类

│   ├── 03-deployment/       # 部署文档├── config/                # 配置文件

│   ├── 04-reports/          # 项目报告├── data/                  # 数据文件

│   ├── 05-user-guides/      # 用户手册├── docs/                  # 项目文档

│   ├── 06-requirements/     # 需求文档├── tests/                 # 测试文件

│   └── 07-ai-instructions/  # AI 辅助开发指令├── scripts/               # 构建脚本

├── config/                  # 配置文件└── logs/                  # 日志文件

├── data/                    # 数据库文件```

└── deploy/                  # 部署脚本

```## 使用说明



---### 设备连接

1. 开启Android设备的开发者选项

## 📝 文档维护规范2. 启用USB调试模式

3. 连接设备到电脑

### 文档命名规范4. 在应用中扫描并添加设备



- 使用英文或拼音，避免使用中文文件名### 任务配置

- 使用连字符 `-` 分隔单词（kebab-case）1. 选择目标平台（抖音/小红书）

- 使用描述性名称，清晰表达文档内容2. 配置操作参数（关注数量、频率等）

3. 设置执行时间和重复规则

### 文档分类原则4. 启动任务执行



- **01-architecture**: 系统设计、架构图、技术选型### 权限管理

- **02-development**: 开发环境、构建流程、编码规范- **管理员**: 完整的系统控制和配置权限

- **03-deployment**: 部署流程、服务器配置、运维指南- **用户**: 基础的任务执行和查看权限

- **04-reports**: 开发进度、问题修复、完成报告- **访客**: 只读权限，无法执行操作

- **05-user-guides**: 用户操作手册、功能说明

- **06-requirements**: 需求文档、功能规格## 安全说明

- **07-ai-instructions**: AI 辅助开发配置

### 合规使用

### 新增文档流程- ⚠️ **遵守平台规则**: 严格遵守各社交媒体平台的使用条款

- ⚠️ **控制操作频率**: 避免过度操作导致账号风险

1. 确定文档类型，选择合适的分类目录- ⚠️ **保护隐私**: 不收集和泄露用户个人信息

2. 使用规范的文件命名- ⚠️ **合法使用**: 仅用于合法的商业推广目的

3. 添加文档标题和目录

4. 在本 `README.md` 中添加索引链接### 技术安全

5. 提交 Git 更新- 🔒 用户数据加密存储

- 🔒 设备通信加密传输

---- 🔒 操作日志安全记录

- 🔒 代码加密防逆向

## 🔗 相关链接

## 开发指南

- **项目仓库**: [GitHub - Flow_Farm](https://github.com/wyw121/Flow_Farm)

- **问题追踪**: GitHub Issues### 代码规范

- **技术支持**: 查看相关用户指南或联系开发团队- 遵循PEP 8编码规范

- 使用类型注解

---- 添加完整的文档字符串

- 实现完善的错误处理

## 📌 文档更新日志

### 测试要求

| 日期 | 版本 | 更新内容 | 更新人 |```bash

|------|------|----------|--------|# 运行单元测试

| 2025-10-28 | 1.0.0 | 完成文档归档整理，创建分类目录和索引 | AI Assistant |python -m pytest tests/unit/



---# 运行集成测试

python -m pytest tests/integration/

**最后更新**: 2025年10月28日

# 代码覆盖率
python -m pytest --cov=src tests/
```

### 构建部署
```bash
# 构建开发版本
python scripts/build.py --mode development

# 构建加密版本
python scripts/build.py --mode production --encrypt

# 创建分发包
python scripts/package.py --output dist/
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/新功能`)
3. 提交更改 (`git commit -am '添加新功能'`)
4. 推送到分支 (`git push origin feature/新功能`)
5. 创建 Pull Request

## 版本历史

### v1.0.0 (计划中)
- [x] 基础设备管理功能
- [x] 小红书自动化模块
- [ ] 抖音自动化模块
- [ ] 权限管理系统
- [ ] 现代化GUI界面
- [ ] 加密打包系统

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系我们

- 项目地址: https://github.com/wyw121/Flow_Farm
- 问题反馈: [Issues](https://github.com/wyw121/Flow_Farm/issues)
- 开发者: wyw121

---

**免责声明**: 本项目仅供学习和研究使用，使用者需要遵守相关法律法规和平台条款，开发者不承担任何法律责任。
