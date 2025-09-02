#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flow Farm 界面恢复和诊断工具
帮助用户检查和恢复被损坏的界面文件
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_interface_files():
    """检查所有界面文件的状态"""
    interface_files = {
        "main_onedragon_optimized.py": "OneDragon 风格界面",
        "main_professional_task_interface.py": "专业任务管理界面",
        "main_modern_task_interface.py": "现代任务界面",
        "main_compatible_professional_interface.py": "兼容性专业界面",
        "main_simple_professional_interface.py": "简单专业界面",
        "minimal_interface.py": "极简界面",
        "main_optimized_clean.py": "清洁优化界面",
    }

    launcher_files = {
        "launch_professional_interface.py": "专业界面启动器",
        "launch_modern_task_interface.py": "现代界面启动器",
        "launch_compatible_interface.py": "兼容界面启动器",
    }

    print("🔍 Flow Farm 界面文件诊断报告")
    print("=" * 60)

    print("\n📋 主界面文件检查:")
    for filename, description in interface_files.items():
        filepath = PROJECT_ROOT / filename
        if filepath.exists():
            size = filepath.stat().st_size
            if size == 0:
                status = "❌ 空文件"
                color = "red"
            elif size < 1000:
                status = "⚠️  文件过小"
                color = "yellow"
            else:
                status = "✅ 正常"
                color = "green"

            print(f"  {filename:35} - {description:20} [{status}] ({size} bytes)")

            # 检查是否有main函数
            if size > 0:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        if "def main(" in content:
                            print(f"    {'':35}   ✅ 包含main函数")
                        else:
                            print(f"    {'':35}   ❌ 缺少main函数")
                except Exception as e:
                    print(f"    {'':35}   ❌ 读取失败: {e}")
        else:
            print(f"  {filename:35} - {description:20} [❌ 文件不存在]")

    print("\n🚀 启动器文件检查:")
    for filename, description in launcher_files.items():
        filepath = PROJECT_ROOT / filename
        if filepath.exists():
            size = filepath.stat().st_size
            status = "✅ 存在" if size > 0 else "❌ 空文件"
            print(f"  {filename:35} - {description:20} [{status}] ({size} bytes)")
        else:
            print(f"  {filename:35} - {description:20} [❌ 文件不存在]")


def test_interface_imports():
    """测试各个界面模块的导入"""
    print("\n\n🧪 界面模块导入测试:")
    print("=" * 60)

    test_modules = [
        ("main_onedragon_optimized", "OneDragon界面"),
        ("minimal_interface", "极简界面"),
        ("main_professional_task_interface", "专业界面"),
        ("main_modern_task_interface", "现代界面"),
        ("main_compatible_professional_interface", "兼容界面"),
        ("main_simple_professional_interface", "简单界面"),
    ]

    working_interfaces = []
    broken_interfaces = []

    for module_name, description in test_modules:
        try:
            module = __import__(module_name)
            if hasattr(module, "main"):
                print(f"  ✅ {module_name:35} - {description} [可以导入和运行]")
                working_interfaces.append((module_name, description))
            else:
                print(f"  ⚠️  {module_name:35} - {description} [可导入但缺少main函数]")
                broken_interfaces.append((module_name, description, "缺少main函数"))
        except ImportError as e:
            print(f"  ❌ {module_name:35} - {description} [导入失败: {str(e)[:50]}...]")
            broken_interfaces.append((module_name, description, f"导入失败: {e}"))
        except Exception as e:
            print(f"  ❌ {module_name:35} - {description} [其他错误: {str(e)[:50]}...]")
            broken_interfaces.append((module_name, description, f"其他错误: {e}"))

    print(f"\n📊 测试总结:")
    print(f"  ✅ 可用界面: {len(working_interfaces)} 个")
    print(f"  ❌ 损坏界面: {len(broken_interfaces)} 个")

    if working_interfaces:
        print(f"\n🎯 推荐使用的界面:")
        for module_name, description in working_interfaces:
            print(
                f"    python src/main.py --interface {module_name.replace('main_', '').replace('_interface', '')}"
            )

    return working_interfaces, broken_interfaces


def suggest_recovery_actions(working_interfaces, broken_interfaces):
    """建议恢复操作"""
    print(f"\n\n🔧 恢复建议:")
    print("=" * 60)

    if len(working_interfaces) >= 2:
        print("✅ 您有多个可用的界面版本，建议:")
        print(
            "   1. 使用 OneDragon 界面 (推荐): python src/main.py --interface onedragon"
        )
        print("   2. 使用极简界面 (备选): python src/main.py --interface minimal")
        print("   3. 查看所有可用版本: python src/main.py --list-interfaces")

    elif len(working_interfaces) == 1:
        module_name, description = working_interfaces[0]
        interface_arg = module_name.replace("main_", "").replace("_interface", "")
        print(f"⚠️  您只有1个可用界面: {description}")
        print(f"   使用命令: python src/main.py --interface {interface_arg}")

    else:
        print("❌ 所有界面都已损坏，需要恢复")
        print("   建议从以下选项选择:")
        print("   1. 从备份恢复界面文件")
        print("   2. 重新克隆项目")
        print("   3. 联系技术支持")

    if broken_interfaces:
        print(f"\n🛠️  需要修复的界面 ({len(broken_interfaces)} 个):")
        for module_name, description, error in broken_interfaces:
            print(f"   ❌ {description}: {error}")


def main():
    """主函数"""
    print("🔍 Flow Farm 界面系统诊断工具")
    print(f"📁 工作目录: {PROJECT_ROOT}")
    print()

    # 检查文件状态
    check_interface_files()

    # 测试导入
    working_interfaces, broken_interfaces = test_interface_imports()

    # 建议恢复操作
    suggest_recovery_actions(working_interfaces, broken_interfaces)

    print(f"\n" + "=" * 60)
    print("🎯 快速启动命令:")
    print("   python src/main.py --list-interfaces        # 查看所有界面")
    print("   python src/main.py --interface onedragon    # OneDragon界面")
    print("   python src/main.py --interface minimal      # 极简界面")
    print("   python interface_recovery.py                # 运行此诊断工具")


if __name__ == "__main__":
    main()
