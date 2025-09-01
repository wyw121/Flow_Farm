"""
Flow Farm 现代化登录对话框
使用 qfluentwidgets 实现美观的登录界面
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout
from qfluentwidgets import (
    BodyLabel,
    FluentIcon,
    InfoBar,
    InfoBarPosition,
    LineEdit,
    MessageBoxBase,
    PasswordLineEdit,
    PrimaryPushButton,
    PushButton,
    SubtitleLabel,
)


class ModernLoginDialog(MessageBoxBase):
    """现代化登录对话框"""

    login_success = Signal(str, str)  # username, password

    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置窗口属性
        self.setWindowTitle("Flow Farm 登录")
        self.setFixedSize(420, 300)

        # 创建界面
        self.setup_ui()

        # 连接信号
        self.connect_signals()

    def setup_ui(self):
        """设置用户界面"""
        # 主标题
        self.title_label = SubtitleLabel("Flow Farm 员工工作台", self)
        self.title_label.setAlignment(Qt.AlignCenter)

        # 副标题
        self.subtitle_label = BodyLabel("请输入您的登录凭据", self)
        self.subtitle_label.setAlignment(Qt.AlignCenter)

        # 用户名输入
        self.username_label = BodyLabel("用户名:", self)
        self.username_edit = LineEdit(self)
        self.username_edit.setPlaceholderText("请输入用户名")
        self.username_edit.setClearButtonEnabled(True)

        # 密码输入
        self.password_label = BodyLabel("密码:", self)
        self.password_edit = PasswordLineEdit(self)
        self.password_edit.setPlaceholderText("请输入密码")

        # 按钮区域
        self.login_button = PrimaryPushButton("登录", self)
        self.cancel_button = PushButton("取消", self)

        # 设置按钮图标
        self.login_button.setIcon(FluentIcon.ACCEPT)
        self.cancel_button.setIcon(FluentIcon.CANCEL)

        # 布局设置
        self.setup_layout()

    def setup_layout(self):
        """设置布局"""
        # 主布局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # 标题区域
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addSpacing(20)

        # 表单区域
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_edit)
        layout.addSpacing(10)

        layout.addWidget(self.password_label)
        layout.addWidget(self.password_edit)
        layout.addSpacing(20)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addSpacing(10)
        button_layout.addWidget(self.login_button)

        layout.addLayout(button_layout)
        layout.addStretch()

        # 设置到对话框
        self.textLayout.addLayout(layout)

        # 隐藏默认按钮
        self.yesButton.hide()
        self.cancelButton.hide()

    def connect_signals(self):
        """连接信号"""
        self.login_button.clicked.connect(self.handle_login)
        self.cancel_button.clicked.connect(self.reject)

        # 回车键登录
        self.username_edit.returnPressed.connect(self.password_edit.setFocus)
        self.password_edit.returnPressed.connect(self.handle_login)

    def handle_login(self):
        """处理登录"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()

        # 验证输入
        if not username:
            self.show_error("请输入用户名")
            self.username_edit.setFocus()
            return

        if not password:
            self.show_error("请输入密码")
            self.password_edit.setFocus()
            return

        # 禁用按钮防止重复点击
        self.login_button.setEnabled(False)
        self.login_button.setText("登录中...")

        # 发送登录信号
        self.login_success.emit(username, password)

    def show_error(self, message: str):
        """显示错误信息"""
        InfoBar.error(
            title="输入错误",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self,
        )

    def login_failed(self, error_message: str):
        """登录失败处理"""
        self.login_button.setEnabled(True)
        self.login_button.setText("登录")

        InfoBar.error(
            title="登录失败",
            content=error_message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self,
        )

        # 清空密码
        self.password_edit.clear()
        self.password_edit.setFocus()

    def login_successful(self):
        """登录成功处理"""
        InfoBar.success(
            title="登录成功",
            content="欢迎使用 Flow Farm 工作台",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self,
        )

        # 延迟关闭对话框
        self.accept()
