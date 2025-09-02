#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flow Farm GUI 文件清理分析器
分析所有GUI相关文件，帮助用户清理不需要的版本
"""

import os
import sys
from pathlib import Path


def analyze_gui_files():
    """分析所有GUI相关文件"""
    src_path = Path("src")

    print("🔍 Flow Farm GUI 文件完整分析")
    print("=" * 80)

    # 主GUI界面文件
    main_interfaces = []
    launch_files = []
    other_files = []

    for file in src_path.glob("*.py"):
        filename = file.name
        size = file.stat().st_size

        if any(
            keyword in filename.lower() for keyword in ["interface", "gui", "main_"]
        ):
            if filename.startswith("main_") and "interface" in filename:
                main_interfaces.append((filename, size))
            elif filename.startswith("launch_"):
                launch_files.append((filename, size))
            elif "interface" in filename:
                other_files.append((filename, size))

    print("\n📋 主界面文件:")
    print("-" * 50)
    for filename, size in sorted(main_interfaces):
        status = "✅ 正常" if size > 1000 else ("❌ 空文件" if size == 0 else "⚠️  过小")
        print(f"  {filename:40} [{status:8}] ({size:,} bytes)")

    print("\n🚀 启动器文件:")
    print("-" * 50)
    for filename, size in sorted(launch_files):
        status = "✅ 正常" if size > 100 else ("❌ 空文件" if size == 0 else "⚠️  过小")
        print(f"  {filename:40} [{status:8}] ({size:,} bytes)")

    print("\n📁 其他界面相关文件:")
    print("-" * 50)
    for filename, size in sorted(other_files):
        status = "✅ 正常" if size > 100 else ("❌ 空文件" if size == 0 else "⚠️  过小")
        print(f"  {filename:40} [{status:8}] ({size:,} bytes)")

    return main_interfaces, launch_files, other_files


def identify_garbage_files():
    """识别垃圾文件"""
    print("\n\n🗑️  垃圾文件识别 (用户指定删除):")
    print("=" * 80)

    garbage_files = [
        "minimal_interface.py",  # 用户明确说是测试用的垃圾
        "main_modern_task_interface.py",  # 用户说是垃圾
        "launch_modern_task_interface.py",  # 对应的启动器
    ]

    print("❌ 确认删除的垃圾文件:")
    for filename in garbage_files:
        filepath = Path("src") / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"  {filename:40} ({size:,} bytes) - 准备删除")
        else:
            print(f"  {filename:40} (不存在)")

    return garbage_files


def check_questionable_files():
    """检查可疑文件"""
    print("\n\n❓ 需要确认的文件 (用户要求先测试):")
    print("=" * 80)

    questionable = [
        ("main_compatible_professional_interface.py", "兼容性专业界面"),
        ("main_simple_professional_interface.py", "简单专业界面"),
        ("launch_compatible_interface.py", "兼容界面启动器"),
        ("launch_professional_interface.py", "专业界面启动器"),
    ]

    print("🧪 需要测试启动的文件:")
    for filename, description in questionable:
        filepath = Path("src") / filename
        if filepath.exists():
            size = filepath.stat().st_size
            status = (
                "✅ 正常" if size > 1000 else ("❌ 空文件" if size == 0 else "⚠️  过小")
            )
            print(f"  {filename:40} - {description:15} [{status}] ({size:,} bytes)")
        else:
            print(f"  {filename:40} - {description:15} [❌ 不存在]")

    return questionable


def show_keep_files():
    """显示保留的文件"""
    print("\n\n✅ 保留的核心文件:")
    print("=" * 80)

    keep_files = [
        ("main_onedragon_optimized.py", "OneDragon风格界面 - 主要开发目标"),
        ("main.py", "主程序入口"),
    ]

    for filename, description in keep_files:
        filepath = Path("src") / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"  ✅ {filename:40} - {description} ({size:,} bytes)")
        else:
            print(f"  ❌ {filename:40} - {description} (文件不存在!)")


def main():
    """主函数"""
    os.chdir(Path(__file__).parent)

    print("🧹 Flow Farm GUI 清理分析工具")
    print(f"📁 工作目录: {Path.cwd()}")
    print()

    # 分析所有GUI文件
    main_interfaces, launch_files, other_files = analyze_gui_files()

    # 识别垃圾文件
    garbage_files = identify_garbage_files()

    # 检查可疑文件
    questionable = check_questionable_files()

    # 显示保留文件
    show_keep_files()

    print("\n" + "=" * 80)
    print("🎯 清理计划总结:")
    print("=" * 80)
    print("1️⃣  立即删除垃圾文件:")
    for filename in garbage_files:
        print(f"   ❌ {filename}")

    print("\n2️⃣  等待测试确认:")
    for filename, description in questionable:
        print(f"   ❓ {filename} - {description}")

    print("\n3️⃣  保留核心文件:")
    print("   ✅ main_onedragon_optimized.py - 主要开发目标")
    print("   ✅ main.py - 主程序入口")

    print("\n🚀 下一步操作:")
    print("   1. 运行删除命令清理垃圾文件")
    print("   2. 测试 compatible 和 simple 界面")
    print("   3. 根据测试结果决定是否保留")


if __name__ == "__main__":
    main()
