"""
认证相关API路由
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import AuditLog, LoginLog, User
from ..schemas import ChangePasswordRequest, LoginRequest, LoginResponse, UserResponse
from ..services.user_service import UserService

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """验证JWT令牌"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_service = UserService(db)
    user = user_service.get_user_by_id(int(user_id))
    if user is None:
        raise credentials_exception

    return user


def get_current_user(current_user: User = Depends(verify_token)):
    """获取当前用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户账号已禁用"
        )
    return current_user


def require_role(required_role: str):
    """角色权限装饰器"""

    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"需要{required_role}权限"
            )
        return current_user

    return role_checker


def require_system_admin(current_user: User = Depends(get_current_user)):
    """要求系统管理员权限"""
    if current_user.role != "system_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="需要系统管理员权限"
        )
    return current_user


def require_user_admin_or_above(current_user: User = Depends(get_current_user)):
    """要求用户管理员或系统管理员权限"""
    if current_user.role not in ["system_admin", "user_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限"
        )
    return current_user


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """用户登录 - 支持用户名、邮箱、手机号登录"""
    user_service = UserService(db)
    user = user_service.authenticate_user(login_data.identifier, login_data.password)

    # 记录登录日志
    login_log = LoginLog(
        user_id=user.id if user else None,
        login_status="success" if user else "failed",
        failure_reason=None if user else "用户名、邮箱或手机号错误，或密码错误",
    )
    db.add(login_log)

    if not user:
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名、邮箱或手机号错误，或密码错误",
        )

    if not user.is_active:
        login_log.failure_reason = "账号已禁用"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="账号已禁用"
        )

    # 更新最后登录时间
    user_service.update_last_login(user.id)

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires,
    )

    # 记录审计日志
    audit_log = AuditLog(
        user_id=user.id,
        action="login",
        resource_type="auth",
        details={"role": user.role},
    )
    db.add(audit_log)
    db.commit()

    return LoginResponse(
        access_token=access_token, token_type="bearer", user=UserResponse.from_orm(user)
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """用户登出"""
    # 记录审计日志
    audit_log = AuditLog(user_id=current_user.id, action="logout", resource_type="auth")
    db.add(audit_log)
    db.commit()

    return {"message": "登出成功"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse.from_orm(current_user)


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改密码"""
    user_service = UserService(db)

    success = user_service.change_password(
        current_user.id, password_data.current_password, password_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="当前密码错误"
        )

    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user.id, action="change_password", resource_type="auth"
    )
    db.add(audit_log)
    db.commit()

    return {"message": "密码修改成功"}


@router.get("/verify-token")
async def verify_user_token(current_user: User = Depends(get_current_user)):
    """验证令牌有效性"""
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
    }
