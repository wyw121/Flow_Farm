"""
创建初始测试数据
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.models import User
from app.services.user_service import UserService


def create_test_users():
    """创建测试用户"""
    db = next(get_db())
    user_service = UserService(db)

    try:
        # 创建系统管理员
        system_admin = user_service.get_user_by_username("system_admin")
        if not system_admin:
            from app.schemas import UserCreate

            admin_data = UserCreate(
                username="system_admin",
                email="admin@flowfarm.com",
                phone="13800000000",
                password="admin123",
                role="system_admin",
                full_name="系统管理员",
                company="Flow Farm",
            )
            system_admin = user_service.create_user(admin_data)
            print(f"✅ 创建系统管理员: {system_admin.username}")
        else:
            print(f"✅ 系统管理员已存在: {system_admin.username}")

        # 创建用户管理员
        user_admin1 = user_service.get_user_by_username("company_admin_1")
        if not user_admin1:
            admin_data = UserCreate(
                username="company_admin_1",
                email="admin1@company1.com",
                phone="13800138001",
                password="123456",
                role="user_admin",
                full_name="公司管理员1",
                company="科技有限公司",
                parent_id=system_admin.id,
                max_employees=10,
            )
            user_admin1 = user_service.create_user(admin_data)
            print(f"✅ 创建用户管理员1: {user_admin1.username}")
        else:
            print(f"✅ 用户管理员1已存在: {user_admin1.username}")

        # 创建第二个用户管理员
        user_admin2 = user_service.get_user_by_username("company_admin_2")
        if not user_admin2:
            admin_data = UserCreate(
                username="company_admin_2",
                email="admin2@company2.com",
                phone="13800138002",
                password="123456",
                role="user_admin",
                full_name="公司管理员2",
                company="营销策划公司",
                parent_id=system_admin.id,
                max_employees=20,
            )
            user_admin2 = user_service.create_user(admin_data)
            print(f"✅ 创建用户管理员2: {user_admin2.username}")
        else:
            print(f"✅ 用户管理员2已存在: {user_admin2.username}")

        print("\n🎉 测试用户创建完成！")
        print("\n登录信息：")
        print("系统管理员:")
        print("  用户名: system_admin")
        print("  密码: admin123")
        print("  邮箱: admin@flowfarm.com")
        print("  手机: 13800000000")
        print("\n用户管理员1:")
        print("  用户名: company_admin_1")
        print("  密码: 123456")
        print("  邮箱: admin1@company1.com")
        print("  手机: 13800138001")
        print("\n用户管理员2:")
        print("  用户名: company_admin_2")
        print("  密码: 123456")
        print("  邮箱: admin2@company2.com")
        print("  手机: 13800138002")

    except Exception as e:
        print(f"❌ 创建测试用户时出错: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_users()
