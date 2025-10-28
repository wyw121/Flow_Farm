# Flow Farm - 社交平台自动化获客管理系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Rust](https://img.shields.io/badge/rust-1.70+-orange.svg)](https://www.rust-lang.org/)
[![React](https://img.shields.io/badge/react-18+-61dafb.svg)](https://reactjs.org/)
[![Tauri](https://img.shields.io/badge/tauri-2.0-24c8db.svg)](https://tauri.app/)

## 📖 项目简介

Flow Farm 是一个专业的**社交平台自动化获客管理系统**，为企业和个人提供多平台社交媒体用户关注、监控和精准获客的自动化解决方案。

### 核心特性

- 🚀 **多平台支持** - 覆盖小红书、抖音等主流社交媒体平台
- 🤖 **智能自动化** - 通讯录管理和精准获客（同行监控）
- 📱 **设备管理** - 支持最多 10 台设备并发执行任务
- 👥 **三角色架构** - 系统管理员、用户管理员、员工三级权限
- 💰 **透明计费** - 基于实际成功关注数量的公平计费系统
- 📊 **实时监控** - 关注统计、任务进度、余额检查

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    Flow Farm 生态系统                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │   服务器前端      │  │   服务器后端      │            │
│  │ React + TypeScript│  │  Rust + Axum     │            │
│  │   端口: 3000      │  │   端口: 8000     │            │
│  └──────────────────┘  └──────────────────┘            │
│           ↓                      ↓                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │              员工客户端                            │   │
│  │          Rust + Tauri 2.0                        │   │
│  │      (桌面 GUI 应用程序)                          │   │
│  └─────────────────────────────────────────────────┘   │
│                      ↓                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │         ADB 设备管理 (最多 10 台)                  │   │
│  │    小红书 / 抖音 / 快手 / B站 自动化               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| **服务器后端** | Rust + Axum + SQLite | RESTful API 服务 |
| **服务器前端** | React 18 + TypeScript + Ant Design 5 | 管理员 Web 界面 |
| **员工客户端** | Rust + Tauri 2.0 + HTML/CSS/JS | 跨平台桌面应用 |
| **设备控制** | ADB (Android Debug Bridge) | Android 设备自动化 |

## 📚 完整文档

所有文档已整理归档到 **[docs/](./docs/)** 目录，按以下分类组织：

### 📂 文档导航

- **[📚 文档中心主页](./docs/README.md)** - 完整的文档索引和导航
- **[📊 文档目录树](./docs/DOCUMENT_TREE.md)** - 可视化文档结构

### 快速链接

| 文档类型 | 链接 | 说明 |
|---------|------|------|
| 🏛️ **架构设计** | [01-architecture/](./docs/01-architecture/) | 系统架构图和技术分析 |
| 💻 **开发指南** | [02-development/](./docs/02-development/) | 环境配置和开发流程 |
| 🚀 **部署文档** | [03-deployment/](./docs/03-deployment/) | 生产环境部署指南 |
| 📝 **项目报告** | [04-reports/](./docs/04-reports/) | 开发进度和完成报告 |
| 📖 **用户手册** | [05-user-guides/](./docs/05-user-guides/) | 操作指南和使用说明 |
| 📋 **需求文档** | [06-requirements/](./docs/06-requirements/) | 完整需求规格说明书 |
| 🤖 **AI 指令** | [07-ai-instructions/](./docs/07-ai-instructions/) | Copilot 辅助开发配置 |

## 🚀 快速开始

### 1. 环境要求

- **Rust**: 1.70+ (用于后端和员工客户端)
- **Node.js**: 18+ (用于前端开发)
- **Python**: 3.8+ (用于构建脚本)
- **ADB**: Android Debug Bridge (用于设备控制)

### 2. 克隆项目

```bash
git clone https://github.com/wyw121/Flow_Farm.git
cd Flow_Farm
```

### 3. 开发模式启动

#### Windows 用户

```bash
# 一键启动开发环境（前后端分离）
dev-start.bat
```

#### Linux/Mac 用户

```bash
# 一键启动开发环境
chmod +x dev-start.sh
./dev-start.sh
```

### 4. 访问系统

- **前端界面**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/api-docs

详细安装步骤请参考 **[安装指南](./docs/02-development/INSTALL.md)**

## 📖 推荐阅读顺序

### 新手入门

1. **[完整需求文档](./docs/06-requirements/COMPLETE_REQUIREMENTS.md)** (1431 行) - 了解项目全貌
2. **[架构可视化](./docs/01-architecture/ARCHITECTURE_VISUALIZATION_2025.md)** (483 行) - 理解系统架构
3. **[安装指南](./docs/02-development/INSTALL.md)** - 配置开发环境
4. **[开发指南](./docs/02-development/DEVELOPMENT_GUIDE.md)** (205 行) - 开始开发

### 系统管理员

1. **[Ubuntu 部署指南](./docs/03-deployment/ubuntu-deployment.md)** - 生产环境部署
2. **[用户使用指南](./docs/USER_GUIDE.md)** - 系统管理操作

### 员工用户

1. **[设备管理用户手册](./docs/05-user-guides/device-management-user-guide.md)** - 设备连接管理
2. **[任务管理用户指南](./docs/05-user-guides/task-management-user-guide.md)** - 任务创建执行

## 🛠️ 项目结构

```
Flow_Farm/
├── server-backend/          # Rust + Axum 后端服务
│   ├── src/                 # 源代码
│   ├── Cargo.toml           # Rust 依赖配置
│   └── ...
├── server-frontend/         # React + TypeScript 前端
│   ├── src/                 # 源代码
│   ├── package.json         # NPM 依赖配置
│   └── ...
├── employee-client/         # Rust + Tauri 员工客户端
│   ├── src-tauri/           # Rust 后端代码
│   ├── src/                 # 前端资源
│   └── ...
├── docs/                    # 📚 完整文档库（36 份文档）
│   ├── 01-architecture/     # 架构设计文档
│   ├── 02-development/      # 开发指南
│   ├── 03-deployment/       # 部署文档
│   ├── 04-reports/          # 项目报告
│   ├── 05-user-guides/      # 用户手册
│   ├── 06-requirements/     # 需求文档
│   └── 07-ai-instructions/  # AI 辅助开发
├── config/                  # 配置文件
├── data/                    # 数据库文件
├── deploy/                  # 部署脚本
├── dev-start.bat            # Windows 开发启动脚本
├── dev-start.sh             # Linux/Mac 开发启动脚本
└── README.md                # 本文件
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看以下文档：

- **[开发者文档](./docs/DEVELOPER.md)** - API 接口和开发规范
- **[AI 指令文档](./docs/07-ai-instructions/)** - GitHub Copilot 辅助开发配置

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📞 联系方式

- **项目仓库**: [GitHub - Flow_Farm](https://github.com/wyw121/Flow_Farm)
- **问题反馈**: [GitHub Issues](https://github.com/wyw121/Flow_Farm/issues)
- **文档中心**: [docs/](./docs/)

---

**最后更新**: 2025年10月28日

**文档统计**: 36 份完整文档，涵盖架构、开发、部署、用户指南等

访问 **[文档中心](./docs/)** 获取完整的项目文档 📚
