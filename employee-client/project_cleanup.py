#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flow Farm 项目清理工具
全面分析项目文件，删除过时内容，只保留两个核心系统
"""

import os
import shutil
from pathlib import Path


def analyze_project_structure():
    """分析整个项目结构"""
    print("🔍 Flow Farm 项目全面分析")
    print("=" * 80)

    # 分析根目录
    root_files = []
    for item in Path(".").iterdir():
        if item.is_file():
            root_files.append((item.name, item.stat().st_size))

    print("\n📁 根目录文件:")
    print("-" * 50)
    for filename, size in sorted(root_files):
        print(f"  {filename:40} ({size:,} bytes)")

    # 分析src目录
    src_path = Path("src")
    if src_path.exists():
        print("\n📁 src目录结构:")
        print("-" * 50)
        for item in sorted(src_path.rglob("*")):
            if item.is_file():
                rel_path = item.relative_to(src_path)
                size = item.stat().st_size
                print(f"  {str(rel_path):50} ({size:,} bytes)")


def identify_core_systems():
    """识别两个核心系统的文件"""
    print("\n\n🎯 核心系统识别")
    print("=" * 80)

    # 系统1: 原始OneDragon完整系统
    core_system_1 = {
        "name": "原始OneDragon完整系统",
        "files": [
            "src/main_onedragon_optimized.py",  # 主界面
            "src/core/",  # 核心模块（设备管理等）
            "src/gui/",  # GUI组件
            "src/auth/",  # 认证系统
            "src/utils/",  # 工具类
            "src/config/",  # 配置管理
        ],
    }

    # 系统2: 任务管理优化版（如果存在）
    core_system_2 = {
        "name": "OneDragon任务管理优化版",
        "files": [
            # 需要识别具体的任务管理优化文件
        ],
    }

    print("✅ 系统1: 原始OneDragon完整系统")
    for file_path in core_system_1["files"]:
        if Path(file_path).exists():
            if Path(file_path).is_dir():
                file_count = len(list(Path(file_path).rglob("*.py")))
                print(f"  ✅ {str(file_path):40} (目录, {file_count} Python文件)")
            else:
                size = Path(file_path).stat().st_size
                print(f"  ✅ {file_path:40} ({size:,} bytes)")
        else:
            print(f"  ❌ {file_path:40} (不存在)")

    return core_system_1, core_system_2


def identify_garbage_files():
    """识别需要删除的垃圾文件"""
    print("\n\n🗑️  垃圾文件识别")
    print("=" * 80)

    # 一次性脚本和测试文件
    script_patterns = [
        "*_test.py",
        "*_demo.py",
        "*test*.py",
        "*demo*.py",
        "test_*.py",
        "demo_*.py",
        "*_temp.py",
        "*temp*.py",
        "*_old.py",
        "*old*.py",
        "*_backup.py",
        "*backup*.py",
        "*_deprecated.py",
        "*deprecated*.py",
    ]

    # 过时的文档
    doc_patterns = [
        "*.tmp",
        "*.bak",
        "*_old.*",
        "*old.*",
        "*_backup.*",
        "*backup.*",
        "*_temp.*",
        "*temp.*",
        "*_deprecated.*",
        "*deprecated.*",
        "TEMP_*",
        "OLD_*",
        "BACKUP_*",
    ]

    # 分析工具和恢复脚本（一次性使用）
    cleanup_scripts = [
        "interface_recovery.py",
        "gui_cleanup_analyzer.py",
        "project_cleanup.py",
    ]

    garbage_files = []

    print("🔍 搜索垃圾文件:")

    # 搜索脚本模式
    for pattern in script_patterns:
        for file_path in Path(".").rglob(pattern):
            if file_path.is_file():
                garbage_files.append(file_path)
                print(f"  🗑️  {str(file_path)} (脚本垃圾)")

    # 搜索文档模式
    for pattern in doc_patterns:
        for file_path in Path(".").rglob(pattern):
            if file_path.is_file():
                garbage_files.append(file_path)
                print(f"  🗑️  {str(file_path)} (文档垃圾)")

    # 清理脚本
    for script_name in cleanup_scripts:
        script_path = Path(script_name)
        if script_path.exists():
            garbage_files.append(script_path)
            print(f"  🗑️  {str(script_path)} (一次性脚本)")

    return garbage_files


def identify_outdated_docs():
    """识别过时的文档"""
    print("\n\n📄 过时文档识别")
    print("=" * 80)

    # 过时文档模式
    outdated_patterns = [
        "*OPTIMIZATION*.md",
        "*CLEANUP*.md",
        "*MIGRATION*.md",
        "*COMPLETION*.md",
        "*PERFORMANCE*.md",
        "*FIX*.md",
        "*REPORT*.md",
        "LAYOUT_*.md",
        "ONEDRAGON_*.md",
        "GUI_*.md",
        "TASK_MANAGEMENT_*.md",
    ]

    outdated_docs = []

    print("📄 搜索过时文档:")
    for pattern in outdated_patterns:
        for file_path in Path(".").rglob(pattern):
            if file_path.is_file() and file_path.suffix.lower() == ".md":
                outdated_docs.append(file_path)
                size = file_path.stat().st_size
                print(f"  📄 {str(file_path):50} ({size:,} bytes)")

    return outdated_docs


def identify_obsolete_interfaces():
    """识别废弃的界面文件"""
    print("\n\n🖥️  废弃界面识别")
    print("=" * 80)

    # 保留的核心界面
    keep_interfaces = {
        "src/main_onedragon_optimized.py",  # 原始完整系统
        "src/main.py",  # 主入口
    }

    # 查找所有界面文件
    interface_files = []
    for file_path in Path("src").rglob("*interface*.py"):
        if file_path.is_file():
            interface_files.append(file_path)

    for file_path in Path("src").rglob("main_*.py"):
        if file_path.is_file() and file_path.name != "main.py":
            interface_files.append(file_path)

    for file_path in Path("src").rglob("launch_*.py"):
        if file_path.is_file():
            interface_files.append(file_path)

    obsolete_interfaces = []

    print("🖥️  界面文件分析:")
    for file_path in interface_files:
        if str(file_path) in keep_interfaces:
            size = file_path.stat().st_size
            print(f"  ✅ 保留: {str(file_path):50} ({size:,} bytes)")
        else:
            obsolete_interfaces.append(file_path)
            size = file_path.stat().st_size
            print(f"  🗑️  删除: {str(file_path):50} ({size:,} bytes)")

    return obsolete_interfaces


def create_cleanup_plan(garbage_files, outdated_docs, obsolete_interfaces):
    """创建清理计划"""
    print("\n\n📋 清理计划")
    print("=" * 80)

    all_delete_files = garbage_files + outdated_docs + obsolete_interfaces

    print(f"📊 清理统计:")
    print(f"  🗑️  垃圾脚本文件: {len(garbage_files)} 个")
    print(f"  📄 过时文档: {len(outdated_docs)} 个")
    print(f"  🖥️  废弃界面: {len(obsolete_interfaces)} 个")
    print(f"  📦 总计删除: {len(all_delete_files)} 个文件")

    if all_delete_files:
        total_size = sum(f.stat().st_size for f in all_delete_files)
        print(f"  💾 释放空间: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")

    print(f"\n🎯 保留的核心文件:")
    keep_files = [
        "src/main_onedragon_optimized.py",
        "src/main.py",
        "src/core/",
        "src/gui/",
        "src/auth/",
        "src/utils/",
        "src/config/",
        "requirements.txt",
        "README.md",
    ]

    for file_path in keep_files:
        if Path(file_path).exists():
            if Path(file_path).is_dir():
                file_count = len(list(Path(file_path).rglob("*.py")))
                print(f"  ✅ {file_path:40} (目录, {file_count} 文件)")
            else:
                size = Path(file_path).stat().st_size
                print(f"  ✅ {file_path:40} ({size:,} bytes)")

    return all_delete_files


def execute_cleanup(delete_files, dry_run=True):
    """执行清理操作"""
    print(f"\n\n{'🧪 模拟清理' if dry_run else '🗑️  执行清理'}")
    print("=" * 80)

    if dry_run:
        print("⚠️  这是模拟运行，不会实际删除文件")
        print("📝 如需实际清理，请设置 dry_run=False")

    success_count = 0
    error_count = 0

    for file_path in delete_files:
        try:
            if dry_run:
                print(f"  🧪 模拟删除: {file_path}")
            else:
                if file_path.is_file():
                    file_path.unlink()
                    print(f"  ✅ 已删除: {file_path}")
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                    print(f"  ✅ 已删除目录: {file_path}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ 删除失败: {file_path} - {e}")
            error_count += 1

    print(f"\n📊 清理结果:")
    print(f"  ✅ 成功: {success_count} 个")
    print(f"  ❌ 失败: {error_count} 个")


def main():
    """主函数"""
    print("🧹 Flow Farm 项目清理工具")
    print(f"📁 工作目录: {Path.cwd()}")
    print()

    # 分析项目结构
    analyze_project_structure()

    # 识别核心系统
    core_system_1, core_system_2 = identify_core_systems()

    # 识别垃圾文件
    garbage_files = identify_garbage_files()

    # 识别过时文档
    outdated_docs = identify_outdated_docs()

    # 识别废弃界面
    obsolete_interfaces = identify_obsolete_interfaces()

    # 创建清理计划
    delete_files = create_cleanup_plan(
        garbage_files, outdated_docs, obsolete_interfaces
    )

    # 模拟清理（安全模式）
    execute_cleanup(delete_files, dry_run=True)

    print("\n" + "=" * 80)
    print("🎯 下一步操作:")
    print("  1. 检查上述清理计划是否正确")
    print("  2. 如果确认，修改 execute_cleanup(delete_files, dry_run=False)")
    print("  3. 或者手动执行删除命令")
    print("  4. 最后验证两个核心系统是否正常工作")


if __name__ == "__main__":
    main()
