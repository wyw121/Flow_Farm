#!/usr/bin/env python3
"""
设备连接诊断脚本
帮助诊断ADB设备连接问题
"""

import os
import subprocess
import sys


def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n🔍 {description}")
    print("-" * 50)

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=10
        )

        if result.stdout:
            print("输出:")
            print(result.stdout)

        if result.stderr:
            print("错误信息:")
            print(result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("❌ 命令执行超时")
        return False
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False


def check_adb_installation():
    """检查ADB安装情况"""
    print("🔧 检查ADB安装情况")
    print("=" * 50)

    # 检查常见ADB路径
    adb_paths = [
        "adb",  # 系统PATH
        r"C:\platform-tools\adb.exe",
        r"C:\adb\adb.exe",
        r"D:\leidian\LDPlayer9\adb.exe",  # 雷电模拟器
        r"C:\Program Files\LDPlayer\ldplayer4.0.1\adb.exe",  # LDPlayer
        r"C:\Program Files (x86)\Nox\bin\nox_adb.exe",  # 夜神模拟器
    ]

    found_adb = []

    for path in adb_paths:
        if path == "adb":
            # 检查系统PATH中的ADB
            success = run_command("adb version", f"检查系统PATH中的ADB")
            if success:
                found_adb.append("系统PATH中的adb")
        else:
            # 检查特定路径的ADB
            if os.path.exists(path):
                success = run_command(f'"{path}" version', f"检查 {path}")
                if success:
                    found_adb.append(path)

    print(f"\n✅ 找到 {len(found_adb)} 个可用的ADB:")
    for adb in found_adb:
        print(f"   - {adb}")

    return found_adb


def check_devices(adb_path):
    """检查设备连接"""
    print(f"\n📱 使用 {adb_path} 检查设备连接")
    print("=" * 50)

    if adb_path == "系统PATH中的adb":
        adb_cmd = "adb"
    else:
        adb_cmd = f'"{adb_path}"'

    # 检查设备列表
    run_command(f"{adb_cmd} devices -l", "获取设备列表")

    # 重启ADB服务
    print("\n🔄 重启ADB服务...")
    run_command(f"{adb_cmd} kill-server", "停止ADB服务")
    run_command(f"{adb_cmd} start-server", "启动ADB服务")
    run_command(f"{adb_cmd} devices -l", "重新获取设备列表")


def provide_connection_guide():
    """提供连接指南"""
    print("\n📋 设备连接指南")
    print("=" * 50)

    print(
        """
Android设备连接步骤:

1. 启用开发者选项:
   - 进入 设置 → 关于手机
   - 连续点击 "版本号" 7次
   - 输入锁屏密码启用开发者选项

2. 启用USB调试:
   - 进入 设置 → 开发者选项
   - 开启 "USB调试"
   - 开启 "USB安装" (可选)

3. 连接设备:
   - 使用数据线连接手机到电脑
   - 选择 "文件传输" 或 "MTP" 模式
   - 在手机上授权此计算机的USB调试

4. 验证连接:
   - 运行: adb devices
   - 应该看到设备列表

模拟器连接步骤:

1. 雷电模拟器:
   - 启动雷电模拟器
   - 在模拟器设置中启用ADB调试
   - 端口通常是 5555

2. 夜神模拟器:
   - 启动夜神模拟器
   - 默认会自动连接到ADB

常见问题解决:

❌ 设备显示 "unauthorized":
   - 在手机上重新授权USB调试
   - 勾选 "始终允许从此计算机"

❌ 设备显示 "offline":
   - 重启ADB服务: adb kill-server && adb start-server
   - 重新插拔USB线
   - 重启设备

❌ 找不到设备:
   - 检查USB线是否支持数据传输
   - 尝试更换USB端口
   - 安装设备驱动程序
   - 检查防火墙设置
    """
    )


def main():
    """主函数"""
    print("🔧 Flow Farm ADB设备连接诊断工具")
    print("=" * 60)

    # 检查ADB安装
    adb_list = check_adb_installation()

    if not adb_list:
        print("\n❌ 未找到可用的ADB工具!")
        print("请安装Android SDK Platform Tools或使用Android模拟器")
        provide_connection_guide()
        return 1

    # 检查设备连接
    for adb_path in adb_list:
        check_devices(adb_path)

    # 提供连接指南
    provide_connection_guide()

    print("\n✅ 诊断完成!")
    print("如果仍有问题，请按照上述指南检查设备连接。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
