#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书完整自动关注工具 - 简化测试版本
验证模块化流程的语法正确性
"""

def test_import():
    """测试导入"""
    try:
        from smart_follow_complete import XiaohongshuFullAutomation
        print("✅ 模块导入成功")

        automation = XiaohongshuFullAutomation()
        print("✅ 类实例化成功")

        print("📋 可用方法:")
        methods = [method for method in dir(automation) if not method.startswith('_')]
        for method in methods:
            print(f"  - {method}")

        return True
    except Exception as e:
        print(f"❌ 模块测试失败: {e}")
        return False

if __name__ == "__main__":
    test_import()
