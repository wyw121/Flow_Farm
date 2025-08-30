"""
用户管理相关API路由
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..api.auth import (
    get_current_user,
    require_system_admin,
    require_user_admin_or_above,
)
from ..database import get_db
from ..models import AuditLog, User
from ..schemas import (
    CompanyStatistics,
    PaginatedResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserWithStats,
)
from ..services.user_service import UserService

# 常量定义
USER_NOT_FOUND_MSG = "用户不存在"

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_user_admin_or_above),
    db: Session = Depends(get_db),
):
    """创建用户（系统管理员创建用户管理员，用户管理员创建员工）"""
    user_service = UserService(db)

    # 权限检查
    if current_user.role == "system_admin":
        # 系统管理员只能创建用户管理员
        if user_data.role not in ["user_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="系统管理员只能创建用户管理员",
            )
        # 设置父级关系
        user_data.parent_id = current_user.id

    elif current_user.role == "user_admin":
        # 用户管理员只能创建员工
        if user_data.role != "employee":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户管理员只能创建员工账号",
            )
        # 设置父级关系
        user_data.parent_id = current_user.id

        # 检查员工数量限制
        if current_user.current_employees >= current_user.max_employees:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"已达到最大员工数量限制({current_user.max_employees})",
            )

    new_user = user_service.create_user(user_data)

    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user.id,
        action="create_user",
        resource_type="user",
        resource_id=str(new_user.id),
        details={"created_username": new_user.username, "created_role": new_user.role},
    )
    db.add(audit_log)
    db.commit()

    return UserResponse.from_orm(new_user)


@router.get("/", response_model=PaginatedResponse)
async def get_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    role: Optional[str] = Query(None),
    current_user: User = Depends(require_user_admin_or_above),
    db: Session = Depends(get_db),
):
    """获取用户列表"""
    user_service = UserService(db)

    if current_user.role == "system_admin":
        # 系统管理员可以看到所有用户管理员和员工
        users = user_service.get_all_users()
        if role:
            users = [user for user in users if user.role == role]
    else:
        # 用户管理员只能看到自己的员工
        users = user_service.get_users_by_parent(current_user.id)

    # 分页计算
    total = len(users)
    skip = (page - 1) * size
    paginated_users = users[skip : skip + size]
    pages = (total + size - 1) // size

    return PaginatedResponse(
        items=[UserWithStats.from_orm(user).__dict__ for user in paginated_users],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/my-employees", response_model=List[UserResponse])
async def get_my_employees(
    current_user: User = Depends(require_user_admin_or_above),
    db: Session = Depends(get_db),
):
    """获取我的员工列表"""
    user_service = UserService(db)
    employees = user_service.get_users_by_parent(current_user.id)
    return [UserResponse.from_orm(emp) for emp in employees]


@router.get("/{user_id}", response_model=UserWithStats)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户详细信息"""
    user_service = UserService(db)

    # 权限检查
    if current_user.role == "employee":
        # 员工只能查看自己的信息
        if user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="只能查看自己的信息"
            )
    elif current_user.role == "user_admin":
        # 用户管理员可以查看自己和自己的员工
        target_user = user_service.get_user_by_id(user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
            )

        if (
            target_user.id != current_user.id
            and target_user.parent_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无权查看该用户信息"
            )
    # 系统管理员可以查看所有用户

    user_with_stats = user_service.get_user_with_stats(user_id)
    if not user_with_stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MSG
        )

    return user_with_stats


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_user_admin_or_above),
    db: Session = Depends(get_db),
):
    """更新用户信息"""
    user_service = UserService(db)

    # 权限检查
    target_user = user_service.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MSG
        )

    if current_user.role == "user_admin":
        # 用户管理员只能更新自己和自己的员工
        if (
            target_user.id != current_user.id
            and target_user.parent_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无权修改该用户信息"
            )

    updated_user = user_service.update_user(user_id, user_data)

    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user.id,
        action="update_user",
        resource_type="user",
        resource_id=str(user_id),
        details=user_data.dict(exclude_unset=True),
    )
    db.add(audit_log)
    db.commit()

    return UserResponse.from_orm(updated_user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_user_admin_or_above),
    db: Session = Depends(get_db),
):
    """删除用户"""
    user_service = UserService(db)

    # 权限检查
    target_user = user_service.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MSG
        )

    if current_user.role == "user_admin":
        # 用户管理员只能删除自己的员工
        if target_user.parent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无权删除该用户"
            )

    # 不能删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="不能删除自己"
        )

    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MSG
        )

    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user.id,
        action="delete_user",
        resource_type="user",
        resource_id=str(user_id),
        details={"deleted_username": target_user.username},
    )
    db.add(audit_log)
    db.commit()

    return {"message": "用户删除成功"}


@router.get("/statistics/company/{user_admin_id}", response_model=CompanyStatistics)
async def get_company_statistics(
    user_admin_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取公司统计信息"""
    user_service = UserService(db)

    # 权限检查
    if current_user.role == "user_admin":
        # 用户管理员只能查看自己的统计
        if user_admin_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看该用户管理员的统计信息",
            )
    elif current_user.role == "employee":
        # 员工无权查看统计信息
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="员工无权查看统计信息"
        )
    # 系统管理员可以查看所有统计

    stats = user_service.get_company_statistics(user_admin_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="用户管理员不存在或无权限"
        )

    return stats


@router.get("/companies/statistics", response_model=List[CompanyStatistics])
async def get_companies_statistics(
    current_user: User = Depends(require_system_admin), db: Session = Depends(get_db)
):
    """获取所有公司的统计信息（仅系统管理员）"""
    user_service = UserService(db)

    # 获取所有用户管理员
    user_admins = user_service.get_users_by_parent(current_user.id)

    stats_list = []
    for user_admin in user_admins:
        stats = user_service.get_company_statistics(user_admin.id)
        if stats:
            stats_list.append(stats)

    return stats_list


@router.post("/{user_id}/toggle-status", response_model=UserResponse)
async def toggle_user_status(
    user_id: int,
    current_user: User = Depends(require_user_admin_or_above),
    db: Session = Depends(get_db),
):
    """切换用户状态（启用/停用）"""
    user_service = UserService(db)

    target_user = user_service.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 权限检查
    if current_user.role == "user_admin":
        # 用户管理员只能操作自己的员工
        if target_user.parent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无权操作该用户"
            )
    elif current_user.role == "system_admin":
        # 系统管理员只能操作用户管理员
        if target_user.role != "user_admin" or target_user.parent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="系统管理员只能操作自己创建的用户管理员",
            )

    # 切换状态
    target_user.is_active = not target_user.is_active
    db.commit()
    db.refresh(target_user)

    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user.id,
        action="toggle_user_status",
        resource_type="user",
        resource_id=str(target_user.id),
        details={
            "target_username": target_user.username,
            "new_status": target_user.is_active,
        },
    )
    db.add(audit_log)
    db.commit()

    return UserResponse.from_orm(target_user)
