"""
Flow Farm 员工客户端 - GUI基础窗口类
基于PySide6的现代化GUI基础框架和通用组件
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

import qtawesome as qta
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QFont, QIcon, QPalette, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFontDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QSystemTrayIcon,
    QTableWidget,
    QTabWidget,
    QTextEdit,
    QTimeEdit,
    QToolBar,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)


class ModernTheme:
    """现代化主题配置 - PySide6版本"""

    # 颜色配置
    COLORS = {
        "primary": "#2196F3",  # 主色调 - 蓝色
        "primary_dark": "#1976D2",  # 主色调深色
        "primary_light": "#BBDEFB",  # 主色调浅色
        "secondary": "#FF9800",  # 辅助色 - 橙色
        "secondary_dark": "#F57C00",  # 辅助色深色
        "secondary_light": "#FFE0B2",  # 辅助色浅色
        "success": "#4CAF50",  # 成功 - 绿色
        "success_dark": "#388E3C",  # 成功深色
        "success_light": "#C8E6C9",  # 成功浅色
        "warning": "#FF9800",  # 警告 - 橙色
        "warning_dark": "#F57C00",  # 警告深色
        "warning_light": "#FFE0B2",  # 警告浅色
        "error": "#F44336",  # 错误 - 红色
        "error_dark": "#D32F2F",  # 错误深色
        "error_light": "#FFCDD2",  # 错误浅色
        "info": "#2196F3",  # 信息 - 蓝色
        "info_dark": "#1976D2",  # 信息深色
        "info_light": "#BBDEFB",  # 信息浅色
        # 背景和表面颜色
        "background": "#FAFAFA",  # 主背景色
        "surface": "#FFFFFF",  # 表面色
        "surface_variant": "#F5F5F5",  # 表面变体
        "card": "#FFFFFF",  # 卡片背景
        "dialog": "#FFFFFF",  # 对话框背景
        # 边框和分割线
        "border": "#E0E0E0",  # 边框色
        "border_light": "#F0F0F0",  # 浅边框
        "border_dark": "#BDBDBD",  # 深边框
        "divider": "#E0E0E0",  # 分割线
        # 文本颜色
        "text_primary": "#212121",  # 主文本
        "text_secondary": "#757575",  # 次要文本
        "text_disabled": "#BDBDBD",  # 禁用文本
        "text_hint": "#9E9E9E",  # 提示文本
        "text_on_primary": "#FFFFFF",  # 主色上的文本
        "text_on_secondary": "#000000",  # 辅助色上的文本
        # 状态颜色
        "hover": "#F5F5F5",  # 悬停背景
        "pressed": "#EEEEEE",  # 按下背景
        "selected": "#E3F2FD",  # 选中背景
        "focus": "#2196F3",  # 焦点边框
        # 透明度变体
        "overlay": "rgba(0, 0, 0, 0.5)",  # 遮罩层
        "shadow": "rgba(0, 0, 0, 0.1)",  # 阴影
        "elevation": "rgba(0, 0, 0, 0.05)",  # 高度阴影
    }

    # 字体配置
    FONTS = {
        "title": QFont("Microsoft YaHei UI", 18, QFont.Weight.Bold),
        "heading": QFont("Microsoft YaHei UI", 14, QFont.Weight.Bold),
        "subheading": QFont("Microsoft YaHei UI", 12, QFont.Weight.DemiBold),
        "body": QFont("Microsoft YaHei UI", 10, QFont.Weight.Normal),
        "body_large": QFont("Microsoft YaHei UI", 11, QFont.Weight.Normal),
        "caption": QFont("Microsoft YaHei UI", 9, QFont.Weight.Normal),
        "button": QFont("Microsoft YaHei UI", 10, QFont.Weight.DemiBold),
        "code": QFont("Consolas", 9, QFont.Weight.Normal),
    }

    # 间距配置
    SPACING = {
        "tiny": 4,
        "small": 8,
        "medium": 16,
        "large": 24,
        "extra_large": 32,
        "huge": 48,
    }

    # 圆角配置
    RADIUS = {
        "small": 4,
        "medium": 8,
        "large": 12,
        "extra_large": 16,
    }

    # 阴影配置
    SHADOWS = {
        "none": "none",
        "small": "0px 1px 3px rgba(0, 0, 0, 0.12), 0px 1px 2px rgba(0, 0, 0, 0.24)",
        "medium": "0px 3px 6px rgba(0, 0, 0, 0.16), 0px 3px 6px rgba(0, 0, 0, 0.23)",
        "large": "0px 10px 20px rgba(0, 0, 0, 0.19), 0px 6px 6px rgba(0, 0, 0, 0.23)",
        "extra_large": "0px 14px 28px rgba(0, 0, 0, 0.25), 0px 10px 10px rgba(0, 0, 0, 0.22)",
    }

    @classmethod
    def get_stylesheet(cls) -> str:
        """获取全局样式表"""
        return f"""
        /* 全局样式 */
        QMainWindow {{
            background-color: {cls.COLORS['background']};
            color: {cls.COLORS['text_primary']};
        }}

        /* 通用Widget样式 */
        QWidget {{
            background-color: transparent;
            color: {cls.COLORS['text_primary']};
            font-family: "Microsoft YaHei UI";
        }}

        /* 按钮样式 */
        QPushButton {{
            background-color: {cls.COLORS['surface']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {cls.RADIUS['medium']}px;
            padding: {cls.SPACING['small']}px {cls.SPACING['medium']}px;
            font-weight: 600;
            color: {cls.COLORS['text_primary']};
        }}

        QPushButton:hover {{
            background-color: {cls.COLORS['hover']};
            border-color: {cls.COLORS['primary']};
        }}

        QPushButton:pressed {{
            background-color: {cls.COLORS['pressed']};
        }}

        QPushButton.primary {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['text_on_primary']};
            border: none;
        }}

        QPushButton.primary:hover {{
            background-color: {cls.COLORS['primary_dark']};
        }}

        QPushButton.secondary {{
            background-color: {cls.COLORS['secondary']};
            color: {cls.COLORS['text_on_secondary']};
            border: none;
        }}

        QPushButton.secondary:hover {{
            background-color: {cls.COLORS['secondary_dark']};
        }}

        QPushButton.success {{
            background-color: {cls.COLORS['success']};
            color: {cls.COLORS['text_on_primary']};
            border: none;
        }}

        QPushButton.warning {{
            background-color: {cls.COLORS['warning']};
            color: {cls.COLORS['text_on_secondary']};
            border: none;
        }}

        QPushButton.error {{
            background-color: {cls.COLORS['error']};
            color: {cls.COLORS['text_on_primary']};
            border: none;
        }}

        /* 输入框样式 */
        QLineEdit, QTextEdit, QComboBox {{
            background-color: {cls.COLORS['surface']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {cls.RADIUS['small']}px;
            padding: {cls.SPACING['small']}px;
            color: {cls.COLORS['text_primary']};
        }}

        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border-color: {cls.COLORS['primary']};
            border-width: 2px;
        }}

        /* 标签样式 */
        QLabel.title {{
            font-size: 18px;
            font-weight: bold;
            color: {cls.COLORS['text_primary']};
        }}

        QLabel.heading {{
            font-size: 14px;
            font-weight: bold;
            color: {cls.COLORS['text_primary']};
        }}

        QLabel.body {{
            font-size: 10px;
            color: {cls.COLORS['text_primary']};
        }}

        QLabel.caption {{
            font-size: 9px;
            color: {cls.COLORS['text_secondary']};
        }}

        /* 分组框样式 */
        QGroupBox {{
            background-color: {cls.COLORS['surface']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {cls.RADIUS['medium']}px;
            margin-top: {cls.SPACING['medium']}px;
            padding-top: {cls.SPACING['medium']}px;
            font-weight: bold;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {cls.SPACING['medium']}px;
            padding: 0 {cls.SPACING['small']}px 0 {cls.SPACING['small']}px;
            color: {cls.COLORS['text_primary']};
        }}

        /* 表格样式 */
        QTableWidget {{
            background-color: {cls.COLORS['surface']};
            alternate-background-color: {cls.COLORS['surface_variant']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {cls.RADIUS['medium']}px;
            gridline-color: {cls.COLORS['border_light']};
        }}

        QTableWidget::item {{
            padding: {cls.SPACING['small']}px;
            border: none;
        }}

        QTableWidget::item:selected {{
            background-color: {cls.COLORS['selected']};
        }}

        QHeaderView::section {{
            background-color: {cls.COLORS['surface_variant']};
            padding: {cls.SPACING['small']}px;
            border: none;
            border-bottom: 1px solid {cls.COLORS['border']};
            font-weight: bold;
        }}

        /* 选项卡样式 */
        QTabWidget::pane {{
            border: 1px solid {cls.COLORS['border']};
            border-radius: {cls.RADIUS['medium']}px;
            background-color: {cls.COLORS['surface']};
        }}

        QTabBar::tab {{
            background-color: {cls.COLORS['surface_variant']};
            border: 1px solid {cls.COLORS['border']};
            padding: {cls.SPACING['small']}px {cls.SPACING['medium']}px;
            margin-right: 2px;
        }}

        QTabBar::tab:selected {{
            background-color: {cls.COLORS['primary']};
            color: {cls.COLORS['text_on_primary']};
        }}

        QTabBar::tab:hover {{
            background-color: {cls.COLORS['hover']};
        }}

        /* 进度条样式 */
        QProgressBar {{
            border: 1px solid {cls.COLORS['border']};
            border-radius: {cls.RADIUS['small']}px;
            text-align: center;
            background-color: {cls.COLORS['surface_variant']};
        }}

        QProgressBar::chunk {{
            background-color: {cls.COLORS['primary']};
            border-radius: {cls.RADIUS['small']}px;
        }}

        /* 滚动条样式 */
        QScrollBar:vertical {{
            background-color: {cls.COLORS['surface_variant']};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {cls.COLORS['border_dark']};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {cls.COLORS['primary']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}

        /* 状态栏样式 */
        QStatusBar {{
            background-color: {cls.COLORS['surface']};
            border-top: 1px solid {cls.COLORS['border']};
            color: {cls.COLORS['text_secondary']};
        }}

        /* 菜单栏样式 */
        QMenuBar {{
            background-color: {cls.COLORS['surface']};
            border-bottom: 1px solid {cls.COLORS['border']};
        }}

        QMenuBar::item {{
            padding: {cls.SPACING['small']}px {cls.SPACING['medium']}px;
            background-color: transparent;
        }}

        QMenuBar::item:selected {{
            background-color: {cls.COLORS['hover']};
        }}

        QMenu {{
            background-color: {cls.COLORS['surface']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: {cls.RADIUS['small']}px;
        }}

        QMenu::item {{
            padding: {cls.SPACING['small']}px {cls.SPACING['medium']}px;
        }}

        QMenu::item:selected {{
            background-color: {cls.COLORS['hover']};
        }}
        """


class ComponentFactory:
    """PySide6组件工厂类"""

    @staticmethod
    def create_button(
        text: str,
        style: str = "default",
        icon: Optional[str] = None,
        tooltip: Optional[str] = None,
        callback: Optional[Callable] = None,
    ) -> QPushButton:
        """创建按钮"""
        button = QPushButton(text)

        # 设置样式
        if style in ["primary", "secondary", "success", "warning", "error"]:
            button.setProperty("class", style)

        # 设置图标
        if icon:
            button.setIcon(qta.icon(icon))

        # 设置工具提示
        if tooltip:
            button.setToolTip(tooltip)

        # 连接回调
        if callback:
            button.clicked.connect(callback)

        return button

    @staticmethod
    def create_label(
        text: str,
        style: str = "body",
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
    ) -> QLabel:
        """创建标签"""
        label = QLabel(text)
        label.setProperty("class", style)
        label.setAlignment(alignment)
        return label

    @staticmethod
    def create_input(
        placeholder: str = "",
        password: bool = False,
        readonly: bool = False,
    ) -> QLineEdit:
        """创建输入框"""
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        if password:
            input_field.setEchoMode(QLineEdit.EchoMode.Password)
        input_field.setReadOnly(readonly)
        return input_field

    @staticmethod
    def create_text_area(
        placeholder: str = "",
        readonly: bool = False,
    ) -> QTextEdit:
        """创建文本区域"""
        text_area = QTextEdit()
        text_area.setPlaceholderText(placeholder)
        text_area.setReadOnly(readonly)
        return text_area

    @staticmethod
    def create_combo_box(
        items: list = None,
        placeholder: str = "",
    ) -> QComboBox:
        """创建下拉框"""
        combo = QComboBox()
        if items:
            combo.addItems(items)
        if placeholder:
            combo.setPlaceholderText(placeholder)
        return combo

    @staticmethod
    def create_group_box(title: str, layout_type: str = "vertical") -> QGroupBox:
        """创建分组框"""
        group = QGroupBox(title)
        if layout_type == "vertical":
            group.setLayout(QVBoxLayout())
        elif layout_type == "horizontal":
            group.setLayout(QHBoxLayout())
        elif layout_type == "grid":
            group.setLayout(QGridLayout())
        return group

    @staticmethod
    def create_progress_bar(
        minimum: int = 0,
        maximum: int = 100,
        value: int = 0,
    ) -> QProgressBar:
        """创建进度条"""
        progress = QProgressBar()
        progress.setMinimum(minimum)
        progress.setMaximum(maximum)
        progress.setValue(value)
        return progress


class BaseWindow(QMainWindow):
    """GUI窗口基类 - PySide6版本"""

    # 信号定义
    window_closing = Signal()
    status_changed = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, title: str = "Flow Farm 员工客户端", size: tuple = (1200, 800)):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

        # 主题和组件工厂
        self.theme = ModernTheme()
        self.components = ComponentFactory()

        # 窗口设置
        self.setWindowTitle(title)
        self.resize(size[0], size[1])
        self.setMinimumSize(800, 600)

        # 设置窗口图标
        self.setWindowIcon(qta.icon("fa5s.leaf", color=self.theme.COLORS["primary"]))

        # 应用样式表
        self.setStyleSheet(self.theme.get_stylesheet())

        # 创建中央widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 初始化UI
        self.setup_ui()
        self.setup_layout()
        self.setup_connections()

        # 居中显示
        self.center_window()

        self.logger.info(f"基础窗口初始化完成: {title}")

    def center_window(self):
        """将窗口居中显示"""
        from PySide6.QtGui import QGuiApplication

        screen = QGuiApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)

    @abstractmethod
    def setup_ui(self):
        """设置UI组件 - 子类必须实现"""
        pass

    @abstractmethod
    def setup_layout(self):
        """设置布局 - 子类必须实现"""
        pass

    def setup_connections(self):
        """设置信号连接 - 子类可选择重写"""
        pass

    def show_message(
        self,
        title: str,
        message: str,
        message_type: str = "info",
        buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
    ) -> QMessageBox.StandardButton:
        """显示消息对话框"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(buttons)

        # 设置图标
        if message_type == "info":
            msg_box.setIcon(QMessageBox.Icon.Information)
        elif message_type == "warning":
            msg_box.setIcon(QMessageBox.Icon.Warning)
        elif message_type == "error":
            msg_box.setIcon(QMessageBox.Icon.Critical)
        elif message_type == "question":
            msg_box.setIcon(QMessageBox.Icon.Question)

        return msg_box.exec()

    def show_error(self, message: str, title: str = "错误"):
        """显示错误消息"""
        self.show_message(title, message, "error")
        self.error_occurred.emit(message)

    def show_warning(self, message: str, title: str = "警告"):
        """显示警告消息"""
        self.show_message(title, message, "warning")

    def show_info(self, message: str, title: str = "信息"):
        """显示信息消息"""
        self.show_message(title, message, "info")

    def show_question(
        self,
        message: str,
        title: str = "确认",
        buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Yes
        | QMessageBox.StandardButton.No,
    ) -> bool:
        """显示确认对话框"""
        result = self.show_message(title, message, "question", buttons)
        return result == QMessageBox.StandardButton.Yes

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.window_closing.emit()
        self.logger.info("窗口关闭")
        event.accept()

    def set_status(self, message: str):
        """设置状态栏消息"""
        if hasattr(self, "statusBar"):
            self.statusBar().showMessage(message)
        self.status_changed.emit(message)
        self.logger.debug(f"状态更新: {message}")


class WorkerThread(QThread):
    """工作线程基类"""

    finished = Signal()
    error = Signal(str)
    progress = Signal(int)
    result = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def run(self):
        """执行工作 - 子类必须实现"""
        pass

    def emit_error(self, error_message: str):
        """发射错误信号"""
        self.logger.error(error_message)
        self.error.emit(error_message)

    def emit_progress(self, progress: int):
        """发射进度信号"""
        self.progress.emit(progress)

    def emit_result(self, result: Any):
        """发射结果信号"""
        self.result.emit(result)
