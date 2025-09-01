"""
Flow Farm 员工客户端 - 集成控制台组件
将命令行功能集成到GUI界面中，提供统一的用户体验
"""

import logging
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

import qtawesome as qta
from PySide6.QtCore import QObject, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..base_window import ComponentFactory, ModernTheme


class CommandExecutor(QThread):
    """命令执行线程"""

    output_received = Signal(str)  # 输出信号
    error_received = Signal(str)  # 错误信号
    finished_signal = Signal(int)  # 完成信号(返回码)
    progress_updated = Signal(int)  # 进度信号

    def __init__(self, command: str, working_dir: str = None):
        super().__init__()
        self.command = command
        self.working_dir = working_dir or str(Path(__file__).parent.parent.parent)
        self.process = None
        self.is_stopped = False

    def run(self):
        """执行命令"""
        try:
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.working_dir,
                bufsize=1,
                universal_newlines=True,
            )

            # 实时读取输出
            while True:
                if self.is_stopped:
                    break

                line = self.process.stdout.readline()
                if not line:
                    break

                self.output_received.emit(line.strip())

            # 等待进程结束
            self.process.wait()
            return_code = self.process.returncode
            self.finished_signal.emit(return_code)

        except Exception as e:
            self.error_received.emit(f"执行命令失败: {str(e)}")
            self.finished_signal.emit(-1)

    def stop(self):
        """停止命令执行"""
        self.is_stopped = True
        if self.process:
            self.process.terminate()


