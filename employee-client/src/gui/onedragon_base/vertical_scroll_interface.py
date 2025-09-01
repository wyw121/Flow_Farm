"""
垂直滚动界面 - 基于 OneDragon 架构
模仿 OneDragon 的 VerticalScrollInterface 设计
"""

from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import FluentIconBase, SingleDirectionScrollArea

from .base_interface import BaseInterface


class VerticalScrollInterface(BaseInterface):
    """
    垂直滚动界面，模仿 OneDragon 的 VerticalScrollInterface
    提供可滚动的内容区域
    """

    def __init__(
        self,
        parent=None,
        content_widget: QWidget = None,
        object_name: str = "vertical_scroll_interface",
        nav_text_cn: str = "滚动界面",
        nav_icon: Union[FluentIconBase, str] = None,
    ):
        """
        初始化垂直滚动界面

        Args:
            parent: 父组件
            content_widget: 内容组件
            object_name: 对象名称
            nav_text_cn: 导航显示文本
            nav_icon: 导航图标
        """
        super().__init__(parent, object_name, nav_text_cn, nav_icon)

        # 创建滚动区域
        self.scroll_area = SingleDirectionScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.scroll_area)

        # 设置内容组件
        if content_widget:
            self.set_content_widget(content_widget)
        else:
            # 创建默认内容组件
            self.content_widget = self.create_default_content()
            self.scroll_area.setWidget(self.content_widget)

    def create_default_content(self) -> QWidget:
        """
        创建默认内容组件
        子类可重写此方法自定义内容
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 添加一个弹性空间
        layout.addStretch()

        return widget

    def set_content_widget(self, widget: QWidget):
        """设置内容组件"""
        self.content_widget = widget
        self.scroll_area.setWidget(widget)

    def add_widget(self, widget: QWidget, alignment: Qt.AlignmentFlag = None):
        """
        向内容区域添加组件

        Args:
            widget: 要添加的组件
            alignment: 对齐方式
        """
        if hasattr(self.content_widget, "layout") and self.content_widget.layout():
            layout = self.content_widget.layout()
            if alignment:
                layout.addWidget(widget, alignment=alignment)
            else:
                layout.addWidget(widget)
        else:
            self.logger.warning("内容组件没有布局管理器，无法添加组件")

    def add_stretch(self, stretch: int = 0):
        """向内容区域添加弹性空间"""
        if hasattr(self.content_widget, "layout") and self.content_widget.layout():
            layout = self.content_widget.layout()
            layout.addStretch(stretch)

    def clear_content(self):
        """清空内容区域"""
        if hasattr(self.content_widget, "layout") and self.content_widget.layout():
            layout = self.content_widget.layout()
            # 移除所有子组件
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

    def get_content_layout(self) -> QVBoxLayout:
        """获取内容布局"""
        if hasattr(self.content_widget, "layout"):
            return self.content_widget.layout()
        return None
