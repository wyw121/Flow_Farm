"""
Flow Farm 员工客户端 - 设备管理视图
实现设备连接、状态监控和管理功能
"""

import logging
import threading
import time
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..base_window import ComponentFactory, ModernTheme


class DeviceStatus:
    """设备状态枚举"""

    DISCONNECTED = "未连接"
    CONNECTING = "连接中"
    CONNECTED = "已连接"
    WORKING = "工作中"
    ERROR = "错误"


class DeviceInfo:
    """设备信息类"""

    def __init__(self, device_id: str, name: str = None):
        self.device_id = device_id
        self.name = name or f"设备{device_id}"
        self.status = DeviceStatus.DISCONNECTED
        self.last_seen = None
        self.tasks_completed = 0
        self.error_message = ""


class DeviceManagementView(QWidget):
    """设备管理视图"""

    def __init__(self, parent: QWidget, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self.theme = ModernTheme()

        # 设备管理状态
        self.devices: Dict[str, DeviceInfo] = {}
        self.max_devices = 10
        self.auto_refresh = True

        # 初始化界面
        self.setup_layout()
        self.initialize_devices()

        # 开始设备监控
        self.start_device_monitoring()

        self.logger.info("设备管理视图初始化完成")

    def setup_layout(self):
        """设置布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(self.theme.SPACING["medium"])

        # 标题区域
        self.create_header(layout)

        # 设备控制区域
        self.create_control_panel(layout)

        # 设备列表区域
        self.create_device_list(layout)

        # 设备详情区域
        self.create_device_details(layout)

    def create_header(self, layout):
        """创建标题区域"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        title_label = ComponentFactory.create_label("设备管理", "title")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # 设备统计
        self.device_count_label = ComponentFactory.create_label(
            "已连接: 0/10", "heading"
        )
        header_layout.addWidget(self.device_count_label)

        layout.addWidget(header_widget)

    def create_control_panel(self, layout):
        """创建控制面板"""
        control_group = QGroupBox("设备控制")
        control_layout = QVBoxLayout(control_group)

        # 按钮组
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # 刷新设备按钮
        self.refresh_btn = ComponentFactory.create_button(
            "🔄 刷新设备", callback=self.refresh_devices, style="primary"
        )
        button_layout.addWidget(self.refresh_btn)

        # 连接所有设备按钮
        self.connect_all_btn = ComponentFactory.create_button(
            "📱 连接所有", callback=self.connect_all_devices, style="secondary"
        )
        button_layout.addWidget(self.connect_all_btn)

        # 断开所有设备按钮
        self.disconnect_all_btn = ComponentFactory.create_button(
            "🔌 断开所有", callback=self.disconnect_all_devices
        )
        button_layout.addWidget(self.disconnect_all_btn)

        button_layout.addStretch()

        # 自动刷新开关
        self.auto_refresh_cb = QCheckBox("自动刷新")
        self.auto_refresh_cb.setChecked(True)
        self.auto_refresh_cb.stateChanged.connect(self.toggle_auto_refresh)
        button_layout.addWidget(self.auto_refresh_cb)

        control_layout.addWidget(button_widget)
        layout.addWidget(control_group)

    def create_device_list(self, layout):
        """创建设备列表"""
        list_group = QGroupBox("设备列表")
        list_layout = QVBoxLayout(list_group)

        # 创建表格
        self.device_table = QTableWidget(0, 5)
        self.device_table.setHorizontalHeaderLabels(
            ["设备ID", "设备名称", "连接状态", "完成任务", "最后连接"]
        )

        # 设置表格样式
        self.device_table.setAlternatingRowColors(True)
        self.device_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.device_table.setSelectionMode(QTableWidget.SingleSelection)

        # 设置列宽
        header = self.device_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)

        self.device_table.setColumnWidth(0, 100)
        self.device_table.setColumnWidth(2, 100)
        self.device_table.setColumnWidth(3, 100)
        self.device_table.setColumnWidth(4, 150)

        # 绑定选择事件
        self.device_table.itemSelectionChanged.connect(self.on_device_select)
        self.device_table.itemDoubleClicked.connect(self.on_device_double_click)

        list_layout.addWidget(self.device_table)
        layout.addWidget(list_group)

    def create_device_details(self, layout):
        """创建设备详情区域"""
        details_group = QGroupBox("设备详情")
        details_layout = QHBoxLayout(details_group)

        # 左侧信息
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)

        # 设备信息标签
        self.selected_device_label = ComponentFactory.create_label(
            "请选择设备", "heading"
        )
        info_layout.addWidget(self.selected_device_label)

        self.device_status_label = ComponentFactory.create_label("", "body")
        info_layout.addWidget(self.device_status_label)

        self.device_error_label = ComponentFactory.create_label("", "error")
        info_layout.addWidget(self.device_error_label)

        info_layout.addStretch()
        details_layout.addWidget(info_widget)

        # 右侧操作按钮
        action_widget = QWidget()
        action_layout = QVBoxLayout(action_widget)
        action_layout.setContentsMargins(0, 0, 0, 0)

        self.connect_btn = ComponentFactory.create_button(
            "连接", callback=self.connect_selected_device, style="primary"
        )
        self.connect_btn.setEnabled(False)
        action_layout.addWidget(self.connect_btn)

        self.disconnect_btn = ComponentFactory.create_button(
            "断开", callback=self.disconnect_selected_device
        )
        self.disconnect_btn.setEnabled(False)
        action_layout.addWidget(self.disconnect_btn)

        self.rename_btn = ComponentFactory.create_button(
            "重命名", callback=self.rename_selected_device
        )
        self.rename_btn.setEnabled(False)
        action_layout.addWidget(self.rename_btn)

        action_layout.addStretch()
        details_layout.addWidget(action_widget)

        layout.addWidget(details_group)

    def initialize_devices(self):
        """初始化设备列表"""
        # 创建10个设备槽位
        for i in range(1, self.max_devices + 1):
            device_id = f"device_{i:02d}"
            device = DeviceInfo(device_id, f"设备{i}")
            self.devices[device_id] = device
            self.add_device_to_table(device)

    def add_device_to_table(self, device: DeviceInfo):
        """将设备添加到表格"""
        row = self.device_table.rowCount()
        self.device_table.insertRow(row)

        # 设置设备信息
        self.device_table.setItem(row, 0, QTableWidgetItem(device.device_id))
        self.device_table.setItem(row, 1, QTableWidgetItem(device.name))
        self.device_table.setItem(row, 2, QTableWidgetItem(device.status))
        self.device_table.setItem(row, 3, QTableWidgetItem(str(device.tasks_completed)))
        self.device_table.setItem(
            row, 4, QTableWidgetItem(device.last_seen or "从未连接")
        )

        # 设置状态颜色
        self.update_device_row_color(row, device.status)

    def update_device_row_color(self, row: int, status: str):
        """更新设备行颜色"""
        color_map = {
            DeviceStatus.CONNECTED: QColor(0, 150, 0),  # 绿色
            DeviceStatus.CONNECTING: QColor(255, 165, 0),  # 橙色
            DeviceStatus.WORKING: QColor(0, 100, 255),  # 蓝色
            DeviceStatus.ERROR: QColor(220, 20, 60),  # 红色
            DeviceStatus.DISCONNECTED: QColor(128, 128, 128),  # 灰色
        }

        color = color_map.get(status, QColor(128, 128, 128))

        for col in range(self.device_table.columnCount()):
            item = self.device_table.item(row, col)
            if item:
                item.setForeground(color)

    def update_device_table(self):
        """更新设备表格"""
        for row in range(self.device_table.rowCount()):
            device_id_item = self.device_table.item(row, 0)
            if device_id_item:
                device_id = device_id_item.text()
                device = self.devices.get(device_id)
                if device:
                    self.device_table.item(row, 1).setText(device.name)
                    self.device_table.item(row, 2).setText(device.status)
                    self.device_table.item(row, 3).setText(str(device.tasks_completed))
                    self.device_table.item(row, 4).setText(
                        device.last_seen or "从未连接"
                    )
                    self.update_device_row_color(row, device.status)

        # 更新设备统计
        connected_count = sum(
            1
            for device in self.devices.values()
            if device.status in [DeviceStatus.CONNECTED, DeviceStatus.WORKING]
        )
        self.device_count_label.setText(f"已连接: {connected_count}/{self.max_devices}")

    def refresh_devices(self):
        """刷新设备列表"""
        self.main_window.update_status("正在刷新设备...", "info")

        def refresh_worker():
            try:
                # 模拟设备发现过程
                import random

                for i in range(1, 4):  # 模拟发现前3个设备
                    device_id = f"device_{i:02d}"
                    if device_id in self.devices:
                        device = self.devices[device_id]
                        if random.choice([True, False]):
                            device.status = DeviceStatus.CONNECTED
                            device.last_seen = time.strftime("%H:%M:%S")
                        else:
                            device.status = DeviceStatus.DISCONNECTED

                # 更新UI（在主线程中）
                self.update_device_table()
                self.main_window.update_status("设备刷新完成", "success")

            except Exception as e:
                self.logger.error(f"刷新设备失败: {e}")
                self.main_window.update_status("设备刷新失败", "error")

        threading.Thread(target=refresh_worker, daemon=True).start()

    def connect_all_devices(self):
        """连接所有设备"""
        reply = QMessageBox.question(
            self, "确认", "确定要连接所有可用设备吗？", QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.main_window.update_status("正在连接所有设备...", "info")

            def connect_worker():
                for device in self.devices.values():
                    if device.status == DeviceStatus.DISCONNECTED:
                        self.connect_device(device)
                        time.sleep(0.5)  # 避免同时连接造成冲突

                self.update_device_table()
                self.main_window.update_status("设备连接完成", "success")

            threading.Thread(target=connect_worker, daemon=True).start()

    def disconnect_all_devices(self):
        """断开所有设备"""
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要断开所有已连接的设备吗？",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            for device in self.devices.values():
                if device.status in [DeviceStatus.CONNECTED, DeviceStatus.WORKING]:
                    self.disconnect_device(device)

            self.update_device_table()
            self.main_window.update_status("所有设备已断开", "info")

    def connect_device(self, device: DeviceInfo):
        """连接单个设备"""
        try:
            device.status = DeviceStatus.CONNECTING
            self.update_device_table()

            # 模拟连接过程
            time.sleep(1)

            # 模拟连接结果
            import random

            if random.choice([True, True, True, False]):  # 75%成功率
                device.status = DeviceStatus.CONNECTED
                device.last_seen = time.strftime("%H:%M:%S")
                device.error_message = ""
                self.logger.info(f"设备 {device.device_id} 连接成功")
            else:
                device.status = DeviceStatus.ERROR
                device.error_message = "连接超时"
                self.logger.error(f"设备 {device.device_id} 连接失败")

        except Exception as e:
            device.status = DeviceStatus.ERROR
            device.error_message = str(e)
            self.logger.error(f"连接设备 {device.device_id} 时发生错误: {e}")

    def disconnect_device(self, device: DeviceInfo):
        """断开单个设备"""
        try:
            device.status = DeviceStatus.DISCONNECTED
            device.error_message = ""
            self.logger.info(f"设备 {device.device_id} 已断开连接")

        except Exception as e:
            self.logger.error(f"断开设备 {device.device_id} 时发生错误: {e}")

    def on_device_select(self):
        """设备选择事件"""
        current_row = self.device_table.currentRow()
        if current_row >= 0:
            device_id_item = self.device_table.item(current_row, 0)
            if device_id_item:
                device_id = device_id_item.text()
                device = self.devices.get(device_id)
                if device:
                    self.update_device_details(device)

    def update_device_details(self, device: DeviceInfo):
        """更新设备详情显示"""
        self.selected_device_label.setText(f"{device.name} ({device.device_id})")
        self.device_status_label.setText(f"状态: {device.status}")

        if device.error_message:
            self.device_error_label.setText(f"错误: {device.error_message}")
        else:
            self.device_error_label.setText("")

        # 更新按钮状态
        if device.status == DeviceStatus.DISCONNECTED:
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
        elif device.status in [DeviceStatus.CONNECTED, DeviceStatus.WORKING]:
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
        else:
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(False)

        self.rename_btn.setEnabled(True)

    def on_device_double_click(self, item):
        """设备双击事件"""
        if item:
            row = item.row()
            device_id_item = self.device_table.item(row, 0)
            if device_id_item:
                device_id = device_id_item.text()
                device = self.devices.get(device_id)
                if device:
                    if device.status == DeviceStatus.DISCONNECTED:
                        self.connect_selected_device()
                    elif device.status in [
                        DeviceStatus.CONNECTED,
                        DeviceStatus.WORKING,
                    ]:
                        self.disconnect_selected_device()

    def connect_selected_device(self):
        """连接选中的设备"""
        current_row = self.device_table.currentRow()
        if current_row >= 0:
            device_id_item = self.device_table.item(current_row, 0)
            if device_id_item:
                device_id = device_id_item.text()
                device = self.devices.get(device_id)
                if device and device.status == DeviceStatus.DISCONNECTED:

                    def connect_worker():
                        self.connect_device(device)
                        self.update_device_table()
                        self.update_device_details(device)

                    threading.Thread(target=connect_worker, daemon=True).start()

    def disconnect_selected_device(self):
        """断开选中的设备"""
        current_row = self.device_table.currentRow()
        if current_row >= 0:
            device_id_item = self.device_table.item(current_row, 0)
            if device_id_item:
                device_id = device_id_item.text()
                device = self.devices.get(device_id)
                if device and device.status in [
                    DeviceStatus.CONNECTED,
                    DeviceStatus.WORKING,
                ]:
                    self.disconnect_device(device)
                    self.update_device_table()
                    self.update_device_details(device)

    def rename_selected_device(self):
        """重命名选中的设备"""
        current_row = self.device_table.currentRow()
        if current_row >= 0:
            device_id_item = self.device_table.item(current_row, 0)
            if device_id_item:
                device_id = device_id_item.text()
                device = self.devices.get(device_id)
                if device:
                    new_name, ok = QInputDialog.getText(
                        self, "重命名设备", "请输入新的设备名称:", text=device.name
                    )
                    if ok and new_name.strip():
                        device.name = new_name.strip()
                        self.update_device_table()
                        self.update_device_details(device)
                        self.logger.info(f"设备 {device_id} 重命名为: {device.name}")

    def toggle_auto_refresh(self):
        """切换自动刷新"""
        self.auto_refresh = self.auto_refresh_cb.isChecked()
        if self.auto_refresh:
            self.main_window.update_status("自动刷新已开启", "info")
        else:
            self.main_window.update_status("自动刷新已关闭", "info")

    def start_device_monitoring(self):
        """开始设备监控"""

        def monitor_worker():
            while True:
                if (
                    self.auto_refresh
                    and hasattr(self.main_window, "is_logged_in")
                    and self.main_window.is_logged_in
                ):
                    # 自动更新设备状态
                    for device in self.devices.values():
                        if device.status == DeviceStatus.CONNECTED:
                            # 模拟随机任务完成
                            import random

                            if random.choice([True, False, False, False]):  # 25%概率
                                device.tasks_completed += 1

                    # 更新UI
                    self.update_device_table()

                time.sleep(10)  # 每10秒检查一次

        # 在后台线程中运行监控
        threading.Thread(target=monitor_worker, daemon=True).start()

    def get_connected_devices(self) -> List[DeviceInfo]:
        """获取已连接的设备列表"""
        return [
            device
            for device in self.devices.values()
            if device.status in [DeviceStatus.CONNECTED, DeviceStatus.WORKING]
        ]
