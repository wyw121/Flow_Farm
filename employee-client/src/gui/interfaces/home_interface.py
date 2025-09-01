"""
主页界面 - 基于 OneDragon HomeInterface 设计
模仿 OneDragon 的主页布局和功能
"""

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    FluentIcon,
    PrimaryPushButton,
    SimpleCardWidget,
    SubtitleLabel,
    Theme,
    TitleLabel,
    qconfig,
)

from ..onedragon_base.vertical_scroll_interface import VerticalScrollInterface


class HomeInterface(VerticalScrollInterface):
    """
    主页界面，模仿 OneDragon 的 HomeInterface
    显示系统状态、快捷操作等
    """

    # 界面信号
    start_work_clicked = Signal()
    view_stats_clicked = Signal()
    device_manage_clicked = Signal()

    def __init__(self, parent=None):
        """初始化主页界面"""
        # 创建内容组件
        content_widget = self._create_home_content()

        super().__init__(
            parent=parent,
            content_widget=content_widget,
            object_name="home_interface",
            nav_text_cn="仪表盘",
            nav_icon=FluentIcon.HOME,
        )

        self.logger.info("主页界面初始化完成")

    def _create_home_content(self) -> QWidget:
        """创建主页内容"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # 顶部标题区域
        title_section = self._create_title_section()
        layout.addWidget(title_section)

        # 状态卡片区域
        status_section = self._create_status_section()
        layout.addWidget(status_section)

        # 快捷操作区域
        action_section = self._create_action_section()
        layout.addWidget(action_section)

        # 添加弹性空间
        layout.addStretch()

        return widget

    def _create_title_section(self) -> QWidget:
        """创建标题区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        # 主标题
        title = TitleLabel("Flow Farm 流量农场")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 副标题
        subtitle = SubtitleLabel("智能设备自动化管理平台")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)

        return widget

    def _create_status_section(self) -> QWidget:
        """创建状态卡片区域"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(20)

        # 设备状态卡片
        device_card = self._create_status_card(
            "设备状态", "0 台在线", FluentIcon.PHONE, "#4CAF50"
        )
        layout.addWidget(device_card)

        # 任务状态卡片
        task_card = self._create_status_card(
            "任务状态", "待启动", FluentIcon.PLAY, "#2196F3"
        )
        layout.addWidget(task_card)

        # 今日统计卡片
        stats_card = self._create_status_card(
            "今日统计", "0 次操作", FluentIcon.GRAPH, "#FF9800"
        )
        layout.addWidget(stats_card)

        return widget

    def _create_status_card(
        self, title: str, value: str, icon: FluentIcon, color: str
    ) -> CardWidget:
        """创建状态卡片"""
        card = CardWidget()
        card.setFixedHeight(120)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        # 标题和图标
        header_layout = QHBoxLayout()

        title_label = BodyLabel(title)
        title_label.setStyleSheet("color: gray; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # 这里可以添加图标
        # icon_widget = IconWidget(icon)
        # icon_widget.setFixedSize(24, 24)
        # header_layout.addWidget(icon_widget)

        layout.addLayout(header_layout)

        # 数值
        value_label = SubtitleLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        layout.addWidget(value_label)

        # 添加弹性空间
        layout.addStretch()

        return card

    def _create_action_section(self) -> QWidget:
        """创建快捷操作区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # 主要操作按钮
        main_button_layout = QHBoxLayout()
        main_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 开始工作按钮 - 模仿 OneDragon 的启动按钮
        self.start_button = PrimaryPushButton("🚀 开始工作")
        self.start_button.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        self.start_button.setFixedSize(200, 50)
        self.start_button.clicked.connect(self.start_work_clicked.emit)
        main_button_layout.addWidget(self.start_button)

        layout.addLayout(main_button_layout)

        # 次要操作按钮组
        secondary_layout = QHBoxLayout()
        secondary_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        secondary_layout.setSpacing(15)

        # 设备管理按钮
        device_btn = self._create_action_button(
            "设备管理", FluentIcon.PHONE, self.device_manage_clicked.emit
        )
        secondary_layout.addWidget(device_btn)

        # 数据统计按钮
        stats_btn = self._create_action_button(
            "数据统计", FluentIcon.GRAPH, self.view_stats_clicked.emit
        )
        secondary_layout.addWidget(stats_btn)

        layout.addLayout(secondary_layout)

        return widget

    def _create_action_button(
        self, text: str, icon: FluentIcon, callback
    ) -> CardWidget:
        """创建操作按钮卡片"""
        card = CardWidget()
        card.setFixedSize(120, 80)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        # 添加点击事件
        card.mousePressEvent = lambda e: (
            callback() if e.button() == Qt.MouseButton.LeftButton else None
        )

        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        # 图标（这里暂时用文字代替，实际可以用IconWidget）
        icon_label = BodyLabel("📱" if icon == FluentIcon.PHONE else "📊")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon_label)

        # 文字
        text_label = BodyLabel(text)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(text_label)

        return card

    def update_device_status(self, online_count: int, total_count: int):
        """更新设备状态显示"""
        # 这里可以更新设备状态卡片的显示
        self.logger.debug(f"设备状态更新: {online_count}/{total_count}")

    def update_task_status(self, status: str):
        """更新任务状态显示"""
        # 这里可以更新任务状态卡片的显示
        self.logger.debug(f"任务状态更新: {status}")

    def update_daily_stats(self, operation_count: int):
        """更新今日统计显示"""
        # 这里可以更新统计卡片的显示
        self.logger.debug(f"今日统计更新: {operation_count} 次操作")
