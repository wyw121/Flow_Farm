"""
主应用窗口 - 基于 OneDragon 架构
模仿 OneDragon 的 AppWindow 设计模式
"""

import logging
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    FluentIcon,
    MSFluentWindow,
    NavigationItemPosition,
    Theme,
    qconfig,
    setFont,
    setTheme,
)

from .base_interface import BaseInterface


class FlowFarmAppWindow(MSFluentWindow):
    """
    Flow Farm 主应用窗口
    基于 OneDragon 的 AppWindow 架构设计
    """

    # 窗口信号
    window_closed = Signal()
    navigation_changed = Signal(str)

    def __init__(self, parent=None):
        """初始化主窗口"""
        super().__init__(parent)

        # 日志记录器
        self.logger = logging.getLogger(self.__class__.__name__)

        # 界面管理
        self.interfaces: Dict[str, BaseInterface] = {}
        self.current_interface: Optional[BaseInterface] = None

        # 初始化窗口
        self._init_window()
        self._init_navigation()
        self._setup_theme()

        self.logger.info("Flow Farm 主窗口初始化完成")

    def _init_window(self):
        """初始化窗口设置"""
        # 窗口基本设置
        self.setWindowTitle("Flow Farm - 流量农场工作台")
        self.setWindowIcon(QIcon("assets/logo.ico"))  # 如果有图标的话

        # 窗口大小和位置 - 模仿 OneDragon 的比例
        self.resize(1095, 730)  # 3:2比例，与 OneDragon 保持一致

        # 居中显示
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            w, h = geometry.width(), geometry.height()
            self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        # 设置对象名称用于样式
        self.setObjectName("FlowFarmWindow")

    def _init_navigation(self):
        """初始化导航界面"""
        # 连接导航变化信号
        self.stackedWidget.currentChanged.connect(self._on_navigation_changed)

        self.logger.debug("导航系统初始化完成")

    def _setup_theme(self):
        """设置主题"""
        # 设置默认主题
        setTheme(Theme.AUTO)  # 自动主题，跟随系统

        # 设置字体 - 模仿 OneDragon 的字体设置
        setFont(QFont("Microsoft YaHei", 9))

        self.logger.debug("主题设置完成")

    def add_sub_interface(
        self,
        interface: BaseInterface,
        position: NavigationItemPosition = NavigationItemPosition.TOP,
    ):
        """
        添加子界面，模仿 OneDragon 的 add_sub_interface 方法

        Args:
            interface: 要添加的界面
            position: 导航位置
        """
        # 获取界面标识
        object_name = interface.objectName()
        nav_text = interface.get_nav_text()
        nav_icon = interface.get_nav_icon() or FluentIcon.HOME

        # 添加到导航
        self.addSubInterface(
            interface=interface, icon=nav_icon, text=nav_text, position=position
        )

        # 保存界面引用
        self.interfaces[object_name] = interface

        self.logger.debug(f"添加子界面: {nav_text} ({object_name})")

    def _on_navigation_changed(self, index: int):
        """导航变化处理"""
        # 获取当前界面
        current_widget = self.stackedWidget.widget(index)

        if isinstance(current_widget, BaseInterface):
            # 处理之前的界面
            if self.current_interface:
                self.current_interface.on_interface_hidden()

            # 设置当前界面
            self.current_interface = current_widget
            self.current_interface.on_interface_shown()

            # 发射导航变化信号
            self.navigation_changed.emit(current_widget.objectName())

            self.logger.debug(f"导航切换到: {current_widget.get_nav_text()}")

    def switch_to_interface(self, interface_name: str):
        """
        切换到指定界面

        Args:
            interface_name: 界面对象名称
        """
        if interface_name in self.interfaces:
            interface = self.interfaces[interface_name]
            self.stackedWidget.setCurrentWidget(interface)
        else:
            self.logger.warning(f"界面不存在: {interface_name}")

    def get_current_interface(self) -> Optional[BaseInterface]:
        """获取当前界面"""
        return self.current_interface

    def get_interface(self, interface_name: str) -> Optional[BaseInterface]:
        """
        获取指定界面

        Args:
            interface_name: 界面对象名称

        Returns:
            界面实例或None
        """
        return self.interfaces.get(interface_name)

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.logger.info("Flow Farm 窗口正在关闭...")

        # 通知所有界面即将关闭
        for interface in self.interfaces.values():
            if hasattr(interface, "on_window_closing"):
                interface.on_window_closing()

        # 发射关闭信号
        self.window_closed.emit()

        # 调用父类关闭事件
        super().closeEvent(event)

        self.logger.info("Flow Farm 窗口已关闭")
