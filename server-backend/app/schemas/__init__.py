"""
Pydantic 数据模型定义 - 用于API请求和响应
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


# 用户相关模型
class UserBase(BaseModel):
    """用户基础模型"""

    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None


class UserCreate(UserBase):
    """创建用户模型"""

    password: str
    role: str = "employee"
    parent_id: Optional[int] = None
    max_employees: Optional[int] = 10


class UserUpdate(BaseModel):
    """更新用户模型"""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    is_active: Optional[bool] = None
    max_employees: Optional[int] = None


class UserResponse(UserBase):
    """用户响应模型"""

    id: int
    role: str
    is_active: bool
    is_verified: bool
    current_employees: int
    max_employees: int
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserWithStats(UserResponse):
    """带统计信息的用户模型"""

    total_work_records: int = 0
    today_work_records: int = 0
    total_billing_amount: float = 0.0


# 工作记录相关模型
class WorkRecordBase(BaseModel):
    """工作记录基础模型"""

    platform: str
    action_type: str
    target_username: Optional[str] = None
    target_user_id: Optional[str] = None
    target_url: Optional[str] = None
    device_id: Optional[str] = None
    device_name: Optional[str] = None


class WorkRecordCreate(WorkRecordBase):
    """创建工作记录模型"""

    employee_id: int


class WorkRecordUpdate(BaseModel):
    """更新工作记录模型"""

    status: str
    error_message: Optional[str] = None
    executed_at: Optional[datetime] = None


class WorkRecordResponse(WorkRecordBase):
    """工作记录响应模型"""

    id: int
    employee_id: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    executed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 计费记录相关模型
class BillingRecordBase(BaseModel):
    """计费记录基础模型"""

    billing_type: str
    quantity: int
    unit_price: float
    total_amount: float
    billing_period: Optional[str] = None


class BillingRecordCreate(BillingRecordBase):
    """创建计费记录模型"""

    user_id: int
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class BillingRecordResponse(BillingRecordBase):
    """计费记录响应模型"""

    id: int
    user_id: int
    status: str
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    created_at: datetime
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 收费规则相关模型
class PricingRuleBase(BaseModel):
    """收费规则基础模型"""

    name: str
    description: Optional[str] = None
    rule_type: str
    unit_price: float
    billing_period: str = "monthly"


class PricingRuleCreate(PricingRuleBase):
    """创建收费规则模型"""

    rule_config: Optional[dict] = None


class PricingRuleUpdate(BaseModel):
    """更新收费规则模型"""

    name: Optional[str] = None
    description: Optional[str] = None
    unit_price: Optional[float] = None
    billing_period: Optional[str] = None
    rule_config: Optional[dict] = None
    is_active: Optional[bool] = None


class PricingRuleResponse(PricingRuleBase):
    """收费规则响应模型"""

    id: int
    rule_config: Optional[dict] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 认证相关模型
class LoginRequest(BaseModel):
    """登录请求模型"""

    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应模型"""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""

    current_password: str
    new_password: str


# 统计数据模型
class WorkStatistics(BaseModel):
    """工作统计模型"""

    total_follows: int = 0
    total_likes: int = 0
    total_comments: int = 0
    today_follows: int = 0
    today_likes: int = 0
    today_comments: int = 0
    success_rate: float = 0.0


class UserStatistics(BaseModel):
    """用户统计模型"""

    user_id: int
    username: str
    full_name: Optional[str] = None
    role: str
    work_stats: WorkStatistics
    created_at: datetime


class CompanyStatistics(BaseModel):
    """公司统计模型"""

    user_admin_id: int
    user_admin_name: str
    company_name: str
    total_employees: int
    active_employees: int = 0
    total_follows: int = 0
    today_follows: int = 0
    total_work_records: int = 0
    today_work_records: int = 0
    total_billing_amount: float = 0.0
    unpaid_amount: float = 0.0
    employees: List[UserStatistics] = []


# 系统设置模型
class SystemSettingBase(BaseModel):
    """系统设置基础模型"""

    key: str
    value: str
    description: Optional[str] = None
    data_type: str = "string"


class SystemSettingCreate(SystemSettingBase):
    """创建系统设置模型"""

    pass


class SystemSettingUpdate(BaseModel):
    """更新系统设置模型"""

    value: str
    description: Optional[str] = None


class SystemSettingResponse(SystemSettingBase):
    """系统设置响应模型"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 分页模型
class PaginationParams(BaseModel):
    """分页参数模型"""

    page: int = 1
    size: int = 20


class PaginatedResponse(BaseModel):
    """分页响应模型"""

    items: List[dict]
    total: int
    page: int
    size: int
    pages: int


# Excel导出模型
class ExportRequest(BaseModel):
    """导出请求模型"""

    user_admin_id: Optional[int] = None
    employee_id: Optional[int] = None
    platform: Optional[str] = None
    action_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ExportResponse(BaseModel):
    """导出响应模型"""

    download_url: str
    filename: str
    expires_at: datetime
