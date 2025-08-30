#!/usr/bin/env python3
"""
Flow Farm 服务器后端测试脚本
测试主要API功能
"""

import json
import time

import requests


class FlowFarmAPITester:
    """API测试器"""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def login(self, username="admin", password="admin123"):
        """登录获取token"""
        url = f"{self.base_url}/api/v1/auth/login"
        data = {"username": username, "password": password}

        response = self.session.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            self.token = result["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            print(f"✅ 登录成功: {username}")
            return True
        else:
            print(f"❌ 登录失败: {response.text}")
            return False

    def test_create_user_admin(self):
        """测试创建用户管理员"""
        url = f"{self.base_url}/api/v1/users/"
        data = {
            "username": "company_admin",
            "password": "password123",
            "email": "company@example.com",
            "role": "user_admin",
            "full_name": "公司管理员",
            "company": "测试公司",
            "max_employees": 5,
        }

        response = self.session.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 用户管理员创建成功: {result['username']}")
            return result
        else:
            print(f"❌ 用户管理员创建失败: {response.text}")
            return None

    def test_create_employee(self, user_admin_token):
        """测试创建员工（使用用户管理员token）"""
        # 临时切换token
        old_token = self.token
        self.session.headers.update({"Authorization": f"Bearer {user_admin_token}"})

        url = f"{self.base_url}/api/v1/users/"
        data = {
            "username": "employee001",
            "password": "password123",
            "email": "employee001@example.com",
            "role": "employee",
            "full_name": "员工001",
        }

        response = self.session.post(url, json=data)

        # 恢复原token
        self.session.headers.update({"Authorization": f"Bearer {old_token}"})

        if response.status_code == 200:
            result = response.json()
            print(f"✅ 员工创建成功: {result['username']}")
            return result
        else:
            print(f"❌ 员工创建失败: {response.text}")
            return None

    def test_pricing_rules(self):
        """测试收费规则管理"""
        # 获取收费规则
        url = f"{self.base_url}/api/v1/billing/pricing-rules"
        response = self.session.get(url)

        if response.status_code == 200:
            rules = response.json()
            print(f"✅ 获取收费规则成功，共{len(rules)}条规则")
            for rule in rules:
                print(
                    f"  - {rule['name']}: {rule['unit_price']}元/{rule['billing_period']}"
                )
            return rules
        else:
            print(f"❌ 获取收费规则失败: {response.text}")
            return []

    def test_work_record_creation(self, employee_id):
        """测试工作记录创建"""
        url = f"{self.base_url}/api/v1/kpi/"
        data = {
            "employee_id": employee_id,
            "platform": "xiaohongshu",
            "action_type": "follow",
            "target_username": "test_user",
            "target_user_id": "12345",
            "device_id": "device001",
        }

        response = self.session.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 工作记录创建成功: ID {result['id']}")
            return result
        else:
            print(f"❌ 工作记录创建失败: {response.text}")
            return None

    def test_dashboard_data(self):
        """测试仪表盘数据"""
        url = f"{self.base_url}/api/v1/reports/dashboard"
        response = self.session.get(url)

        if response.status_code == 200:
            result = response.json()
            print("✅ 仪表盘数据获取成功:")
            print(f"  - 用户管理员数量: {result.get('total_user_admins', 0)}")
            print(f"  - 总员工数: {result.get('total_employees', 0)}")
            return result
        else:
            print(f"❌ 仪表盘数据获取失败: {response.text}")
            return None

    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始API功能测试...")
        print("=" * 50)

        # 1. 测试登录
        if not self.login():
            print("❌ 测试终止：登录失败")
            return

        time.sleep(1)

        # 2. 测试创建用户管理员
        user_admin = self.test_create_user_admin()
        if not user_admin:
            print("⚠️  跳过后续测试：用户管理员创建失败")
            return

        time.sleep(1)

        # 3. 获取用户管理员的token（需要该管理员重新登录）
        print("\n🔄 用户管理员登录测试...")
        user_admin_tester = FlowFarmAPITester(self.base_url)
        if user_admin_tester.login("company_admin", "password123"):
            user_admin_token = user_admin_tester.token

            # 4. 测试创建员工
            employee = self.test_create_employee(user_admin_token)

            if employee:
                time.sleep(1)
                # 5. 测试创建工作记录
                self.test_work_record_creation(employee["id"])

        time.sleep(1)

        # 6. 测试收费规则
        self.test_pricing_rules()

        time.sleep(1)

        # 7. 测试仪表盘
        self.test_dashboard_data()

        print("\n" + "=" * 50)
        print("🎉 API测试完成！")


def main():
    """主函数"""
    print("Flow Farm API 测试工具")
    print("确保服务器已启动在 http://localhost:8000")

    # 等待用户确认
    input("按回车键开始测试...")

    tester = FlowFarmAPITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
