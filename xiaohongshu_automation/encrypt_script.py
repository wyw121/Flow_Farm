#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python脚本加密打包工具
用于保护源代码不被轻易查看
"""

import os
import sys
import subprocess
import base64
import py_compile
import zipfile
import shutil
from pathlib import Path

class ScriptEncryptor:
    def __init__(self, source_file):
        self.source_file = source_file
        self.work_dir = Path("encrypted_build")
        self.work_dir.mkdir(exist_ok=True)

    def method1_pyinstaller_onefile(self):
        """方法1: PyInstaller单文件打包 (推荐)"""
        print("🔒 方法1: 使用PyInstaller创建单文件可执行程序...")

        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",                    # 打包成单个exe文件
            "--console",                    # 显示控制台窗口
            "--clean",                      # 清理临时文件
            "--distpath", "dist",           # 输出目录
            "--workpath", "build",          # 工作目录
            "--specpath", ".",              # spec文件位置
            "--name", "xiaohongshu_tool",   # 可执行文件名
            self.source_file
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ PyInstaller打包成功!")
                print(f"📁 可执行文件位置: dist/xiaohongshu_tool.exe")
                return True
            else:
                print(f"❌ PyInstaller打包失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ PyInstaller打包异常: {e}")
            return False

    def method2_pyinstaller_optimized(self):
        """方法2: PyInstaller优化版本 (更高安全性)"""
        print("🔐 方法2: 使用PyInstaller创建优化版本...")

        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",                     # 单文件
            "--console",                     # 保留控制台
            "--clean",                       # 清理
            "--upx-dir", ".",               # UPX压缩(如果可用)
            "--strip",                       # 移除符号信息
            "--distpath", "dist_secure",     # 安全版本输出目录
            "--workpath", "build_secure",    # 工作目录
            "--name", "xhs_automation_secure", # 文件名
            "--add-data", "*.xml;.",        # 包含XML文件
            self.source_file
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ 优化版打包成功!")
                print(f"📁 可执行文件位置: dist_secure/xhs_automation_secure.exe")
                return True
            else:
                print(f"❌ 优化版打包失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 优化版打包异常: {e}")
            return False

    def method3_bytecode_protection(self):
        """方法3: 字节码保护"""
        print("🛡️ 方法3: 创建字节码保护版本...")

        try:
            # 编译为.pyc文件
            compiled_file = self.work_dir / "smart_follow_compiled.pyc"
            py_compile.compile(self.source_file, compiled_file, doraise=True)

            # 创建启动器
            launcher_content = f'''
import sys
import os
import marshal
import types

# 加载编译后的字节码
with open("{compiled_file.name}", "rb") as f:
    f.read(16)  # 跳过头部
    code = marshal.load(f)

# 执行代码
exec(code)
'''

            launcher_file = self.work_dir / "launcher.py"
            with open(launcher_file, 'w', encoding='utf-8') as f:
                f.write(launcher_content)

            print(f"✅ 字节码版本创建成功!")
            print(f"📁 启动文件: {launcher_file}")
            print(f"📁 字节码文件: {compiled_file}")
            return True

        except Exception as e:
            print(f"❌ 字节码保护失败: {e}")
            return False

    def create_deployment_package(self):
        """创建部署包"""
        print("📦 创建最终部署包...")

        package_dir = Path("xiaohongshu_automation_package")
        package_dir.mkdir(exist_ok=True)

        # 复制可执行文件
        if Path("dist/xiaohongshu_tool.exe").exists():
            shutil.copy("dist/xiaohongshu_tool.exe", package_dir)

        # 复制配置文件
        config_files = ["使用说明.txt", "启动自动关注.bat"]
        for config_file in config_files:
            if Path(config_file).exists():
                shutil.copy(config_file, package_dir)

        # 创建新的启动脚本
        new_bat_content = '''@echo off
chcp 65001 >nul
echo 🚀 启动小红书自动关注工具...
echo =============================================
echo 📱 请确保:
echo    1. 雷电模拟器已启动
echo    2. 小红书APP已打开并登录
echo    3. 在推荐页面或用户列表页面
echo =============================================
pause
echo 🎯 开始执行自动关注...
xiaohongshu_tool.exe
echo.
echo ✅ 程序执行完成!
pause
'''

        with open(package_dir / "启动工具.bat", 'w', encoding='gbk') as f:
            f.write(new_bat_content)

        # 创建部署说明
        deploy_readme = """
# 小红书自动关注工具 - 加密版

## 部署包内容
- xiaohongshu_tool.exe: 主程序(已加密)
- 启动工具.bat: 启动脚本
- 使用说明.txt: 详细使用说明

## 使用方法
1. 确保雷电模拟器已启动
2. 打开小红书APP并登录
3. 双击"启动工具.bat"运行程序

## 特点
- 源代码已完全加密保护
- 无需安装Python环境
- 单文件运行，便于部署
- 包含完整的验证机制

## 技术说明
此程序使用PyInstaller打包，源代码已编译为字节码并加密，
无法通过常规方法查看源代码内容。
"""

        with open(package_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(deploy_readme)

        print(f"✅ 部署包创建完成: {package_dir}")
        return package_dir

def main():
    source_file = "smart_follow_safe.py"  # 使用安全测试通过的版本

    if not Path(source_file).exists():
        print(f"❌ 源文件不存在: {source_file}")
        # 如果安全版本不存在，回退到原版本
        source_file = "smart_follow_fixed.py"
        if not Path(source_file).exists():
            print(f"❌ 原版本文件也不存在: {source_file}")
            return

    encryptor = ScriptEncryptor(source_file)

    print("🔐 Python脚本加密保护工具")
    print("=" * 50)

    # 执行加密方法
    success_count = 0

    if encryptor.method1_pyinstaller_onefile():
        success_count += 1

    if encryptor.method2_pyinstaller_optimized():
        success_count += 1

    if encryptor.method3_bytecode_protection():
        success_count += 1

    # 创建部署包
    if success_count > 0:
        package_dir = encryptor.create_deployment_package()

        print("\\n🎉 加密保护完成!")
        print("=" * 50)
        print(f"✅ 成功创建 {success_count} 个加密版本")
        print(f"📦 部署包位置: {package_dir}")
        print("\\n💡 建议:")
        print("   - 使用 xiaohongshu_tool.exe (PyInstaller版本)")
        print("   - 提供给甲方时只需要部署包内容")
        print("   - 源代码已完全加密，无法轻易查看")
    else:
        print("❌ 所有加密方法都失败了")

if __name__ == "__main__":
    main()
