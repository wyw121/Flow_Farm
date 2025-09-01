"""
Flow Farm 员工客户端 - 现代化主窗口示例
基于 PySide6 + qfluentwidgets 的现代化实现
展示 OneDragon 架构的应用
"""

import logging
from typing import Dict, Optional

# 兼容现有组件
import qtawesome as qta
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

# 现代化 Fluent Design 组件
from qfluentwidgets import (  # 基础容器; 按钮组件; 设置组件; 输入组件; 信息组件; 图标系统; 主题系统; 布局组件
    ComboBox,
    ComboBoxSettingCard,
    FluentIcon,
    HBoxLayout,
    IconWidget,
    InfoBar,
    InfoBarPosition,
    LineEdit,
    MessageBox,
    PrimaryPushButton,
    PushButton,
    SettingCard,
    SettingCardGroup,
    SwitchSettingCard,
    TextEdit,
    Theme,
    ToolButton,
    VBoxLayout,
    VerticalScrollInterface,
    qconfig,
    setTheme,
)

from .base_window import ComponentFactory, ModernTheme


class ModernMainWindow(VerticalScrollInterface):
    """现代化主窗口 - 基于 qfluentwidgets 架构"""

    # 自定义信号
    login_requested = Signal(str, str)  # username, password
    logout_requested = Signal()
    device_refresh_requested = Signal()
    task_started = Signal(str)  # task_type

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            object_name="modern_main_window",
            nav_text_cn="Flow Farm 工作台",
            nav_icon=FluentIcon.HOME,
        )

        # 初始化应用状态
        self.is_logged_in = False
        self.current_user = None
        self.server_connected = False

        # 设置日志
        self.logger = logging.getLogger(__name__)

        # 设置主题
        self.setup_theme()

        # 创建现代化界面
        self.setup_modern_ui()

        # 连接信号
        self.connect_signals()

        self.logger.info("现代化主窗口初始化完成")

    def setup_theme(self):
        """配置主题系统"""
        # 自动跟随系统主题
        qconfig.theme = Theme.AUTO

        # 设置窗口属性
        self.resize(1400, 900)
        self.setWindowTitle("Flow Farm 员工工作台")
        self.setWindowIcon(FluentIcon.HOME.icon())

    def setup_modern_ui(self):
        """创建现代化用户界面"""
        # 创建主要内容容器
        content_widget = QWidget()
        content_layout = VBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(30, 30, 30, 30)

        # 顶部快速操作区
        self.create_quick_actions(content_layout)

        # 设备管理区域
        self.create_device_management_section(content_layout)

        # 自动化设置区域
        self.create_automation_settings_section(content_layout)

        # 任务监控区域
        self.create_task_monitoring_section(content_layout)

        # 设置为主要内容
        self.setWidget(content_widget)

    def create_quick_actions(self, layout: VBoxLayout):
        """创建快速操作区域"""
        # 快速操作卡片组
        quick_group = SettingCardGroup("快速操作")

        # 登录状态卡片
        self.login_status_card = SettingCard(
            FluentIcon.PEOPLE, "登录状态", "当前未登录，请先登录"
        )

        # 添加登录按钮
        self.login_button = PrimaryPushButton("登录")
        self.login_button.clicked.connect(self.show_login_dialog)
        self.login_status_card.hBoxLayout.addWidget(self.login_button)

        quick_group.addSettingCard(self.login_status_card)

        # 设备刷新卡片
        self.device_refresh_card = SettingCard(
            FluentIcon.SYNC, "设备发现", "扫描和连接可用的自动化设备"
        )

        self.refresh_button = PushButton("刷新设备")
        self.refresh_button.clicked.connect(self.refresh_devices)
        self.device_refresh_card.hBoxLayout.addWidget(self.refresh_button)

        quick_group.addSettingCard(self.device_refresh_card)

        layout.addWidget(quick_group)

    def create_device_management_section(self, layout: VBoxLayout):
        """创建设备管理区域"""
        device_group = SettingCardGroup("设备管理")

        # 设备列表卡片
        self.device_list_card = SettingCard(
            FluentIcon.DEVICE_MANAGER, "连接设备", "0 台设备已连接"
        )

        # 设备管理按钮
        self.manage_devices_button = PushButton("管理设备")
        self.manage_devices_button.clicked.connect(self.show_device_manager)
        self.device_list_card.hBoxLayout.addWidget(self.manage_devices_button)

        device_group.addSettingCard(self.device_list_card)

        # 设备状态监控卡片
        self.device_status_card = SwitchSettingCard(
            FluentIcon.IOT, "设备监控", "实时监控设备状态和连接"
        )
        self.device_status_card.checkedChanged.connect(self.toggle_device_monitoring)

        device_group.addSettingCard(self.device_status_card)

        layout.addWidget(device_group)

    def create_automation_settings_section(self, layout: VBoxLayout):
        """创建自动化设置区域"""
        automation_group = SettingCardGroup("自动化设置")

        # 平台选择卡片
        self.platform_card = ComboBoxSettingCard(
            FluentIcon.APPLICATION,
            "目标平台",
            "选择要操作的社交媒体平台",
            texts=["抖音", "小红书", "微博"],
        )
        self.platform_card.comboBox.currentTextChanged.connect(self.on_platform_changed)

        automation_group.addSettingCard(self.platform_card)

        # 自动启动开关
        self.auto_start_card = SwitchSettingCard(
            FluentIcon.POWER_BUTTON, "自动启动", "程序启动时自动开始任务"
        )

        automation_group.addSettingCard(self.auto_start_card)

        # 操作频率设置
        self.frequency_card = ComboBoxSettingCard(
            FluentIcon.SPEED_OFF,
            "操作频率",
            "设置自动化操作的频率",
            texts=["低频率 (安全)", "中频率 (平衡)", "高频率 (快速)"],
        )

        automation_group.addSettingCard(self.frequency_card)

        layout.addWidget(automation_group)

    def create_task_monitoring_section(self, layout: VBoxLayout):
        """创建任务监控区域"""
        task_group = SettingCardGroup("任务监控")

        # 任务状态卡片
        self.task_status_card = SettingCard(
            FluentIcon.COMMAND_PROMPT, "任务状态", "当前无运行任务"
        )

        # 任务控制按钮
        self.start_task_button = PrimaryPushButton("开始任务")
        self.start_task_button.clicked.connect(self.start_automation_task)
        self.task_status_card.hBoxLayout.addWidget(self.start_task_button)

        self.stop_task_button = PushButton("停止任务")
        self.stop_task_button.clicked.connect(self.stop_automation_task)
        self.stop_task_button.setEnabled(False)
        self.task_status_card.hBoxLayout.addWidget(self.stop_task_button)

        task_group.addSettingCard(self.task_status_card)

        # 工作统计卡片
        self.work_stats_card = SettingCard(
            FluentIcon.CHART, "工作统计", "今日操作: 0 次"
        )

        self.view_stats_button = PushButton("查看详情")
        self.view_stats_button.clicked.connect(self.show_work_statistics)
        self.work_stats_card.hBoxLayout.addWidget(self.view_stats_button)

        task_group.addSettingCard(self.work_stats_card)

        layout.addWidget(task_group)

    def connect_signals(self):
        """连接信号和槽"""
        # 可以连接业务逻辑信号
        pass

    # 事件处理方法
    def show_login_dialog(self):
        """显示登录对话框"""
        # TODO: 创建现代化登录对话框
        self.show_info_message("登录功能", "登录对话框功能待实现")

    def refresh_devices(self):
        """刷新设备列表"""
        self.show_info_message("设备刷新", "正在扫描可用设备...")
        # TODO: 实现设备发现逻辑

    def show_device_manager(self):
        """显示设备管理器"""
        # TODO: 打开设备管理窗口
        self.show_info_message("设备管理", "设备管理器功能待实现")

    def toggle_device_monitoring(self, enabled: bool):
        """切换设备监控状态"""
        status = "已启用" if enabled else "已禁用"
        self.show_info_message("设备监控", f"设备监控{status}")

    def on_platform_changed(self, platform: str):
        """平台选择变更"""
        self.show_info_message("平台切换", f"已切换到: {platform}")

    def start_automation_task(self):
        """开始自动化任务"""
        self.start_task_button.setEnabled(False)
        self.stop_task_button.setEnabled(True)
        self.task_status_card.setContent("任务正在运行...")
        self.show_success_message("任务启动", "自动化任务已开始执行")

    def stop_automation_task(self):
        """停止自动化任务"""
        self.start_task_button.setEnabled(True)
        self.stop_task_button.setEnabled(False)
        self.task_status_card.setContent("当前无运行任务")
        self.show_info_message("任务停止", "自动化任务已停止")

    def show_work_statistics(self):
        """显示工作统计"""
        # TODO: 打开统计窗口
        self.show_info_message("工作统计", "统计详情功能待实现")

    # 信息反馈方法
    def show_success_message(self, title: str, message: str):
        """显示成功消息"""
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
        """显示信息消息"""
        InfoBar.info(
            title=title,
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=3000,
            parent=self,
        )

    def show_error_message(self, title: str, message: str):
        """显示错误消息"""
        InfoBar.error(
            title=title,
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=5000,
            parent=self,
        )

    def update_login_status(self, logged_in: bool, username: str = None):
        """更新登录状态"""
        if logged_in:
            self.is_logged_in = True
            self.current_user = username
            self.login_status_card.setContent(f"已登录: {username}")
            self.login_button.setText("注销")
            self.login_button.clicked.disconnect()
            self.login_button.clicked.connect(self.logout)
        else:
            self.is_logged_in = False
            self.current_user = None
            self.login_status_card.setContent("当前未登录，请先登录")
            self.login_button.setText("登录")
            self.login_button.clicked.disconnect()
            self.login_button.clicked.connect(self.show_login_dialog)

    def logout(self):
        """用户注销"""
        self.update_login_status(False)
        self.show_info_message("注销", "已成功注销")

    def update_device_count(self, count: int):
        """更新设备数量显示"""
        self.device_list_card.setContent(f"{count} 台设备已连接")

    def update_work_stats(self, stats: Dict):
        """更新工作统计"""
        today_count = stats.get("today_operations", 0)
        self.work_stats_card.setContent(f"今日操作: {today_count} 次")


# 兼容性适配器 - 保持与现有代码的兼容性
class MainWindow(ModernMainWindow):
    """
    主窗口兼容性适配器
    继承现代化窗口，保持现有接口
    """

    def __init__(self):
        super().__init__()

        # 为现有代码提供兼容性属性
        self.tab_widget = None  # 兼容性属性
        self.user_info_label = None
        self.connection_status_label = None
        self.progress_bar = None
        self.task_counter_label = None

        self.logger.info("兼容性主窗口初始化完成")

    # 兼容性方法 - 保持现有接口
    def setup_ui(self):
        """兼容性方法 - UI已在父类中设置"""
        pass

    def setup_layout(self):
        """兼容性方法 - 布局已在父类中设置"""
        pass

    def create_menu_bar(self):
        """兼容性方法 - 暂时保留空实现"""
        pass

    def create_status_bar(self):
        """兼容性方法 - 暂时保留空实现"""
        pass

    def import_contacts(self):
        """兼容性方法 - 通讯录导入"""
        self.show_info_message("通讯录导入", "通讯录导入功能待实现")
