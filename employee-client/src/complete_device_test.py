"""
Flow Farm - 完整的设备检测和测试工具
支持真机和模拟器的自动检测与测试
"""

import json
import os
import subprocess
import time
from typing import Dict, List, Optional


class DeviceDetector:
    """设备检测器"""

    def __init__(self):
        self.adb_path = r"D:\leidian\LDPlayer9\adb.exe"

    def restart_adb_server(self) -> bool:
        """重启ADB服务"""
        print("🔄 重启ADB服务...")
        try:
            subprocess.run(
                [self.adb_path, "kill-server"], capture_output=True, check=False
            )
            time.sleep(1)
            result = subprocess.run(
                [self.adb_path, "start-server"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                print("✅ ADB服务重启成功")
                return True
            else:
                print(f"❌ ADB服务重启失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 重启ADB失败: {e}")
            return False

    def get_device_list(self) -> List[Dict]:
        """获取设备列表"""
        try:
            result = subprocess.run(
                [self.adb_path, "devices", "-l"],
                capture_output=True,
                text=True,
                check=False,
            )

            devices = []
            lines = result.stdout.strip().split("\n")[1:]  # 跳过标题行

            for line in lines:
                line = line.strip()
                if line and not line.startswith("*"):
                    parts = line.split()
                    if len(parts) >= 2:
                        device_info = {
                            "id": parts[0],
                            "status": parts[1],
                            "details": " ".join(parts[2:]) if len(parts) > 2 else "",
                        }
                        devices.append(device_info)

            return devices

        except Exception as e:
            print(f"❌ 获取设备列表失败: {e}")
            return []

    def get_device_properties(self, device_id: str) -> Dict:
        """获取设备属性"""
        props = {}

        try:
            # 获取基本属性
            properties = [
                ("model", "ro.product.model"),
                ("brand", "ro.product.brand"),
                ("android_version", "ro.build.version.release"),
                ("sdk_version", "ro.build.version.sdk"),
                ("architecture", "ro.product.cpu.abi"),
                ("device_name", "ro.product.device"),
            ]

            for prop_name, prop_key in properties:
                result = subprocess.run(
                    [self.adb_path, "-s", device_id, "shell", "getprop", prop_key],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode == 0:
                    props[prop_name] = result.stdout.strip()

            # 获取屏幕分辨率
            result = subprocess.run(
                [self.adb_path, "-s", device_id, "shell", "wm", "size"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "Physical size:" in line:
                        props["resolution"] = line.split("Physical size:")[-1].strip()
                        break

            # 获取电池信息
            result = subprocess.run(
                [self.adb_path, "-s", device_id, "shell", "dumpsys", "battery"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "level:" in line:
                        try:
                            props["battery"] = int(line.split(":")[-1].strip())
                        except ValueError:
                            pass
                        break

        except Exception as e:
            print(f"⚠️ 获取设备属性时出错: {e}")

        return props

    def test_device_connection(self, device_id: str) -> bool:
        """测试设备连接"""
        try:
            # 简单的shell命令测试
            result = subprocess.run(
                [self.adb_path, "-s", device_id, "shell", "echo", "test"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            return result.returncode == 0 and "test" in result.stdout

        except Exception:
            return False

    def check_installed_apps(self, device_id: str) -> List[str]:
        """检查已安装的目标应用"""
        target_apps = {
            "com.ss.android.ugc.aweme": "抖音",
            "com.xingin.xhs": "小红书",
            "com.tencent.mm": "微信",
            "com.android.chrome": "Chrome浏览器",
        }

        installed_apps = []

        for package, name in target_apps.items():
            try:
                result = subprocess.run(
                    [
                        self.adb_path,
                        "-s",
                        device_id,
                        "shell",
                        "pm",
                        "list",
                        "packages",
                        package,
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if result.returncode == 0 and package in result.stdout:
                    installed_apps.append(name)

            except Exception:
                continue

        return installed_apps

    def take_screenshot_test(self, device_id: str) -> bool:
        """测试截图功能"""
        try:
            print(f"📸 测试设备 {device_id} 截图功能...")

            # 在设备上截图
            result = subprocess.run(
                [
                    self.adb_path,
                    "-s",
                    device_id,
                    "shell",
                    "screencap",
                    "-p",
                    "/sdcard/test_screenshot.png",
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode != 0:
                print(f"❌ 设备截图失败: {result.stderr}")
                return False

            # 拉取到本地
            local_path = f"test_screenshot_{device_id}_{int(time.time())}.png"
            result = subprocess.run(
                [
                    self.adb_path,
                    "-s",
                    device_id,
                    "pull",
                    "/sdcard/test_screenshot.png",
                    local_path,
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                print(f"❌ 截图文件拉取失败: {result.stderr}")
                return False

            # 检查文件是否存在并且有内容
            if os.path.exists(local_path) and os.path.getsize(local_path) > 1000:
                print(f"✅ 截图成功: {local_path}")
                print(f"   文件大小: {os.path.getsize(local_path)/1024:.1f} KB")

                # 清理设备上的临时文件
                subprocess.run(
                    [
                        self.adb_path,
                        "-s",
                        device_id,
                        "shell",
                        "rm",
                        "/sdcard/test_screenshot.png",
                    ],
                    capture_output=True,
                    check=False,
                )

                return True
            else:
                print("❌ 截图文件无效")
                return False

        except Exception as e:
            print(f"❌ 截图测试失败: {e}")
            return False

    def get_ui_dump_test(self, device_id: str) -> bool:
        """测试UI dump功能"""
        try:
            print(f"📋 测试设备 {device_id} UI获取功能...")

            # 生成UI dump
            result = subprocess.run(
                [
                    self.adb_path,
                    "-s",
                    device_id,
                    "shell",
                    "uiautomator",
                    "dump",
                    "/sdcard/test_ui.xml",
                ],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )

            if result.returncode != 0:
                print(f"❌ UI dump失败: {result.stderr}")
                return False

            # 拉取到本地
            local_path = f"test_ui_{device_id}_{int(time.time())}.xml"
            result = subprocess.run(
                [
                    self.adb_path,
                    "-s",
                    device_id,
                    "pull",
                    "/sdcard/test_ui.xml",
                    local_path,
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                print(f"❌ UI文件拉取失败: {result.stderr}")
                return False

            # 检查XML文件
            if os.path.exists(local_path):
                with open(local_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "hierarchy" in content and len(content) > 100:
                        print(f"✅ UI dump成功: {local_path}")
                        print(f"   文件大小: {len(content)/1024:.1f} KB")

                        # 简单分析UI内容
                        node_count = content.count("<node")
                        print(f"   UI节点数量: {node_count}")

                        # 清理设备上的临时文件
                        subprocess.run(
                            [
                                self.adb_path,
                                "-s",
                                device_id,
                                "shell",
                                "rm",
                                "/sdcard/test_ui.xml",
                            ],
                            capture_output=True,
                            check=False,
                        )

                        return True
                    else:
                        print("❌ UI文件内容无效")
                        return False
            else:
                print("❌ UI文件不存在")
                return False

        except Exception as e:
            print(f"❌ UI dump测试失败: {e}")
            return False


def main():
    """主函数"""
    print("🔧 Flow Farm 设备检测和测试工具")
    print("=" * 50)

    detector = DeviceDetector()

    # 重启ADB服务
    if not detector.restart_adb_server():
        print("❌ ADB服务启动失败，无法继续")
        return 1

    print("\n🔍 扫描设备...")
    devices = detector.get_device_list()

    if not devices:
        print("\n❌ 未发现任何设备")
        print("\n📋 请按照以下步骤连接设备:")
        print("1. 真机连接:")
        print("   - 启用开发者选项和USB调试")
        print("   - 用数据线连接手机")
        print("   - 授权USB调试")
        print("\n2. 模拟器连接:")
        print("   - 启动雷电模拟器或其他Android模拟器")
        print("   - 等待模拟器完全启动")
        print("   - 模拟器会自动连接ADB")

        return 1

    print(f"\n✅ 发现 {len(devices)} 台设备:")

    for i, device in enumerate(devices, 1):
        print(f"\n📱 设备 {i}: {device['id']}")
        print(f"   状态: {device['status']}")

        if device["status"] == "device":
            print("   ✅ 设备已授权，开始详细测试...")

            # 测试连接
            if detector.test_device_connection(device["id"]):
                print("   ✅ 设备连接正常")
            else:
                print("   ❌ 设备连接异常")
                continue

            # 获取设备属性
            props = detector.get_device_properties(device["id"])
            if props:
                print(f"   📋 设备信息:")
                for key, value in props.items():
                    if value:
                        print(f"      {key}: {value}")

            # 检查已安装应用
            apps = detector.check_installed_apps(device["id"])
            if apps:
                print(f"   📱 已安装目标应用: {', '.join(apps)}")
            else:
                print("   ⚠️ 未发现目标应用")

            # 测试截图功能
            screenshot_ok = detector.take_screenshot_test(device["id"])

            # 测试UI dump功能
            ui_dump_ok = detector.get_ui_dump_test(device["id"])

            # 功能测试总结
            print(f"   📊 功能测试结果:")
            print(f"      截图功能: {'✅' if screenshot_ok else '❌'}")
            print(f"      UI获取: {'✅' if ui_dump_ok else '❌'}")

            if screenshot_ok and ui_dump_ok:
                print(f"   🎉 设备 {device['id']} 完全可用!")
            else:
                print(f"   ⚠️ 设备 {device['id']} 功能受限")

        elif device["status"] == "unauthorized":
            print("   ⚠️ 设备未授权，请在手机上允许USB调试")
        elif device["status"] == "offline":
            print("   ❌ 设备离线，请检查连接")
        else:
            print(f"   ❓ 未知状态: {device['status']}")

    print(f"\n✅ 检测完成!")
    print("现在你可以使用检测到的设备进行自动化操作了。")

    return 0


if __name__ == "__main__":
    main()
