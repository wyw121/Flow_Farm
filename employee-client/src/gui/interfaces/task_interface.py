"""
任务界面 - 基于 OneDragon 设计
管理和执行自动化任务
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    ComboBoxSettingCard,
    FluentIcon,
    PrimaryPushButton,
    PushButton,
    SettingCardGroup,
    SpinBoxSettingCard,
    SwitchSettingCard,
    TitleLabel,
)

from gui.onedragon_base.vertical_scroll_interface import VerticalScrollInterface


class TaskInterface(VerticalScrollInterface):
    """任务管理界面"""

    # 界面信号
    task_start_requested = Signal(str)  # task_type
    task_stop_requested = Signal()
    task_config_changed = Signal(dict)  # config

    def __init__(self, parent=None):
        """初始化任务界面"""
        # 创建内容组件
        content_widget = self._create_task_content()

        super().__init__(
            parent=parent,
            content_widget=content_widget,
            object_name="task_interface",
            nav_text_cn="任务管理",
            nav_icon=FluentIcon.PLAY,
        )

        self.is_running = False
        self.logger.info("任务管理界面初始化完成")

    def _create_task_content(self) -> QWidget:
        """创建任务管理内容"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # 标题区域
        title = TitleLabel("任务管理")
        layout.addWidget(title)

        # 任务控制区域
        control_section = self._create_control_section()
        layout.addWidget(control_section)

        # 平台选择区域
        platform_section = self._create_platform_section()
        layout.addWidget(platform_section)

        # 任务配置区域
        config_section = self._create_config_section()
        layout.addWidget(config_section)

        layout.addStretch()
        return widget

    def _create_control_section(self) -> QWidget:
        """创建任务控制区域"""
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        title_label = BodyLabel("任务控制")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # 控制按钮
        button_layout = QHBoxLayout()

        # 开始任务按钮
        self.start_btn = PrimaryPushButton("▶️ 开始任务")
        self.start_btn.clicked.connect(self._start_task)
        button_layout.addWidget(self.start_btn)

        # 停止任务按钮
        self.stop_btn = PushButton("⏹️ 停止任务")
        self.stop_btn.clicked.connect(self._stop_task)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # 任务状态
        self.status_label = BodyLabel("状态: 待启动")
        self.status_label.setStyleSheet("color: gray; margin-top: 10px;")
        layout.addWidget(self.status_label)

        return card

    def _create_platform_section(self) -> QWidget:
        """创建平台选择区域"""
        platform_group = SettingCardGroup("目标平台")

        # 平台选择
        self.platform_card = ComboBoxSettingCard(
            icon=FluentIcon.GLOBE,
            title="选择平台",
            content="选择要执行自动化操作的平台",
        )
        self.platform_card.comboBox.addItems(
            ["抖音 (Douyin)", "小红书 (Xiaohongshu)", "微博 (Weibo)", "快手 (Kuaishou)"]
        )
        self.platform_card.comboBox.currentTextChanged.connect(
            self._on_platform_changed
        )
        platform_group.addSettingCard(self.platform_card)

        return platform_group

    def _create_config_section(self) -> QWidget:
        """创建任务配置区域"""
        config_group = SettingCardGroup("任务配置")

        # 操作类型
        self.operation_card = ComboBoxSettingCard(
            icon=FluentIcon.SETTING, title="操作类型", content="选择要执行的自动化操作"
        )
        self.operation_card.comboBox.addItems(
            ["自动关注", "自动点赞", "自动评论", "自动浏览"]
        )
        config_group.addSettingCard(self.operation_card)

        # 执行数量
        self.count_card = SpinBoxSettingCard(
            icon=FluentIcon.TAG, title="执行数量", content="单次任务执行的操作数量"
        )
        self.count_card.spinBox.setRange(1, 1000)
        self.count_card.spinBox.setValue(10)
        config_group.addSettingCard(self.count_card)

        # 执行间隔
        self.interval_card = SpinBoxSettingCard(
            icon=FluentIcon.CALENDAR,
            title="执行间隔(秒)",
            content="每次操作之间的等待时间",
        )
        self.interval_card.spinBox.setRange(1, 60)
        self.interval_card.spinBox.setValue(3)
        config_group.addSettingCard(self.interval_card)

        # 随机化选项
        self.random_card = SwitchSettingCard(
            icon=FluentIcon.SYNC,
            title="随机化间隔",
            content="在设定间隔基础上添加随机延迟",
        )
        self.random_card.switchButton.setChecked(True)
        config_group.addSettingCard(self.random_card)

        # 安全模式
        self.safe_mode_card = SwitchSettingCard(
            icon=FluentIcon.SHIELD,
            title="安全模式",
            content="启用更保守的操作策略，降低被检测风险",
        )
        self.safe_mode_card.switchButton.setChecked(True)
        config_group.addSettingCard(self.safe_mode_card)

        return config_group

    def _start_task(self):
        """开始任务"""
        if not self.is_running:
            # 获取配置
            platform = self.platform_card.comboBox.currentText()
            operation = self.operation_card.comboBox.currentText()

            # 发射开始信号
            self.task_start_requested.emit(f"{platform}-{operation}")

            # 更新UI状态
            self.is_running = True
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("状态: 运行中...")
            self.status_label.setStyleSheet("color: green; margin-top: 10px;")

            self.show_info_bar(
                "任务启动", f"已开始执行 {platform} - {operation}", "success"
            )

    def _stop_task(self):
        """停止任务"""
        if self.is_running:
            # 发射停止信号
            self.task_stop_requested.emit()

            # 更新UI状态
            self.is_running = False
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_label.setText("状态: 已停止")
            self.status_label.setStyleSheet("color: orange; margin-top: 10px;")

            self.show_info_bar("任务停止", "任务已停止执行", "warning")

    def _on_platform_changed(self, platform: str):
        """平台选择变化"""
        self.logger.debug(f"平台选择变化: {platform}")

        # 根据平台更新操作类型
        if "抖音" in platform:
            operations = ["自动关注", "自动点赞", "自动评论", "直播间互动"]
        elif "小红书" in platform:
            operations = ["自动关注", "自动点赞", "自动收藏", "笔记浏览"]
        else:
            operations = ["自动关注", "自动点赞", "自动评论", "自动浏览"]

        # 更新操作类型选项
        self.operation_card.comboBox.clear()
        self.operation_card.comboBox.addItems(operations)

    def update_task_status(self, status: str, message: str = ""):
        """更新任务状态"""
        self.status_label.setText(f"状态: {status}")

        if status == "运行中":
            self.status_label.setStyleSheet("color: green; margin-top: 10px;")
        elif status == "已停止":
            self.status_label.setStyleSheet("color: orange; margin-top: 10px;")
        elif status == "错误":
            self.status_label.setStyleSheet("color: red; margin-top: 10px;")
        else:
            self.status_label.setStyleSheet("color: gray; margin-top: 10px;")

        if message:
            self.show_info_bar("任务状态", message, "info")

    def get_task_config(self) -> dict:
        """获取当前任务配置"""
        return {
            "platform": self.platform_card.comboBox.currentText(),
            "operation": self.operation_card.comboBox.currentText(),
            "count": self.count_card.spinBox.value(),
            "interval": self.interval_card.spinBox.value(),
            "random_interval": self.random_card.switchButton.isChecked(),
            "safe_mode": self.safe_mode_card.switchButton.isChecked(),
        }
