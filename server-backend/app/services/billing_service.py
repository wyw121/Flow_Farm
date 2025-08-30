"""
计费管理服务
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models import BillingRecord, PricingRule, User, WorkRecord
from app.schemas import PricingRuleCreate, PricingRuleUpdate


class BillingService:
    """计费管理服务类"""

    def __init__(self, db: Session):
        self.db = db

    def create_pricing_rule(self, rule_data: PricingRuleCreate) -> PricingRule:
        """创建收费规则"""
        db_rule = PricingRule(
            name=rule_data.name,
            description=rule_data.description,
            rule_type=rule_data.rule_type,
            unit_price=rule_data.unit_price,
            billing_period=rule_data.billing_period,
            rule_config=rule_data.rule_config,
        )

        self.db.add(db_rule)
        self.db.commit()
        self.db.refresh(db_rule)
        return db_rule

    def update_pricing_rule(
        self, rule_id: int, rule_data: PricingRuleUpdate
    ) -> Optional[PricingRule]:
        """更新收费规则"""
        rule = self.db.query(PricingRule).filter(PricingRule.id == rule_id).first()
        if not rule:
            return None

        for field, value in rule_data.dict(exclude_unset=True).items():
            setattr(rule, field, value)

        self.db.commit()
        self.db.refresh(rule)
        return rule

    def get_pricing_rules(self, active_only: bool = True) -> List[PricingRule]:
        """获取收费规则列表"""
        query = self.db.query(PricingRule)
        if active_only:
            query = query.filter(PricingRule.is_active == True)
        return query.all()

    def get_pricing_rule(self, rule_id: int) -> Optional[PricingRule]:
        """获取单个收费规则"""
        return self.db.query(PricingRule).filter(PricingRule.id == rule_id).first()

    def delete_pricing_rule(self, rule_id: int) -> bool:
        """删除收费规则（软删除）"""
        rule = self.get_pricing_rule(rule_id)
        if not rule:
            return False

        rule.is_active = False
        self.db.commit()
        return True

    def calculate_employee_billing(
        self, user_admin_id: int, period_start: datetime, period_end: datetime
    ) -> float:
        """计算员工数量计费"""
        # 获取员工收费规则
        rule = (
            self.db.query(PricingRule)
            .filter(
                and_(
                    PricingRule.rule_type == "employee_count",
                    PricingRule.is_active == True,
                )
            )
            .first()
        )

        if not rule:
            return 0.0

        # 获取用户管理员的员工数量
        user_admin = self.db.query(User).filter(User.id == user_admin_id).first()
        if not user_admin:
            return 0.0

        return user_admin.current_employees * rule.unit_price

    def calculate_follow_billing(
        self, user_admin_id: int, period_start: datetime, period_end: datetime
    ) -> float:
        """计算关注数量计费"""
        # 获取关注收费规则
        rule = (
            self.db.query(PricingRule)
            .filter(
                and_(
                    PricingRule.rule_type == "follow_count",
                    PricingRule.is_active == True,
                )
            )
            .first()
        )

        if not rule:
            return 0.0

        # 统计该用户管理员下所有员工的关注数量
        follow_count = (
            self.db.query(WorkRecord)
            .join(User)
            .filter(
                and_(
                    User.parent_id == user_admin_id,
                    WorkRecord.action_type == "follow",
                    WorkRecord.status == "success",
                    WorkRecord.created_at >= period_start,
                    WorkRecord.created_at <= period_end,
                )
            )
            .count()
        )

        return follow_count * rule.unit_price

    def generate_billing_record(
        self,
        user_admin_id: int,
        billing_type: str,
        period_start: datetime,
        period_end: datetime,
    ) -> BillingRecord:
        """生成计费记录"""
        # 根据计费类型计算金额
        if billing_type == "employee_count":
            amount = self.calculate_employee_billing(
                user_admin_id, period_start, period_end
            )
            # 获取员工数量
            user_admin = self.db.query(User).filter(User.id == user_admin_id).first()
            quantity = user_admin.current_employees if user_admin else 0
        elif billing_type == "follow_count":
            # 获取关注数量
            quantity = (
                self.db.query(WorkRecord)
                .join(User)
                .filter(
                    and_(
                        User.parent_id == user_admin_id,
                        WorkRecord.action_type == "follow",
                        WorkRecord.status == "success",
                        WorkRecord.created_at >= period_start,
                        WorkRecord.created_at <= period_end,
                    )
                )
                .count()
            )
            amount = self.calculate_follow_billing(
                user_admin_id, period_start, period_end
            )
        else:
            raise ValueError(f"不支持的计费类型: {billing_type}")

        # 获取定价规则
        rule = (
            self.db.query(PricingRule)
            .filter(
                and_(
                    PricingRule.rule_type == billing_type, PricingRule.is_active == True
                )
            )
            .first()
        )

        if not rule:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"未找到有效的{billing_type}收费规则",
            )

        # 创建计费记录
        billing_record = BillingRecord(
            user_id=user_admin_id,
            billing_type=billing_type,
            quantity=quantity,
            unit_price=rule.unit_price,
            total_amount=amount,
            billing_period=rule.billing_period,
            period_start=period_start,
            period_end=period_end,
            status="pending",
        )

        self.db.add(billing_record)
        self.db.commit()
        self.db.refresh(billing_record)
        return billing_record

    def get_billing_records(
        self, user_admin_id: Optional[int] = None, status: Optional[str] = None
    ) -> List[BillingRecord]:
        """获取计费记录列表"""
        query = self.db.query(BillingRecord)

        if user_admin_id:
            query = query.filter(BillingRecord.user_id == user_admin_id)

        if status:
            query = query.filter(BillingRecord.status == status)

        return query.order_by(BillingRecord.created_at.desc()).all()

    def update_billing_status(
        self, billing_id: int, status: str
    ) -> Optional[BillingRecord]:
        """更新计费记录状态"""
        billing = (
            self.db.query(BillingRecord).filter(BillingRecord.id == billing_id).first()
        )
        if not billing:
            return None

        billing.status = status
        if status == "paid":
            billing.paid_at = datetime.now()

        self.db.commit()
        self.db.refresh(billing)
        return billing

    def get_monthly_billing_summary(
        self, user_admin_id: int, year: int, month: int
    ) -> dict:
        """获取月度计费汇总"""
        # 计算月份的开始和结束时间
        period_start = datetime(year, month, 1)
        if month == 12:
            period_end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            period_end = datetime(year, month + 1, 1) - timedelta(seconds=1)

        # 获取该月的计费记录
        billing_records = (
            self.db.query(BillingRecord)
            .filter(
                and_(
                    BillingRecord.user_id == user_admin_id,
                    BillingRecord.period_start >= period_start,
                    BillingRecord.period_end <= period_end,
                )
            )
            .all()
        )

        # 计算汇总信息
        total_amount = sum(record.total_amount for record in billing_records)
        paid_amount = sum(
            record.total_amount for record in billing_records if record.status == "paid"
        )
        pending_amount = sum(
            record.total_amount
            for record in billing_records
            if record.status == "pending"
        )

        # 按类型分组统计
        employee_billing = sum(
            record.total_amount
            for record in billing_records
            if record.billing_type == "employee_count"
        )
        follow_billing = sum(
            record.total_amount
            for record in billing_records
            if record.billing_type == "follow_count"
        )

        return {
            "period": f"{year}-{month:02d}",
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "pending_amount": pending_amount,
            "employee_billing": employee_billing,
            "follow_billing": follow_billing,
            "records": billing_records,
        }

    def auto_generate_monthly_billing(self) -> List[BillingRecord]:
        """自动生成月度计费记录"""
        # 获取上个月的时间范围
        now = datetime.now()
        if now.month == 1:
            last_month_start = datetime(now.year - 1, 12, 1)
            last_month_end = datetime(now.year, 1, 1) - timedelta(seconds=1)
        else:
            last_month_start = datetime(now.year, now.month - 1, 1)
            last_month_end = datetime(now.year, now.month, 1) - timedelta(seconds=1)

        # 获取所有用户管理员
        user_admins = self.db.query(User).filter(User.role == "user_admin").all()

        generated_records = []
        for user_admin in user_admins:
            # 检查是否已经生成过该月的计费记录
            existing_record = (
                self.db.query(BillingRecord)
                .filter(
                    and_(
                        BillingRecord.user_id == user_admin.id,
                        BillingRecord.period_start >= last_month_start,
                        BillingRecord.period_end <= last_month_end,
                    )
                )
                .first()
            )

            if not existing_record:
                # 生成员工数量计费
                if user_admin.current_employees > 0:
                    employee_record = self.generate_billing_record(
                        user_admin.id,
                        "employee_count",
                        last_month_start,
                        last_month_end,
                    )
                    generated_records.append(employee_record)

                # 生成关注数量计费
                follow_record = self.generate_billing_record(
                    user_admin.id, "follow_count", last_month_start, last_month_end
                )
                generated_records.append(follow_record)

        return generated_records
