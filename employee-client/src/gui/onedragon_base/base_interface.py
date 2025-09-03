"""
基础界面类 - 基于 OneDragon 架构
模仿 OneDragon 的 BaseInterface 设计模式
"""

import logging
from typing import Optional, Union

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget
from qfluentwidgets import FluentIconBase, InfoBar, InfoBarPosition


class BaseInterface(QWidget):
    """
    基础界面类，模仿 OneDragon 的 BaseInterface
    所有界面组件的基类，提供通用功能
    """

    # 界面导航信号
    navigation_changed = Signal(str)  # 导航变化信号

    def __init__(
        self,
        parent=None,
        object_name: str = "base_interface",
        nav_text_cn: str = "基础界面",
        nav_icon: Union[FluentIconBase, str] = None,
    ):
        """
        初始化基础界面

        Args:
            parent: 父组件
            object_name: 对象名称，用于样式和识别
            nav_text_cn: 导航显示的中文文本
            nav_icon: 导航图标
        """
        super().__init__(parent)

        # 设置对象名称
        self.setObjectName(object_name)

        # 界面元数据
        self.nav_text_cn = nav_text_cn
        self.nav_icon = nav_icon

        # 日志记录器
        self.logger = logging.getLogger(self.__class__.__name__)

        # 初始化界面
        self._init_interface()

    def _init_interface(self):
        """初始化界面，子类可重写"""
        self.logger.debug(f"初始化界面: {self.nav_text_cn}")

        # 设置默认属性
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

    def show_info_bar(
        self,
        title: str,
        content: str = "",
        info_type: str = "info",
        duration: int = 3000,
    ):
        """
        显示信息条，模仿 OneDragon 的信息提示方式

        Args:
            title: 信息标题
            content: 信息内容
            info_type: 信息类型 ("info", "success", "warning", "error")
            duration: 显示持续时间(毫秒)
        """
        # 映射信息类型
        type_mapping = {
            "info": InfoBar.info,
            "success": InfoBar.success,
            "warning": InfoBar.warning,
            "error": InfoBar.error,
        }

        info_func = type_mapping.get(info_type, InfoBar.info)

        info_func(
            title=title,
            content=content,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=duration,
            parent=self,
        )

    def on_interface_shown(self):
        """
        界面显示时调用，模仿 OneDragon 的生命周期管理
        子类可重写此方法进行界面激活时的操作
        """
        self.logger.debug(f"界面已显示: {self.nav_text_cn}")

    def on_interface_hidden(self):
        """
        界面隐藏时调用，模仿 OneDragon 的生命周期管理
        子类可重写此方法进行界面隐藏时的清理操作
        """
        self.logger.debug(f"界面已隐藏: {self.nav_text_cn}")

    def get_nav_text(self) -> str:
        """获取导航文本"""
        return self.nav_text_cn

    def get_nav_icon(self) -> Union[FluentIconBase, str, None]:
        """获取导航图标"""
        return self.nav_icon
