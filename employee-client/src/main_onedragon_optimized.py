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

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
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
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 标题
        title_label = QLabel("设备管理")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title_label.setStyleSheet("color: #1a1a1a; margin-bottom: 16px;")
        layout.addWidget(title_label)

        # 操作按钮栏
        button_layout = QHBoxLayout()

        add_btn = QPushButton("➕ 添加设备")
        add_btn.setStyleSheet(
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
        """
        )

        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setStyleSheet(
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
        """
        )

        button_layout.addWidget(add_btn)
        button_layout.addWidget(refresh_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # 设备列表表格
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(
            ["设备名称", "设备ID", "状态", "最后连接", "操作"]
        )

        # 添加示例数据
        devices = [
            ("iPhone-001", "abc123", "在线", "2分钟前"),
            ("Android-002", "def456", "离线", "1小时前"),
            ("iPad-003", "ghi789", "在线", "刚刚"),
        ]

        table.setRowCount(len(devices))
        for i, (name, device_id, status, last_seen) in enumerate(devices):
            table.setItem(i, 0, QTableWidgetItem(name))
            table.setItem(i, 1, QTableWidgetItem(device_id))

            status_item = QTableWidgetItem(status)
            if status == "在线":
                status_item.setBackground(QColor("#e8f5e8"))
            else:
                status_item.setBackground(QColor("#fce8e6"))
            table.setItem(i, 2, status_item)

            table.setItem(i, 3, QTableWidgetItem(last_seen))
            table.setItem(i, 4, QTableWidgetItem("管理"))

        # 表格样式
        table.setStyleSheet(
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
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f0f0f0;
            }
        """
        )

        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)

        layout.addWidget(table)


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

        # 设置应用程序图标（如果有的话）
        # self.app.setWindowIcon(QIcon("icon.png"))

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
