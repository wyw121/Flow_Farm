"""
Flow Farm - 异步设备管理器
专门为GUI界面优化的异步设备管理封装
解决主线程阻塞问题
"""

import logging
import threading
import time
from typing import Callable, Dict, List, Optional

from PySide6.QtCore import QObject, QTimer, Signal

from .device_manager import ADBDeviceManager, DeviceInfo, DeviceStatus


class AsyncDeviceManager(QObject):
    """异步设备管理器

    为GUI界面提供非阻塞的设备管理功能
    """

    # 信号定义
    devices_scanned = Signal(list)  # 设备扫描完成信号
    device_connected = Signal(str)  # 设备连接信号
    device_disconnected = Signal(str)  # 设备断开信号
    scan_progress = Signal(str)  # 扫描进度信号
    error_occurred = Signal(str)  # 错误信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # 设备管理器实例 - 延迟初始化
        self._device_manager: Optional[ADBDeviceManager] = None
        self._init_thread: Optional[threading.Thread] = None
        self._scan_thread: Optional[threading.Thread] = None

        # 状态标记
        self._initialized = False
        self._scanning = False

        # 启动异步初始化
        self._async_initialize()

    def _async_initialize(self):
        """异步初始化设备管理器"""
        if self._init_thread and self._init_thread.is_alive():
            return

        self._init_thread = threading.Thread(
            target=self._initialize_device_manager,
            daemon=True,
            name="DeviceManagerInit",
        )
        self._init_thread.start()

    def _initialize_device_manager(self):
        """在后台线程中初始化设备管理器"""
        try:
            self.scan_progress.emit("正在初始化设备管理器...")

            # 创建设备管理器实例
            self._device_manager = ADBDeviceManager()

            # 等待稍许时间确保初始化完成
            time.sleep(0.5)

            self._initialized = True
            self.scan_progress.emit("设备管理器初始化完成")

            # 自动执行首次设备扫描
            QTimer.singleShot(100, self.scan_devices_async)

        except Exception as e:
            self.logger.error(f"设备管理器初始化失败: {e}")
            self.error_occurred.emit(f"初始化失败: {str(e)}")

    def scan_devices_async(self):
        """异步扫描设备"""
        if self._scanning:
            self.scan_progress.emit("设备扫描正在进行中...")
            return

        if not self._initialized:
            self.scan_progress.emit("设备管理器尚未初始化完成...")
            return

        self._scanning = True
        self.scan_progress.emit("开始扫描设备...")

        # 在后台线程中执行扫描
        self._scan_thread = threading.Thread(
            target=self._perform_device_scan, daemon=True, name="DeviceScan"
        )
        self._scan_thread.start()

    def _perform_device_scan(self):
        """在后台线程中执行设备扫描"""
        try:
            if not self._device_manager:
                self.error_occurred.emit("设备管理器未初始化")
                return

            # 执行扫描
            devices = self._device_manager.scan_devices()

            # 发送结果信号
            self.devices_scanned.emit(devices)
            self.scan_progress.emit(f"扫描完成，发现 {len(devices)} 台设备")

        except Exception as e:
            self.logger.error(f"设备扫描失败: {e}")
            self.error_occurred.emit(f"扫描失败: {str(e)}")
        finally:
            self._scanning = False

    def get_device_info_async(self, device_id: str, callback: Callable):
        """异步获取设备信息"""
        if not self._initialized or not self._device_manager:
            callback(None)
            return

        def _get_info():
            try:
                device_info = self._device_manager.get_device_info(device_id)
                callback(device_info)
            except Exception as e:
                self.logger.error(f"获取设备信息失败: {e}")
                callback(None)

        thread = threading.Thread(target=_get_info, daemon=True)
        thread.start()

    def test_device_async(self, device_id: str):
        """异步测试设备"""
        if not self._initialized or not self._device_manager:
            self.error_occurred.emit("设备管理器未就绪")
            return

        def _test_device():
            try:
                self.scan_progress.emit(f"正在测试设备: {device_id}")

                # 获取设备详细信息
                device_info = self._device_manager.get_device_info(device_id)
                if device_info:
                    info_lines = [
                        f"设备型号: {device_info.model}",
                        f"Android版本: {device_info.android_version}",
                        f"屏幕分辨率: {device_info.screen_resolution}",
                        f"电池电量: {device_info.battery_level}%",
                        f"已安装应用: {', '.join(device_info.capabilities or [])}",
                    ]

                    for line in info_lines:
                        self.scan_progress.emit(line)

                    self.scan_progress.emit(f"设备 {device_info.model} 测试完成")
                else:
                    self.error_occurred.emit(f"无法获取设备 {device_id} 的信息")

            except Exception as e:
                self.logger.error(f"设备测试失败: {e}")
                self.error_occurred.emit(f"设备测试失败: {str(e)}")

        thread = threading.Thread(target=_test_device, daemon=True)
        thread.start()

    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized

    def is_scanning(self) -> bool:
        """检查是否正在扫描"""
        return self._scanning

    def get_connected_devices(self) -> List[DeviceInfo]:
        """获取已连接设备列表（同步方法，仅在已初始化时调用）"""
        if self._initialized and self._device_manager:
            return self._device_manager.get_connected_devices()
        return []

    def cleanup(self):
        """清理资源"""
        try:
            if self._device_manager:
                self._device_manager.stop_monitoring()

            # 等待线程结束
            if self._init_thread and self._init_thread.is_alive():
                self._init_thread.join(timeout=2)

            if self._scan_thread and self._scan_thread.is_alive():
                self._scan_thread.join(timeout=2)

        except Exception as e:
            self.logger.error(f"清理资源时出错: {e}")