class ConsoleWidget(QWidget):
    """集成控制台组件"""

    # 预定义的脚本命令
    PREDEFINED_COMMANDS = {
        "设备连接测试": {
            "command": "python src/test_device_connection.py",
            "description": "测试Android设备连接状态",
            "category": "设备管理",
        },
        "完整设备测试": {
            "command": "python src/complete_device_test.py",
            "description": "执行完整的设备功能测试",
            "category": "设备管理",
        },
        "快速测试": {
            "command": "python src/quick_test.py",
            "description": "快速验证核心功能",
            "category": "功能测试",
        },
        "设备诊断": {
            "command": "python src/diagnose_connection.py",
            "description": "诊断设备连接问题",
            "category": "设备管理",
        },
        "简单检查": {
            "command": "python src/simple_check.py",
            "description": "执行基础状态检查",
            "category": "系统检查",
        },
        "演示系统": {
            "command": "python src/demo_system.py",
            "description": "运行系统演示程序",
            "category": "演示",
        },
        "小红书自动化": {
            "command": "python xiaohongshu_automation/xhs_automation.py",
            "description": "启动小红书自动关注功能",
            "category": "平台操作",
        },
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.theme = ModernTheme()
        self.components = ComponentFactory()

        # 执行器和状态
        self.current_executor = None
        self.command_history = []
        self.is_running = False

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """设置UI组件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建分隔器
        splitter = QSplitter()
        layout.addWidget(splitter)

        # 左侧：命令面板
        left_panel = self.create_command_panel()
        splitter.addWidget(left_panel)

        # 右侧：输出面板
        right_panel = self.create_output_panel()
        splitter.addWidget(right_panel)

        # 设置分隔器比例
        splitter.setSizes([300, 700])

    def create_command_panel(self) -> QWidget:
        """创建命令控制面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 标题
        title_label = self.components.create_label("集成控制台", "heading")
        layout.addWidget(title_label)

        # 分类选择
        category_group = QGroupBox("命令分类")
        category_layout = QVBoxLayout(category_group)

        self.category_combo = QComboBox()
        categories = set(cmd["category"] for cmd in self.PREDEFINED_COMMANDS.values())
        self.category_combo.addItem("全部")
        self.category_combo.addItems(sorted(categories))
        self.category_combo.currentTextChanged.connect(self.filter_commands)
        category_layout.addWidget(self.category_combo)

        layout.addWidget(category_group)

        # 命令列表
        commands_group = QGroupBox("可用命令")
        commands_layout = QVBoxLayout(commands_group)

        self.command_list = QListWidget()
        self.populate_command_list()
        commands_layout.addWidget(self.command_list)

        layout.addWidget(commands_group)

        # 控制按钮
        control_group = QGroupBox("控制")
        control_layout = QVBoxLayout(control_group)

        self.execute_btn = self.components.create_button(
            "执行选中命令",
            "primary",
            "fa5s.play",
            "执行当前选中的命令",
            self.execute_selected_command,
        )
        control_layout.addWidget(self.execute_btn)

        self.stop_btn = self.components.create_button(
            "停止执行", "error", "fa5s.stop", "停止当前执行的命令", self.stop_execution
        )
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)

        self.clear_btn = self.components.create_button(
            "清空输出", "secondary", "fa5s.eraser", "清空输出内容", self.clear_output
        )
        control_layout.addWidget(self.clear_btn)

        layout.addWidget(control_group)

        # 自动滚动选项
        options_group = QGroupBox("选项")
        options_layout = QVBoxLayout(options_group)

        self.auto_scroll_cb = QCheckBox("自动滚动到底部")
        self.auto_scroll_cb.setChecked(True)
        options_layout.addWidget(self.auto_scroll_cb)

        self.save_output_cb = QCheckBox("保存输出到文件")
        options_layout.addWidget(self.save_output_cb)

        layout.addWidget(options_group)

        return panel

    def create_output_panel(self) -> QWidget:
        """创建输出显示面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 状态栏
        status_layout = QHBoxLayout()

        self.status_label = self.components.create_label("就绪", "body")
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)

        layout.addLayout(status_layout)

        # 输出选项卡
        self.output_tabs = QTabWidget()

        # 实时输出
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: #1E1E1E;
                color: #FFFFFF;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
                border: 1px solid {self.theme.COLORS['border']};
                border-radius: {self.theme.RADIUS['small']}px;
            }}
        """
        )
        self.output_tabs.addTab(self.output_text, qta.icon("fa5s.terminal"), "实时输出")

        # 历史记录
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setStyleSheet(self.output_text.styleSheet())
        self.output_tabs.addTab(self.history_text, qta.icon("fa5s.history"), "历史记录")

        layout.addWidget(self.output_tabs)

        return panel

    def populate_command_list(self):
        """填充命令列表"""
        self.command_list.clear()

        for name, info in self.PREDEFINED_COMMANDS.items():
            item = QListWidgetItem()
            item.setText(f"{name}\n{info['description']}")
            item.setData(256, info)  # 存储命令信息
            item.setIcon(qta.icon("fa5s.terminal"))
            self.command_list.addItem(item)

    def filter_commands(self, category: str):
        """根据分类过滤命令"""
        self.command_list.clear()

        for name, info in self.PREDEFINED_COMMANDS.items():
            if category == "全部" or info["category"] == category:
                item = QListWidgetItem()
                item.setText(f"{name}\n{info['description']}")
                item.setData(256, info)
                item.setIcon(qta.icon("fa5s.terminal"))
                self.command_list.addItem(item)

    def setup_connections(self):
        """设置信号连接"""
        self.command_list.itemDoubleClicked.connect(self.execute_selected_command)

    def execute_selected_command(self):
        """执行选中的命令"""
        current_item = self.command_list.currentItem()
        if not current_item:
            self.logger.warning("没有选中的命令")
            return

        if self.is_running:
            self.logger.warning("已有命令在执行中")
            return

        command_info = current_item.data(256)
        command = command_info["command"]

        self.logger.info(f"执行命令: {command}")

        # 更新UI状态
        self.is_running = True
        self.execute_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText(f"执行中: {command}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度

        # 清空输出（如果需要）
        if not self.auto_scroll_cb.isChecked():
            self.output_text.clear()

        # 添加命令标题
        self.append_output(f"\n{'='*60}")
        self.append_output(f"执行命令: {command}")
        self.append_output(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.append_output(f"{'='*60}\n")

        # 创建并启动执行器
        self.current_executor = CommandExecutor(command)
        self.current_executor.output_received.connect(self.append_output)
        self.current_executor.error_received.connect(self.append_error)
        self.current_executor.finished_signal.connect(self.on_execution_finished)
        self.current_executor.start()

    def stop_execution(self):
        """停止当前执行"""
        if self.current_executor:
            self.current_executor.stop()
            self.append_output("\n[用户中断执行]")

    def append_output(self, text: str):
        """添加输出文本"""
        self.output_text.append(text)

        # 自动滚动
        if self.auto_scroll_cb.isChecked():
            scrollbar = self.output_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

        # 添加到历史
        self.history_text.append(text)

    def append_error(self, text: str):
        """添加错误文本"""
        error_text = f"<span style='color: #FF6B6B;'>[错误] {text}</span>"
        self.append_output(error_text)

    def on_execution_finished(self, return_code: int):
        """命令执行完成"""
        self.is_running = False
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

        if return_code == 0:
            self.status_label.setText("执行完成")
            self.append_output(f"\n[命令执行完成，返回码: {return_code}]")
        else:
            self.status_label.setText(f"执行失败 (返回码: {return_code})")
            self.append_output(f"\n[命令执行失败，返回码: {return_code}]")

        self.current_executor = None

    def clear_output(self):
        """清空输出"""
        self.output_text.clear()

    def add_custom_command(
        self, name: str, command: str, description: str = "", category: str = "自定义"
    ):
        """添加自定义命令"""
        self.PREDEFINED_COMMANDS[name] = {
            "command": command,
            "description": description,
            "category": category,
        }

        # 更新分类列表
        categories = set(cmd["category"] for cmd in self.PREDEFINED_COMMANDS.values())
        current_text = self.category_combo.currentText()
        self.category_combo.clear()
        self.category_combo.addItem("全部")
        self.category_combo.addItems(sorted(categories))
        self.category_combo.setCurrentText(current_text)

        # 刷新命令列表
        self.filter_commands(current_text)
