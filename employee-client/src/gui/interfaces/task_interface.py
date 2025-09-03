"""
任务界面 - 基于 OneDragon 设计
管理和执行自动化任务
"""

import sys
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    ComboBoxSettingCard,
    FluentIcon,
    PrimaryPushButton,
    PushButton,
    RangeSettingCard,
    SettingCardGroup,
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
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        title_label = BodyLabel("目标平台")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # 平台选择（简化版本）
        platform_label = BodyLabel("🎯 当前平台: 抖音 (Douyin)")
        layout.addWidget(platform_label)

        return card

    def _create_config_section(self) -> QWidget:
        """创建任务配置区域"""
        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        title_label = BodyLabel("任务配置")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # 配置选项（简化版本）
        config_labels = [
            "📋 操作类型: 自动关注",
            "🔢 执行数量: 10",
            "⏱️ 执行间隔: 3秒",
            "🎲 随机化间隔: 启用",
            "🛡️ 安全模式: 启用",
        ]

        for label_text in config_labels:
            label = BodyLabel(label_text)
            layout.addWidget(label)

        return card

    def _start_task(self):
        """开始任务"""
        if not self.is_running:
            # 发射开始信号
            self.task_start_requested.emit("抖音-自动关注")

            # 更新UI状态
            self.is_running = True
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("状态: 运行中...")
            self.status_label.setStyleSheet("color: green; margin-top: 10px;")

            self.show_info_bar("任务启动", "已开始执行 抖音 - 自动关注", "success")

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
        # 简化版本，不做实际操作

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
            "platform": "抖音 (Douyin)",
            "operation": "自动关注",
            "count": 10,
            "interval": 3,
            "random_interval": True,
            "safe_mode": True,
        }
