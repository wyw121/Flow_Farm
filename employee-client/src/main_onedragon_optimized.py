#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flow Farm - OneDragon 风格 GUI (优化版本)
基于OneDragon项目的成功设计模式完全重构
"""

import os
import sys
from typing import Optional

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# 常量定义
FONT_FAMILY = "Microsoft YaHei"


class TaskInterface(QWidget):
    """任务管理界面 - 基于OneDragon设计模式重构"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_platform = "xiaohongshu"
        self.user_balance = 1250.00
        self.contacts_data = []
        self.available_devices = []

        # 初始化通讯录服务
        try:
            from core.contacts_service import ContactsService

            self.contacts_service = ContactsService()
        except ImportError:
            self.contacts_service = None
            print("警告: 无法导入通讯录服务，使用模拟数据")

        self.setup_ui()

    def setup_ui(self):
        """设置OneDragon风格的UI"""
        # 主布局 - 水平布局，左右分割
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)

        # 左侧控制面板
        left_widget = self.create_left_control_panel()
        main_layout.addWidget(left_widget)

        # 右侧内容区域
        right_widget = self.create_right_content_area()
        main_layout.addWidget(right_widget, stretch=1)

    def create_left_control_panel(self) -> QWidget:
        """创建左侧控制面板 - OneDragon风格"""
        control_widget = QWidget()
        control_widget.setFixedWidth(340)
        control_layout = QVBoxLayout(control_widget)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(12)

        # 平台选择组
        platform_group = self.create_platform_selection_group()
        control_layout.addWidget(platform_group)

        # 任务操作组
        task_group = self.create_task_operations_group()
        control_layout.addWidget(task_group)

        # 设备管理组
        device_group = self.create_device_management_group()
        control_layout.addWidget(device_group)

        # 快速操作组
        quick_actions_group = self.create_quick_actions_group()
        control_layout.addWidget(quick_actions_group)

        control_layout.addStretch(1)
        return control_widget

    def create_platform_selection_group(self) -> QWidget:
        """创建平台选择组"""
        group_widget = QWidget()
        layout = QVBoxLayout(group_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 标题
        title_label = QLabel("🎯 平台选择")
        title_label.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
        title_label.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(title_label)

        # 平台按钮行
        platform_layout = QHBoxLayout()
        platform_layout.setSpacing(8)

        self.xiaohongshu_btn = self.create_platform_toggle_button("📖", "小红书", True)
        self.douyin_btn = self.create_platform_toggle_button("🎵", "抖音", False)

        self.xiaohongshu_btn.clicked.connect(
            lambda: self.select_platform("xiaohongshu")
        )
        self.douyin_btn.clicked.connect(lambda: self.select_platform("douyin"))

        platform_layout.addWidget(self.xiaohongshu_btn)
        platform_layout.addWidget(self.douyin_btn)
        platform_layout.addStretch()

        layout.addLayout(platform_layout)

        # 余额显示
        balance_layout = QHBoxLayout()
        balance_icon = QLabel("💰")
        balance_text = QLabel(f"余额: ¥{self.user_balance:.2f}")
        balance_text.setFont(QFont(FONT_FAMILY, 11, QFont.Bold))
        balance_text.setStyleSheet("color: #107C10;")

        balance_layout.addWidget(balance_icon)
        balance_layout.addWidget(balance_text)
        balance_layout.addStretch()

        layout.addLayout(balance_layout)

        # 定价信息
        pricing_label = QLabel("小红书 ¥0.12/次 · 抖音 ¥0.15/次")
        pricing_label.setFont(QFont(FONT_FAMILY, 10))
        pricing_label.setStyleSheet("color: #666666;")
        layout.addWidget(pricing_label)

        self.apply_group_style(group_widget)
        return group_widget

    def create_task_operations_group(self) -> QWidget:
        """创建任务操作组"""
        group_widget = QWidget()
        layout = QVBoxLayout(group_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 标题
        title_label = QLabel("📋 任务操作")
        title_label.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
        title_label.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(title_label)

        # 任务类型选择
        task_type_layout = QHBoxLayout()
        task_type_label = QLabel("类型:")
        self.task_type_combo = QComboBox()
        self.task_type_combo.addItems(
            ["👥 批量关注", "❤️ 批量点赞", "💬 批量评论", "📩 私信发送"]
        )
        self.task_type_combo.setStyleSheet(self.get_combo_style())

        task_type_layout.addWidget(task_type_label)
        task_type_layout.addWidget(self.task_type_combo)
        layout.addLayout(task_type_layout)

        # 数量设置
        quantity_layout = QHBoxLayout()
        quantity_label = QLabel("数量:")
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 1000)
        self.quantity_spin.setValue(50)
        self.quantity_spin.valueChanged.connect(self.calculate_cost)
        self.quantity_spin.setStyleSheet(self.get_spinbox_style())

        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(self.quantity_spin)
        layout.addLayout(quantity_layout)

        # 预计费用
        self.cost_label = QLabel("预计费用: ¥6.00")
        self.cost_label.setFont(QFont(FONT_FAMILY, 11, QFont.Bold))
        self.cost_label.setStyleSheet("color: #EA4335;")
        layout.addWidget(self.cost_label)

        # 文件导入按钮
        import_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("选择联系人文件")
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setStyleSheet(self.get_lineedit_style())

        browse_btn = QPushButton("📂")
        browse_btn.setFixedSize(32, 32)
        browse_btn.clicked.connect(self.browse_contacts_file)
        browse_btn.setStyleSheet(self.get_icon_button_style())

        import_layout.addWidget(self.file_path_edit)
        import_layout.addWidget(browse_btn)
        layout.addLayout(import_layout)

        self.apply_group_style(group_widget)
        return group_widget

    def create_device_management_group(self) -> QWidget:
        """创建设备管理组"""
        group_widget = QWidget()
        layout = QVBoxLayout(group_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 标题
        title_label = QLabel("📱 设备管理")
        title_label.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
        title_label.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(title_label)

        # 设备选择
        device_layout = QHBoxLayout()
        device_label = QLabel("设备:")
        self.device_combo = QComboBox()
        self.device_combo.addItems(
            ["🔍 检测设备中...", "📱 雷电模拟器-5554", "📱 夜神模拟器-62001"]
        )
        self.device_combo.setStyleSheet(self.get_combo_style())

        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(32, 32)
        refresh_btn.setToolTip("刷新设备列表")
        refresh_btn.setStyleSheet(self.get_icon_button_style())

        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_combo)
        device_layout.addWidget(refresh_btn)
        layout.addLayout(device_layout)

        # 设备状态
        status_label = QLabel("状态: 🟢 在线 (1/3)")
        status_label.setFont(QFont(FONT_FAMILY, 10))
        status_label.setStyleSheet("color: #107C10;")
        layout.addWidget(status_label)

        self.apply_group_style(group_widget)
        return group_widget

    def create_quick_actions_group(self) -> QWidget:
        """创建快速操作组"""
        group_widget = QWidget()
        layout = QVBoxLayout(group_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 标题
        title_label = QLabel("🚀 快速操作")
        title_label.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
        title_label.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(title_label)

        # 操作按钮
        start_btn = QPushButton("▶️ 开始任务")
        start_btn.clicked.connect(self.submit_follow_task)
        start_btn.setStyleSheet(self.get_primary_button_style())

        pause_btn = QPushButton("⏸️ 暂停所有")
        pause_btn.setStyleSheet(self.get_warning_button_style())

        stop_btn = QPushButton("⏹️ 停止所有")
        stop_btn.setStyleSheet(self.get_danger_button_style())

        layout.addWidget(start_btn)
        layout.addWidget(pause_btn)
        layout.addWidget(stop_btn)

        self.apply_group_style(group_widget)
        return group_widget

    def create_right_content_area(self) -> QWidget:
        """创建右侧内容区域"""
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 任务状态监控
        status_monitor = self.create_task_status_monitor()
        layout.addWidget(status_monitor)

        # 实时日志
        log_monitor = self.create_log_monitor()
        layout.addWidget(log_monitor, stretch=1)

        return content_widget

    def create_task_status_monitor(self) -> QWidget:
        """创建任务状态监控"""
        monitor_widget = QWidget()
        layout = QVBoxLayout(monitor_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 标题
        title_label = QLabel("📊 任务状态监控")
        title_label.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
        title_label.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(title_label)

        # 任务列表
        tasks_data = [
            {
                "name": "小红书关注任务_001",
                "status": "运行中",
                "progress": 75,
                "device": "雷电模拟器-5554",
                "speed": "8.5/分钟",
            },
            {
                "name": "小红书关注任务_002",
                "status": "队列中",
                "progress": 0,
                "device": "夜神模拟器-62001",
                "speed": "等待中",
            },
            {
                "name": "抖音关注任务_001",
                "status": "已完成",
                "progress": 100,
                "device": "雷电模拟器-5554",
                "speed": "已完成",
            },
        ]

        for task_data in tasks_data:
            task_item = self.create_task_status_item(task_data)
            layout.addWidget(task_item)

        self.apply_group_style(monitor_widget)
        return monitor_widget

    def create_task_status_item(self, task_data) -> QWidget:
        """创建任务状态项"""
        item_widget = QWidget()
        layout = QVBoxLayout(item_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # 第一行：任务名称和状态
        top_layout = QHBoxLayout()

        name_label = QLabel(task_data["name"])
        name_label.setFont(QFont(FONT_FAMILY, 11, QFont.Bold))
        name_label.setStyleSheet("color: #1a1a1a;")

        status_label = QLabel(task_data["status"])
        status_label.setFont(QFont(FONT_FAMILY, 10, QFont.Bold))
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setFixedSize(60, 20)

        if task_data["status"] == "运行中":
            status_label.setStyleSheet(
                """
                background-color: #107C10; color: white;
                border-radius: 10px; padding: 2px 8px;
            """
            )
        elif task_data["status"] == "队列中":
            status_label.setStyleSheet(
                """
                background-color: #FF8C00; color: white;
                border-radius: 10px; padding: 2px 8px;
            """
            )
        else:
            status_label.setStyleSheet(
                """
                background-color: #666666; color: white;
                border-radius: 10px; padding: 2px 8px;
            """
            )

        top_layout.addWidget(name_label)
        top_layout.addStretch()
        top_layout.addWidget(status_label)
        layout.addLayout(top_layout)

        # 第二行：设备和速度
        info_layout = QHBoxLayout()
        device_label = QLabel(f"📱 {task_data['device']}")
        device_label.setFont(QFont(FONT_FAMILY, 9))
        device_label.setStyleSheet("color: #666666;")

        speed_label = QLabel(f"⚡ {task_data['speed']}")
        speed_label.setFont(QFont(FONT_FAMILY, 9))
        speed_label.setStyleSheet("color: #666666;")

        info_layout.addWidget(device_label)
        info_layout.addStretch()
        info_layout.addWidget(speed_label)
        layout.addLayout(info_layout)

        # 进度条
        progress_bar = QProgressBar()
        progress_bar.setValue(task_data["progress"])
        progress_bar.setFixedHeight(6)
        progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: none; border-radius: 3px;
                background-color: #F0F0F0;
            }
            QProgressBar::chunk {
                background-color: #0078D4; border-radius: 3px;
            }
        """
        )
        layout.addWidget(progress_bar)

        item_widget.setStyleSheet(
            """
            QWidget {
                background-color: #F9F9F9;
                border: 1px solid #E5E5E5;
                border-radius: 6px;
                margin: 2px 0;
            }
            QWidget:hover {
                background-color: #F0F0F0;
                border-color: #0078D4;
            }
        """
        )

        return item_widget

    def create_log_monitor(self) -> QWidget:
        """创建日志监控"""
        log_widget = QWidget()
        layout = QVBoxLayout(log_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 标题
        title_label = QLabel("📜 实时日志")
        title_label.setFont(QFont(FONT_FAMILY, 12, QFont.Bold))
        title_label.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(title_label)

        # 日志文本区域
        self.log_text = QTextEdit()
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 8px;
            }
        """
        )

        # 添加示例日志
        sample_logs = [
            "[2025-09-03 14:30:15] 📱 设备连接: 雷电模拟器-5554",
            "[2025-09-03 14:30:16] 📂 导入联系人: 125个用户",
            "[2025-09-03 14:30:17] 🚀 开始小红书关注任务",
            "[2025-09-03 14:30:20] ✅ 关注用户: user_0001",
            "[2025-09-03 14:30:23] ✅ 关注用户: user_0002",
            "[2025-09-03 14:30:26] ⚡ 任务进度: 3/50 (6%)",
        ]
        self.log_text.setText("\n".join(sample_logs))

        layout.addWidget(self.log_text)

        self.apply_group_style(log_widget)
        return log_widget

    # ====================
    # 样式方法 - OneDragon风格
    # ====================

    def create_platform_toggle_button(
        self, icon: str, text: str, is_selected: bool = False
    ) -> QPushButton:
        """创建平台切换按钮"""
        btn = QPushButton(f"{icon} {text}")
        btn.setCheckable(True)
        btn.setChecked(is_selected)
        btn.setFixedHeight(40)

        style = """
            QPushButton {
                border: 2px solid #E5E5E5;
                border-radius: 8px;
                background-color: #FFFFFF;
                color: #666666;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:checked {
                border-color: #0078D4;
                background-color: #F3F9FF;
                color: #0078D4;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
            }
            QPushButton:checked:hover {
                background-color: #E6F3FF;
            }
        """
        btn.setStyleSheet(style)
        return btn

    def apply_group_style(self, widget: QWidget):
        """应用组样式"""
        widget.setStyleSheet(
            """
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #E5E5E5;
                border-radius: 8px;
            }
        """
        )

    def get_combo_style(self) -> str:
        """获取下拉框样式"""
        return """
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #D1D1D1;
                border-radius: 6px;
                background-color: #FFFFFF;
                font-size: 11px;
            }
            QComboBox:hover {
                border-color: #0078D4;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
        """

    def get_spinbox_style(self) -> str:
        """获取数字输入框样式"""
        return """
            QSpinBox {
                padding: 8px 12px;
                border: 1px solid #D1D1D1;
                border-radius: 6px;
                background-color: #FFFFFF;
                font-size: 11px;
            }
            QSpinBox:hover {
                border-color: #0078D4;
            }
        """

    def get_lineedit_style(self) -> str:
        """获取文本输入框样式"""
        return """
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #D1D1D1;
                border-radius: 6px;
                background-color: #FFFFFF;
                font-size: 11px;
            }
            QLineEdit:hover {
                border-color: #0078D4;
            }
            QLineEdit:focus {
                border-color: #0078D4;
                outline: none;
            }
        """

    def get_icon_button_style(self) -> str:
        """获取图标按钮样式"""
        return """
            QPushButton {
                border: 1px solid #D1D1D1;
                border-radius: 6px;
                background-color: #F5F5F5;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #E6F3FF;
                border-color: #0078D4;
            }
            QPushButton:pressed {
                background-color: #D1E8FF;
            }
        """

    def get_primary_button_style(self) -> str:
        """获取主要按钮样式"""
        return """
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
        """

    def get_warning_button_style(self) -> str:
        """获取警告按钮样式"""
        return """
            QPushButton {
                background-color: #FF8C00;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF7F00;
            }
            QPushButton:pressed {
                background-color: #FF6347;
            }
        """

    def get_danger_button_style(self) -> str:
        """获取危险按钮样式"""
        return """
            QPushButton {
                background-color: #EA4335;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D33B2C;
            }
            QPushButton:pressed {
                background-color: #B32D20;
            }
        """

    # ====================
    # 事件处理方法
    # ====================

    def select_platform(self, platform: str):
        """选择平台"""
        self.selected_platform = platform

        # 更新按钮状态
        if platform == "xiaohongshu":
            self.xiaohongshu_btn.setChecked(True)
            self.douyin_btn.setChecked(False)
        else:
            self.xiaohongshu_btn.setChecked(False)
            self.douyin_btn.setChecked(True)

        # 重新计算费用
        self.calculate_cost()

        # 添加日志
        platform_name = "小红书" if platform == "xiaohongshu" else "抖音"
        self.add_log(f"📱 切换到{platform_name}平台", "info")

    def calculate_cost(self):
        """计算预计费用"""
        quantity = self.quantity_spin.value()
        unit_price = 0.12 if self.selected_platform == "xiaohongshu" else 0.15
        total_cost = quantity * unit_price
        self.cost_label.setText(f"预计费用: ¥{total_cost:.2f}")

    def browse_contacts_file(self):
        """浏览联系人文件"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "选择联系人文件",
            "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)",
        )

        if file_path:
            self.file_path_edit.setText(file_path)
            self.add_log(f"📂 选择文件: {file_path}", "info")

            # 可以在这里添加文件验证逻辑
            try:
                # 模拟文件加载
                import os

                file_size = os.path.getsize(file_path)
                self.add_log(f"📊 文件大小: {file_size} bytes", "info")
            except Exception as e:
                self.add_log(f"❌ 文件读取失败: {str(e)}", "error")

    def submit_follow_task(self):
        """提交关注任务"""
        if not self.file_path_edit.text():
            QMessageBox.warning(self, "警告", "请先选择联系人文件！")
            return

        quantity = self.quantity_spin.value()
        platform_name = "小红书" if self.selected_platform == "xiaohongshu" else "抖音"

        # 模拟任务提交
        self.add_log(f"🚀 提交{platform_name}关注任务", "info")
        self.add_log(f"📊 目标数量: {quantity}", "info")
        self.add_log(f"📱 使用设备: {self.device_combo.currentText()}", "info")

        QMessageBox.information(
            self,
            "任务提交成功",
            f"已成功提交{platform_name}关注任务\n目标数量: {quantity}",
        )

    def add_log(self, message: str, level: str = "info"):
        """添加日志"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        level_icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
        icon = level_icons.get(level, "ℹ️")

        log_entry = f"[{timestamp}] {icon} {message}"

        # 添加到日志显示区域
        self.log_text.append(log_entry)

        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)


class FlowFarmMainWindow(QMainWindow):
    """Flow Farm 主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flow Farm - 智能流量管理系统")
        self.setMinimumSize(1200, 800)
        self.setup_ui()

    def setup_ui(self):
        """设置主界面"""
        # 创建中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建界面字典
        interfaces = {
            "tasks": TaskInterface(),
        }

        # 添加任务界面作为默认显示
        layout.addWidget(interfaces["tasks"])


class FlowFarmApp:
    """Flow Farm 应用程序"""

    def __init__(self):
        self.app = None
        self.window = None

    def setup_app(self):
        """设置应用程序"""
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication([])

        # 应用性能优化
        self.apply_performance_optimizations()

        # 创建主窗口
        self.window = FlowFarmMainWindow()

    def apply_performance_optimizations(self):
        """应用性能优化"""
        try:
            # 设置应用程序属性
            self.app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            self.app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

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
