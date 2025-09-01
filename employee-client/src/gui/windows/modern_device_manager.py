"""
Flow Farm 现代化设备管理器
使用 qfluentwidgets 实现设备监控和管理界面
"""

from typing import Dict, List, Optional

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    ComboBoxSettingCard,
    FluentIcon,
    HBoxLayout,
    InfoBar,
    InfoBarPosition,
    PrimaryPushButton,
    PushButton,
    SettingCard,
    SettingCardGroup,
    SwitchSettingCard,
    Theme,
    ToolButton,
    VBoxLayout,
    VerticalScrollInterface,
    qconfig,
)


class DeviceCard(SettingCard):
    """设备信息卡片"""

    connect_requested = Signal(str)  # device_id
    disconnect_requested = Signal(str)

    def __init__(self, device_info: Dict, parent=None):
        self.device_info = device_info
        device_id = device_info.get("id", "unknown")
        device_name = device_info.get("name", "未知设备")
        device_status = device_info.get("status", "offline")

        # 根据状态选择图标
        icon = (
            FluentIcon.DEVICE_MANAGER
            if device_status == "online"
            else FluentIcon.DISCONNECT
        )

        super().__init__(
            icon, device_name, f"设备ID: {device_id} | 状态: {device_status}", parent
        )

        self.setup_device_controls()

    def setup_device_controls(self):
        """设置设备控制按钮"""
        status = self.device_info.get("status", "offline")

        if status == "online":
            self.action_button = PushButton("断开连接")
            self.action_button.clicked.connect(self.disconnect_device)
        else:
            self.action_button = PrimaryPushButton("连接设备")
            self.action_button.clicked.connect(self.connect_device)

        # 添加详情按钮
        self.detail_button = ToolButton(FluentIcon.INFO)
        self.detail_button.clicked.connect(self.show_device_details)

        # 添加到布局
        self.hBoxLayout.addWidget(self.detail_button)
        self.hBoxLayout.addWidget(self.action_button)

    def connect_device(self):
        """连接设备"""
        device_id = self.device_info.get("id")
        self.connect_requested.emit(device_id)

    def disconnect_device(self):
        """断开设备"""
        device_id = self.device_info.get("id")
        self.disconnect_requested.emit(device_id)

    def show_device_details(self):
        """显示设备详情"""
        # TODO: 实现设备详情对话框
        pass

    def update_status(self, new_status: str):
        """更新设备状态"""
        self.device_info["status"] = new_status
        device_id = self.device_info.get("id", "unknown")
        device_name = self.device_info.get("name", "未知设备")

        # 更新显示内容
        self.setContent(f"设备ID: {device_id} | 状态: {new_status}")

        # 更新图标
        if new_status == "online":
            self.setIcon(FluentIcon.DEVICE_MANAGER)
            self.action_button.setText("断开连接")
            self.action_button.clicked.disconnect()
            self.action_button.clicked.connect(self.disconnect_device)
        else:
            self.setIcon(FluentIcon.DISCONNECT)
            self.action_button.setText("连接设备")
            self.action_button.clicked.disconnect()
            self.action_button.clicked.connect(self.connect_device)


