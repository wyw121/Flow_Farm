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
    QFormLayout,
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
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


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
    """设备管理界面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 导入设备管理器
        from core.device_manager import ADBDeviceManager

        self.device_manager = ADBDeviceManager()
        self.devices_data = []
        self.setup_ui()

        # 初始扫描设备
        self.refresh_devices()

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

        # 使用QTimer模拟异步操作，避免界面冻结
        QTimer.singleShot(100, self._perform_scan)

    def _perform_scan(self):
        """执行实际的设备扫描"""
        try:
            devices = self.device_manager.scan_devices()
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
                    device_msg = (
                        f"发现设备: {device_info['name']} " f"({device.device_id})"
                    )
                    self.log_message(device_msg, "success")

                self.log_message(f"扫描完成，共发现 {len(devices)} 台设备", "success")

            self.update_table()

        except Exception as e:
            self.log_message(f"设备扫描失败: {str(e)}", "error")
            self.log_message("请检查ADB是否正确安装", "error")

        finally:
            self.add_btn.setEnabled(True)
            self.refresh_btn.setEnabled(True)
            self.add_btn.setText("➕ 扫描设备")

    def refresh_devices(self):
        """刷新设备列表"""
        self.log_message("刷新设备状态...", "info")
        self.scan_devices()

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
        """测试设备功能"""
        if device_index >= len(self.devices_data):
            return

        device_info = self.devices_data[device_index]

        self.log_message(f"测试设备: {device_info['name']}", "info")

        try:
            # 执行设备信息获取测试
            device_obj = device_info["device_obj"]

            self.log_message(f"设备型号: {device_obj.model}", "info")
            android_msg = f"Android版本: {device_obj.android_version}"
            self.log_message(android_msg, "info")
            resolution_msg = f"屏幕分辨率: {device_obj.screen_resolution}"
            self.log_message(resolution_msg, "info")

            if device_obj.battery_level >= 0:
                battery_msg = f"电池电量: {device_obj.battery_level}%"
                self.log_message(battery_msg, "info")

            if device_obj.capabilities:
                capabilities = device_obj.capabilities
                app_names = [app.split(".")[-1] for app in capabilities]
                apps = ", ".join(app_names)
                self.log_message(f"已安装应用: {apps}", "info")

            complete_msg = f"设备 {device_info['name']} 测试完成"
            self.log_message(complete_msg, "success")

        except Exception as e:
            self.log_message(f"设备测试失败: {str(e)}", "error")


class TaskInterface(QWidget):
    """任务管理界面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 标题
        title_label = QLabel("任务管理")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title_label.setStyleSheet("color: #1a1a1a; margin-bottom: 16px;")
        layout.addWidget(title_label)

        # 任务创建卡片
        create_form = QFormLayout()

        task_name = QLineEdit()
        task_name.setPlaceholderText("输入任务名称")
        task_name.setStyleSheet(
            """
            QLineEdit {
                padding: 10px;
                border: 1px solid #dadce0;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #1a73e8;
            }
        """
        )

        task_type = QComboBox()
        task_type.addItems(["小红书自动化", "抖音自动化", "数据采集", "其他"])
        task_type.setStyleSheet(
            """
            QComboBox {
                padding: 10px;
                border: 1px solid #dadce0;
                border-radius: 6px;
                font-size: 14px;
            }
        """
        )

        create_form.addRow("任务名称:", task_name)
        create_form.addRow("任务类型:", task_type)

        create_widget = QWidget()
        create_widget.setLayout(create_form)
        create_card = ModernCard("创建新任务", create_widget)
        layout.addWidget(create_card)

        # 运行中的任务
        running_layout = QVBoxLayout()

        tasks = [
            ("小红书自动点赞", "运行中", "75%"),
            ("数据采集任务", "队列中", "0%"),
            ("内容发布", "已完成", "100%"),
        ]

        for task_name, status, progress in tasks:
            task_item = QHBoxLayout()

            name_label = QLabel(task_name)
            name_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))

            status_label = QLabel(status)
            if status == "运行中":
                status_label.setStyleSheet(
                    "color: #34a853; background-color: #e8f5e8; padding: 4px 8px; border-radius: 4px;"
                )
            elif status == "队列中":
                status_label.setStyleSheet(
                    "color: #ea4335; background-color: #fce8e6; padding: 4px 8px; border-radius: 4px;"
                )
            else:
                status_label.setStyleSheet(
                    "color: #5f6368; background-color: #f1f3f4; padding: 4px 8px; border-radius: 4px;"
                )

            progress_bar = QProgressBar()
            progress_bar.setValue(int(progress.replace("%", "")))
            progress_bar.setStyleSheet(
                """
                QProgressBar {
                    border: 1px solid #dadce0;
                    border-radius: 4px;
                    background-color: #f8f9fa;
                    height: 20px;
                }
                QProgressBar::chunk {
                    background-color: #1a73e8;
                    border-radius: 3px;
                }
            """
            )

            task_item.addWidget(name_label)
            task_item.addWidget(status_label)
            task_item.addWidget(progress_bar)
            task_item.addStretch()

            task_widget = QWidget()
            task_widget.setLayout(task_item)
            task_widget.setStyleSheet(
                """
                QWidget {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                    padding: 12px;
                    margin: 4px;
                }
            """
            )

            running_layout.addWidget(task_widget)

        running_widget = QWidget()
        running_widget.setLayout(running_layout)
        running_card = ModernCard("任务列表", running_widget)
        layout.addWidget(running_card)

        layout.addStretch()


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
    """Flow Farm 应用程序"""

    def __init__(self):
        self.app = None
        self.window = None

    def setup_app(self):
        """初始化应用程序"""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Flow Farm")
        self.app.setApplicationVersion("2.0.0")

        # 创建主窗口
        self.window = FlowFarmMainWindow()

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
