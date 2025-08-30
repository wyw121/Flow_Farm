# Flow Farm - 计费自动化流量农场系统

## 🚀 项目概述

Flow Farm 是一个企业级计费自动化流量农场系统，专为多角色权限管理和社交媒体自动化操作而设计。系统采用三角色架构，通过现代化技术栈实现高效的设备管理、任务调度和计费系统。

## 🏗️ 系统架构

### 三角色架构设计

#### 🔑 系统管理员 (一级管理员，服务器端)
- **权限级别**: 最高权限
- **主要功能**:
  - 开通用户管理员权限
  - 查看所有员工工作信息和统计数据  
  - 设置收费规则和计费标准
  - 系统配置和监控

#### 👥 用户管理员 (二级管理员，服务器端)
- **权限级别**: 公司级权限
- **主要功能**:
  - 开通员工权限（最多10个用户）
  - 查看本公司员工工作信息
  - 查看结算界面，调整关注数量
  - 扣费计划管理

#### 💻 员工 (脚本用户，桌面客户端)
- **权限级别**: 操作级权限
- **主要功能**:
  - 多设备自动化控制
  - 抖音、小红书关注引流操作
  - 工作数据上传和同步
  - 任务执行和状态汇报

## 🛠️ 技术栈

### 服务器端技术栈
- **后端**: FastAPI + Python 3.8+ + SQLAlchemy
- **前端**: Vue.js 3 + TypeScript + Vite + Element Plus
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: JWT + OAuth2
- **部署**: Docker + Nginx

### 员工客户端技术栈
- **GUI框架**: tkinter (主要) / PyQt5 (备选)
- **自动化**: ADB + uiautomator2 + Appium
- **数据存储**: SQLite (本地缓存) + REST API
- **加密**: PyInstaller + 自定义加密算法
- **通信**: requests + websocket-client

## 📁 项目结构

```
Flow_Farm/
├── 🌐 server-backend/          # 服务器后端 (FastAPI)
├── 🖥️ server-frontend/         # 服务器前端 (Vue.js 3)
├── 💻 employee-client/         # 员工客户端 (Python GUI)
├── 📝 .github/                # GitHub配置和指令
│   ├── copilot-instructions.md
│   ├── instructions/           # 模块化指令
│   └── prompts/               # 提示文件
├── 🔧 scripts/                # 构建和部署脚本
├── 📊 docs/                   # 项目文档
├── 🧪 tests/                  # 测试文件
└── ⚙️ config/                 # 全局配置
```

## 🚀 快速开始

### 环境要求
- **Python**: 3.8+ (后端和客户端)
- **Node.js**: 18+ (前端)
- **Android SDK**: Platform Tools (ADB)
- **Docker**: (可选，用于部署)

### 初始化项目
```bash
# 克隆项目
git clone <repository-url>
cd Flow_Farm

# 初始化所有模块
python scripts/init_project.py

# 或者分别初始化
cd server-backend && python -m venv venv && pip install -r requirements.txt
cd server-frontend && npm install
cd employee-client && python -m venv venv && pip install -r requirements.txt
```

### 启动开发环境
```bash
# 启动服务器后端 (终端1)
cd server-backend
python -m uvicorn app.main:app --reload

# 启动服务器前端 (终端2)  
cd server-frontend
npm run dev

# 启动员工客户端 (终端3)
cd employee-client
python src/main.py --gui --debug
```

## 📚 文档导航

- **[开发者指南](DEVELOPER.md)** - 详细的开发说明和API文档
- **[用户手册](USER_GUIDE.md)** - 用户操作指南
- **[功能需求](FEATURE_REQUIREMENTS.md)** - 详细功能规格说明
- **[GitHub Copilot配置](.github/copilot-instructions.md)** - AI辅助开发配置

## 🔧 开发工具配置

### VS Code 推荐扩展
- Python Extension Pack
- Vue - Official
- TypeScript Vue Plugin (Volar)
- GitHub Copilot
- Thunder Client (API测试)

### 代码规范
- **Python**: PEP 8 + Black 格式化
- **TypeScript/Vue**: ESLint + Prettier
- **提交信息**: Conventional Commits

## 🛡️ 安全和合规

### 重要提醒
1. **始终遵循相关平台的使用条款和法律法规**
2. **合理控制操作频率，避免被平台检测为异常行为**
3. **定期备份重要数据和配置**
4. **监控设备状态，避免过度使用导致设备损坏**
5. **保护用户隐私，严格控制数据访问权限**

### 数据安全
- 用户数据加密存储
- API通信HTTPS加密
- 设备标识信息脱敏
- 操作日志安全存储

## 📞 支持与反馈

如有问题或建议，请通过以下方式联系：
- 创建 GitHub Issue
- 查看文档中的故障排除部分
- 联系开发团队

---

**注意**: 本项目仅供学习和研究使用，请确保在使用过程中遵守相关法律法规和平台条款。
