"""
数据报表相关API路由
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, require_user_admin_or_above
from app.database import get_db
from app.models import User

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(require_user_admin_or_above),
    db: Session = Depends(get_db),
):
    """获取仪表盘数据"""
    # 根据用户角色返回不同的仪表盘数据
    if current_user.role == "system_admin":
        # 系统管理员看到所有用户管理员的汇总数据
        from app.services.user_service import UserService

        user_service = UserService(db)
        user_admins = user_service.get_users_by_parent(current_user.id)

        dashboard_data = {
            "total_user_admins": len(user_admins),
            "total_employees": sum(ua.current_employees for ua in user_admins),
            "user_admins": [],
        }

        for user_admin in user_admins:
            stats = user_service.get_company_statistics(user_admin.id)
            if stats:
                dashboard_data["user_admins"].append(stats)

        return dashboard_data

    elif current_user.role == "user_admin":
        # 用户管理员看到自己公司的详细数据
        from app.services.user_service import UserService
        from app.services.work_record_service import WorkRecordService

        user_service = UserService(db)
        work_service = WorkRecordService(db)

        company_stats = user_service.get_company_statistics(current_user.id)
        work_stats = work_service.get_work_statistics_by_user_admin(current_user.id)

        return {"company_stats": company_stats, "work_stats": work_stats}

    return {"message": "无权限查看仪表盘"}


@router.get("/work-trends")
async def get_work_trends(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_user_admin_or_above),
    db: Session = Depends(get_db),
):
    """获取工作趋势数据"""
    # 获取指定天数内的工作趋势
    return {"message": "工作趋势功能待实现", "days": days}


@router.get("/billing-trends")
async def get_billing_trends(
    months: int = Query(12, ge=1, le=24),
    current_user: User = Depends(require_user_admin_or_above),
    db: Session = Depends(get_db),
):
    """获取计费趋势数据"""
    # 获取指定月数内的计费趋势
    return {"message": "计费趋势功能待实现", "months": months}
