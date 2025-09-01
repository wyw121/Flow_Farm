"""
Flow Farm GUI 框架迁移示例
展示如何从传统 PySide6 迁移到 qfluentwidgets
"""

import logging
import sys
from pathlib import Path

# 确保导入路径正确
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))

try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

    # 检查 qfluentwidgets 可用性
    try:
        # 尝试导入 PySide6-Fluent-Widgets (实际可用的包)
        from qfluentwidgets import (
            FluentIcon,
            InfoBar,
            InfoBarPosition,
            PrimaryPushButton,
            PushButton,
            SettingCard,
            SettingCardGroup,
            Theme,
            VerticalScrollInterface,
            qconfig,
            setTheme,
        )

        QFLUENTWIDGETS_AVAILABLE = True
        print("✅ qfluentwidgets 可用 - 使用现代化界面")
    except ImportError:
        try:
            # 尝试备用导入路径
            from PySide6_Fluent_Widgets.qfluentwidgets import (
                FluentIcon,
                InfoBar,
                InfoBarPosition,
                PrimaryPushButton,
                PushButton,
                SettingCard,
                SettingCardGroup,
                Theme,
                VerticalScrollInterface,
                qconfig,
                setTheme,
            )

            QFLUENTWIDGETS_AVAILABLE = True
            print("✅ PySide6-Fluent-Widgets 可用 - 使用现代化界面")
        except ImportError as e:
            print(f"❌ qfluentwidgets 不可用: {e}")
            print("📦 请安装: pip install PySide6-Fluent-Widgets")
            QFLUENTWIDGETS_AVAILABLE = False

        # 使用传统组件作为回退
        from PySide6.QtWidgets import QFrame, QLabel, QPushButton

except ImportError as e:
    print(f"❌ PySide6 导入失败: {e}")
    print("📦 请安装: pip install PySide6==6.8.0.2")
    sys.exit(1)


class DemoMainWindow(QMainWindow):
    """GUI框架迁移演示窗口"""

    def __init__(self):
        super().__init__()

        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # 窗口基本设置
        self.setWindowTitle("Flow Farm GUI 框架演示")
        self.setGeometry(100, 100, 1200, 800)

        # 根据可用性选择界面风格
        if QFLUENTWIDGETS_AVAILABLE:
            self.setup_modern_ui()
        else:
            self.setup_fallback_ui()

        self.logger.info("演示窗口初始化完成")

    def setup_modern_ui(self):
        """设置现代化界面 (qfluentwidgets)"""
        self.logger.info("使用 qfluentwidgets 现代化界面")

        # 设置主题
        qconfig.theme = Theme.AUTO

        # 创建中央容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 演示组件组
        demo_group = SettingCardGroup("GUI 框架对比演示")

        # 现代化按钮卡片
        modern_card = SettingCard(
            FluentIcon.PALETTE, "现代化组件", "使用 qfluentwidgets 的美观组件"
        )

        modern_button = PrimaryPushButton("体验现代界面")
        modern_button.clicked.connect(self.show_modern_demo)
        modern_card.hBoxLayout.addWidget(modern_button)

        demo_group.addSettingCard(modern_card)

        # 传统组件对比卡片
        traditional_card = SettingCard(
            FluentIcon.DEVELOPER_TOOLS, "传统组件", "原生 PySide6 组件对比"
        )

        traditional_button = PushButton("查看传统界面")
        traditional_button.clicked.connect(self.show_traditional_demo)
        traditional_card.hBoxLayout.addWidget(traditional_button)

        demo_group.addSettingCard(traditional_card)

        # 框架信息卡片
        info_card = SettingCard(
            FluentIcon.INFO, "框架信息", "OneDragon 项目使用的现代化架构"
        )

        info_button = PushButton("技术详情")
        info_button.clicked.connect(self.show_framework_info)
        info_card.hBoxLayout.addWidget(info_button)

        demo_group.addSettingCard(info_card)

        layout.addWidget(demo_group)

        # 添加弹性空间
        layout.addStretch()

        # 显示成功消息
        QTimer.singleShot(
            1000,
            lambda: self.show_success_message(
                "现代化界面已加载", "体验 OneDragon 风格的美观组件"
            ),
        )

    def setup_fallback_ui(self):
        """设置回退界面 (传统 PySide6)"""
        self.logger.info("使用传统 PySide6 界面作为回退")

        # 创建中央容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 标题
        title_label = QLabel("Flow Farm GUI 框架演示 (回退模式)")
        title_label.setStyleSheet(
            """
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
            }
        """
        )
        layout.addWidget(title_label)

        # 说明文本
        info_label = QLabel(
            "当前使用传统 PySide6 组件。\n"
            "要体验现代化界面，请安装 qfluentwidgets:\n"
            "pip install qfluentwidgets==1.7.0"
        )
        info_label.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
        """
        )
        layout.addWidget(info_label)

        # 传统按钮示例
        traditional_button = QPushButton("传统 PySide6 按钮")
        traditional_button.setStyleSheet(
            """
            QPushButton {
                font-size: 16px;
                padding: 10px 20px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        traditional_button.clicked.connect(self.show_traditional_demo)
        layout.addWidget(traditional_button)

        # 添加弹性空间
        layout.addStretch()

    def show_modern_demo(self):
        """显示现代化组件演示"""
        if QFLUENTWIDGETS_AVAILABLE:
            self.show_success_message(
                "现代化组件", "这是使用 qfluentwidgets 的美观按钮，具有阴影和动画效果"
            )
        else:
            self.show_fallback_message("需要安装 qfluentwidgets 才能体验现代化组件")

    def show_traditional_demo(self):
        """显示传统组件演示"""
        if QFLUENTWIDGETS_AVAILABLE:
            self.show_info_message(
                "传统组件", "这是原生 PySide6 组件，功能完整但缺乏现代美感"
            )
        else:
            self.show_fallback_message("当前正在使用传统 PySide6 组件")

    def show_framework_info(self):
        """显示框架信息"""
        info_text = (
            "OneDragon 项目使用的技术栈:\n"
            "• PySide6 6.8.0.2 (Qt6 基础)\n"
            "• qfluentwidgets 1.7.0 (Fluent Design)\n"
            "• VerticalScrollInterface (滚动容器)\n"
            "• FluentIcon (图标系统)\n"
            "• 自动主题切换 (深色/浅色)\n"
            "• 动画和阴影效果"
        )

        if QFLUENTWIDGETS_AVAILABLE:
            self.show_info_message("框架技术详情", info_text)
        else:
            self.show_fallback_message(f"框架信息:\n{info_text}")

    # 消息显示方法
    def show_success_message(self, title: str, message: str):
        """显示成功消息 (现代化)"""
        InfoBar.success(
            title=title,
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=3000,
            parent=self,
        )

    def show_info_message(self, title: str, message: str):
        """显示信息消息 (现代化)"""
        InfoBar.info(
            title=title,
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=4000,
            parent=self,
        )

    def show_fallback_message(self, message: str):
        """回退消息显示 (传统)"""
        self.logger.info(f"消息: {message}")
        # 可以使用 QMessageBox 或状态栏
        self.statusBar().showMessage(message, 3000)


def main():
    """主函数"""
    # 创建应用程序
    app = QApplication(sys.argv)

    # 设置应用程序属性
    app.setApplicationName("Flow Farm GUI Demo")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Flow Farm")

    # 创建并显示主窗口
    window = DemoMainWindow()
    window.show()

    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
