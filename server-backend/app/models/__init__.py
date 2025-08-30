"""
数据库模型定义
"""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base

# 常量定义
USERS_TABLE = "users"


class User(Base):
    """用户模型 - 支持三级权限"""

    __tablename__ = USERS_TABLE

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)

    # 用户角色: system_admin, user_admin, employee
    role = Column(String(20), nullable=False, default="employee")

    # 用户状态
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # 层级关系 - 用户管理员归属于系统管理员，员工归属于用户管理员
    parent_id = Column(Integer, ForeignKey(f"{USERS_TABLE}.id"), nullable=True)
    parent = relationship("User", remote_side=[id], backref="children")

    # 个人信息
    full_name = Column(String(100))
    phone = Column(String(20))
    company = Column(String(100))  # 用户管理员的公司名称

    # 限制设置 - 仅对用户管理员有效
    max_employees = Column(Integer, default=10)  # 最多可添加的员工数
    current_employees = Column(Integer, default=0)  # 当前员工数

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # 关系
    work_records = relationship("WorkRecord", back_populates="employee")
    billing_records = relationship("BillingRecord", back_populates="user")


class WorkRecord(Base):
    """工作记录模型 - 记录员工的关注等工作数据"""

    __tablename__ = "work_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey(f"{USERS_TABLE}.id"), nullable=False)

    # 工作内容
    platform = Column(String(20), nullable=False)  # xiaohongshu, douyin
    action_type = Column(String(20), nullable=False)  # follow, like, comment
    target_username = Column(String(100))  # 被关注的用户名
    target_user_id = Column(String(100))  # 被关注的用户ID
    target_url = Column(String(500))  # 目标链接

    # 执行结果
    status = Column(String(20), default="pending")  # pending, success, failed
    error_message = Column(Text, nullable=True)

    # 设备信息
    device_id = Column(String(100))
    device_name = Column(String(100))

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True), nullable=True)

    # 关系
    employee = relationship("User", back_populates="work_records")


class BillingRecord(Base):
    """计费记录模型 - 记录用户管理员的费用"""

    __tablename__ = "billing_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(f"{USERS_TABLE}.id"), nullable=False)

    # 计费类型: employee_count, follow_count
    billing_type = Column(String(20), nullable=False)

    # 计费数据
    quantity = Column(Integer, nullable=False)  # 员工数量或关注数量
    unit_price = Column(Float, nullable=False)  # 单价
    total_amount = Column(Float, nullable=False)  # 总金额

    # 计费周期
    billing_period = Column(String(20))  # monthly, yearly, one_time
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))

    # 状态
    status = Column(String(20), default="pending")  # pending, paid, overdue

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # 关系
    user = relationship("User", back_populates="billing_records")


class PricingRule(Base):
    """收费规则模型 - 系统管理员设置的收费标准"""

    __tablename__ = "pricing_rules"

    id = Column(Integer, primary_key=True, index=True)

    # 规则名称和描述
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # 规则类型
    rule_type = Column(String(20), nullable=False)  # employee_count, follow_count

    # 价格设置
    unit_price = Column(Float, nullable=False)  # 单价
    billing_period = Column(String(20), default="monthly")  # 计费周期

    # 规则配置 (JSON格式，存储复杂的定价逻辑)
    rule_config = Column(JSON, nullable=True)

    # 状态
    is_active = Column(Boolean, default=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SystemSettings(Base):
    """系统设置模型"""

    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text)
    # string, integer, float, boolean, json
    data_type = Column(String(20), default="string")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LoginLog(Base):
    """登录日志模型"""

    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(f"{USERS_TABLE}.id"), nullable=False)

    # 登录信息
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    login_status = Column(String(20))  # success, failed
    failure_reason = Column(String(200), nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    """操作审计日志模型"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(f"{USERS_TABLE}.id"), nullable=False)

    # 操作信息
    action = Column(String(100), nullable=False)  # 操作类型
    resource_type = Column(String(50))  # 资源类型
    resource_id = Column(String(100))  # 资源ID

    # 操作详情
    details = Column(JSON, nullable=True)  # 操作详细信息
    ip_address = Column(String(50))
    user_agent = Column(String(500))

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
