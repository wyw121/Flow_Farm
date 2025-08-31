"""
Flow Farm 员工客户端 - 主窗口
基于PySide6的现代化主窗口实现，包含设备管理和功能界面
"""

import logging
from typing import Dict

import qtawesome as qta
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .base_window import BaseWindow, ComponentFactory
from .views.device_view import DeviceManagementView


class MainWindow(BaseWindow):
    """员工客户端主窗口 - PySide6版本"""

    # 自定义信号
    login_requested = Signal(str, str)  # username, password
    logout_requested = Signal()
    device_refresh_requested = Signal()
    task_started = Signal(str)  # task_type

    def __init__(self):
        # 应用程序状态
        self.is_logged_in = False
        self.current_user = None
        self.server_connected = False

        # 视图组件
        self.device_view = None
        self.function_view = None

        # UI组件
        self.tab_widget = None
        self.user_info_label = None
        self.login_button = None
        self.connection_status_label = None
        self.progress_bar = None
        self.task_counter_label = None

        # 初始化窗口
        super().__init__(title="Flow Farm 员工工作台", size=(1400, 900))

        self.logger.info("主窗口初始化完成")

    def setup_ui(self):
        """设置UI组件"""
        # 创建菜单栏
        self.create_menu_bar()

        # 创建状态栏
        self.create_status_bar()

    def setup_layout(self):
        """设置主窗口布局"""
        # 主布局
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建顶部工具栏
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)

        # 创建主内容区域
        content_widget = self.create_main_content()
        main_layout.addWidget(content_widget)

        # 初始化为登录界面
        self.show_login_interface()

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        # 导入数据
        import_action = QAction(qta.icon("fa5s.file-import"), "导入通讯录(&I)", self)
        import_action.setShortcut(QKeySequence.Open)
        import_action.triggered.connect(self.import_contacts)
        file_menu.addAction(import_action)

        # 导出数据
        export_action = QAction(qta.icon("fa5s.file-export"), "导出数据(&E)", self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        # 退出
        exit_action = QAction(qta.icon("fa5s.sign-out-alt"), "退出(&Q)", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 设备菜单
        device_menu = menubar.addMenu("设备(&D)")

        # 刷新设备
        refresh_action = QAction(qta.icon("fa5s.sync"), "刷新设备(&R)", self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.triggered.connect(self.refresh_devices)
        device_menu.addAction(refresh_action)

        # 连接所有设备
        connect_all_action = QAction(qta.icon("fa5s.link"), "连接所有设备(&C)", self)
        connect_all_action.triggered.connect(self.connect_all_devices)
        device_menu.addAction(connect_all_action)

        # 断开所有设备
        disconnect_all_action = QAction(
            qta.icon("fa5s.unlink"), "断开所有设备(&D)", self
        )
        disconnect_all_action.triggered.connect(self.disconnect_all_devices)
        device_menu.addAction(disconnect_all_action)

        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")

        # 设置
        settings_action = QAction(qta.icon("fa5s.cog"), "设置(&S)", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)

        # 日志查看器
        logs_action = QAction(qta.icon("fa5s.file-alt"), "查看日志(&L)", self)
        logs_action.triggered.connect(self.show_logs)
        tools_menu.addAction(logs_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        # 用户手册
        manual_action = QAction(qta.icon("fa5s.book"), "用户手册(&M)", self)
        manual_action.triggered.connect(self.show_manual)
        help_menu.addAction(manual_action)

        # 关于
        about_action = QAction(qta.icon("fa5s.info-circle"), "关于(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self) -> QWidget:
        """创建顶部工具栏"""
        toolbar_widget = QWidget()
        toolbar_widget.setFixedHeight(60)
        toolbar_widget.setStyleSheet(
            f"""
            QWidget {{
                background-color: {self.theme.COLORS['surface']};
                border-bottom: 1px solid {self.theme.COLORS['border']};
            }}
        """
        )

        layout = QHBoxLayout(toolbar_widget)
        layout.setContentsMargins(
            self.theme.SPACING["medium"],
            self.theme.SPACING["small"],
            self.theme.SPACING["medium"],
            self.theme.SPACING["small"],
        )

        # 左侧：标题和用户信息
        left_widget = QWidget()
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # 应用图标和标题
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel()
        icon_label.setPixmap(
            qta.icon("fa5s.leaf", color=self.theme.COLORS["primary"]).pixmap(32, 32)
        )
        title_layout.addWidget(icon_label)

        title_label = self.components.create_label("Flow Farm 员工工作台", "title")
        title_layout.addWidget(title_label)

        left_layout.addWidget(title_widget)
        left_layout.addSpacing(self.theme.SPACING["large"])

        # 用户信息
        self.user_info_label = self.components.create_label("未登录", "body")
        self.user_info_label.setStyleSheet(
            f"color: {self.theme.COLORS['text_secondary']}"
        )
        left_layout.addWidget(self.user_info_label)

        left_layout.addStretch()
        layout.addWidget(left_widget)

        # 右侧：操作按钮
        right_widget = QWidget()
        right_layout = QHBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # 连接状态指示器
        self.connection_status_label = self.components.create_label("● 未连接", "body")
        self.connection_status_label.setStyleSheet(
            f"color: {self.theme.COLORS['error']}"
        )
        right_layout.addWidget(self.connection_status_label)

        right_layout.addSpacing(self.theme.SPACING["medium"])

        # 设置按钮
        settings_button = self.components.create_button(
            "设置", "default", "fa5s.cog", "打开设置", self.show_settings
        )
        right_layout.addWidget(settings_button)

        # 登录/登出按钮
        self.login_button = self.components.create_button(
            "登录", "primary", "fa5s.sign-in-alt", "登录到服务器", self.toggle_login
        )
        right_layout.addWidget(self.login_button)

        layout.addWidget(right_widget)

        return toolbar_widget

    def create_main_content(self) -> QWidget:
        """创建主内容区域"""
        # 创建选项卡控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabsClosable(False)

        # 添加选项卡
        self.add_tabs()

        return self.tab_widget

    def add_tabs(self):
        """添加选项卡"""
        # 设备管理选项卡
        device_widget = QWidget()
        self.device_view = DeviceManagementView(device_widget, self)
        device_layout = QVBoxLayout(device_widget)
        device_layout.addWidget(self.device_view)
        device_layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget.addTab(device_widget, qta.icon("fa5s.mobile-alt"), "设备管理")

        # 功能操作选项卡
        function_widget = QWidget()
        function_layout = QVBoxLayout(function_widget)
        function_layout.addWidget(QLabel("功能操作模块 - 待实现"))
        function_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_widget.addTab(self.function_view, qta.icon("fa5s.tasks"), "功能操作")

        # 数据统计选项卡
        stats_widget = self.create_stats_view()
        self.tab_widget.addTab(stats_widget, qta.icon("fa5s.chart-bar"), "数据统计")

        # 设置默认选项卡
        self.tab_widget.setCurrentIndex(0)

    def create_stats_view(self) -> QWidget:
        """创建统计视图"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 标题
        title_label = self.components.create_label("工作数据统计", "heading")
        layout.addWidget(title_label)

        # 统计卡片网格
        stats_grid = QGridLayout()

        # 今日任务完成数
        today_card = self.create_stat_card(
            "今日完成", "0", "fa5s.check-circle", self.theme.COLORS["success"]
        )
        stats_grid.addWidget(today_card, 0, 0)

        # 总任务数
        total_card = self.create_stat_card(
            "总完成数", "0", "fa5s.tasks", self.theme.COLORS["primary"]
        )
        stats_grid.addWidget(total_card, 0, 1)

        # 在线设备数
        online_card = self.create_stat_card(
            "在线设备", "0/0", "fa5s.mobile-alt", self.theme.COLORS["info"]
        )
        stats_grid.addWidget(online_card, 0, 2)

        # 成功率
        success_card = self.create_stat_card(
            "成功率", "0%", "fa5s.percentage", self.theme.COLORS["warning"]
        )
        stats_grid.addWidget(success_card, 0, 3)

        layout.addLayout(stats_grid)
        layout.addStretch()

        return widget

    def create_stat_card(
        self, title: str, value: str, icon: str, color: str
    ) -> QWidget:
        """创建统计卡片"""
        card = QGroupBox()
        card.setFixedHeight(120)
        card.setStyleSheet(
            f"""
            QGroupBox {{
                border: 1px solid {self.theme.COLORS['border']};
                border-radius: {self.theme.RADIUS['medium']}px;
                background-color: {self.theme.COLORS['surface']};
                margin: {self.theme.SPACING['small']}px;
            }}
        """
        )

        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 图标
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(icon, color=color).pixmap(32, 32))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # 数值
        value_label = self.components.create_label(value, "title")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet(f"color: {color}")
        layout.addWidget(value_label)

        # 标题
        title_label = self.components.create_label(title, "caption")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        return card

    def create_status_bar(self):
        """创建状态栏"""
        status_bar = self.statusBar()

        # 状态消息
        status_bar.showMessage("就绪")

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedWidth(200)
        status_bar.addPermanentWidget(self.progress_bar)

        # 任务计数器
        self.task_counter_label = QLabel("任务: 0/0")
        status_bar.addPermanentWidget(self.task_counter_label)

    def show_login_interface(self):
        """显示登录界面"""
        if self.is_logged_in:
            return

        # 禁用功能选项卡
        if self.tab_widget:
            for i in range(1, self.tab_widget.count()):
                self.tab_widget.setTabEnabled(i, False)

        # 显示登录提示
        self.set_status("请先登录到服务器")

    def show_main_interface(self):
        """显示主界面"""
        if not self.is_logged_in:
            return

        # 启用所有选项卡
        if self.tab_widget:
            for i in range(self.tab_widget.count()):
                self.tab_widget.setTabEnabled(i, True)

        # 更新状态
        self.set_status("已连接到服务器")

    def toggle_login(self):
        """切换登录状态"""
        if self.is_logged_in:
            self.logout()
        else:
            self.show_login_dialog()

    def show_login_dialog(self):
        """显示登录对话框"""
        # 暂时使用简单的输入对话框，后续可以创建专门的登录对话框
        from PySide6.QtWidgets import QInputDialog

        username, ok1 = QInputDialog.getText(self, "登录", "用户名:")
        if ok1 and username:
            password, ok2 = QInputDialog.getText(
                self, "登录", "密码:", QInputDialog.EchoMode.Password
            )
            if ok2 and password:
                self.login_requested.emit(username, password)

    def login_success(self, user_info: dict):
        """登录成功处理"""
        self.is_logged_in = True
        self.current_user = user_info

        # 更新UI
        self.user_info_label.setText(f"欢迎，{user_info.get('username', '用户')}")
        self.login_button.setText("登出")
        self.login_button.setIcon(qta.icon("fa5s.sign-out-alt"))

        # 更新连接状态
        self.connection_status_label.setText("● 已连接")
        self.connection_status_label.setStyleSheet(
            f"color: {self.theme.COLORS['success']}"
        )

        # 显示主界面
        self.show_main_interface()

        self.logger.info(f"用户 {user_info.get('username')} 登录成功")

    def logout(self):
        """退出登录"""
        if self.show_question("确认退出", "确定要退出登录吗？"):
            self.is_logged_in = False
            self.current_user = None

            # 更新UI
            self.user_info_label.setText("未登录")
            self.login_button.setText("登录")
            self.login_button.setIcon(qta.icon("fa5s.sign-in-alt"))

            # 更新连接状态
            self.connection_status_label.setText("● 未连接")
            self.connection_status_label.setStyleSheet(
                f"color: {self.theme.COLORS['error']}"
            )

            # 显示登录界面
            self.show_login_interface()

            self.logout_requested.emit()
            self.logger.info("用户退出登录")

    def refresh_devices(self):
        """刷新设备列表"""
        if self.device_view:
            self.device_view.refresh_devices()
        self.device_refresh_requested.emit()

    def connect_all_devices(self):
        """连接所有设备"""
        if self.device_view:
            self.device_view.connect_all_devices()

    def disconnect_all_devices(self):
        """断开所有设备"""
        if self.device_view:
            self.device_view.disconnect_all_devices()

    def import_contacts(self):
        """导入通讯录"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择通讯录文件",
            "",
            "文本文件 (*.txt);;CSV文件 (*.csv);;JSON文件 (*.json)",
        )

        if file_path and self.function_view:
            self.function_view.load_contacts_file(file_path)

    def export_data(self):
        """导出数据"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出数据", "", "CSV文件 (*.csv);;JSON文件 (*.json)"
        )

        if file_path:
            # 实现数据导出逻辑
            self.show_info("导出成功", f"数据已导出到: {file_path}")

    def show_settings(self):
        """显示设置窗口"""
        self.show_info("设置", "设置功能正在开发中...")

    def show_logs(self):
        """显示日志查看器"""
        self.show_info("日志", "日志查看器功能正在开发中...")

    def show_manual(self):
        """显示用户手册"""
        self.show_info("用户手册", "用户手册功能正在开发中...")

    def show_about(self):
        """显示关于对话框"""
        self.show_info(
            "关于 Flow Farm",
            "Flow Farm 员工客户端 v1.0.0\n\n"
            "企业级计费自动化流量农场系统\n"
            "员工工作台 - 基于PySide6开发\n\n"
            "Copyright © 2024 Flow Farm Team",
        )

    def update_progress(self, current: int, total: int):
        """更新进度显示"""
        if total > 0:
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
            self.task_counter_label.setText(f"任务: {current}/{total}")
        else:
            self.progress_bar.setVisible(False)
            self.task_counter_label.setText("任务: 0/0")

    def setup_connections(self):
        """设置信号连接"""
        # 连接设备视图信号
        if self.device_view:
            # 这些信号将在视图类中定义
            pass

        # 连接功能视图信号
        if self.function_view:
            # 这些信号将在视图类中定义
            pass

    def on_device_selected(self, device_info: dict):
        """设备选择事件处理"""
        self.logger.debug(f"选择设备: {device_info}")

    def on_device_status_changed(self, device_id: str, status: str):
        """设备状态变化事件处理"""
        self.logger.debug(f"设备 {device_id} 状态变更为: {status}")

    def on_task_started(self, task_type: str):
        """任务开始事件处理"""
        self.set_status(f"正在执行: {task_type}")
        self.task_started.emit(task_type)

    def on_task_completed(self, task_type: str, success: bool):
        """任务完成事件处理"""
        if success:
            self.set_status(f"{task_type} 执行完成")
        else:
            self.set_status(f"{task_type} 执行失败")

        self.update_progress(0, 0)  # 隐藏进度条

    def get_user_info(self) -> dict:
        """获取当前用户信息"""
        return {
            "username": (
                self.current_user.get("username", "") if self.current_user else ""
            ),
            "is_logged_in": self.is_logged_in,
            "server_connected": self.server_connected,
        }
