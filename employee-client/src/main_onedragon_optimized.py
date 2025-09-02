#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flow Farm - OneDragon 风格 GUI (优化版本)
去除了不兼容的 CSS 属性，减少警告信息
"""

import os
import sys
from typing import Optional

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# 常量定义
FONT_FAMILY = "Microsoft YaHei"
DEVICE_EMULATOR_LEIDIAN = "雷电模拟器-5554"
DEVICE_EMULATOR_YESHEN = "夜神模拟器-62001"

# 平台扣费规则
PLATFORM_PRICING = {
    "xiaohongshu": {"name": "小红书", "price": 0.12, "icon": "📖"},
    "douyin": {"name": "抖音", "price": 0.15, "icon": "🎵"},
}

# 任务状态常量
TASK_STATUS_RUNNING = "运行中"
TASK_STATUS_PENDING = "队列中"
TASK_STATUS_COMPLETED = "已完成"


class ModernCard(QFrame):
    """现代化卡片组件"""

    def __init__(
        self, title: str = "", content_widget: Optional[QWidget] = None, parent=None
    ):
        super().__init__(parent)
        self.setup_ui(title, content_widget)

    def setup_ui(self, title: str, content_widget: Optional[QWidget]):
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(
            """
            ModernCard {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin: 5px;
            }
            ModernCard:hover {
                border-color: #4285f4;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 标题
        if title:
            title_label = QLabel(title)
            title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
            title_label.setStyleSheet("color: #1a1a1a; margin-bottom: 8px;")
            layout.addWidget(title_label)

        # 内容
        if content_widget:
            layout.addWidget(content_widget)


class SidebarButton(QPushButton):
    """侧边栏按钮"""

    def __init__(self, text: str, icon_text: str = "", parent=None):
        super().__init__(parent)
        self.setText(f"{icon_text} {text}" if icon_text else text)
        self.setCheckable(True)
        self.setStyleSheet(
            """
            SidebarButton {
                text-align: left;
                padding: 12px 16px;
                margin: 2px 8px;
                border: none;
                border-radius: 6px;
                background-color: transparent;
                color: #5f6368;
                font-size: 14px;
                font-family: "Microsoft YaHei";
            }
            SidebarButton:hover {
                background-color: #f1f3f4;
                color: #1a73e8;
            }
            SidebarButton:checked {
                background-color: #e8f0fe;
                color: #1a73e8;
                font-weight: bold;
            }
        """
        )


class ModernSidebar(QFrame):
    """现代化侧边栏"""

    page_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons = {}
        self.setup_ui()

    def setup_ui(self):
        self.setFixedWidth(240)
        self.setStyleSheet(
            """
            ModernSidebar {
                background-color: #fafbfc;
                border-right: 1px solid #e8eaed;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setSpacing(8)

        # Logo 区域
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(16, 8, 16, 8)

        logo_label = QLabel("🚜 Flow Farm")
        logo_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        logo_label.setStyleSheet("color: #1a73e8; margin-bottom: 16px;")
        logo_layout.addWidget(logo_label)

        layout.addWidget(logo_widget)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #e8eaed; margin: 8px 16px;")
        layout.addWidget(separator)

        # 导航按钮
        nav_items = [
            ("首页", "🏠", "home"),
            ("设备管理", "📱", "devices"),
            ("任务管理", "⚡", "tasks"),
            ("数据统计", "📊", "statistics"),
            ("系统设置", "⚙️", "settings"),
        ]

        for text, icon, key in nav_items:
            btn = SidebarButton(text, icon)
            btn.clicked.connect(lambda checked=False, k=key: self.on_button_clicked(k))
            self.buttons[key] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # 默认选中首页
        self.buttons["home"].setChecked(True)

    def on_button_clicked(self, key: str):
        # 取消其他按钮的选中状态
        for btn_key, btn in self.buttons.items():
            btn.setChecked(btn_key == key)

        self.page_changed.emit(key)


class HomeInterface(QWidget):
    """首页界面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 欢迎标题
        title_label = QLabel("欢迎使用 Flow Farm")
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        title_label.setStyleSheet("color: #1a1a1a; margin-bottom: 8px;")
        layout.addWidget(title_label)

        subtitle_label = QLabel("智能农场管理系统")
        subtitle_label.setFont(QFont("Microsoft YaHei", 14))
        subtitle_label.setStyleSheet("color: #5f6368; margin-bottom: 24px;")
        layout.addWidget(subtitle_label)

        # 状态卡片网格
        cards_layout = QGridLayout()
        cards_layout.setSpacing(16)

        # 系统状态卡片
        status_content = QVBoxLayout()
        status_label = QLabel("● 系统运行正常")
        status_label.setStyleSheet("color: #34a853; font-size: 14px;")
        uptime_label = QLabel("运行时间: 24小时")
        uptime_label.setStyleSheet("color: #5f6368; font-size: 12px;")
        status_content.addWidget(status_label)
        status_content.addWidget(uptime_label)
        status_widget = QWidget()
        status_widget.setLayout(status_content)

        status_card = ModernCard("系统状态", status_widget)
        cards_layout.addWidget(status_card, 0, 0)

        # 设备数量卡片
        device_content = QVBoxLayout()
        device_count = QLabel("12")
        device_count.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        device_count.setStyleSheet("color: #1a73e8;")
        device_desc = QLabel("在线设备")
        device_desc.setStyleSheet("color: #5f6368; font-size: 12px;")
        device_content.addWidget(device_count)
        device_content.addWidget(device_desc)
        device_widget = QWidget()
        device_widget.setLayout(device_content)

        device_card = ModernCard("设备统计", device_widget)
        cards_layout.addWidget(device_card, 0, 1)

        # 任务统计卡片
        task_content = QVBoxLayout()
        task_count = QLabel("8")
        task_count.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        task_count.setStyleSheet("color: #ea4335;")
        task_desc = QLabel("运行中任务")
        task_desc.setStyleSheet("color: #5f6368; font-size: 12px;")
        task_content.addWidget(task_count)
        task_content.addWidget(task_desc)
        task_widget = QWidget()
        task_widget.setLayout(task_content)

        task_card = ModernCard("任务统计", task_widget)
        cards_layout.addWidget(task_card, 0, 2)

        # 效率统计卡片
        efficiency_content = QVBoxLayout()
        efficiency_count = QLabel("95%")
        efficiency_count.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        efficiency_count.setStyleSheet("color: #34a853;")
        efficiency_desc = QLabel("工作效率")
        efficiency_desc.setStyleSheet("color: #5f6368; font-size: 12px;")
        efficiency_content.addWidget(efficiency_count)
        efficiency_content.addWidget(efficiency_desc)
        efficiency_widget = QWidget()
        efficiency_widget.setLayout(efficiency_content)

        efficiency_card = ModernCard("效率统计", efficiency_widget)
        cards_layout.addWidget(efficiency_card, 0, 3)

        layout.addLayout(cards_layout)

        # 最近活动
        activity_content = QVBoxLayout()
        activities = [
            "📱 设备 iPhone-001 连接成功",
            "⚡ 任务 '小红书自动化' 开始执行",
            "📊 生成今日工作报告",
            "🔧 系统配置已更新",
        ]

        for activity in activities:
            activity_label = QLabel(activity)
            activity_label.setStyleSheet(
                "padding: 8px; color: #1a1a1a; font-size: 14px;"
            )
            activity_content.addWidget(activity_label)

        activity_widget = QWidget()
        activity_widget.setLayout(activity_content)
        activity_card = ModernCard("最近活动", activity_widget)
        layout.addWidget(activity_card)

        layout.addStretch()


class DeviceInterface(QWidget):
    """设备管理界面 - 优化版本"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 导入异步设备管理器
        from core.async_device_manager import AsyncDeviceManager

        # 使用异步设备管理器避免阻塞GUI线程
        self.async_device_manager = AsyncDeviceManager(self)
        self.devices_data = []

        self.setup_ui()
        self.setup_connections()

    def setup_connections(self):
        """设置信号连接"""
        # 连接异步设备管理器的信号
        self.async_device_manager.devices_scanned.connect(self.on_devices_scanned)
        self.async_device_manager.scan_progress.connect(self.log_message)
        self.async_device_manager.error_occurred.connect(
            lambda msg: self.log_message(msg, "error")
        )

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)  # 减少整体间距

        # 标题
        title_label = QLabel("设备管理")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title_label.setStyleSheet("color: #1a1a1a; margin-bottom: 12px;")
        layout.addWidget(title_label)

        # 操作按钮栏
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("➕ 扫描设备")
        self.add_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """
        )
        self.add_btn.clicked.connect(self.scan_devices)

        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #f8f9fa;
                color: #1a1a1a;
                border: 1px solid #dadce0;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f1f3f4;
            }
            QPushButton:disabled {
                background-color: #eeeeee;
            }
        """
        )
        self.refresh_btn.clicked.connect(self.refresh_devices)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # 设备列表表格 - 优化高度设置
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["设备名称", "设备ID", "状态", "最后连接", "操作"]
        )

        # 设置表格合理的高度范围
        self.table.setMaximumHeight(250)  # 减少最大高度
        self.table.setMinimumHeight(150)  # 设置最小高度

        # 禁用表格的垂直扩展策略，让它保持紧凑
        self.table.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )

        # 表格样式 - 增加行高以确保操作按钮完整显示
        self.table.setStyleSheet(
            """
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                gridline-color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 12px;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                font-weight: bold;
                height: 35px;
            }
            QTableWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #f0f0f0;
                min-height: 40px;
            }
        """
        )

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        # 设置行高以确保操作按钮能完整显示
        self.table.verticalHeader().setDefaultSectionSize(45)

        layout.addWidget(self.table)

        # 添加日志反馈模块 - 立即跟在表格后面
        self.create_log_widget(layout)

        # 添加弹性空间，把所有内容向上推
        layout.addStretch()

    def create_log_widget(self, layout):
        """创建日志反馈模块"""
        # 日志区域标题 - 紧挨着表格
        log_title = QLabel("📋 操作日志")
        log_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        log_title.setStyleSheet("color: #1a1a1a; margin-top: 5px; margin-bottom: 5px;")
        layout.addWidget(log_title)

        # 日志文本框 - 增加高度，让内容更清晰
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(180)  # 增加日志显示高度
        self.log_text.setMinimumHeight(120)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(
            """
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #f8f9fa;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                color: #333333;
                padding: 8px;
            }
        """
        )

        # 添加欢迎消息
        self.log_text.append("🚀 Flow Farm 设备管理器已启动")
        self.log_text.append("💡 点击'扫描设备'来查找可用的Android设备")

        layout.addWidget(self.log_text)

    def log_message(self, message: str, level: str = "info"):
        """添加日志消息"""
        import datetime

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        level_icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}

        icon = level_icons.get(level, "ℹ️")
        formatted_message = f"[{timestamp}] {icon} {message}"

        self.log_text.append(formatted_message)
        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)

    def scan_devices(self):
        """扫描并添加设备"""
        self.log_message("开始扫描设备...", "info")
        self.add_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        self.add_btn.setText("扫描中...")

        # 调用异步设备管理器进行扫描
        self.async_device_manager.scan_devices_async()

    def on_devices_scanned(self, devices):
        """设备扫描完成回调"""
        self.devices_data = []

        if not devices:
            self.log_message("未发现任何设备，请检查：", "warning")
            self.log_message("1. USB调试是否开启", "warning")
            self.log_message("2. 设备是否正确连接", "warning")
            self.log_message("3. ADB驱动是否安装", "warning")
        else:
            for device in devices:
                device_info = {
                    "name": device.model or f"设备-{device.device_id[:8]}",
                    "device_id": device.device_id,
                    "status": self._get_status_text(device.status),
                    "last_seen": self._format_time(device.last_seen),
                    "device_obj": device,
                }
                self.devices_data.append(device_info)
                device_msg = f"发现设备: {device_info['name']} ({device.device_id})"
                self.log_message(device_msg, "success")

            self.log_message(f"扫描完成，共发现 {len(devices)} 台设备", "success")

        self.update_table()

        # 恢复按钮状态
        self.add_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        self.add_btn.setText("➕ 扫描设备")

    def _perform_scan(self):
        """执行实际的设备扫描 - 已废弃，使用异步版本"""
        # 这个方法已被 on_devices_scanned 替代
        pass

    def refresh_devices(self):
        """刷新设备列表"""
        self.log_message("刷新设备状态...", "info")

        # 如果异步管理器已初始化，则重新扫描
        if self.async_device_manager.is_initialized():
            self.scan_devices()
        else:
            self.log_message("设备管理器正在初始化中，请稍后...", "warning")

    def _get_status_text(self, status):
        """获取状态文本"""
        status_map = {
            "CONNECTED": "在线",
            "DISCONNECTED": "离线",
            "CONNECTING": "连接中",
            "WORKING": "工作中",
            "ERROR": "错误",
            "OFFLINE": "离线",
        }
        return status_map.get(str(status).upper(), "未知")

    def _format_time(self, timestamp):
        """格式化时间"""
        import datetime

        try:
            dt = datetime.datetime.fromtimestamp(timestamp)
            now = datetime.datetime.now()
            diff = now - dt

            if diff.seconds < 60:
                return "刚刚"
            elif diff.seconds < 3600:
                return f"{diff.seconds // 60}分钟前"
            else:
                return dt.strftime("%H:%M")
        except Exception:
            return "未知"

    def update_table(self):
        """更新设备表格"""
        self.table.setRowCount(len(self.devices_data))

        for i, device_info in enumerate(self.devices_data):
            self.table.setItem(i, 0, QTableWidgetItem(device_info["name"]))
            device_id_item = QTableWidgetItem(device_info["device_id"])
            self.table.setItem(i, 1, device_id_item)

            status_item = QTableWidgetItem(device_info["status"])
            if device_info["status"] == "在线":
                status_item.setBackground(QColor("#e8f5e8"))
            elif device_info["status"] == "工作中":
                status_item.setBackground(QColor("#e3f2fd"))
            else:
                status_item.setBackground(QColor("#fce8e6"))
            self.table.setItem(i, 2, status_item)

            last_seen_item = QTableWidgetItem(device_info["last_seen"])
            self.table.setItem(i, 3, last_seen_item)

            # 创建操作按钮
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(3, 3, 3, 3)  # 增加内边距
            action_layout.setSpacing(5)  # 增加按钮之间的间距

            status = device_info["status"]
            btn_text = "连接" if status != "在线" else "断开"
            connect_btn = QPushButton(btn_text)
            connect_btn.setFixedSize(55, 32)  # 调整按钮大小
            connect_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """
            )

            test_btn = QPushButton("测试")
            test_btn.setFixedSize(55, 32)  # 调整按钮大小
            test_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """
            )

            # 绑定事件 - 使用正确的函数定义方式
            def make_connect_handler(idx):
                def handler():
                    self.toggle_device_connection(idx)

                return handler

            def make_test_handler(idx):
                def handler():
                    self.test_device(idx)

                return handler

            connect_btn.clicked.connect(make_connect_handler(i))
            test_btn.clicked.connect(make_test_handler(i))

            action_layout.addWidget(connect_btn)
            action_layout.addWidget(test_btn)

            self.table.setCellWidget(i, 4, action_widget)

    def toggle_device_connection(self, device_index):
        """切换设备连接状态"""
        if device_index >= len(self.devices_data):
            return

        device_info = self.devices_data[device_index]

        if device_info["status"] == "在线":
            self.log_message(f"断开设备: {device_info['name']}", "info")
            # 这里可以添加实际的断开逻辑
        else:
            self.log_message(f"尝试连接设备: {device_info['name']}", "info")
            # 这里可以添加实际的连接逻辑

    def test_device(self, device_index):
        """测试设备功能 - 异步版本"""
        if device_index >= len(self.devices_data):
            return

        device_info = self.devices_data[device_index]
        device_id = device_info["device_id"]

        self.log_message(f"开始测试设备: {device_info['name']}", "info")

        # 调用异步设备管理器进行测试
        self.async_device_manager.test_device_async(device_id)


class TaskInterface(QWidget):
    """任务管理界面 - 通讯录导入和同行监控"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_platform = "xiaohongshu"  # 默认选择小红书
        self.user_balance = 1250.00  # 模拟用户余额
        self.contacts_data = []  # 通讯录数据
        self.available_devices = []  # 可用设备列表

        # 初始化通讯录服务
        try:
            from core.contacts_service import ContactsService

            self.contacts_service = ContactsService()
        except ImportError:
            self.contacts_service = None
            print("警告: 无法导入通讯录服务，使用模拟数据")

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 标题和余额显示
        header_layout = QHBoxLayout()

        title_label = QLabel("任务管理")
        title_label.setFont(QFont(FONT_FAMILY, 18, QFont.Bold))
        title_label.setStyleSheet("color: #1a1a1a;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # 用户余额显示
        balance_widget = QWidget()
        balance_layout = QHBoxLayout(balance_widget)
        balance_layout.setContentsMargins(16, 8, 16, 8)

        balance_icon = QLabel("💰")
        balance_icon.setFont(QFont("Microsoft YaHei", 16))

        balance_text = QLabel(f"账户余额: ¥{self.user_balance:.2f}")
        balance_text.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        balance_text.setStyleSheet("color: #34a853;")

        balance_layout.addWidget(balance_icon)
        balance_layout.addWidget(balance_text)

        balance_widget.setStyleSheet(
            """
            QWidget {
                background-color: #e8f5e8;
                border: 1px solid #34a853;
                border-radius: 8px;
            }
        """
        )

        header_layout.addWidget(balance_widget)
        layout.addLayout(header_layout)

        # 平台选择区域
        platform_card = self.create_platform_selection()
        layout.addWidget(platform_card)

        # 主要任务区域 - 使用水平布局
        main_tasks_layout = QHBoxLayout()
        main_tasks_layout.setSpacing(16)

        # 通讯录导入模块
        contacts_card = self.create_contacts_import_module()
        main_tasks_layout.addWidget(contacts_card)

        # 同行监控模块（预留）
        monitoring_card = self.create_monitoring_module()
        main_tasks_layout.addWidget(monitoring_card)

        layout.addLayout(main_tasks_layout)

        # 任务执行状态区域
        status_card = self.create_task_status_area()
        layout.addWidget(status_card)

        layout.addStretch()

    def create_platform_selection(self):
        """创建平台选择区域"""
        platform_layout = QHBoxLayout()

        # 平台选择标题
        platform_title = QLabel("选择平台:")
        platform_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        platform_title.setStyleSheet("color: #1a1a1a; margin-right: 16px;")
        platform_layout.addWidget(platform_title)

        # 小红书按钮
        self.xiaohongshu_btn = QPushButton("📖 小红书")
        self.xiaohongshu_btn.setCheckable(True)
        self.xiaohongshu_btn.setChecked(True)
        self.xiaohongshu_btn.clicked.connect(
            lambda: self.select_platform("xiaohongshu")
        )

        # 抖音按钮
        self.douyin_btn = QPushButton("🎵 抖音")
        self.douyin_btn.setCheckable(True)
        self.douyin_btn.clicked.connect(lambda: self.select_platform("douyin"))

        # 设置按钮样式
        for btn in [self.xiaohongshu_btn, self.douyin_btn]:
            btn.setStyleSheet(
                """
                QPushButton {
                    padding: 12px 24px;
                    border: 2px solid #dadce0;
                    border-radius: 8px;
                    background-color: #ffffff;
                    color: #5f6368;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 120px;
                }
                QPushButton:checked {
                    border-color: #1a73e8;
                    background-color: #e3f2fd;
                    color: #1a73e8;
                }
                QPushButton:hover {
                    background-color: #f1f3f4;
                }
                QPushButton:checked:hover {
                    background-color: #bbdefb;
                }
            """
            )

        platform_layout.addWidget(self.xiaohongshu_btn)
        platform_layout.addWidget(self.douyin_btn)
        platform_layout.addStretch()

        # 添加扣费规则显示
        pricing_info = QLabel("当前扣费: 小红书关注 ¥0.12/次 | 抖音关注 ¥0.15/次")
        pricing_info.setStyleSheet(
            "color: #666666; font-size: 12px; margin-left: 16px;"
        )
        platform_layout.addWidget(pricing_info)

        platform_widget = QWidget()
        platform_widget.setLayout(platform_layout)

        return ModernCard("平台选择", platform_widget)

    def create_contacts_import_module(self):
        """创建通讯录导入模块"""
        contacts_layout = QVBoxLayout()

        # 导入区域
        import_layout = QVBoxLayout()

        # 文件选择
        file_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("选择通讯录文件 (.csv, .xlsx, .txt)")
        self.file_path_edit.setReadOnly(True)

        browse_btn = QPushButton("📁 浏览文件")
        browse_btn.clicked.connect(self.browse_contacts_file)

        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(browse_btn)
        import_layout.addLayout(file_layout)

        # 导入统计信息
        self.import_stats = QLabel("未导入文件")
        self.import_stats.setStyleSheet("color: #666666; margin: 8px 0;")
        import_layout.addWidget(self.import_stats)

        # 导入按钮
        import_btn = QPushButton("📤 导入通讯录")
        import_btn.clicked.connect(self.import_contacts)
        import_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #34a853;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2e7d32;
            }
        """
        )
        import_layout.addWidget(import_btn)

        contacts_layout.addLayout(import_layout)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #e0e0e0;")
        contacts_layout.addWidget(separator)

        # 任务配置区域
        config_layout = QVBoxLayout()

        # 设备选择
        device_layout = QHBoxLayout()
        device_label = QLabel("选择设备:")
        device_label.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))

        self.device_combo = QComboBox()
        # 模拟数据
        device_options = [
            "请先连接设备",
            DEVICE_EMULATOR_LEIDIAN,
            DEVICE_EMULATOR_YESHEN,
        ]
        self.device_combo.addItems(device_options)

        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_combo)
        config_layout.addLayout(device_layout)

        # 任务数量设置
        quantity_layout = QHBoxLayout()
        quantity_label = QLabel("关注数量:")
        quantity_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 1000)
        self.quantity_spin.setValue(50)
        self.quantity_spin.valueChanged.connect(self.calculate_cost)

        self.cost_label = QLabel("预计费用: ¥6.00")
        cost_style = "color: #ea4335; font-weight: bold; " "margin-left: 16px;"
        self.cost_label.setStyleSheet(cost_style)

        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(self.quantity_spin)
        quantity_layout.addWidget(self.cost_label)
        quantity_layout.addStretch()
        config_layout.addLayout(quantity_layout)

        # 提交任务按钮
        submit_btn = QPushButton("🚀 提交关注任务")
        submit_btn.clicked.connect(self.submit_follow_task)
        submit_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """
        )
        config_layout.addWidget(submit_btn)

        contacts_layout.addLayout(config_layout)

        contacts_widget = QWidget()
        contacts_widget.setLayout(contacts_layout)

        return ModernCard("📇 通讯录导入", contacts_widget)

    def create_monitoring_module(self):
        """创建同行监控模块（预留）"""
        monitoring_layout = QVBoxLayout()

        # 预留提示
        coming_soon = QLabel("🔍 同行监控")
        coming_soon.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        coming_soon.setAlignment(Qt.AlignCenter)
        coming_soon.setStyleSheet("color: #666666; margin: 20px 0;")

        description = QLabel("监控同行账号动态\n自动分析竞品策略\n智能推荐优化方案")
        description.setAlignment(Qt.AlignCenter)
        desc_style = "color: #999999; line-height: 1.6; " "margin: 16px 0;"
        description.setStyleSheet(desc_style)

        status_label = QLabel("🚧 功能开发中...")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet(
            """
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 6px;
            padding: 12px;
            color: #856404;
            font-weight: bold;
        """
        )

        monitoring_layout.addWidget(coming_soon)
        monitoring_layout.addWidget(description)
        monitoring_layout.addWidget(status_label)
        monitoring_layout.addStretch()

        monitoring_widget = QWidget()
        monitoring_widget.setLayout(monitoring_layout)

        return ModernCard("🔍 同行监控", monitoring_widget)

    def create_task_status_area(self):
        """创建任务状态区域"""
        status_layout = QVBoxLayout()

        # 运行中的任务
        tasks = [
            ("小红书关注任务_001", "运行中", 75, "雷电模拟器-5554"),
            ("小红书关注任务_002", "队列中", 0, "夜神模拟器-62001"),
            ("抖音关注任务_001", "已完成", 100, "雷电模拟器-5554"),
        ]

        for task_name, status, progress, device in tasks:
            task_layout = QHBoxLayout()

            # 任务信息
            info_layout = QVBoxLayout()
            name_label = QLabel(task_name)
            name_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))

            device_label = QLabel(f"设备: {device}")
            device_label.setStyleSheet("color: #666666; font-size: 11px;")

            info_layout.addWidget(name_label)
            info_layout.addWidget(device_label)

            # 状态标签
            status_label = QLabel(status)
            if status == TASK_STATUS_RUNNING:
                status_style = (
                    "color: #34a853; background-color: #e8f5e8; "
                    "padding: 6px 12px; border-radius: 4px; "
                    "font-weight: bold;"
                )
                status_label.setStyleSheet(status_style)
            elif status == TASK_STATUS_PENDING:
                status_style = (
                    "color: #ea4335; background-color: #fce8e6; "
                    "padding: 6px 12px; border-radius: 4px; "
                    "font-weight: bold;"
                )
                status_label.setStyleSheet(status_style)
            else:
                status_style = (
                    "color: #5f6368; background-color: #f1f3f4; "
                    "padding: 6px 12px; border-radius: 4px; "
                    "font-weight: bold;"
                )
                status_label.setStyleSheet(status_style)

            # 进度条
            progress_bar = QProgressBar()
            progress_bar.setValue(progress)
            progress_bar.setStyleSheet(
                """
                QProgressBar {
                    border: 1px solid #dadce0;
                    border-radius: 4px;
                    background-color: #f8f9fa;
                    height: 24px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #1a73e8;
                    border-radius: 3px;
                }
            """
            )

            # 操作按钮
            if status == TASK_STATUS_RUNNING:
                action_text = "⏸️ 暂停"
            elif status == TASK_STATUS_PENDING:
                action_text = "▶️ 开始"
            else:
                action_text = "✅ 完成"

            action_btn = QPushButton(action_text)
            action_btn.setEnabled(status != TASK_STATUS_COMPLETED)
            action_btn.setStyleSheet(
                """
                QPushButton {
                    padding: 6px 12px;
                    border: 1px solid #dadce0;
                    border-radius: 4px;
                    background-color: #ffffff;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #f1f3f4;
                }
                QPushButton:disabled {
                    background-color: #eeeeee;
                    color: #cccccc;
                }
            """
            )

            task_layout.addLayout(info_layout)
            task_layout.addWidget(status_label)
            task_layout.addWidget(progress_bar, 1)
            task_layout.addWidget(action_btn)

            # 任务容器
            task_widget = QWidget()
            task_widget.setLayout(task_layout)
            task_widget.setStyleSheet(
                """
                QWidget {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 12px;
                    margin: 4px 0;
                }
            """
            )

            status_layout.addWidget(task_widget)

        status_widget = QWidget()
        status_widget.setLayout(status_layout)

        return ModernCard("📊 任务执行状态", status_widget)

    def select_platform(self, platform):
        """选择平台"""
        self.selected_platform = platform

        # 更新按钮状态
        self.xiaohongshu_btn.setChecked(platform == "xiaohongshu")
        self.douyin_btn.setChecked(platform == "douyin")

        # 重新计算费用
        self.calculate_cost()

        print(f"已选择平台: {platform}")

    def browse_contacts_file(self):
        """浏览通讯录文件"""
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择通讯录文件", "", "通讯录文件 (*.csv *.xlsx *.txt);;所有文件 (*)"
        )

        if file_path:
            self.file_path_edit.setText(file_path)
            # 模拟文件分析
            self.import_stats.setText("📊 检测到 1,234 条联系人数据")

    def import_contacts(self):
        """导入通讯录"""
        if not self.file_path_edit.text():
            self.show_message("请先选择通讯录文件", "warning")
            return

        try:
            # 如果有通讯录服务，使用真实导入
            if self.contacts_service:
                file_path = self.file_path_edit.text()
                contacts, stats = self.contacts_service.import_contacts_file(file_path)

                # 转换为简单的用户名列表用于界面显示
                self.contacts_data = [contact.username for contact in contacts]

                stats_text = (
                    f"✅ 已导入 {stats['valid_count']} 条有效数据，"
                    f"去重 {stats['duplicates_removed']} 条，"
                    "待分配关注任务"
                )
                self.import_stats.setText(stats_text)

                success_msg = (
                    f"成功导入通讯录！\n"
                    f"有效数据: {stats['valid_count']} 条\n"
                    f"去重数据: {stats['duplicates_removed']} 条\n"
                    f"包含手机号: {stats['has_phone']} 条"
                )
                self.show_message(success_msg, "success")
            else:
                # 模拟导入过程
                user_count = 1234
                self.contacts_data = [f"user_{i:04d}" for i in range(1, user_count + 1)]
                stats_text = (
                    f"✅ 已导入 {len(self.contacts_data)} 条数据，" "待分配关注任务"
                )
                self.import_stats.setText(stats_text)
                self.show_message(
                    f"成功导入 {len(self.contacts_data)} 条通讯录数据", "success"
                )

        except Exception as e:
            error_msg = f"导入通讯录失败: {str(e)}"
            self.import_stats.setText("❌ 导入失败")
            self.show_message(error_msg, "error")

    def calculate_cost(self):
        """计算费用"""
        quantity = self.quantity_spin.value()
        unit_price = 0.12 if self.selected_platform == "xiaohongshu" else 0.15
        total_cost = quantity * unit_price

        self.cost_label.setText(f"预计费用: ¥{total_cost:.2f}")

        # 检查余额是否足够
        if total_cost > self.user_balance:
            error_style = (
                "color: #ea4335; font-weight: bold; "
                "background-color: #fce8e6; padding: 4px 8px; "
                "border-radius: 4px;"
            )
            self.cost_label.setStyleSheet(error_style)
        else:
            self.cost_label.setStyleSheet("color: #34a853; font-weight: bold;")

    def submit_follow_task(self):
        """提交关注任务"""
        if not self.contacts_data:
            self.show_message("请先导入通讯录数据", "warning")
            return

        quantity = self.quantity_spin.value()
        unit_price = 0.12 if self.selected_platform == "xiaohongshu" else 0.15
        total_cost = quantity * unit_price

        if total_cost > self.user_balance:
            error_msg = (
                f"余额不足！需要 ¥{total_cost:.2f}，"
                f"当前余额 ¥{self.user_balance:.2f}"
            )
            self.show_message(error_msg, "error")
            return

        if self.device_combo.currentText() == "请先连接设备":
            self.show_message("请先选择可用设备", "warning")
            return

        # 模拟提交任务
        self.user_balance -= total_cost

        # 更新余额显示
        for child in self.findChildren(QLabel):
            if "账户余额" in child.text():
                child.setText(f"账户余额: ¥{self.user_balance:.2f}")
                break

        platform_info = PLATFORM_PRICING.get(self.selected_platform, {})
        platform_name = platform_info.get("name", "未知平台")

        success_msg = (
            f"任务提交成功！\n平台: {platform_name}\n"
            f"数量: {quantity}\n费用: ¥{total_cost:.2f}\n"
            f"剩余余额: ¥{self.user_balance:.2f}"
        )
        self.show_message(success_msg, "success")

    def show_message(self, message, msg_type="info"):
        """显示消息"""
        from PySide6.QtWidgets import QMessageBox

        msg_box = QMessageBox()
        msg_box.setWindowTitle("Flow Farm")
        msg_box.setText(message)

        if msg_type == "success":
            msg_box.setIcon(QMessageBox.Information)
        elif msg_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif msg_type == "error":
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Information)

        msg_box.exec()


