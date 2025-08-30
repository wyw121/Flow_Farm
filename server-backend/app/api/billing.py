"""
计费管理相关API路由
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.auth import (
    get_current_user,
    require_system_admin,
    require_user_admin_or_above,
)
from app.database import get_db
from app.models import AuditLog, User
from app.schemas import (
    BillingRecordResponse,
    PricingRuleCreate,
    PricingRuleResponse,
    PricingRuleUpdate,
)
from app.services.billing_service import BillingService

router = APIRouter()


# 收费规则管理（仅系统管理员）
@router.post("/pricing-rules", response_model=PricingRuleResponse)
async def create_pricing_rule(
    rule_data: PricingRuleCreate,
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """创建收费规则（仅系统管理员）"""
    billing_service = BillingService(db)

    rule = billing_service.create_pricing_rule(rule_data)

    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user.id,
        action="create_pricing_rule",
        resource_type="pricing_rule",
        resource_id=str(rule.id),
        details={"rule_type": rule.rule_type, "unit_price": rule.unit_price},
    )
    db.add(audit_log)
    db.commit()

    return PricingRuleResponse.from_orm(rule)


@router.get("/pricing-rules", response_model=List[PricingRuleResponse])
async def get_pricing_rules(
    active_only: bool = Query(True),
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """获取收费规则列表（仅系统管理员）"""
    billing_service = BillingService(db)
    rules = billing_service.get_pricing_rules(active_only)
    return [PricingRuleResponse.from_orm(rule) for rule in rules]


@router.put("/pricing-rules/{rule_id}", response_model=PricingRuleResponse)
async def update_pricing_rule(
    rule_id: int,
    rule_data: PricingRuleUpdate,
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """更新收费规则（仅系统管理员）"""
    billing_service = BillingService(db)

    updated_rule = billing_service.update_pricing_rule(rule_id, rule_data)
    if not updated_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="收费规则不存在"
        )

    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user.id,
        action="update_pricing_rule",
        resource_type="pricing_rule",
        resource_id=str(rule_id),
        details=rule_data.dict(exclude_unset=True),
    )
    db.add(audit_log)
    db.commit()

    return PricingRuleResponse.from_orm(updated_rule)


@router.delete("/pricing-rules/{rule_id}")
async def delete_pricing_rule(
    rule_id: int,
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """删除收费规则（仅系统管理员）"""
    billing_service = BillingService(db)

    success = billing_service.delete_pricing_rule(rule_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="收费规则不存在"
        )

    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user.id,
        action="delete_pricing_rule",
        resource_type="pricing_rule",
        resource_id=str(rule_id),
    )
    db.add(audit_log)
    db.commit()

    return {"message": "收费规则删除成功"}


# 计费记录管理
@router.get("/billing-records", response_model=List[BillingRecordResponse])
async def get_billing_records(
    user_admin_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取计费记录列表"""
    billing_service = BillingService(db)

    # 权限检查
    if current_user.role == "user_admin":
        # 用户管理员只能查看自己的计费记录
        user_admin_id = current_user.id
    elif current_user.role == "employee":
        # 员工无权查看计费记录
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="员工无权查看计费记录"
        )
    # 系统管理员可以查看所有记录

    records = billing_service.get_billing_records(user_admin_id, status)
    return [BillingRecordResponse.from_orm(record) for record in records]


@router.put("/billing-records/{billing_id}/status")
async def update_billing_status(
    billing_id: int,
    status: str,
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db),
):
    """更新计费记录状态（仅系统管理员）"""
    billing_service = BillingService(db)

    if status not in ["pending", "paid", "overdue"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="无效的状态值"
        )

    updated_record = billing_service.update_billing_status(billing_id, status)
    if not updated_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="计费记录不存在"
        )

    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user.id,
        action="update_billing_status",
        resource_type="billing_record",
        resource_id=str(billing_id),
        details={"new_status": status},
    )
    db.add(audit_log)
    db.commit()

    return {"message": "计费状态更新成功"}


@router.get("/billing-summary/{user_admin_id}")
async def get_monthly_billing_summary(
    user_admin_id: int,
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取月度计费汇总"""
    billing_service = BillingService(db)

    # 权限检查
    if current_user.role == "user_admin":
        if user_admin_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看其他管理员的计费信息",
            )
    elif current_user.role == "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="员工无权查看计费信息"
        )

    summary = billing_service.get_monthly_billing_summary(user_admin_id, year, month)
    return summary


@router.post("/generate-monthly-billing")
async def generate_monthly_billing(
    current_user: User = Depends(require_system_admin), db: Session = Depends(get_db)
):
    """生成月度计费记录（仅系统管理员）"""
    billing_service = BillingService(db)

    try:
        generated_records = billing_service.auto_generate_monthly_billing()

        # 记录审计日志
        audit_log = AuditLog(
            user_id=current_user.id,
            action="generate_monthly_billing",
            resource_type="billing_record",
            details={"generated_count": len(generated_records)},
        )
        db.add(audit_log)
        db.commit()

        return {
            "message": "月度计费记录生成成功",
            "generated_count": len(generated_records),
            "records": [
                BillingRecordResponse.from_orm(record) for record in generated_records
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成计费记录失败: {str(e)}",
        )


# 用户管理员的结算界面相关API
@router.get("/my-billing-info")
async def get_my_billing_info(
    current_user: User = Depends(require_user_admin_or_above),
    db: Session = Depends(get_db),
):
    """获取我的计费信息（用户管理员查看自己的结算界面）"""
    if current_user.role != "user_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="仅用户管理员可以查看结算信息"
        )

    billing_service = BillingService(db)

    # 获取当前计费记录
    records = billing_service.get_billing_records(current_user.id)

    # 计算总欠费
    pending_amount = sum(r.total_amount for r in records if r.status == "pending")
    paid_amount = sum(r.total_amount for r in records if r.status == "paid")
    total_amount = sum(r.total_amount for r in records)

    # 获取当前员工数
    from ..services.user_service import UserService

    user_service = UserService(db)
    employees = user_service.get_users_by_parent(current_user.id)

    return {
        "user_admin_id": current_user.id,
        "company_name": current_user.company,
        "current_employees": current_user.current_employees,
        "max_employees": current_user.max_employees,
        "total_amount": total_amount,
        "paid_amount": paid_amount,
        "pending_amount": pending_amount,
        "billing_records": [
            BillingRecordResponse.from_orm(record) for record in records
        ],
        "employees": [
            {"id": emp.id, "username": emp.username, "full_name": emp.full_name}
            for emp in employees
        ],
    }
