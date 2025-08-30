---
applyTo: "server-backend/**/*.py"
---

# 服务器后端开发指令

## 适用范围
本指令适用于 `server-backend/` 目录下的所有 Python 文件，专门用于构建 FastAPI 后端服务。

## 技术要求

### 框架和库
- 使用 FastAPI 作为主要 Web 框架
- 使用 SQLAlchemy 作为 ORM
- 使用 Pydantic 进行数据验证
- 使用 JWT 进行身份认证
- 使用 uvicorn 作为 ASGI 服务器

### 三角色权限系统
1. **系统管理员 (SYSTEM_ADMIN)**
   - 权限级别: 1 (最高)
   - 可访问所有 API 端点
   - 可管理用户管理员账户
   - 可查看全系统统计数据

2. **用户管理员 (USER_ADMIN)**
   - 权限级别: 2
   - 只能管理自己公司的员工（最多10个）
   - 可访问计费和结算相关 API
   - 可查看本公司员工数据

3. **员工 (EMPLOYEE)**
   - 权限级别: 3
   - 只能访问基本的数据上报 API
   - 只能查看自己的工作数据
   - 通过客户端进行身份验证

### API 设计规范
- 所有 API 路由使用 `/api/v1/` 前缀
- 使用 RESTful 设计原则
- 每个端点都必须有权限验证装饰器
- 使用 HTTP 状态码标准
- 提供完整的 OpenAPI 文档

### 数据库设计
- 使用 SQLAlchemy 声明式模型
- 所有表必须包含 `created_at` 和 `updated_at` 字段
- 使用外键维护数据完整性
- 实现软删除功能

### 错误处理
- 使用 FastAPI 的 HTTPException
- 创建自定义异常类
- 记录所有错误到日志文件
- 返回用户友好的错误信息

### 安全要求
- 所有密码使用 bcrypt 哈希
- API 密钥和敏感配置使用环境变量
- 实现请求频率限制
- 输入数据严格验证

## 代码示例

### API 路由示例
```python
from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user, require_permission
from app.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/api/v1/users")

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("SYSTEM_ADMIN"))
):
    # 实现用户创建逻辑
    pass
```

### 权限验证示例
```python
from functools import wraps
from fastapi import HTTPException, status

def require_permission(required_role: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user or current_user.role != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## 重要提醒
- 始终验证用户权限
- 记录所有重要操作
- 使用事务确保数据一致性
- 实现适当的缓存策略
- 监控 API 性能指标
