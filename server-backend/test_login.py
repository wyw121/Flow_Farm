#!/usr/bin/env python
"""
测试登录功能
"""

import json

import requests

# 服务器地址
BASE_URL = "http://localhost:8000"


def test_login():
    """测试登录功能"""
    print("🧪 测试登录功能...")

    # 测试默认管理员登录
    login_data = {"username": "admin", "password": "admin123"}

    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)

        if response.status_code == 200:
            result = response.json()
            print("✅ 登录成功！")
            print(f"用户: {result.get('username')}")
            print(f"角色: {result.get('role')}")
            print(f"Token: {result.get('access_token')[:50]}...")
            return result.get("access_token")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None

    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


def test_get_users(token):
    """测试获取用户列表"""
    if not token:
        print("⚠️ 无token，跳过用户列表测试")
        return

    print("\n🧪 测试获取用户列表...")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BASE_URL}/api/v1/users/", headers=headers)

        if response.status_code == 200:
            result = response.json()
            print("✅ 获取用户列表成功！")
            print(f"总用户数: {result.get('total', 0)}")
            print(f"当前页: {result.get('page', 1)}")

            users = result.get("items", [])
            for user in users[:3]:  # 只显示前3个用户
                print(f"  - {user.get('username')} ({user.get('role')})")
        else:
            print(f"❌ 获取用户列表失败: {response.status_code}")
            print(f"错误信息: {response.text}")

    except Exception as e:
        print(f"❌ 请求失败: {e}")


def test_health():
    """测试服务器健康状态"""
    print("🧪 测试服务器连接...")

    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ 服务器运行正常")
        else:
            print(f"⚠️ 服务器响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 无法连接服务器: {e}")


if __name__ == "__main__":
    print("🚀 Flow Farm 服务器测试")
    print("=" * 50)

    # 测试服务器连接
    test_health()

    # 测试登录
    token = test_login()

    # 测试API功能
    test_get_users(token)

    print("\n" + "=" * 50)
    print("✅ 测试完成")
