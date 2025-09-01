# Flow Farm 员工客户端 - OneDragon 现代化版本

![OneDragon GUI](https://img.shields.io/badge/GUI-OneDragon%20Style-blue)
![PySide6](https://img.shields.io/badge/Framework-PySide6-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## 🎉 全新界面架构

**Flow Farm 员工客户端已完全重构为 OneDragon 风格的现代化界面！**

基于 OneDragon 项目的界面架构，采用 Microsoft Fluent Design 组件，提供专业、美观、易用的工作体验。

## ✨ 核心功能
- 🔐 **员工登录认证** - JWT Token + 管理员授权
- 📱 **设备自动化管理** - ADB + uiautomator2 一体化界面
- ⚡ **智能任务执行** - 可视化任务配置和监控
- 📊 **实时数据统计** - 工作量统计和效率分析
- 🔄 **服务器同步** - 实时数据同步和离线工作支持
- 🎨 **现代化界面** - OneDragon 风格的专业界面设计

## 🚀 快速开始

### 启动 OneDragon GUI (推荐)
```bash
# 启动现代化界面
python src/main.py --gui --debug

# 或直接运行优化版本
python src/main_onedragon_optimized.py
```

## 🏗️ 技术架构

### OneDragon GUI 架构
- **界面框架**: PySide6 6.6.0+ (Qt6 现代化框架)
- **设计语言**: Microsoft Fluent Design
- **组件库**: qfluentwidgets 1.7.0 (专业组件)
- **图标系统**: qtawesome 1.3.1
- **架构模式**: MVC + 信号槽 + 组件化设计

### 自动化引擎
- **设备控制**: ADB + uiautomator2 + Appium
- **任务调度**: 异步任务队列 + 状态监控
- **数据持久化**: SQLAlchemy + HTTP API
- **认证系统**: JWT Token + 加密存储

## 📂 项目结构
```
employee-client/
├── src/                           # 源代码目录
│   ├── main.py                   # 🚀 OneDragon 风格主入口
│   ├── main_onedragon_optimized.py # 💎 OneDragon GUI 核心实现
│   ├── auth/                     # 🔐 认证和授权模块
│   │   ├── login.py             # 登录管理
│   │   └── token_manager.py     # Token管理
│   ├── gui/                     # 🎨 现代化用户界面
│   │   ├── onedragon_base/      # 🏗️ OneDragon 基础架构
│   │   │   ├── app_window.py    # 主窗口类 (MSFluentWindow)
│   │   │   ├── base_interface.py # 基础界面类
│   │   │   └── vertical_scroll_interface.py # 滚动界面基类
│   │   ├── backup_old_gui/      # 📦 旧版GUI备份
│   │   ├── components/          # 🧩 可复用组件
│   │   ├── dialogs/            # 💬 对话框组件
│   │   ├── views/              # 📄 视图组件
│   │   └── windows/            # 🪟 窗口组件
│   ├── automation/             # 🤖 自动化操作引擎
│   │   ├── device_manager.py   # 设备管理
│   │   ├── task_executor.py    # 任务执行器
│   │   └── platforms/          # 平台适配器
│   ├── sync/                   # 🔄 数据同步模块
│   ├── utils/                  # 🛠️ 工具模块
│   └── config/                 # ⚙️ 配置管理
├── requirements.txt            # 📋 依赖清单 (OneDragon 兼容)
├── README_OneDragon.md        # 📖 OneDragon 架构详细文档
├── ONEDRAGON_GUI_MIGRATION.md # 📝 GUI 重构说明
└── README.md                  # 🌟 项目主文档
```

## 🎯 界面特色

### 🏠 主页界面
- **📊 状态卡片**: 系统状态、设备数量、任务统计、工作效率
- **📈 实时监控**: 系统运行状态和性能指标
- **📋 活动日志**: 最近操作和系统事件展示

### 📱 设备管理界面
- **➕ 设备添加**: 一键扫描和连接新设备
- **🔄 状态刷新**: 实时设备连接状态监控
- **📊 设备表格**: 设备信息、状态、操作统一管理

### ⚡ 任务管理界面
- **📝 任务创建**: 直观的任务配置表单
- **📊 进度监控**: 实时任务执行进度条
- **🏷️ 状态管理**: 运行中、队列中、已完成状态分类

### 📊 数据统计界面
- **📈 效率分析**: 工作效率和性能统计
- **📊 数据可视化**: 图表化数据展示（开发中）

### ⚙️ 系统设置界面
- **🎨 主题配置**: 明亮/暗黑主题切换
- **🔧 系统偏好**: 个性化设置和配置

## 🔧 开发环境
│   ├── sync/              # 数据同步
│   │   ├── __init__.py
│   │   ├── kpi_uploader.py # KPI数据上传
│   │   ├── task_downloader.py # 任务下载
│   │   └── offline_cache.py # 离线缓存
│   ├── config/            # 配置管理
│   │   ├── __init__.py
│   │   ├── settings.py    # 设置管理
│   │   └── encryption.py  # 配置加密
│   └── utils/             # 工具函数
│       ├── __init__.py
│       ├── logger.py      # 日志配置
│       └── validator.py   # 数据验证
├── config/                # 配置文件
│   ├── client_config.json # 客户端配置
│   └── server_config.json # 服务器连接配置
├── tests/                 # 测试文件
├── requirements.txt       # 依赖列表
└── README.md             # 说明文档
```

## 核心功能
1. **认证登录**: 使用管理员分配的账号登录
2. **设备操作**: 连接和控制Android设备
3. **任务执行**: 执行抖音、小红书等平台操作
4. **数据上传**: 实时上传工作量KPI到服务器
5. **离线工作**: 网络断开时保存数据，恢复后同步
