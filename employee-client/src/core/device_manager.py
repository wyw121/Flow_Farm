"""
Flow Farm - ADB设备管理器
负责Android设备的连接、监控和控制

功能特性:
- 设备自动发现和连接
- 设备状态实时监控
- 多设备并发管理
- 设备健康检查
- 热插拔支持
"""

import json
import logging
import os
import subprocess
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DeviceStatus(Enum):
    """设备状态枚举"""

    UNKNOWN = "unknown"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    WORKING = "working"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class DeviceInfo:
    """设备信息数据类"""

    device_id: str
    model: str = "Unknown"
    android_version: str = "Unknown"
    screen_resolution: str = "Unknown"
    battery_level: int = -1
    status: DeviceStatus = DeviceStatus.UNKNOWN
    last_seen: float = 0.0
    capabilities: Optional[List[str]] = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if abs(self.last_seen) < 1e-6:  # 使用浮点数比较
            self.last_seen = time.time()


class ADBDeviceManager:
    """ADB设备管理器

    负责管理Android设备的连接和控制：
    - 设备发现和连接
    - 状态监控
    - 命令执行
    - 多设备管理
    """

    def __init__(self, adb_path: Optional[str] = None):
        """初始化设备管理器

        Args:
            adb_path: ADB工具路径，如果为None则从系统PATH查找
        """
        self.logger = logging.getLogger(__name__)
        self.devices: Dict[str, DeviceInfo] = {}
        self.device_locks: Dict[str, threading.Lock] = {}
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None

        # 初始化ADB路径
        self.adb_path = self._initialize_adb_path(adb_path)

        # 启动监控线程
        self.start_monitoring()

        self.logger.info("🔧 ADB设备管理器初始化完成")

    def _initialize_adb_path(self, custom_path: Optional[str]) -> str:
        """初始化ADB路径"""
        if custom_path and os.path.exists(custom_path):
            self.logger.info("📱 使用自定义ADB路径: %s", custom_path)
            return custom_path

        # 尝试从系统PATH找到ADB
        try:
            result = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0:
                self.logger.info("📱 使用系统PATH中的ADB")
                return "adb"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # 尝试常见安装路径
        common_paths = [
            r"C:\platform-tools\adb.exe",
            r"C:\adb\adb.exe",
            r"D:\leidian\LDPlayer9\adb.exe",  # 雷电模拟器
            "/usr/local/bin/adb",
            "/usr/bin/adb",
        ]

        for path in common_paths:
            if os.path.exists(path):
                self.logger.info("📱 找到ADB: %s", path)
                return path

        # 如果都找不到，使用默认值并记录警告
        self.logger.warning("⚠️ 未找到ADB工具，某些功能可能无法使用")
        return "adb"

    def execute_adb_command(
        self, command: str, device_id: str = None, timeout: int = 30
    ) -> Tuple[str, str]:
        """执行ADB命令

        Args:
            command: ADB命令（不包含adb前缀）
            device_id: 设备ID，为None时不指定设备
            timeout: 超时时间（秒）

        Returns:
            (stdout, stderr) 元组
        """
        if device_id:
            full_command = f'"{self.adb_path}" -s {device_id} {command}'
        else:
            full_command = f'"{self.adb_path}" {command}'

        try:
            self.logger.debug(f"🔍 执行ADB命令: {full_command}")
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
            )

            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            if result.returncode != 0 and stderr:
                self.logger.warning(f"⚠️ ADB命令警告: {stderr}")

            return stdout, stderr

        except subprocess.TimeoutExpired:
            error_msg = f"ADB命令超时: {command}"
            self.logger.error(f"❌ {error_msg}")
            return "", error_msg
        except Exception as e:
            error_msg = f"ADB命令执行失败: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            return "", error_msg

    def scan_devices(self) -> List[DeviceInfo]:
        """扫描可用设备

        Returns:
            设备信息列表
        """
        self.logger.info("🔍 开始扫描设备...")

        stdout, stderr = self.execute_adb_command("devices -l")

        if stderr and "daemon not running" in stderr:
            self.logger.info("🚀 启动ADB服务...")
            self.execute_adb_command("start-server")
            stdout, stderr = self.execute_adb_command("devices -l")

        devices = []
        lines = stdout.split("\n")[1:]  # 跳过标题行

        for line in lines:
            line = line.strip()
            if not line or line.startswith("*"):
                continue

            parts = line.split()
            if len(parts) >= 2:
                device_id = parts[0]
                status = parts[1]

                if status == "device":
                    # 获取设备详细信息
                    device_info = self._get_device_details(device_id)
                    devices.append(device_info)

                    # 更新设备池
                    self.devices[device_id] = device_info
                    if device_id not in self.device_locks:
                        self.device_locks[device_id] = threading.Lock()

        self.logger.info(f"📱 发现 {len(devices)} 台设备")
        return devices

    def _get_device_details(self, device_id: str) -> DeviceInfo:
        """获取设备详细信息"""
        device_info = DeviceInfo(device_id=device_id)

        try:
            # 获取设备型号
            model, _ = self.execute_adb_command(
                "shell getprop ro.product.model", device_id
            )
            device_info.model = model or "Unknown"

            # 获取Android版本
            version, _ = self.execute_adb_command(
                "shell getprop ro.build.version.release", device_id
            )
            device_info.android_version = version or "Unknown"

            # 获取屏幕分辨率
            resolution, _ = self.execute_adb_command("shell wm size", device_id)
            if resolution and "Physical size:" in resolution:
                device_info.screen_resolution = resolution.split("Physical size:")[
                    -1
                ].strip()

            # 获取电池电量
            battery, _ = self.execute_adb_command(
                "shell dumpsys battery | grep level", device_id
            )
            if battery:
                try:
                    level = int(battery.split(":")[-1].strip())
                    device_info.battery_level = level
                except (ValueError, IndexError):
                    pass

            # 检查关键应用是否安装
            apps_check = [
                "com.ss.android.ugc.aweme",  # 抖音
                "com.xingin.xhs",  # 小红书
            ]

            for app in apps_check:
                installed, _ = self.execute_adb_command(
                    f"shell pm list packages {app}", device_id
                )
                if installed:
                    device_info.capabilities.append(app)

            device_info.status = DeviceStatus.CONNECTED
            device_info.last_seen = time.time()

        except Exception as e:
            self.logger.error(f"❌ 获取设备 {device_id} 详细信息失败: {str(e)}")
            device_info.status = DeviceStatus.ERROR

        return device_info

    def get_device_info(self, device_id: str) -> Optional[DeviceInfo]:
        """获取指定设备信息"""
        return self.devices.get(device_id)

    def get_connected_devices(self) -> List[DeviceInfo]:
        """获取已连接设备列表"""
        return [
            device
            for device in self.devices.values()
            if device.status == DeviceStatus.CONNECTED
        ]

    def is_device_connected(self, device_id: str) -> bool:
        """检查设备是否已连接"""
        device = self.devices.get(device_id)
        return device is not None and device.status == DeviceStatus.CONNECTED

    def take_screenshot(self, device_id: str, save_path: str = None) -> Optional[str]:
        """设备截图

        Args:
            device_id: 设备ID
            save_path: 保存路径，如果为None则使用默认路径

        Returns:
            截图文件路径，失败返回None
        """
        if not self.is_device_connected(device_id):
            self.logger.error(f"❌ 设备 {device_id} 未连接")
            return None

        try:
            with self.device_locks[device_id]:
                # 生成截图文件名
                if save_path is None:
                    timestamp = int(time.time())
                    save_path = f"screenshot_{device_id}_{timestamp}.png"

                # 在设备上截图
                remote_path = "/sdcard/screenshot_temp.png"
                stdout, stderr = self.execute_adb_command(
                    f"shell screencap -p {remote_path}", device_id
                )

                if stderr:
                    self.logger.error(f"❌ 设备截图失败: {stderr}")
                    return None

                # 拉取截图到本地
                stdout, stderr = self.execute_adb_command(
                    f"pull {remote_path} {save_path}", device_id
                )

                if stderr and "error" in stderr.lower():
                    self.logger.error(f"❌ 截图拉取失败: {stderr}")
                    return None

                # 清理设备上的临时文件
                self.execute_adb_command(f"shell rm {remote_path}", device_id)

                self.logger.info(f"📸 截图保存: {save_path}")
                return save_path

        except Exception as e:
            self.logger.error(f"❌ 截图操作失败: {str(e)}")
            return None

    def get_ui_dump(self, device_id: str, save_path: str = None) -> Optional[str]:
        """获取UI层次结构

        Args:
            device_id: 设备ID
            save_path: 保存路径

        Returns:
            UI XML文件路径，失败返回None
        """
        if not self.is_device_connected(device_id):
            self.logger.error(f"❌ 设备 {device_id} 未连接")
            return None

        try:
            with self.device_locks[device_id]:
                # 生成UI dump文件名
                if save_path is None:
                    timestamp = int(time.time())
                    save_path = f"ui_dump_{device_id}_{timestamp}.xml"

                # 在设备上生成UI dump
                remote_path = "/sdcard/ui_dump_temp.xml"
                stdout, stderr = self.execute_adb_command(
                    f"shell uiautomator dump {remote_path}", device_id
                )

                if stderr and "error" in stderr.lower():
                    self.logger.error(f"❌ UI dump失败: {stderr}")
                    return None

                # 拉取UI dump到本地
                stdout, stderr = self.execute_adb_command(
                    f"pull {remote_path} {save_path}", device_id
                )

                if stderr and "error" in stderr.lower():
                    self.logger.error(f"❌ UI dump拉取失败: {stderr}")
                    return None

                # 清理设备上的临时文件
                self.execute_adb_command(f"shell rm {remote_path}", device_id)

                self.logger.info(f"📋 UI dump保存: {save_path}")
                return save_path

        except Exception as e:
            self.logger.error(f"❌ UI dump操作失败: {str(e)}")
            return None

    def click_coordinate(self, device_id: str, x: int, y: int) -> bool:
        """点击指定坐标

        Args:
            device_id: 设备ID
            x: X坐标
            y: Y坐标

        Returns:
            操作是否成功
        """
        if not self.is_device_connected(device_id):
            self.logger.error(f"❌ 设备 {device_id} 未连接")
            return False

        try:
            with self.device_locks[device_id]:
                stdout, stderr = self.execute_adb_command(
                    f"shell input tap {x} {y}", device_id
                )

                if stderr:
                    self.logger.error(f"❌ 点击操作失败: {stderr}")
                    return False

                self.logger.debug(f"👆 点击坐标: ({x}, {y})")
                return True

        except Exception as e:
            self.logger.error(f"❌ 点击操作异常: {str(e)}")
            return False

    def input_text(self, device_id: str, text: str) -> bool:
        """输入文本

        Args:
            device_id: 设备ID
            text: 要输入的文本

        Returns:
            操作是否成功
        """
        if not self.is_device_connected(device_id):
            self.logger.error(f"❌ 设备 {device_id} 未连接")
            return False

        try:
            with self.device_locks[device_id]:
                # 转义特殊字符
                escaped_text = text.replace(" ", "%s").replace("&", "\\&")

                stdout, stderr = self.execute_adb_command(
                    f"shell input text '{escaped_text}'", device_id
                )

                if stderr:
                    self.logger.error(f"❌ 文本输入失败: {stderr}")
                    return False

                self.logger.debug(f"⌨️ 输入文本: {text}")
                return True

        except Exception as e:
            self.logger.error(f"❌ 文本输入异常: {str(e)}")
            return False

    def start_monitoring(self):
        """启动设备监控"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_devices, daemon=True
        )
        self.monitor_thread.start()
        self.logger.info("📡 设备监控已启动")

    def stop_monitoring(self):
        """停止设备监控"""
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        self.logger.info("📡 设备监控已停止")

    def _monitor_devices(self):
        """设备监控循环"""
        while self.monitoring_active:
            try:
                # 每30秒检查一次设备状态
                current_devices = self.scan_devices()

                # 检查设备是否离线
                current_time = time.time()
                for device_id, device_info in list(self.devices.items()):
                    if current_time - device_info.last_seen > 60:  # 60秒未响应视为离线
                        device_info.status = DeviceStatus.OFFLINE
                        self.logger.warning(f"⚠️ 设备 {device_id} 离线")

                time.sleep(30)  # 30秒检查间隔

            except Exception as e:
                self.logger.error(f"❌ 设备监控异常: {str(e)}")
                time.sleep(10)

    def get_device_status_summary(self) -> Dict:
        """获取设备状态摘要"""
        summary = {
            "total": len(self.devices),
            "connected": 0,
            "working": 0,
            "offline": 0,
            "error": 0,
        }

        for device in self.devices.values():
            if device.status == DeviceStatus.CONNECTED:
                summary["connected"] += 1
            elif device.status == DeviceStatus.WORKING:
                summary["working"] += 1
            elif device.status == DeviceStatus.OFFLINE:
                summary["offline"] += 1
            elif device.status == DeviceStatus.ERROR:
                summary["error"] += 1

        return summary

    def __del__(self):
        """析构函数，确保清理资源"""
        self.stop_monitoring()


if __name__ == "__main__":
    # 测试代码
    import logging

    logging.basicConfig(level=logging.DEBUG)

    # 创建设备管理器
    device_manager = ADBDeviceManager()

    # 扫描设备
    devices = device_manager.scan_devices()
    print(f"发现 {len(devices)} 台设备:")

    for device in devices:
        print(f"  设备ID: {device.device_id}")
        print(f"  型号: {device.model}")
        print(f"  Android版本: {device.android_version}")
        print(f"  分辨率: {device.screen_resolution}")
        print(f"  电池: {device.battery_level}%")
        print(f"  支持应用: {device.capabilities}")
        print()

    # 如果有设备，测试截图和UI dump
    if devices:
        test_device = devices[0]
        print(f"测试设备: {test_device.device_id}")

        # 截图测试
        screenshot_path = device_manager.take_screenshot(test_device.device_id)
        if screenshot_path:
            print(f"✅ 截图成功: {screenshot_path}")

        # UI dump测试
        ui_dump_path = device_manager.get_ui_dump(test_device.device_id)
        if ui_dump_path:
            print(f"✅ UI dump成功: {ui_dump_path}")

    # 显示状态摘要
    summary = device_manager.get_device_status_summary()
    print(f"设备状态摘要: {summary}")
