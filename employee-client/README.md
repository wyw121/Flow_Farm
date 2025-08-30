# Flow Farm 员工客户端

## 功能概述
- 员工登录认证（需要管理员授权的账号）
- 设备自动化操作界面
- 工作任务执行和监控
- 工作量统计和展示
- 与服务器数据库实时同步
- 离线工作支持

## 技术栈
- **界面框架**: tkinter (轻量级) / PyQt5 (功能丰富)
- **自动化引擎**: ADB + uiautomator2 + Appium
- **数据库通信**: SQLAlchemy + HTTP API
- **认证**: JWT Token
- **配置管理**: JSON + 加密存储
- **日志系统**: Python logging

## 目录结构
```
employee-client/
├── src/                    # 源代码
│   ├── main.py            # 应用程序入口
│   ├── auth/              # 认证和授权
│   │   ├── __init__.py
│   │   ├── login.py       # 登录模块
│   │   ├── token_manager.py # Token管理
│   │   └── api_client.py  # API客户端
│   ├── gui/               # 用户界面
│   │   ├── __init__.py
│   │   ├── main_window.py # 主窗口
│   │   ├── login_dialog.py # 登录对话框
│   │   ├── work_panel.py  # 工作面板
│   │   └── stats_panel.py # 统计面板
│   ├── automation/        # 自动化操作
│   │   ├── __init__.py
│   │   ├── device_manager.py # 设备管理
│   │   ├── task_executor.py # 任务执行器
│   │   └── platforms/     # 平台操作
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
