"""
数据库初始化脚本
创建默认系统管理员和基础数据
"""

import logging

from sqlalchemy.orm import Session

from .config import settings
from .database import Base, SessionLocal, engine
from .models import PricingRule, SystemSettings, User
from .services.user_service import UserService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_default_admin(db: Session):
    """创建默认系统管理员"""
    user_service = UserService(db)

    # 检查是否已存在管理员
    existing_admin = user_service.get_user_by_username(settings.DEFAULT_ADMIN_USERNAME)
    if existing_admin:
        logger.info("默认管理员已存在")
        return existing_admin

    # 创建默认管理员
    admin_data = {
        "username": settings.DEFAULT_ADMIN_USERNAME,
        "email": settings.DEFAULT_ADMIN_EMAIL,
        "password": settings.DEFAULT_ADMIN_PASSWORD,
        "role": "system_admin",
        "full_name": "系统管理员",
        "is_active": True,
        "is_verified": True,
    }

    # 直接创建用户而不通过API验证
    admin_user = User(
        username=admin_data["username"],
        email=admin_data["email"],
        hashed_password=user_service.get_password_hash(admin_data["password"]),
        role=admin_data["role"],
        full_name=admin_data["full_name"],
        is_active=admin_data["is_active"],
        is_verified=admin_data["is_verified"],
    )

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    logger.info(f"默认系统管理员创建成功: {admin_data['username']}")
    return admin_user


def create_default_pricing_rules(db: Session):
    """创建默认收费规则"""
    # 检查是否已存在收费规则
    existing_rules = db.query(PricingRule).count()
    if existing_rules > 0:
        logger.info("收费规则已存在")
        return

    # 员工数量收费规则
    employee_rule = PricingRule(
        name="员工数量收费",
        description="按员工数量每月收费",
        rule_type="employee_count",
        unit_price=50.0,  # 每个员工每月50元
        billing_period="monthly",
        is_active=True,
    )

    # 关注数量收费规则
    follow_rule = PricingRule(
        name="关注数量收费",
        description="按关注数量收费",
        rule_type="follow_count",
        unit_price=0.1,  # 每次关注0.1元
        billing_period="monthly",
        is_active=True,
    )

    db.add(employee_rule)
    db.add(follow_rule)
    db.commit()

    logger.info("默认收费规则创建成功")


def create_default_settings(db: Session):
    """创建默认系统设置"""
    default_settings = [
        {
            "key": "system_name",
            "value": "Flow Farm 管理系统",
            "description": "系统名称",
            "data_type": "string",
        },
        {
            "key": "max_employees_per_admin",
            "value": "10",
            "description": "每个用户管理员最大员工数",
            "data_type": "integer",
        },
        {
            "key": "auto_billing_enabled",
            "value": "true",
            "description": "是否启用自动计费",
            "data_type": "boolean",
        },
    ]

    for setting_data in default_settings:
        existing_setting = (
            db.query(SystemSettings)
            .filter(SystemSettings.key == setting_data["key"])
            .first()
        )

        if not existing_setting:
            setting = SystemSettings(**setting_data)
            db.add(setting)

    db.commit()
    logger.info("默认系统设置创建成功")


def init_database():
    """初始化数据库"""
    logger.info("开始初始化数据库...")

    # 创建所有表
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建完成")

    # 创建数据库会话
    db = SessionLocal()

    try:
        # 创建默认数据
        create_default_admin(db)
        create_default_pricing_rules(db)
        create_default_settings(db)

        logger.info("数据库初始化完成")

    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