class ModernDeviceManager(VerticalScrollInterface):
    """现代化设备管理器"""

    device_connected = Signal(str)  # device_id
    device_disconnected = Signal(str)
    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            object_name="device_manager",
            nav_text_cn="设备管理器",
            nav_icon=FluentIcon.DEVICE_MANAGER,
        )

        # 设备列表
        self.devices: List[Dict] = []
        self.device_cards: List[DeviceCard] = []

        # 设置界面
        self.setup_ui()

        # 设置定时刷新
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh_devices)
        self.refresh_timer.start(5000)  # 5秒刷新一次

    def setup_ui(self):
        """设置用户界面"""
        # 创建主容器
        content_widget = QWidget()
        content_layout = VBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(30, 30, 30, 30)

        # 设备管理控制区
        self.create_control_section(content_layout)

        # 已连接设备区域
        self.create_connected_devices_section(content_layout)

        # 可用设备区域
        self.create_available_devices_section(content_layout)

        # 设备配置区域
        self.create_device_settings_section(content_layout)

        # 设置为主要内容
        self.setWidget(content_widget)

    def create_control_section(self, layout: VBoxLayout):
        """创建控制区域"""
        control_group = SettingCardGroup("设备控制")

        # 设备扫描卡片
        self.scan_card = SettingCard(
            FluentIcon.SYNC, "设备扫描", "扫描并发现可用的自动化设备"
        )

        self.scan_button = PrimaryPushButton("扫描设备")
        self.scan_button.clicked.connect(self.scan_devices)
        self.scan_card.hBoxLayout.addWidget(self.scan_button)

        control_group.addSettingCard(self.scan_card)

        # 自动刷新设置
        self.auto_refresh_card = SwitchSettingCard(
            FluentIcon.UPDATE, "自动刷新", "定期自动扫描设备状态"
        )
        self.auto_refresh_card.setChecked(True)
        self.auto_refresh_card.checkedChanged.connect(self.toggle_auto_refresh)

        control_group.addSettingCard(self.auto_refresh_card)

        layout.addWidget(control_group)

    def create_connected_devices_section(self, layout: VBoxLayout):
        """创建已连接设备区域"""
        self.connected_group = SettingCardGroup("已连接设备 (0)")
        layout.addWidget(self.connected_group)

    def create_available_devices_section(self, layout: VBoxLayout):
        """创建可用设备区域"""
        self.available_group = SettingCardGroup("可用设备 (0)")
        layout.addWidget(self.available_group)

    def create_device_settings_section(self, layout: VBoxLayout):
        """创建设备设置区域"""
        settings_group = SettingCardGroup("设备设置")

        # 连接超时设置
        self.timeout_card = ComboBoxSettingCard(
            FluentIcon.TIMER,
            "连接超时",
            "设备连接超时时间",
            texts=["10秒", "20秒", "30秒", "60秒"],
        )
        self.timeout_card.comboBox.setCurrentText("20秒")

        settings_group.addSettingCard(self.timeout_card)

        # 重试次数设置
        self.retry_card = ComboBoxSettingCard(
            FluentIcon.REFRESH,
            "重试次数",
            "连接失败时的重试次数",
            texts=["1次", "3次", "5次", "10次"],
        )
        self.retry_card.comboBox.setCurrentText("3次")

        settings_group.addSettingCard(self.retry_card)

        layout.addWidget(settings_group)

    def scan_devices(self):
        """扫描设备"""
        self.scan_button.setText("扫描中...")
        self.scan_button.setEnabled(False)

        # 模拟设备扫描 - 实际实现中应调用设备管理器
        self.simulate_device_scan()

        # 恢复按钮状态
        self.scan_button.setText("扫描设备")
        self.scan_button.setEnabled(True)

        self.show_info_message("设备扫描", "设备扫描完成")

    def simulate_device_scan(self):
        """模拟设备扫描 - 仅用于演示"""
        # 模拟发现的设备
        mock_devices = [
            {
                "id": "emulator-5554",
                "name": "Android模拟器",
                "status": "online",
                "type": "emulator",
                "version": "Android 11",
            },
            {
                "id": "device-001",
                "name": "小米手机",
                "status": "offline",
                "type": "physical",
                "version": "Android 12",
            },
            {
                "id": "device-002",
                "name": "华为手机",
                "status": "online",
                "type": "physical",
                "version": "HarmonyOS 3.0",
            },
        ]

        self.update_device_list(mock_devices)

    def update_device_list(self, devices: List[Dict]):
        """更新设备列表"""
        self.devices = devices

        # 清除现有卡片
        self.clear_device_cards()

        # 分类设备
        connected_devices = [d for d in devices if d.get("status") == "online"]
        available_devices = [d for d in devices if d.get("status") != "online"]

        # 更新已连接设备
        self.connected_group.titleLabel.setText(
            f"已连接设备 ({len(connected_devices)})"
        )
        for device in connected_devices:
            self.add_device_card(device, self.connected_group)

        # 更新可用设备
        self.available_group.titleLabel.setText(f"可用设备 ({len(available_devices)})")
        for device in available_devices:
            self.add_device_card(device, self.available_group)

    def add_device_card(self, device_info: Dict, group: SettingCardGroup):
        """添加设备卡片"""
        card = DeviceCard(device_info, self)
        card.connect_requested.connect(self.connect_device)
        card.disconnect_requested.connect(self.disconnect_device)

        group.addSettingCard(card)
        self.device_cards.append(card)

    def clear_device_cards(self):
        """清除设备卡片"""
        for card in self.device_cards:
            card.setParent(None)
            card.deleteLater()
        self.device_cards.clear()

    def connect_device(self, device_id: str):
        """连接设备"""
        self.show_info_message("设备连接", f"正在连接设备: {device_id}")
        # TODO: 实际连接设备的逻辑
        self.device_connected.emit(device_id)

    def disconnect_device(self, device_id: str):
        """断开设备连接"""
        self.show_info_message("设备断开", f"正在断开设备: {device_id}")
        # TODO: 实际断开设备的逻辑
        self.device_disconnected.emit(device_id)

    def toggle_auto_refresh(self, enabled: bool):
        """切换自动刷新"""
        if enabled:
            self.refresh_timer.start(5000)
            self.show_info_message("自动刷新", "已启用自动刷新")
        else:
            self.refresh_timer.stop()
            self.show_info_message("自动刷新", "已禁用自动刷新")

    def auto_refresh_devices(self):
        """自动刷新设备"""
        # 静默刷新，不显示消息
        self.refresh_requested.emit()

    def show_info_message(self, title: str, message: str):
        """显示信息消息"""
        InfoBar.info(
            title=title,
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=3000,
            parent=self,
        )
