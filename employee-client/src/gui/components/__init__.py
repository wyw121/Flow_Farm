"""
Flow Farm 员工客户端 - GUI组件模块
提供可复用的GUI组件，包括控制台集成和通讯录管理
"""

from .console_widget import ConsoleWidget
from .contacts_widget import ContactsAutoFollowWidget

__all__ = ["ConsoleWidget", "ContactsAutoFollowWidget"]
