"""
简单的ADB设备检查脚本
"""

import subprocess
import sys


def check_adb():
    """检查ADB和设备连接"""
    print("🔧 检查ADB设备连接状态")
    print("=" * 40)

    # 使用检测到的ADB路径
    adb_path = r"D:\leidian\LDPlayer9\adb.exe"

    try:
        # 检查ADB版本
        print("📱 ADB版本:")
        result = subprocess.run(
            [adb_path, "version"], capture_output=True, text=True, check=False
        )
        print(result.stdout)

        # 重启ADB服务
        print("🔄 重启ADB服务...")
        subprocess.run([adb_path, "kill-server"], capture_output=True, check=False)
        subprocess.run([adb_path, "start-server"], capture_output=True, check=False)

        # 检查设备
        print("📱 扫描设备:")
        result = subprocess.run(
            [adb_path, "devices", "-l"], capture_output=True, text=True, check=False
        )

        print(result.stdout)

        # 分析结果
        lines = result.stdout.strip().split("\n")
        device_lines = [
            line for line in lines[1:] if line.strip() and not line.startswith("*")
        ]

        if device_lines:
            print(f"✅ 发现 {len(device_lines)} 台设备:")
            for line in device_lines:
                parts = line.split()
                if len(parts) >= 2:
                    device_id = parts[0]
                    status = parts[1]
                    print(f"   设备ID: {device_id}")
                    print(f"   状态: {status}")

                    if status == "device":
                        print("   ✅ 设备已授权，可以使用")
                    elif status == "unauthorized":
                        print("   ⚠️ 设备未授权，请在手机上允许USB调试")
                    elif status == "offline":
                        print("   ❌ 设备离线，请检查连接")
        else:
            print("❌ 未发现任何设备")
            print("\n请检查:")
            print("1. 手机是否已连接并启用USB调试")
            print("2. 是否已在手机上授权此计算机")
            print("3. USB线是否支持数据传输")
            print("4. 如果使用模拟器，请确保模拟器已启动")

    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False

    return True


if __name__ == "__main__":
    check_adb()
