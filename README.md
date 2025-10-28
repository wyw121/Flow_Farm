# Flow Farm - 市场调研与客户拜访管理平台

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Rust](https://img.shields.io/badge/rust-1.70+-orange.svg)](https://www.rust-lang.org/)
[![React](https://img.shields.io/badge/react-18+-61dafb.svg)](https://reactjs.org/)
[![Tauri](https://img.shields.io/badge/tauri-2.0-24c8db.svg)](https://tauri.app/)

## 📖 项目简介

Flow Farm 是一个专注于**市场调研与客户拜访管理**的垂直行业工具，为B2B企业提供从市场洞察到客户关系管理的一体化解决方案。

### 核心特性

- 🎯 **市场调研管理** - 问卷设计、数据采集、分析报告生成
- 👔 **客户拜访跟踪** - 拜访计划、行程管理、拜访记录
- � **数据分析引擎** - 市场趋势分析、客户画像、竞品对比
- 📱 **移动端支持** - 外勤人员实时数据同步和离线作业
- 👥 **三角色架构** - 系统管理员、调研经理、外勤员工三级权限
- � **企业级功能** - 多公司管理、费用控制、KPI 统计
- � **数据安全** - 敏感数据加密、访问审计、权限隔离

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│           Flow Farm 市场调研与客户拜访管理平台              │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │   管理后台        │  │   业务后端        │            │
│  │ React + TypeScript│  │  Rust + Axum     │            │
│  │   端口: 3000      │  │   端口: 8000     │            │
│  └──────────────────┘  └──────────────────┘            │
│     (调研经理使用)            ↓                          │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │            外勤员工客户端                           │   │
│  │          Rust + Tauri 2.0                        │   │
│  │      (桌面 + 移动端应用)                          │   │
│  └─────────────────────────────────────────────────┘   │
│                      ↓                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │      核心业务功能                                   │   │
│  │  • 市场调研问卷设计与数据采集                       │   │
│  │  • 客户拜访计划与行程管理                          │   │
│  │  • 拜访记录（照片、语音、定位）                     │   │
│  │  • 费用报销管理                                    │   │
│  │  • 数据分析与报表生成                              │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| **服务器后端** | Rust + Axum + SQLite | RESTful API 服务 |
| **服务器前端** | React 18 + TypeScript + Ant Design 5 | 调研经理管理后台 |
| **外勤客户端** | Rust + Tauri 2.0 + HTML/CSS/JS | 跨平台移动应用 |
| **数据分析** | ECharts + 自定义算法 | 市场洞察和客户画像 |

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

- **Rust**: 1.70+ (用于后端和外勤客户端)
- **Node.js**: 18+ (用于管理后台前端开发)
- **Python**: 3.8+ (用于构建脚本和数据分析工具)
- **SQLite**: 3.35+ (数据存储)

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

1. **[完整需求文档](./docs/06-requirements/COMPLETE_REQUIREMENTS.md)** (1431 行) - 了解市场调研和客户拜访业务全貌
2. **[架构可视化](./docs/01-architecture/ARCHITECTURE_VISUALIZATION_2025.md)** (483 行) - 理解系统架构和数据流
3. **[安装指南](./docs/02-development/INSTALL.md)** - 配置开发环境
4. **[开发指南](./docs/02-development/DEVELOPMENT_GUIDE.md)** (205 行) - 开始开发

### 调研经理

1. **[Ubuntu 部署指南](./docs/03-deployment/ubuntu-deployment.md)** - 生产环境部署
2. **[用户使用指南](./docs/USER_GUIDE.md)** - 调研管理和数据分析操作

### 外勤员工

1. **[客户端用户手册](./docs/05-user-guides/device-management-user-guide.md)** - 移动端使用指南
2. **[拜访管理指南](./docs/05-user-guides/task-management-user-guide.md)** - 客户拜访记录与报销

## 🛠️ 项目结构

```
Flow_Farm/
├── server-backend/          # Rust + Axum 后端服务
│   ├── src/                 # 源代码
│   ├── Cargo.toml           # Rust 依赖配置
│   └── ...
├── server-frontend/         # React + TypeScript 管理后台
│   ├── src/                 # 源代码
│   ├── package.json         # NPM 依赖配置
│   └── ...
├── employee-client/         # Rust + Tauri 外勤客户端
│   ├── src-tauri/           # Rust 后端代码
│   ├── src/                 # 前端资源
│   └── ...
├── docs/                    # 📚 完整文档库（36 份文档）
│   ├── 01-architecture/     # 架构设计文档
│   ├── 02-development/      # 开发指南
│   ├── 03-deployment/       # 部署文档
│   ├── 04-reports/          # 项目报告
│   ├── 05-user-guides/      # 用户手册
│   ├── 06-requirements/     # 需求文档（含垂直领域专属需求）
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
