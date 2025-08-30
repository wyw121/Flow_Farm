#!/usr/bin/env python3
"""
调试登录API的脚本
"""
import json

import requests


def test_login_api():
    url = "http://localhost:8000/api/v1/auth/login"

    # 测试数据
    test_data = {"identifier": "admin", "password": "admin123"}

    print("🧪 测试登录API...")
    print(f"URL: {url}")
    print(f"数据: {json.dumps(test_data, indent=2)}")

    try:
        response = requests.post(
            url, json=test_data, headers={"Content-Type": "application/json"}
        )

        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")

        if response.status_code == 200:
            print("✅ 登录成功!")
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2)}")
        else:
            print("❌ 登录失败!")
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, indent=2)}")
            except:
                print(f"响应文本: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        print("请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 请求失败: {e}")


if __name__ == "__main__":
    test_login_api()
