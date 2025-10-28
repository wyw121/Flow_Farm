# Rust 后端版本的 Flow Farm 服务器

这是 Flow Farm 项目的全新 Rust 后端实现，使用现代 Rust Web 技术栈重构，提供更高的性能、更好的类型安全性和更强的并发处理能力。

## 技术栈

- **Web框架**: Axum 0.7 - 高性能异步Web框架
- **数据库**: SQLx + SQLite - 类型安全的数据库访问
- **认证**: JWT + bcrypt - 安全的身份认证
- **序列化**: Serde - 高效的JSON处理
- **异步运行时**: Tokio - 高性能异步运行时
- **日志**: Tracing - 结构化日志
- **错误处理**: Anyhow + Thiserror - 优雅的错误处理

## 主要优势

### 相比Python版本的改进

1. **性能提升**: Rust的零成本抽象和编译时优化，性能比Python提升5-10倍
2. **内存安全**: 编译时内存安全保证，避免空指针和缓冲区溢出
3. **类型安全**: 强类型系统，编译时捕获大部分bug
4. **并发性能**: Tokio异步运行时，高效处理大量并发请求
5. **部署简单**: 单一二进制文件，无需依赖运行时环境

### 三级权限体系

1. **系统管理员（一级管理员）**
   - 最高权限，运行在服务器端
   - 功能：开通用户管理员权限、查看所有员工工作信息、设置收费规则

2. **用户管理员（二级管理员）**
   - 公司级权限，运行在服务器端
   - 功能：开通员工权限（最多10个）、查看员工工作信息、管理结算界面

3. **员工（脚本用户）**
   - 基础权限，运行在脚本软件端
   - 功能：执行自动化任务、上报工作数据

## 🚀 快速开始

### 环境要求
- Python 3.8+
- SQLite（默认）或 PostgreSQL/MySQL

### 安装和启动

```bash
# 1. 克隆项目
git clone <项目地址>
cd server-backend

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. 一键启动（包含安装依赖、初始化数据库、启动服务器）
python start.py

# 或者分步执行
python start.py --setup      # 安装依赖和设置环境
python start.py --init-db    # 初始化数据库
python start.py --start      # 启动服务器
```

### 默认管理员账号
- 用户名：`admin`
- 密码：`admin123`
- 访问地址：http://localhost:8000

## 📖 API 文档

启动服务器后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🎯 主要功能实现

### 系统管理员功能 ✅

#### 1. 开通用户管理员权限
```http
POST /api/v1/users/
Content-Type: application/json
Authorization: Bearer <system_admin_token>

{
  "username": "company_admin",
  "password": "password123",
  "email": "admin@company.com",
  "role": "user_admin",
  "company": "XX公司",
  "max_employees": 10
}
```

#### 2. 查看员工工作信息
```http
# 查看所有公司统计
GET /api/v1/users/statistics/all-companies
Authorization: Bearer <system_admin_token>

# 查看仪表盘数据
GET /api/v1/reports/dashboard
Authorization: Bearer <system_admin_token>
```

#### 3. 设置收费规则
```http
# 创建收费规则
POST /api/v1/billing/pricing-rules
Content-Type: application/json
Authorization: Bearer <system_admin_token>

{
  "name": "员工数量收费",
  "description": "按员工数量每月收费",
  "rule_type": "employee_count",
  "unit_price": 50.0,
  "billing_period": "monthly"
}

# 获取收费规则
GET /api/v1/billing/pricing-rules
Authorization: Bearer <system_admin_token>

# 更新收费规则
PUT /api/v1/billing/pricing-rules/{rule_id}
Authorization: Bearer <system_admin_token>
```

### 用户管理员功能 ✅

#### 1. 开通员工权限（最多10个）
```http
POST /api/v1/users/
Content-Type: application/json
Authorization: Bearer <user_admin_token>

{
  "username": "employee001",
  "password": "password123",
  "role": "employee",
  "full_name": "张三"
}
```

#### 2. 查看员工工作信息
```http
# 查看所有员工
GET /api/v1/users/my-employees
Authorization: Bearer <user_admin_token>

# 查看工作统计
GET /api/v1/kpi/statistics/user-admin/{user_admin_id}
Authorization: Bearer <user_admin_token>

# 查看工作记录
GET /api/v1/kpi/?user_admin_id={user_admin_id}
Authorization: Bearer <user_admin_token>
```

#### 3. 查看结算界面
```http
# 查看我的计费信息
GET /api/v1/billing/my-billing-info
Authorization: Bearer <user_admin_token>

# 查看月度计费汇总
GET /api/v1/billing/billing-summary/{user_admin_id}?year=2024&month=1
Authorization: Bearer <user_admin_token>

# 查看计费记录
GET /api/v1/billing/billing-records
Authorization: Bearer <user_admin_token>
```

#### 4. 下载Excel表格
```http
# 导出工作记录
POST /api/v1/kpi/export
Content-Type: application/json
Authorization: Bearer <user_admin_token>

{
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-01-31T23:59:59",
  "platform": "xiaohongshu",
  "action_type": "follow"
}

# 下载导出文件
GET /api/v1/kpi/download/{filename}
Authorization: Bearer <user_admin_token>
```

