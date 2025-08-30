"""
用户管理服务
"""

from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from ..models import BillingRecord, User, WorkRecord
from ..schemas import (
    CompanyStatistics,
    UserCreate,
    UserResponse,
    UserStatistics,
    UserUpdate,
    UserWithStats,
    WorkStatistics,
)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """用户管理服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_password_hash(self, password: str) -> str:
        """获取密码哈希值"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """用户认证"""
        user = self.get_user_by_username(username)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        if self.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
            )

        # 检查邮箱是否已存在
        if user_data.email:
            existing_email = (
                self.db.query(User).filter(User.email == user_data.email).first()
            )
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已存在"
                )

        # 验证父级用户和权限
        if user_data.parent_id:
            parent_user = self.get_user_by_id(user_data.parent_id)
            if not parent_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="父级用户不存在"
                )

            # 检查用户管理员是否已达到员工数量限制
            if (
                user_data.role == "employee"
                and parent_user.role == "user_admin"
                and parent_user.current_employees >= parent_user.max_employees
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"用户管理员已达到最大员工数量限制({parent_user.max_employees})",
                )

        # 创建用户
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=self.get_password_hash(user_data.password),
            role=user_data.role,
            parent_id=user_data.parent_id,
            full_name=user_data.full_name,
            phone=user_data.phone,
            company=user_data.company,
            max_employees=(
                user_data.max_employees if user_data.role == "user_admin" else 0
            ),
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        # 如果是员工，更新父级用户的员工数量
        if user_data.role == "employee" and user_data.parent_id:
            parent_user = self.get_user_by_id(user_data.parent_id)
            parent_user.current_employees += 1
            self.db.commit()

        return db_user

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """更新用户信息"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
            )

        # 更新用户信息
        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        # 如果是员工，更新父级用户的员工数量
        if user.role == "employee" and user.parent_id:
            parent_user = self.get_user_by_id(user.parent_id)
            parent_user.current_employees = max(0, parent_user.current_employees - 1)

        self.db.delete(user)
        self.db.commit()
        return True

    def get_users_by_parent(self, parent_id: int) -> List[User]:
        """获取指定父级用户的子用户列表"""
        return self.db.query(User).filter(User.parent_id == parent_id).all()

    def get_user_with_stats(self, user_id: int) -> Optional[UserWithStats]:
        """获取带统计信息的用户信息"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        # 计算工作记录统计
        total_work_records = (
            self.db.query(WorkRecord).filter(WorkRecord.employee_id == user_id).count()
        )

        today_work_records = (
            self.db.query(WorkRecord)
            .filter(
                and_(
                    WorkRecord.employee_id == user_id,
                    func.date(WorkRecord.created_at) == datetime.now().date(),
                )
            )
            .count()
        )

        # 计算计费统计
        total_billing = (
            self.db.query(func.sum(BillingRecord.total_amount))
            .filter(BillingRecord.user_id == user_id)
            .scalar()
            or 0.0
        )

        return UserWithStats(
            **user.__dict__,
            total_work_records=total_work_records,
            today_work_records=today_work_records,
            total_billing_amount=total_billing,
        )

    def get_work_statistics(self, user_id: int) -> WorkStatistics:
        """获取用户工作统计"""
        # 总体统计
        total_follows = (
            self.db.query(WorkRecord)
            .filter(
                and_(
                    WorkRecord.employee_id == user_id,
                    WorkRecord.action_type == "follow",
                    WorkRecord.status == "success",
                )
            )
            .count()
        )

        total_likes = (
            self.db.query(WorkRecord)
            .filter(
                and_(
                    WorkRecord.employee_id == user_id,
                    WorkRecord.action_type == "like",
                    WorkRecord.status == "success",
                )
            )
            .count()
        )

        total_comments = (
            self.db.query(WorkRecord)
            .filter(
                and_(
                    WorkRecord.employee_id == user_id,
                    WorkRecord.action_type == "comment",
                    WorkRecord.status == "success",
                )
            )
            .count()
        )

        # 今日统计
        today = datetime.now().date()
        today_follows = (
            self.db.query(WorkRecord)
            .filter(
                and_(
                    WorkRecord.employee_id == user_id,
                    WorkRecord.action_type == "follow",
                    WorkRecord.status == "success",
                    func.date(WorkRecord.created_at) == today,
                )
            )
            .count()
        )

        today_likes = (
            self.db.query(WorkRecord)
            .filter(
                and_(
                    WorkRecord.employee_id == user_id,
                    WorkRecord.action_type == "like",
                    WorkRecord.status == "success",
                    func.date(WorkRecord.created_at) == today,
                )
            )
            .count()
        )

        today_comments = (
            self.db.query(WorkRecord)
            .filter(
                and_(
                    WorkRecord.employee_id == user_id,
                    WorkRecord.action_type == "comment",
                    WorkRecord.status == "success",
                    func.date(WorkRecord.created_at) == today,
                )
            )
            .count()
        )

        # 成功率计算
        total_attempts = (
            self.db.query(WorkRecord).filter(WorkRecord.employee_id == user_id).count()
        )

        successful_attempts = (
            self.db.query(WorkRecord)
            .filter(
                and_(WorkRecord.employee_id == user_id, WorkRecord.status == "success")
            )
            .count()
        )

        success_rate = (
            (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
        )

        return WorkStatistics(
            total_follows=total_follows,
            total_likes=total_likes,
            total_comments=total_comments,
            today_follows=today_follows,
            today_likes=today_likes,
            today_comments=today_comments,
            success_rate=round(success_rate, 2),
        )

    def get_company_statistics(self, user_admin_id: int) -> Optional[CompanyStatistics]:
        """获取公司（用户管理员）的统计信息"""
        user_admin = self.get_user_by_id(user_admin_id)
        if not user_admin or user_admin.role != "user_admin":
            return None

        # 获取所有员工
        employees = self.get_users_by_parent(user_admin_id)

        # 统计活跃员工数
        today = datetime.now().date()
        active_employees = 0
        total_work_records = 0
        today_work_records = 0
        employee_stats = []

        for employee in employees:
            # 获取员工工作统计
            work_stats = self.get_work_statistics(employee.id)

            # 检查是否为活跃员工（今日有工作记录）
            if (
                work_stats.today_follows > 0
                or work_stats.today_likes > 0
                or work_stats.today_comments > 0
            ):
                active_employees += 1

            total_work_records += (
                work_stats.total_follows
                + work_stats.total_likes
                + work_stats.total_comments
            )

            today_work_records += (
                work_stats.today_follows
                + work_stats.today_likes
                + work_stats.today_comments
            )

            employee_stats.append(
                UserStatistics(
                    user_id=employee.id,
                    username=employee.username,
                    full_name=employee.full_name,
                    role=employee.role,
                    work_stats=work_stats,
                    created_at=employee.created_at,
                )
            )

        # 计算总计费金额
        total_billing = (
            self.db.query(func.sum(BillingRecord.total_amount))
            .filter(BillingRecord.user_id == user_admin_id)
            .scalar()
            or 0.0
        )

        return CompanyStatistics(
            user_admin_id=user_admin_id,
            company_name=user_admin.company or "未设置公司名称",
            total_employees=len(employees),
            active_employees=active_employees,
            total_work_records=total_work_records,
            today_work_records=today_work_records,
            total_billing_amount=total_billing,
            employees=employee_stats,
        )

    def update_last_login(self, user_id: int) -> None:
        """更新用户最后登录时间"""
        user = self.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.now()
            self.db.commit()

    def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> bool:
        """修改用户密码"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        if not self.verify_password(current_password, user.hashed_password):
            return False

        user.hashed_password = self.get_password_hash(new_password)
        self.db.commit()
        return True