class FlowFarmMainWindow(QMainWindow):
    """Flow Farm 主窗口"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setWindowTitle("Flow Farm - 智能农场管理系统")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # 设置应用程序样式
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #ffffff;
            }
            * {
                font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
            }
        """
        )

        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 侧边栏
        self.sidebar = ModernSidebar()
        main_layout.addWidget(self.sidebar)

        # 页面容器
        self.page_stack = QStackedWidget()
        main_layout.addWidget(self.page_stack)

        # 创建页面
        self.pages = {
            "home": HomeInterface(),
            "devices": DeviceInterface(),
            "tasks": TaskInterface(),
            "statistics": QLabel("数据统计页面 - 开发中..."),
            "settings": QLabel("系统设置页面 - 开发中..."),
        }

        # 添加页面到堆栈
        for page in self.pages.values():
            if isinstance(page, QLabel):
                page.setAlignment(Qt.AlignCenter)
                page.setFont(QFont("Microsoft YaHei", 16))
                page.setStyleSheet("color: #5f6368; padding: 50px;")
            self.page_stack.addWidget(page)

        # 设置默认页面
        self.page_stack.setCurrentWidget(self.pages["home"])

    def setup_connections(self):
        """设置信号连接"""
        self.sidebar.page_changed.connect(self.on_page_changed)

    def on_page_changed(self, page_key: str):
        """切换页面"""
        if page_key in self.pages:
            self.page_stack.setCurrentWidget(self.pages[page_key])


class FlowFarmApp:
    """Flow Farm 应用程序 - 性能优化版本"""

    def __init__(self):
        self.app = None
        self.window = None

    def setup_app(self):
        """初始化应用程序"""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Flow Farm")
        self.app.setApplicationVersion("2.0.0")

        # 应用性能优化
        self._apply_performance_optimizations()

        # 创建主窗口
        self.window = FlowFarmMainWindow()

    def _apply_performance_optimizations(self):
        """应用性能优化设置"""
        try:
            # 导入性能优化器
            from gui.performance_optimizer import apply_performance_optimizations

            # 应用优化设置
            apply_performance_optimizations()

            # 设置应用程序属性
            self.app.setAttribute(self.app.AA_EnableHighDpiScaling, True)
            self.app.setAttribute(self.app.AA_UseHighDpiPixmaps, True)

        except ImportError:
            # 如果性能优化器不可用，使用基本优化
            self.app.setAttribute(self.app.AA_EnableHighDpiScaling, True)
        except Exception as e:
            print(f"性能优化应用失败: {e}")

    def run(self):
        """运行应用程序"""
        if not self.app:
            self.setup_app()

        self.window.show()
        return self.app.exec()


def main():
    """主函数"""
    app = FlowFarmApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
