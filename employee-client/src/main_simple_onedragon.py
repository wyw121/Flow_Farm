"""
Flow Farm OneDragon 架构测试版本
使用标准 PySide6 组件实现 OneDragon 风格界面
"""

import logging
import sys
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


class ModernCard(QFrame):
    """现代化卡片组件"""

    def __init__(self, title: str = "", content: str = "", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
            QFrame:hover {
                border-color: #1890ff;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        """
        )

        layout = QVBoxLayout(self)

        if title:
            title_label = QLabel(title)
            title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
            layout.addWidget(title_label)

        if content:
            content_label = QLabel(content)
            content_label.setWordWrap(True)
            layout.addWidget(content_label)


class BaseInterface(QWidget):
    """基础界面类"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 内容区域
        content_area = self.create_content()
        if content_area:
            layout.addWidget(content_area)

        layout.addStretch()

    def create_content(self) -> QWidget:
        """子类重写此方法创建内容"""
        return None


class HomeInterface(BaseInterface):
    """主页界面"""

    start_work_clicked = Signal()
    device_manage_clicked = Signal()
    view_stats_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__("🏠 Flow Farm 工作台", parent)

    def create_content(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 状态卡片
        status_layout = QHBoxLayout()

        device_card = ModernCard("设备状态", "0 台在线")
        status_layout.addWidget(device_card)

        task_card = ModernCard("任务状态", "待启动")
        status_layout.addWidget(task_card)

        stats_card = ModernCard("今日统计", "0 次操作")
        status_layout.addWidget(stats_card)

        layout.addLayout(status_layout)

        # 主要操作按钮
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        start_btn = QPushButton("🚀 开始工作")
        start_btn.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        start_btn.setFixedSize(200, 50)
        start_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
            QPushButton:pressed {
                background-color: #096dd9;
            }
        """
        )
        start_btn.clicked.connect(self.start_work_clicked.emit)
        button_layout.addWidget(start_btn)

        layout.addLayout(button_layout)

        # 次要操作
        secondary_layout = QHBoxLayout()
        secondary_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        device_btn = QPushButton("📱 设备管理")
        device_btn.clicked.connect(self.device_manage_clicked.emit)
        secondary_layout.addWidget(device_btn)

        stats_btn = QPushButton("📊 数据统计")
        stats_btn.clicked.connect(self.view_stats_clicked.emit)
        secondary_layout.addWidget(stats_btn)

        layout.addLayout(secondary_layout)

        return widget


class DeviceInterface(BaseInterface):
    """设备管理界面"""

    def __init__(self, parent=None):
        super().__init__("📱 设备管理", parent)

    def create_content(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 扫描按钮
        scan_btn = QPushButton("🔍 扫描设备")
        scan_btn.setFixedHeight(40)
        layout.addWidget(scan_btn)

        # 设备列表
        device_list = ModernCard(
            "已连接设备", "暂无设备连接\n\n请点击扫描设备按钮搜索可用设备"
        )
        layout.addWidget(device_list)

        return widget


class TaskInterface(BaseInterface):
    """任务管理界面"""

    def __init__(self, parent=None):
        super().__init__("⚙️ 任务管理", parent)

    def create_content(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 任务控制
        control_card = ModernCard("任务控制")
        control_layout = QVBoxLayout()

        start_task_btn = QPushButton("▶️ 开始任务")
        start_task_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #52c41a;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #73d13d;
            }
        """
        )
        control_layout.addWidget(start_task_btn)

        stop_task_btn = QPushButton("⏹️ 停止任务")
        stop_task_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #ff4d4f;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #ff7875;
            }
        """
        )
        control_layout.addWidget(stop_task_btn)

        status_label = QLabel("状态: 待启动")
        control_layout.addWidget(status_label)

        control_card.layout().addLayout(control_layout)
        layout.addWidget(control_card)

        # 任务配置
        config_card = ModernCard(
            "任务配置", "平台: 抖音\n操作: 自动关注\n数量: 10\n间隔: 3秒"
        )
        layout.addWidget(config_card)

        return widget


class FlowFarmMainWindow(QMainWindow):
    """Flow Farm 主窗口"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("Flow Farm - 流量农场工作台 (OneDragon 风格)")
        self.setMinimumSize(1095, 730)

        # 主部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 主布局
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 侧边栏
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        # 内容区域
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(
            """
            QStackedWidget {
                background-color: #f5f5f5;
            }
        """
        )
        main_layout.addWidget(self.content_stack)

        # 创建界面
        self.create_interfaces()

        # 设置默认样式
        self.set_style()

    def create_sidebar(self) -> QWidget:
        """创建侧边栏"""
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(
            """
            QWidget {
                background-color: #001529;
                color: white;
            }
        """
        )

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)

        # 标题
        title = QLabel("Flow Farm")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; padding: 20px;")
        layout.addWidget(title)

        # 导航列表
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet(
            """
            QListWidget {
                background-color: transparent;
                border: none;
                color: white;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #002140;
            }
            QListWidget::item:selected {
                background-color: #1890ff;
            }
            QListWidget::item:hover {
                background-color: #002140;
            }
        """
        )

        # 添加导航项
        nav_items = ["🏠 仪表盘", "📱 设备管理", "⚙️ 任务管理"]
        for item_text in nav_items:
            item = QListWidgetItem(item_text)
            self.nav_list.addItem(item)

        self.nav_list.setCurrentRow(0)
        self.nav_list.currentRowChanged.connect(self.switch_interface)

        layout.addWidget(self.nav_list)
        layout.addStretch()

        return sidebar

    def create_interfaces(self):
        """创建所有界面"""
        self.home_interface = HomeInterface()
        self.device_interface = DeviceInterface()
        self.task_interface = TaskInterface()

        self.content_stack.addWidget(self.home_interface)
        self.content_stack.addWidget(self.device_interface)
        self.content_stack.addWidget(self.task_interface)

    def connect_signals(self):
        """连接信号"""
        # 主页信号
        if hasattr(self, "home_interface"):
            self.home_interface.device_manage_clicked.connect(
                lambda: self.switch_to_interface(1)
            )
            self.home_interface.start_work_clicked.connect(
                lambda: self.switch_to_interface(2)
            )

    def switch_interface(self, index: int):
        """切换界面"""
        self.content_stack.setCurrentIndex(index)

    def switch_to_interface(self, index: int):
        """切换到指定界面并更新导航"""
        self.nav_list.setCurrentRow(index)
        self.switch_interface(index)

    def set_style(self):
        """设置全局样式"""
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f0f2f5;
            }
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
            QPushButton:pressed {
                background-color: #096dd9;
            }
        """
        )


class FlowFarmApp:
    """Flow Farm 应用程序"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Flow Farm OneDragon")
        self.window = None

        # 设置字体
        font = QFont("Microsoft YaHei", 9)
        self.app.setFont(font)

    def create_window(self):
        """创建主窗口"""
        self.window = FlowFarmMainWindow()
        return self.window

    def run(self):
        """运行应用程序"""
        if not self.window:
            self.create_window()

        self.window.show()
        return self.app.exec()


def main():
    """主函数"""
    # 启用高DPI支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = FlowFarmApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
