# 认证系统开发指令

## 适用范围
这些指令适用于 `src/auth/**/*.py` 路径下的所有认证相关代码文件。

## 技术栈

### 核心技术
- **认证框架**: JWT (JSON Web Tokens)
- **密码加密**: bcrypt / argon2
- **会话管理**: Redis / 内存存储
- **权限控制**: RBAC (基于角色的访问控制)
- **数据验证**: Pydantic / marshmallow
- **加密工具**: cryptography

## 三角色权限架构

### 1. 系统管理员 (SystemAdmin)
```python
class SystemAdmin:
    """系统管理员 - 权限级别: 1 (最高)"""

    PERMISSIONS = [
        "user:create",           # 创建用户管理员
        "user:read:all",         # 查看所有用户
        "user:update:all",       # 更新所有用户
        "user:delete:all",       # 删除用户
        "system:settings",       # 系统设置
        "billing:configure",     # 计费配置
        "reports:global",        # 全局报表
        "audit:logs",           # 审计日志
    ]

    MAX_MANAGED_USERS = None  # 无限制
```

### 2. 用户管理员 (UserAdmin)
```python
class UserAdmin:
    """用户管理员 - 权限级别: 2"""

    PERMISSIONS = [
        "employee:create",       # 创建员工 (最多10个)
        "employee:read:company", # 查看本公司员工
        "employee:update:company", # 更新本公司员工
        "employee:delete:company", # 删除本公司员工
        "billing:view:company",  # 查看本公司计费
        "reports:company",       # 本公司报表
        "tasks:assign",         # 分配任务
    ]

    MAX_MANAGED_USERS = 10    # 最多管理10个员工
```

### 3. 员工 (Employee)
```python
class Employee:
    """员工 - 权限级别: 3 (最低)"""

    PERMISSIONS = [
        "task:execute",         # 执行任务
        "work_record:create",   # 创建工作记录
        "work_record:read:self", # 查看自己的工作记录
        "device:manage:self",   # 管理自己的设备
        "profile:update:self",  # 更新自己的资料
    ]

    MAX_MANAGED_USERS = 0     # 不能管理其他用户
```

### 权限验证机制
- 基于JWT的身份认证
- 角色继承权限模型
- 操作级别权限控制
- 会话状态管理

## 实现规范

### 用户认证
```python
class AuthManager:
    def authenticate(self, username: str, password: str) -> bool:
        # 实现用户名密码验证
        pass

    def generate_token(self, user: User) -> str:
        # 生成JWT Token
        pass

    def verify_token(self, token: str) -> Optional[User]:
        # 验证Token有效性
        pass
```

### 权限控制
```python
def require_permission(permission: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            current_user = get_current_user()
            if not has_permission(current_user, permission):
                raise PermissionDeniedError()
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### 权限枚举定义
```python
from enum import Enum

class UserRole(Enum):
    SYSTEM_ADMIN = "system_admin"
    USER_ADMIN = "user_admin"
    EMPLOYEE = "employee"

class Permission(Enum):
    # 系统管理员专有权限
    MANAGE_USER_ADMINS = "manage_user_admins"
    VIEW_ALL_DATA = "view_all_data"
    SYSTEM_CONFIG = "system_config"
    BILLING_RULES = "billing_rules"

    # 用户管理员权限
    MANAGE_EMPLOYEES = "manage_employees"
    VIEW_COMPANY_DATA = "view_company_data"
    BILLING_MANAGEMENT = "billing_management"
    ADJUST_WORKLOAD = "adjust_workload"

    # 员工权限
    UPLOAD_DATA = "upload_data"
    RECEIVE_TASKS = "receive_tasks"
    VIEW_PERSONAL_DATA = "view_personal_data"
    DEVICE_CONTROL = "device_control"
```

## 安全要求
- 密码哈希存储（bcrypt）
- Token有效期管理
- 防止暴力破解
- 敏感操作审计日志
- 加密传输敏感数据

## 数据库设计
- 用户表：存储基本用户信息
- 角色表：定义角色权限
- 权限表：具体权限定义
- 会话表：活跃会话管理
- 审计表：操作日志记录

## 重要提醒
- 严格验证用户输入
- 实现适当的错误处理
- 记录所有权限相关操作
- 定期清理过期会话
- 监控异常登录行为

def require_permission(permission: Permission):
    """权限检查装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.current_user.has_permission(permission):
                raise PermissionError(f"需要权限: {permission.value}")
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
```

## 角色权限映射

- 管理员：全部权限
- 普通用户：基础操作权限（任务执行、查看状态）
- 访客：只读权限

## 安全机制

- 实现登录失败次数限制
- 添加会话超时机制
- 记录所有权限相关操作日志
- 支持强制用户下线功能

## 数据库设计

```sql
-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 会话表
CREATE TABLE sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```