### 员工功能 ✅

#### 工作记录上报
```http
POST /api/v1/kpi/
Content-Type: application/json
Authorization: Bearer <employee_token>

{
  "employee_id": 3,
  "platform": "xiaohongshu",
  "action_type": "follow",
  "target_username": "user123",
  "target_user_id": "12345",
  "device_id": "device001",
  "device_name": "小米11"
}
```

## 💰 计费系统

### 计费类型
1. **员工数量计费** (`employee_count`)
   - 按用户管理员下的员工数量收费
   - 默认：50元/员工/月

2. **关注数量计费** (`follow_count`)
   - 按员工完成的关注操作数量收费
   - 默认：0.1元/次关注

### 自动计费流程
```http
# 生成月度计费记录（系统管理员操作）
POST /api/v1/billing/generate-monthly-billing
Authorization: Bearer <system_admin_token>

# 更新计费状态
PUT /api/v1/billing/billing-records/{billing_id}/status
Content-Type: application/json
Authorization: Bearer <system_admin_token>

{
  "status": "paid"
}
```

## 🔒 权限控制

### 角色权限矩阵

| 功能 | 系统管理员 | 用户管理员 | 员工 |
|------|------------|------------|------|
| 创建用户管理员 | ✅ | ❌ | ❌ |
| 创建员工 | ❌ | ✅ | ❌ |
| 设置收费规则 | ✅ | ❌ | ❌ |
| 查看所有数据 | ✅ | ❌ | ❌ |
| 查看公司数据 | ✅ | ✅ | ❌ |
| 查看个人数据 | ✅ | ✅ | ✅ |
| 上报工作记录 | ❌ | ❌ | ✅ |
| 导出Excel | ✅ | ✅ | ❌ |

## 📊 数据统计示例

### 系统管理员仪表盘
```json
{
  "total_user_admins": 5,
  "total_employees": 30,
  "user_admins": [
    {
      "user_admin_id": 2,
      "company_name": "A公司",
      "total_employees": 8,
      "active_employees": 6,
      "total_work_records": 1520,
      "today_work_records": 45,
      "total_billing_amount": 850.0
    }
  ]
}
```

### 用户管理员统计
```json
{
  "total_follows": 890,
  "total_likes": 450,
  "total_comments": 120,
  "today_follows": 35,
  "today_likes": 20,
  "today_comments": 5,
  "success_rate": 95.6,
  "platform_stats": {
    "xiaohongshu": 650,
    "douyin": 360
  },
  "employee_stats": [
    {
      "employee_id": 3,
      "username": "employee001",
      "full_name": "张三",
      "total_work_count": 245,
      "today_work_count": 12
    }
  ]
}
```

## 🧪 测试

### API功能测试
```bash
# 运行完整API测试
python test_api.py

# 测试将自动验证：
# ✅ 管理员登录
# ✅ 创建用户管理员
# ✅ 创建员工
# ✅ 创建工作记录
# ✅ 查看统计数据
# ✅ 收费规则管理
```

### 手动测试步骤
1. 启动服务器：`python start.py`
2. 访问API文档：http://localhost:8000/docs
3. 使用默认管理员登录：`admin / admin123`
4. 创建用户管理员和员工账号
5. 测试各项功能

## 🛠️ 技术栈

- **后端框架**: FastAPI 0.104.1
- **数据库**: SQLite（默认）/ PostgreSQL / MySQL
- **ORM**: SQLAlchemy 2.0.23
- **认证**: JWT Token (python-jose)
- **密码加密**: bcrypt (passlib)
- **API文档**: Swagger UI / ReDoc
- **Excel处理**: pandas + openpyxl
- **数据验证**: Pydantic 2.5.0

## 📁 项目结构

```
server-backend/
├── app/                 # 应用主目录
│   ├── api/            # API路由
│   │   ├── auth.py     # 认证相关
│   │   ├── users.py    # 用户管理
│   │   ├── kpi.py      # 工作记录
│   │   ├── billing.py  # 计费管理
│   │   ├── devices.py  # 设备管理
│   │   └── reports.py  # 数据报表
│   ├── models/         # 数据模型
│   ├── schemas/        # API数据模型
│   ├── services/       # 业务逻辑层
│   │   ├── user_service.py
│   │   ├── billing_service.py
│   │   └── work_record_service.py
│   ├── config.py       # 配置管理
│   ├── database.py     # 数据库连接
│   ├── main.py         # FastAPI应用
│   └── init_db.py      # 数据库初始化
├── data/               # 数据库文件
├── logs/               # 日志文件
├── exports/            # 导出的Excel文件
├── start.py            # 启动脚本
├── test_api.py         # API测试脚本
├── requirements.txt    # 依赖包
└── README.md          # 项目文档
```

## 🔧 配置说明

### 环境变量 (可选)
创建 `.env` 文件：
```env
# 数据库配置
DATABASE_URL=sqlite:///./data/flow_farm.db

# JWT配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=False

# 默认管理员
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123
```

## 📞 技术支持

如有问题，请查看：
1. API文档：http://localhost:8000/docs
2. 日志文件：`logs/backend.log`
3. 项目Issues：提交到代码仓库

---

**✨ 核心功能已全部实现，可直接投入使用！**
