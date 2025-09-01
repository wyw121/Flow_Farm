"""
Flow Farm 员工客户端 - 通讯录导入和自动关注组件
提供通讯录导入、用户筛选、自动关注等功能
"""

import csv
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import qtawesome as qta
from PySide6.QtCore import QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..base_window import ComponentFactory, ModernTheme


class ContactImporter(QThread):
    """通讯录导入线程"""

    progress_updated = Signal(int, str)  # 进度, 状态消息
    contacts_loaded = Signal(list)  # 联系人数据
    error_occurred = Signal(str)  # 错误信息

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.contacts = []

    def run(self):
        """执行导入"""
        try:
            file_ext = Path(self.file_path).suffix.lower()

            if file_ext == ".csv":
                self.import_from_csv()
            elif file_ext == ".json":
                self.import_from_json()
            elif file_ext in [".txt", ".text"]:
                self.import_from_txt()
            else:
                self.error_occurred.emit(f"不支持的文件格式: {file_ext}")
                return

            self.contacts_loaded.emit(self.contacts)

        except Exception as e:
            self.error_occurred.emit(f"导入失败: {str(e)}")

    def import_from_csv(self):
        """从CSV文件导入"""
        self.progress_updated.emit(10, "读取CSV文件...")

        with open(self.file_path, "r", encoding="utf-8-sig") as file:
            # 尝试检测分隔符
            sample = file.read(1024)
            file.seek(0)

            delimiter = ","
            if ";" in sample and sample.count(";") > sample.count(","):
                delimiter = ";"

            reader = csv.DictReader(file, delimiter=delimiter)

            total_rows = sum(1 for _ in file)
            file.seek(0)
            reader = csv.DictReader(file, delimiter=delimiter)

            for i, row in enumerate(reader):
                contact = self.normalize_contact(row)
                if contact:
                    self.contacts.append(contact)

                progress = int((i + 1) / total_rows * 90) + 10
                self.progress_updated.emit(progress, f"处理联系人 {i+1}/{total_rows}")

    def import_from_json(self):
        """从JSON文件导入"""
        self.progress_updated.emit(10, "读取JSON文件...")

        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            contacts_data = data
        elif isinstance(data, dict) and "contacts" in data:
            contacts_data = data["contacts"]
        else:
            raise ValueError("无效的JSON格式")

        total_contacts = len(contacts_data)

        for i, contact_data in enumerate(contacts_data):
            contact = self.normalize_contact(contact_data)
            if contact:
                self.contacts.append(contact)

            progress = int((i + 1) / total_contacts * 90) + 10
            self.progress_updated.emit(progress, f"处理联系人 {i+1}/{total_contacts}")

    def import_from_txt(self):
        """从文本文件导入"""
        self.progress_updated.emit(10, "读取文本文件...")

        with open(self.file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        total_lines = len(lines)

        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                # 假设每行一个用户名或ID
                contact = {
                    "username": line,
                    "display_name": line,
                    "platform": "未知",
                    "follow_status": "未关注",
                    "import_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                self.contacts.append(contact)

            progress = int((i + 1) / total_lines * 90) + 10
            self.progress_updated.emit(progress, f"处理行 {i+1}/{total_lines}")

    def normalize_contact(self, raw_contact: dict) -> Optional[dict]:
        """标准化联系人数据"""
        # 尝试从不同的字段名中提取信息
        username_fields = [
            "username",
            "user_name",
            "user",
            "id",
            "user_id",
            "用户名",
            "账号",
        ]
        name_fields = ["name", "display_name", "nickname", "昵称", "姓名", "名称"]
        platform_fields = ["platform", "source", "app", "平台", "来源"]

        username = ""
        for field in username_fields:
            if field in raw_contact and raw_contact[field]:
                username = str(raw_contact[field]).strip()
                break

        if not username:
            return None

        display_name = ""
        for field in name_fields:
            if field in raw_contact and raw_contact[field]:
                display_name = str(raw_contact[field]).strip()
                break

        if not display_name:
            display_name = username

        platform = "未知"
        for field in platform_fields:
            if field in raw_contact and raw_contact[field]:
                platform = str(raw_contact[field]).strip()
                break

        return {
            "username": username,
            "display_name": display_name,
            "platform": platform,
            "follow_status": "未关注",
            "import_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "raw_data": raw_contact,
        }


class AutoFollowWorker(QThread):
    """自动关注工作线程"""

    progress_updated = Signal(int, str, dict)  # 进度, 状态, 当前联系人
    follow_completed = Signal(dict, bool, str)  # 联系人, 成功, 消息
    batch_completed = Signal(int, int)  # 成功数, 失败数

    def __init__(self, contacts: List[dict], settings: dict):
        super().__init__()
        self.contacts = contacts
        self.settings = settings
        self.is_stopped = False
        self.success_count = 0
        self.failure_count = 0

    def run(self):
        """执行自动关注"""
        total_contacts = len(self.contacts)

        for i, contact in enumerate(self.contacts):
            if self.is_stopped:
                break

            # 更新进度
            progress = int((i + 1) / total_contacts * 100)
            self.progress_updated.emit(
                progress, f"关注 {contact['display_name']}", contact
            )

            # 执行关注操作
            success, message = self.follow_user(contact)

            if success:
                self.success_count += 1
                contact["follow_status"] = "已关注"
                contact["follow_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                self.failure_count += 1
                contact["follow_status"] = "关注失败"
                contact["error_message"] = message

            self.follow_completed.emit(contact, success, message)

            # 间隔等待
            if i < total_contacts - 1:  # 不是最后一个
                wait_time = self.settings.get("follow_interval", 3)
                self.msleep(wait_time * 1000)

        self.batch_completed.emit(self.success_count, self.failure_count)

    def follow_user(self, contact: dict) -> tuple[bool, str]:
        """关注单个用户"""
        try:
            # 这里应该调用实际的关注逻辑
            # 目前返回模拟结果
            platform = contact.get("platform", "").lower()

            if platform == "小红书":
                return self.follow_xiaohongshu_user(contact)
            elif platform == "抖音":
                return self.follow_douyin_user(contact)
            else:
                return False, f"不支持的平台: {platform}"

        except Exception as e:
            return False, f"关注失败: {str(e)}"

    def follow_xiaohongshu_user(self, contact: dict) -> tuple[bool, str]:
        """关注小红书用户"""
        # TODO: 集成实际的小红书关注逻辑
        # 模拟关注过程
        self.msleep(2000)  # 模拟操作时间

        # 模拟成功率 (实际应该调用自动化脚本)
        import random

        if random.random() > 0.1:  # 90% 成功率
            return True, "关注成功"
        else:
            return False, "用户不存在或网络错误"

    def follow_douyin_user(self, contact: dict) -> tuple[bool, str]:
        """关注抖音用户"""
        # TODO: 集成实际的抖音关注逻辑
        self.msleep(2000)

        import random

        if random.random() > 0.15:  # 85% 成功率
            return True, "关注成功"
        else:
            return False, "用户不存在或关注失败"

    def stop(self):
        """停止关注"""
        self.is_stopped = True


class ContactsAutoFollowWidget(QWidget):
    """通讯录导入和自动关注组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.theme = ModernTheme()
        self.components = ComponentFactory()

        # 数据
        self.contacts = []
        self.filtered_contacts = []

        # 工作线程
        self.import_worker = None
        self.follow_worker = None

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)

        # 导入区域
        import_group = self.create_import_section()
        layout.addWidget(import_group)

        # 筛选区域
        filter_group = self.create_filter_section()
        layout.addWidget(filter_group)

        # 联系人列表
        contacts_group = self.create_contacts_section()
        layout.addWidget(contacts_group)

        # 关注控制区域
        follow_group = self.create_follow_section()
        layout.addWidget(follow_group)

    def create_import_section(self) -> QGroupBox:
        """创建导入区域"""
        group = QGroupBox("通讯录导入")
        layout = QGridLayout(group)

        # 文件选择
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("选择通讯录文件...")
        self.file_path_edit.setReadOnly(True)
        layout.addWidget(QLabel("文件路径:"), 0, 0)
        layout.addWidget(self.file_path_edit, 0, 1)

        self.browse_btn = self.components.create_button(
            "浏览", "secondary", "fa5s.folder-open", "选择通讯录文件", self.browse_file
        )
        layout.addWidget(self.browse_btn, 0, 2)

        # 导入按钮
        self.import_btn = self.components.create_button(
            "导入通讯录",
            "primary",
            "fa5s.file-import",
            "开始导入通讯录数据",
            self.start_import,
        )
        layout.addWidget(self.import_btn, 1, 1)

        # 进度条
        self.import_progress = QProgressBar()
        self.import_progress.setVisible(False)
        layout.addWidget(self.import_progress, 2, 0, 1, 3)

        # 状态标签
        self.import_status_label = QLabel("就绪")
        layout.addWidget(self.import_status_label, 3, 0, 1, 3)

        return group

    def create_filter_section(self) -> QGroupBox:
        """创建筛选区域"""
        group = QGroupBox("筛选和设置")
        layout = QGridLayout(group)

        # 平台筛选
        layout.addWidget(QLabel("平台:"), 0, 0)
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["全部", "小红书", "抖音", "其他"])
        layout.addWidget(self.platform_combo, 0, 1)

        # 状态筛选
        layout.addWidget(QLabel("状态:"), 0, 2)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["全部", "未关注", "已关注", "关注失败"])
        layout.addWidget(self.status_combo, 0, 3)

        # 搜索框
        layout.addWidget(QLabel("搜索:"), 1, 0)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入用户名或昵称...")
        layout.addWidget(self.search_edit, 1, 1, 1, 2)

        # 筛选按钮
        self.filter_btn = self.components.create_button(
            "应用筛选", "secondary", "fa5s.filter", "应用筛选条件", self.apply_filters
        )
        layout.addWidget(self.filter_btn, 1, 3)

        return group

    def create_contacts_section(self) -> QGroupBox:
        """创建联系人列表区域"""
        group = QGroupBox("联系人列表")
        layout = QVBoxLayout(group)

        # 统计信息
        stats_layout = QHBoxLayout()
        self.total_label = QLabel("总数: 0")
        self.selected_label = QLabel("已选: 0")
        self.followed_label = QLabel("已关注: 0")

        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.selected_label)
        stats_layout.addWidget(self.followed_label)
        stats_layout.addStretch()

        # 全选/取消全选
        self.select_all_btn = self.components.create_button(
            "全选",
            "secondary",
            "fa5s.check-square",
            "选择所有联系人",
            self.select_all_contacts,
        )
        stats_layout.addWidget(self.select_all_btn)

        self.deselect_all_btn = self.components.create_button(
            "取消全选",
            "secondary",
            "fa5s.square",
            "取消选择所有联系人",
            self.deselect_all_contacts,
        )
        stats_layout.addWidget(self.deselect_all_btn)

        layout.addLayout(stats_layout)

        # 联系人表格
        self.contacts_table = QTableWidget()
        self.contacts_table.setColumnCount(6)
        self.contacts_table.setHorizontalHeaderLabels(
            ["选择", "用户名", "显示名称", "平台", "状态", "导入时间"]
        )

        # 设置表格列宽
        header = self.contacts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.contacts_table.setColumnWidth(0, 60)

        layout.addWidget(self.contacts_table)

        return group

    def create_follow_section(self) -> QGroupBox:
        """创建关注控制区域"""
        group = QGroupBox("自动关注")
        layout = QGridLayout(group)

        # 关注设置
        layout.addWidget(QLabel("关注间隔 (秒):"), 0, 0)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 30)
        self.interval_spin.setValue(3)
        layout.addWidget(self.interval_spin, 0, 1)

        layout.addWidget(QLabel("最大关注数:"), 0, 2)
        self.max_follow_spin = QSpinBox()
        self.max_follow_spin.setRange(1, 1000)
        self.max_follow_spin.setValue(50)
        layout.addWidget(self.max_follow_spin, 0, 3)

        # 控制按钮
        self.start_follow_btn = self.components.create_button(
            "开始关注",
            "primary",
            "fa5s.heart",
            "开始自动关注选中的用户",
            self.start_auto_follow,
        )
        layout.addWidget(self.start_follow_btn, 1, 0)

        self.stop_follow_btn = self.components.create_button(
            "停止关注", "error", "fa5s.stop", "停止自动关注", self.stop_auto_follow
        )
        self.stop_follow_btn.setEnabled(False)
        layout.addWidget(self.stop_follow_btn, 1, 1)

        # 导出按钮
        self.export_btn = self.components.create_button(
            "导出结果",
            "secondary",
            "fa5s.file-export",
            "导出关注结果",
            self.export_results,
        )
        layout.addWidget(self.export_btn, 1, 2)

        # 关注进度
        self.follow_progress = QProgressBar()
        self.follow_progress.setVisible(False)
        layout.addWidget(self.follow_progress, 2, 0, 1, 4)

        # 关注状态
        self.follow_status_label = QLabel("就绪")
        layout.addWidget(self.follow_status_label, 3, 0, 1, 4)

        return group

    def setup_connections(self):
        """设置信号连接"""
        self.platform_combo.currentTextChanged.connect(self.apply_filters)
        self.status_combo.currentTextChanged.connect(self.apply_filters)
        self.search_edit.textChanged.connect(self.apply_filters)

    def browse_file(self):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择通讯录文件",
            "",
            "支持的文件 (*.csv *.json *.txt);;CSV文件 (*.csv);;JSON文件 (*.json);;文本文件 (*.txt)",
        )

        if file_path:
            self.file_path_edit.setText(file_path)

    def start_import(self):
        """开始导入"""
        file_path = self.file_path_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "警告", "请先选择通讯录文件")
            return

        if not os.path.exists(file_path):
            QMessageBox.warning(self, "警告", "文件不存在")
            return

        # 启动导入线程
        self.import_worker = ContactImporter(file_path)
        self.import_worker.progress_updated.connect(self.on_import_progress)
        self.import_worker.contacts_loaded.connect(self.on_contacts_loaded)
        self.import_worker.error_occurred.connect(self.on_import_error)

        # 更新UI状态
        self.import_btn.setEnabled(False)
        self.import_progress.setVisible(True)
        self.import_progress.setValue(0)
        self.import_status_label.setText("导入中...")

        self.import_worker.start()

    def on_import_progress(self, progress: int, message: str):
        """导入进度更新"""
        self.import_progress.setValue(progress)
        self.import_status_label.setText(message)

    def on_contacts_loaded(self, contacts: List[dict]):
        """联系人数据加载完成"""
        self.contacts = contacts
        self.filtered_contacts = contacts.copy()

        # 更新UI
        self.import_btn.setEnabled(True)
        self.import_progress.setVisible(False)
        self.import_status_label.setText(f"导入完成，共 {len(contacts)} 个联系人")

        # 刷新表格
        self.refresh_contacts_table()
        self.update_statistics()

        # 更新平台筛选列表
        platforms = {"全部"}
        for contact in contacts:
            platforms.add(contact.get("platform", "未知"))

        current_platform = self.platform_combo.currentText()
        self.platform_combo.clear()
        self.platform_combo.addItems(sorted(platforms))

        if current_platform in platforms:
            self.platform_combo.setCurrentText(current_platform)

    def on_import_error(self, error_message: str):
        """导入错误"""
        self.import_btn.setEnabled(True)
        self.import_progress.setVisible(False)
        self.import_status_label.setText("导入失败")

        QMessageBox.critical(self, "导入失败", error_message)

    def apply_filters(self):
        """应用筛选条件"""
        if not self.contacts:
            return

        platform_filter = self.platform_combo.currentText()
        status_filter = self.status_combo.currentText()
        search_text = self.search_edit.text().strip().lower()

        self.filtered_contacts = []

        for contact in self.contacts:
            # 平台筛选
            if platform_filter != "全部" and contact.get("platform") != platform_filter:
                continue

            # 状态筛选
            if (
                status_filter != "全部"
                and contact.get("follow_status") != status_filter
            ):
                continue

            # 搜索筛选
            if search_text:
                username = contact.get("username", "").lower()
                display_name = contact.get("display_name", "").lower()
                if search_text not in username and search_text not in display_name:
                    continue

            self.filtered_contacts.append(contact)

        self.refresh_contacts_table()
        self.update_statistics()

    def refresh_contacts_table(self):
        """刷新联系人表格"""
        self.contacts_table.setRowCount(len(self.filtered_contacts))

        for row, contact in enumerate(self.filtered_contacts):
            # 选择框
            checkbox = QCheckBox()
            self.contacts_table.setCellWidget(row, 0, checkbox)

            # 用户名
            self.contacts_table.setItem(
                row, 1, QTableWidgetItem(contact.get("username", ""))
            )

            # 显示名称
            self.contacts_table.setItem(
                row, 2, QTableWidgetItem(contact.get("display_name", ""))
            )

            # 平台
            self.contacts_table.setItem(
                row, 3, QTableWidgetItem(contact.get("platform", ""))
            )

            # 状态
            status_item = QTableWidgetItem(contact.get("follow_status", ""))
            if contact.get("follow_status") == "已关注":
                status_item.setBackground(self.theme.COLORS["success_light"])
            elif contact.get("follow_status") == "关注失败":
                status_item.setBackground(self.theme.COLORS["error_light"])
            self.contacts_table.setItem(row, 4, status_item)

            # 导入时间
            self.contacts_table.setItem(
                row, 5, QTableWidgetItem(contact.get("import_time", ""))
            )

    def update_statistics(self):
        """更新统计信息"""
        total = len(self.filtered_contacts)
        followed = sum(
            1 for c in self.filtered_contacts if c.get("follow_status") == "已关注"
        )
        selected = self.get_selected_count()

        self.total_label.setText(f"总数: {total}")
        self.selected_label.setText(f"已选: {selected}")
        self.followed_label.setText(f"已关注: {followed}")

    def get_selected_count(self) -> int:
        """获取选中的联系人数量"""
        count = 0
        for row in range(self.contacts_table.rowCount()):
            checkbox = self.contacts_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                count += 1
        return count

    def get_selected_contacts(self) -> List[dict]:
        """获取选中的联系人"""
        selected = []
        for row in range(self.contacts_table.rowCount()):
            checkbox = self.contacts_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                if row < len(self.filtered_contacts):
                    selected.append(self.filtered_contacts[row])
        return selected

    def select_all_contacts(self):
        """全选联系人"""
        for row in range(self.contacts_table.rowCount()):
            checkbox = self.contacts_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)
        self.update_statistics()

    def deselect_all_contacts(self):
        """取消全选联系人"""
        for row in range(self.contacts_table.rowCount()):
            checkbox = self.contacts_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)
        self.update_statistics()

    def start_auto_follow(self):
        """开始自动关注"""
        selected_contacts = self.get_selected_contacts()

        if not selected_contacts:
            QMessageBox.warning(self, "警告", "请先选择要关注的联系人")
            return

        # 设置
        settings = {
            "follow_interval": self.interval_spin.value(),
            "max_follow": min(len(selected_contacts), self.max_follow_spin.value()),
        }

        # 限制关注数量
        if len(selected_contacts) > settings["max_follow"]:
            selected_contacts = selected_contacts[: settings["max_follow"]]

        # 启动关注线程
        self.follow_worker = AutoFollowWorker(selected_contacts, settings)
        self.follow_worker.progress_updated.connect(self.on_follow_progress)
        self.follow_worker.follow_completed.connect(self.on_follow_completed)
        self.follow_worker.batch_completed.connect(self.on_follow_batch_completed)

        # 更新UI状态
        self.start_follow_btn.setEnabled(False)
        self.stop_follow_btn.setEnabled(True)
        self.follow_progress.setVisible(True)
        self.follow_progress.setValue(0)
        self.follow_status_label.setText(f"开始关注 {len(selected_contacts)} 个用户...")

        self.follow_worker.start()

    def stop_auto_follow(self):
        """停止自动关注"""
        if self.follow_worker:
            self.follow_worker.stop()

    def on_follow_progress(self, progress: int, message: str, contact: dict):
        """关注进度更新"""
        self.follow_progress.setValue(progress)
        self.follow_status_label.setText(message)

    def on_follow_completed(self, contact: dict, success: bool, message: str):
        """单个关注完成"""
        # 刷新表格显示
        self.refresh_contacts_table()
        self.update_statistics()

        # 记录日志
        if success:
            self.logger.info(f"关注成功: {contact['display_name']}")
        else:
            self.logger.warning(f"关注失败: {contact['display_name']} - {message}")

    def on_follow_batch_completed(self, success_count: int, failure_count: int):
        """批量关注完成"""
        # 更新UI状态
        self.start_follow_btn.setEnabled(True)
        self.stop_follow_btn.setEnabled(False)
        self.follow_progress.setVisible(False)

        total = success_count + failure_count
        self.follow_status_label.setText(
            f"关注完成: 成功 {success_count}/{total}, 失败 {failure_count}/{total}"
        )

        # 显示完成消息
        QMessageBox.information(
            self,
            "关注完成",
            f"关注任务已完成！\n\n成功: {success_count} 个\n失败: {failure_count} 个",
        )

        # 刷新显示
        self.refresh_contacts_table()
        self.update_statistics()

    def export_results(self):
        """导出关注结果"""
        if not self.contacts:
            QMessageBox.warning(self, "警告", "没有可导出的数据")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出关注结果",
            f"关注结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV文件 (*.csv);;JSON文件 (*.json)",
        )

        if not file_path:
            return

        try:
            if file_path.endswith(".json"):
                self.export_to_json(file_path)
            else:
                self.export_to_csv(file_path)

            QMessageBox.information(self, "导出成功", f"结果已导出到: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出失败: {str(e)}")

    def export_to_csv(self, file_path: str):
        """导出到CSV"""
        with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)

            # 写入表头
            writer.writerow(
                [
                    "用户名",
                    "显示名称",
                    "平台",
                    "关注状态",
                    "导入时间",
                    "关注时间",
                    "错误信息",
                ]
            )

            # 写入数据
            for contact in self.contacts:
                writer.writerow(
                    [
                        contact.get("username", ""),
                        contact.get("display_name", ""),
                        contact.get("platform", ""),
                        contact.get("follow_status", ""),
                        contact.get("import_time", ""),
                        contact.get("follow_time", ""),
                        contact.get("error_message", ""),
                    ]
                )

    def export_to_json(self, file_path: str):
        """导出到JSON"""
        export_data = {
            "export_time": datetime.now().isoformat(),
            "total_contacts": len(self.contacts),
            "contacts": self.contacts,
        }

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(export_data, file, ensure_ascii=False, indent=2)
