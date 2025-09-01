"""
Flow Farm OneDragon 架构升级脚本
自动安装和配置 OneDragon 版本的依赖
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """运行命令并显示结果"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False


def main():
    """主函数"""
    print("🚀 Flow Farm OneDragon 架构升级开始...")

    # 检查 Python 版本
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python 版本太低: {sys.version}")
        print("请使用 Python 3.8 或更高版本")
        return False

    print(f"✅ Python 版本: {sys.version}")

    # 升级 pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "升级 pip"):
        return False

    # 安装核心依赖
    dependencies = [
        "PySide6==6.8.0.2",
        "PyQt-Fluent-Widgets>=1.5.0",  # 修正包名
        "qtawesome==1.3.1",
    ]

    for dep in dependencies:
        if not run_command(f"{sys.executable} -m pip install {dep}", f"安装 {dep}"):
            return False

    # 验证安装
    print("\n🔍 验证安装...")

    try:
        import PySide6

        print(f"✅ PySide6: {PySide6.__version__}")
    except ImportError:
        print("❌ PySide6 安装失败")
        return False

    try:
        from qfluentwidgets import FluentIcon  # 正确的导入方式

        print("✅ qfluentwidgets 安装成功")
    except ImportError:
        try:
            import PyQt_Fluent_Widgets

            print("✅ PyQt-Fluent-Widgets 安装成功")
        except ImportError:
            print("❌ Fluent Widgets 安装失败")
            return False

    try:
        import qtawesome

        print("✅ qtawesome 安装成功")
    except ImportError:
        print("❌ qtawesome 安装失败")
        return False

    print("\n🎉 OneDragon 架构升级完成!")
    print("现在可以运行: python start_onedragon.py")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
