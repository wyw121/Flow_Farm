"""
设备管理界面 - 基于 OneDragon 设计
显示和管理连接的设备
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    ComboBoxSettingCard,
    FluentIcon,
    InfoBar,
    InfoBarPosition,
    PrimaryPushButton,
    PushButton,
    SettingCard,
    SettingCardGroup,
    SwitchSettingCard,
    TitleLabel,
)

from gui.onedragon_base.vertical_scroll_interface import VerticalScrollInterface


class DeviceInterface(VerticalScrollInterface):
    """设备管理界面"""

    # 界面信号
    device_refresh_requested = Signal()
    device_connect_requested = Signal(str)  # device_id
    device_disconnect_requested = Signal(str)  # device_id

    def __init__(self, parent=None):
        """初始化设备管理界面"""
        # 创建内容组件
        content_widget = self._create_device_content()

        super().__init__(
            parent=parent,
            content_widget=content_widget,
            object_name="device_interface",
            nav_text_cn="设备管理",
            nav_icon=FluentIcon.PHONE,
        )

        self.connected_devices = []
        self.logger.info("设备管理界面初始化完成")

    def _create_device_content(self) -> QWidget:
        """创建设备管理内容"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # 标题区域
        title = TitleLabel("设备管理")
        layout.addWidget(title)

        # 设备扫描区域
        scan_section = self._create_scan_section()
        layout.addWidget(scan_section)

        # 设备列表区域
        device_list_section = self._create_device_list_section()
        layout.addWidget(device_list_section)

        # 设备设置区域
        settings_section = self._create_settings_section()
        layout.addWidget(settings_section)

        layout.addStretch()
        return widget

    def _create_scan_section(self) -> QWidget:
        """创建设备扫描区域"""
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        title_label = BodyLabel("设备扫描")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # 按钮区域
        button_layout = QHBoxLayout()

        # 刷新设备按钮
        refresh_btn = PrimaryPushButton("🔍 扫描设备")
        refresh_btn.clicked.connect(self.device_refresh_requested.emit)
        button_layout.addWidget(refresh_btn)

        # ADB连接按钮
        adb_btn = PushButton("📱 连接ADB")
        adb_btn.clicked.connect(self._connect_adb)
        button_layout.addWidget(adb_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        return card

    def _create_device_list_section(self) -> QWidget:
        """创建设备列表区域"""
        self.device_list_card = CardWidget()
        layout = QVBoxLayout(self.device_list_card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        title_label = BodyLabel("已连接设备")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # 设备列表容器
        self.device_container = QWidget()
        self.device_layout = QVBoxLayout(self.device_container)
        self.device_layout.setSpacing(10)
        layout.addWidget(self.device_container)

        # 空状态提示
        self.empty_label = BodyLabel("暂无连接的设备")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: gray; padding: 20px;")
        layout.addWidget(self.empty_label)

        return self.device_list_card

    def _create_settings_section(self) -> QWidget:
        """创建设备设置区域"""
        # 创建设置组
        settings_group = SettingCardGroup("设备设置")

        # 自动重连设置
        self.auto_reconnect_card = SwitchSettingCard(
            icon=FluentIcon.SYNC, title="自动重连", content="设备断开后自动尝试重连"
        )
        settings_group.addSettingCard(self.auto_reconnect_card)

        # 操作间隔设置
        self.operation_interval_card = ComboBoxSettingCard(
            icon=FluentIcon.TIMER, title="操作间隔", content="设备操作之间的等待时间"
        )
        self.operation_interval_card.comboBox.addItems(
            ["1秒", "2秒", "3秒", "5秒", "10秒"]
        )
        self.operation_interval_card.comboBox.setCurrentText("3秒")
        settings_group.addSettingCard(self.operation_interval_card)

        return settings_group

    def _connect_adb(self):
        """连接ADB设备"""
        self.show_info_bar("ADB连接", "正在尝试连接ADB设备...", "info")
        # 这里可以添加实际的ADB连接逻辑

    def add_device(self, device_info: dict):
        """添加设备到列表"""
        device_card = self._create_device_card(device_info)
        self.device_layout.addWidget(device_card)
        self.connected_devices.append(device_info)

        # 隐藏空状态提示
        self.empty_label.hide()

        self.show_info_bar("设备连接", f"设备 {device_info['name']} 已连接", "success")

    def remove_device(self, device_id: str):
        """从列表中移除设备"""
        # 移除设备逻辑
        self.connected_devices = [
            d for d in self.connected_devices if d["id"] != device_id
        ]

        # 重新构建设备列表
        self._rebuild_device_list()

        self.show_info_bar("设备断开", f"设备 {device_id} 已断开连接", "warning")

    def _create_device_card(self, device_info: dict) -> CardWidget:
        """创建单个设备卡片"""
        card = CardWidget()
        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)

        # 设备信息
        info_layout = QVBoxLayout()

        name_label = BodyLabel(device_info.get("name", "未知设备"))
        name_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(name_label)

        id_label = BodyLabel(f"ID: {device_info.get('id', 'Unknown')}")
        id_label.setStyleSheet("color: gray; font-size: 12px;")
        info_layout.addWidget(id_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        # 操作按钮
        btn_layout = QVBoxLayout()

        # 连接状态指示
        status_label = BodyLabel(
            "🟢 已连接" if device_info.get("connected") else "🔴 已断开"
        )
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(status_label)

        # 断开按钮
        disconnect_btn = PushButton("断开")
        disconnect_btn.setFixedWidth(60)
        disconnect_btn.clicked.connect(
            lambda: self.device_disconnect_requested.emit(device_info["id"])
        )
        btn_layout.addWidget(disconnect_btn)

        layout.addLayout(btn_layout)

        return card

    def _rebuild_device_list(self):
        """重新构建设备列表"""
        # 清空现有设备
        while self.device_layout.count():
            child = self.device_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 重新添加设备
        for device_info in self.connected_devices:
            device_card = self._create_device_card(device_info)
            self.device_layout.addWidget(device_card)

        # 如果没有设备，显示空状态
        if not self.connected_devices:
            self.empty_label.show()

    def update_device_list(self, devices: list):
        """更新设备列表"""
        self.connected_devices = devices
        self._rebuild_device_list()
