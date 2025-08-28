---
applyTo: "src/auth/**/*.py"
---

# 权限认证系统开发指令

## 用户管理系统

- 支持用户注册、登录、注销功能
- 实现密码加密存储（使用bcrypt或类似库）
- 支持用户角色分配（管理员、普通用户）
- 实现用户会话管理

## 权限控制机制

```python
from functools import wraps
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class Permission(Enum):
    DEVICE_MANAGE = "device_manage"
    TASK_CREATE = "task_create"
    TASK_EXECUTE = "task_execute"
    SYSTEM_CONFIG = "system_config"
    USER_MANAGE = "user_manage"

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
