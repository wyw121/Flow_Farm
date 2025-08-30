# Flow Farm 服务器后端

## 功能概述
- 员工账号管理和授权
- 员工工作量KPI数据记录
- 设备使用情况监控
- 数据统计和分析
- RESTful API服务

## 技术栈
- **框架**: FastAPI
- **数据库**: PostgreSQL / MySQL
- **ORM**: SQLAlchemy
- **认证**: JWT Token
- **部署**: Docker + Nginx

## 目录结构
```
server-backend/
├── app/                    # 主应用程序
│   ├── __init__.py
│   ├── main.py            # FastAPI应用入口
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库连接
│   ├── models/            # 数据模型
│   ├── schemas/           # Pydantic模式
│   ├── crud/              # 数据库操作
│   ├── api/               # API路由
│   ├── auth/              # 认证和授权
│   └── utils/             # 工具函数
├── alembic/               # 数据库迁移
├── tests/                 # 测试
├── docker/                # Docker配置
├── requirements.txt       # 依赖
└── README.md             # 说明文档
```

## API 接口
- `/auth/` - 认证相关
- `/users/` - 用户管理
- `/kpi/` - KPI数据
- `/devices/` - 设备管理
- `/reports/` - 数据报表
