#!/usr/bin/env python3
"""
测试登录API的脚本
"""
import json

import requests


def test_login():
    url = "http://localhost:8000/api/v1/auth/login"
    headers = {"Content-Type": "application/json"}

    # 测试数据
    test_data = {"identifier": "admin", "password": "admin123"}

    try:
        response = requests.post(url, json=test_data, headers=headers, timeout=10)

        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")

        if response.status_code == 422:
            print("\n422 错误详情:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except ValueError:
                print("无法解析错误响应")

    except requests.RequestException as e:
        print(f"请求异常: {e}")


if __name__ == "__main__":
    test_login()
