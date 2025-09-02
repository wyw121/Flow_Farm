#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flow Farm 项目清理工具 - 简化版本
用于清理不需要的文件，只保留两个核心系统
"""

import os
import shutil
from pathlib import Path


def main():
    print("🧹 Flow Farm 项目清理工具 - 执行模式")
    print("=" * 50)

    # 删除根目录中的清理分析脚本
    cleanup_scripts = [
        "gui_cleanup_analyzer.py",
        "interface_recovery.py",
        "project_cleanup.py",
        "test_gui.py",
        "test_performance.py",
        "launch_simple_interface.py",
    ]

    deleted_count = 0

    print("\n🗑️ 删除一次性脚本和测试文件:")
    for script_name in cleanup_scripts:
        script_path = Path(script_name)
        if script_path.exists():
            try:
                script_path.unlink()
                print(f"  ✅ 已删除: {script_name}")
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ 删除失败: {script_name} - {e}")
        else:
            print(f"  ⚠️  不存在: {script_name}")

    # 删除src目录中的多余interface文件
    src_cleanup_files = [
        "src/main_modern_task_interface.py",
        "src/main_professional_task_interface.py",
        "src/main_simple_professional_interface.py",
        "src/minimal_interface.py",
        "src/launch_compatible_interface.py",
        "src/launch_modern_task_interface.py",
        "src/launch_professional_interface.py",
    ]

    print("\n🗑️ 删除多余界面文件:")
    for file_name in src_cleanup_files:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"  ✅ 已删除: {file_name}")
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ 删除失败: {file_name} - {e}")
        else:
            print(f"  ⚠️  不存在: {file_name}")

    # 删除backup目录中的空文件
    backup_cleanup_files = [
        "src/gui/backup_old_gui/compatible_main_window.py",
        "src/gui/backup_old_gui/simple_modern_window.py",
    ]

    print("\n🗑️ 删除备份目录中的空文件:")
    for file_name in backup_cleanup_files:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                file_size = file_path.stat().st_size
                if file_size == 0:
                    file_path.unlink()
                    print(f"  ✅ 已删除空文件: {file_name}")
                    deleted_count += 1
                else:
                    print(f"  ⚠️  非空文件，跳过: {file_name} ({file_size} bytes)")
            except Exception as e:
                print(f"  ❌ 删除失败: {file_name} - {e}")
        else:
            print(f"  ⚠️  不存在: {file_name}")

    # 删除不必要的报告文档（保留核心文档）
    doc_cleanup_files = [
        "GUI_PERFORMANCE_FIX_REPORT.md",
        "GUI_REDESIGN_COMPLETION_REPORT.md",
        "LAYOUT_OPTIMIZATION_SUMMARY.md",
        "ONEDRAGON_COMPLETION_REPORT.md",
        "ONEDRAGON_GUI_MIGRATION.md",
        "TASK_MANAGEMENT_OPTIMIZATION_REPORT.md",
    ]

    print("\n🗑️ 删除过时报告文档:")
    for doc_name in doc_cleanup_files:
        doc_path = Path(doc_name)
        if doc_path.exists():
            try:
                doc_path.unlink()
                print(f"  ✅ 已删除: {doc_name}")
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ 删除失败: {doc_name} - {e}")
        else:
            print(f"  ⚠️  不存在: {doc_name}")

    print(f"\n✅ 清理完成！总共删除了 {deleted_count} 个文件")

    # 显示保留的核心系统
    print("\n🎯 保留的核心系统:")

    core_files = [
        "src/main_onedragon_optimized.py",
        "src/main.py",
        "README.md",
        "requirements.txt",
        "DEVICE_MANAGEMENT_GUIDE.md",
        "TASK_MANAGEMENT_USER_GUIDE.md",
    ]

    for file_name in core_files:
        file_path = Path(file_name)
        if file_path.exists():
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"  ✅ {file_name:40} ({size:,} bytes)")
            else:
                print(f"  ✅ {file_name:40} (目录)")
        else:
            print(f"  ❌ {file_name:40} (丢失)")

    print("\n🎉 项目清理完成！现在只保留两个核心系统:")
    print("   1. 原始OneDragon完整系统 (main_onedragon_optimized.py)")
    print("   2. 任务管理优化系统 (通过main.py选择)")


if __name__ == "__main__":
    main()
