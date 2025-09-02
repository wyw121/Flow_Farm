"""
Flow Farm - 通讯录服务模块
负责通讯录数据的导入、解析和任务分配

功能特性:
- 支持多种格式的通讯录文件导入 (CSV, XLSX, TXT)
- 数据去重和验证
- 智能任务分配算法
- 与服务器端数据同步
"""

import csv
import json
import logging
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
import requests


@dataclass
class ContactInfo:
    """联系人信息数据类"""

    username: str
    user_id: Optional[str] = None
    platform: str = "xiaohongshu"  # 默认小红书
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        """数据后处理"""
        # 清理用户名
        if self.username:
            self.username = self.username.strip()

        # 验证手机号格式
        if self.phone:
            self.phone = self._clean_phone_number(self.phone)

    def _clean_phone_number(self, phone: str) -> Optional[str]:
        """清理手机号格式"""
        # 移除所有非数字字符
        cleaned = re.sub(r"\D", "", phone)

        # 验证中国手机号格式
        if len(cleaned) == 11 and cleaned.startswith("1"):
            return cleaned

        return None

    def is_valid(self) -> bool:
        """验证联系人信息是否有效"""
        return bool(self.username and len(self.username) > 0)


@dataclass
class TaskAssignment:
    """任务分配信息"""

    device_id: str
    contact_batch: List[ContactInfo]
    platform: str
    task_type: str = "follow"  # follow, like, comment
    estimated_cost: float = 0.0
    estimated_duration: int = 0  # 预计执行时间(秒)


class ContactsService:
    """通讯录服务类"""

    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.logger = logging.getLogger(__name__)

        # 支持的文件格式
        self.supported_formats = {
            ".csv": self._read_csv,
            ".xlsx": self._read_excel,
            ".xls": self._read_excel,
            ".txt": self._read_txt,
        }

        # 平台扣费规则 (与服务器同步)
        self.pricing_rules = {
            "xiaohongshu": {"follow": 0.12, "like": 0.08, "comment": 0.20},
            "douyin": {"follow": 0.15, "like": 0.10, "comment": 0.25},
        }

    def import_contacts_file(self, file_path: str) -> Tuple[List[ContactInfo], Dict]:
        """
        导入通讯录文件

        Args:
            file_path: 文件路径

        Returns:
            Tuple[List[ContactInfo], Dict]: 联系人列表和统计信息
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        file_ext = file_path.suffix.lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"不支持的文件格式: {file_ext}")

        try:
            # 根据文件类型调用相应的读取方法
            contacts = self.supported_formats[file_ext](file_path)

            # 数据清理和去重
            cleaned_contacts = self._clean_and_deduplicate(contacts)

            # 统计信息
            stats = self._generate_stats(contacts, cleaned_contacts)

            self.logger.info(f"成功导入通讯录: {len(cleaned_contacts)} 条有效数据")

            return cleaned_contacts, stats

        except Exception as e:
            self.logger.error(f"导入文件失败: {e}")
            raise

    def _read_csv(self, file_path: Path) -> List[ContactInfo]:
        """读取CSV文件"""
        contacts = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # 尝试检测分隔符
                sample = f.read(1024)
                f.seek(0)

                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter

                reader = csv.DictReader(f, delimiter=delimiter)

                for row in reader:
                    contact = self._parse_contact_row(row)
                    if contact and contact.is_valid():
                        contacts.append(contact)

        except Exception as e:
            self.logger.error(f"读取CSV文件失败: {e}")
            raise

        return contacts

    def _read_excel(self, file_path: Path) -> List[ContactInfo]:
        """读取Excel文件"""
        contacts = []

        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)

            for _, row in df.iterrows():
                contact = self._parse_contact_row(row.to_dict())
                if contact and contact.is_valid():
                    contacts.append(contact)

        except Exception as e:
            self.logger.error(f"读取Excel文件失败: {e}")
            raise

        return contacts

    def _read_txt(self, file_path: Path) -> List[ContactInfo]:
        """读取TXT文件"""
        contacts = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

                for line in lines:
                    line = line.strip()
                    if line:
                        # 简单的用户名解析
                        username = line.split()[0] if line.split() else line
                        contact = ContactInfo(username=username)
                        if contact.is_valid():
                            contacts.append(contact)

        except Exception as e:
            self.logger.error(f"读取TXT文件失败: {e}")
            raise

        return contacts

    def _parse_contact_row(self, row: Dict) -> Optional[ContactInfo]:
        """解析联系人行数据"""
        try:
            # 尝试从行数据中提取字段
            username = None
            user_id = None
            phone = None
            email = None
            notes = None

            # 灵活的字段匹配
            for key, value in row.items():
                if not key or pd.isna(value):
                    continue

                key_lower = str(key).lower()
                value_str = str(value).strip()

                if not value_str or value_str.lower() in ["nan", "null", ""]:
                    continue

                # 用户名匹配
                if any(
                    keyword in key_lower
                    for keyword in ["用户名", "username", "name", "姓名", "昵称"]
                ):
                    username = value_str
                elif any(
                    keyword in key_lower
                    for keyword in ["用户id", "userid", "user_id", "id"]
                ):
                    user_id = value_str
                elif any(
                    keyword in key_lower
                    for keyword in ["手机", "phone", "mobile", "电话"]
                ):
                    phone = value_str
                elif any(keyword in key_lower for keyword in ["邮箱", "email", "mail"]):
                    email = value_str
                elif any(
                    keyword in key_lower
                    for keyword in ["备注", "note", "remark", "说明"]
                ):
                    notes = value_str

            # 如果没有找到用户名，使用第一个非空值
            if not username:
                for value in row.values():
                    if value and not pd.isna(value):
                        username = str(value).strip()
                        break

            if username:
                return ContactInfo(
                    username=username,
                    user_id=user_id,
                    phone=phone,
                    email=email,
                    notes=notes,
                )

        except Exception as e:
            self.logger.warning(f"解析联系人行失败: {e}")

        return None

    def _clean_and_deduplicate(self, contacts: List[ContactInfo]) -> List[ContactInfo]:
        """清理和去重联系人数据"""
        # 使用用户名去重
        seen_usernames = set()
        cleaned_contacts = []

        for contact in contacts:
            if contact.username.lower() not in seen_usernames:
                seen_usernames.add(contact.username.lower())
                cleaned_contacts.append(contact)

        return cleaned_contacts

    def _generate_stats(
        self, original: List[ContactInfo], cleaned: List[ContactInfo]
    ) -> Dict:
        """生成统计信息"""
        return {
            "original_count": len(original),
            "valid_count": len(cleaned),
            "duplicates_removed": len(original) - len(cleaned),
            "has_phone": sum(1 for c in cleaned if c.phone),
            "has_email": sum(1 for c in cleaned if c.email),
            "has_user_id": sum(1 for c in cleaned if c.user_id),
        }

    def create_task_assignments(
        self,
        contacts: List[ContactInfo],
        available_devices: List[str],
        platform: str,
        task_type: str = "follow",
        max_per_device: int = 100,
    ) -> List[TaskAssignment]:
        """
        创建任务分配

        Args:
            contacts: 联系人列表
            available_devices: 可用设备列表
            platform: 目标平台
            task_type: 任务类型
            max_per_device: 每台设备最大任务数

        Returns:
            List[TaskAssignment]: 任务分配列表
        """
        if not available_devices:
            raise ValueError("没有可用设备")

        assignments = []
        device_count = len(available_devices)

        # 计算每台设备分配的任务数量
        contacts_per_device = min(max_per_device, len(contacts) // device_count + 1)

        # 获取扣费规则
        unit_price = self.pricing_rules.get(platform, {}).get(task_type, 0.15)

        # 分配任务
        for i, device_id in enumerate(available_devices):
            start_idx = i * contacts_per_device
            end_idx = min(start_idx + contacts_per_device, len(contacts))

            if start_idx >= len(contacts):
                break

            contact_batch = contacts[start_idx:end_idx]
            estimated_cost = len(contact_batch) * unit_price
            estimated_duration = len(contact_batch) * 5  # 假设每个操作5秒

            assignment = TaskAssignment(
                device_id=device_id,
                contact_batch=contact_batch,
                platform=platform,
                task_type=task_type,
                estimated_cost=estimated_cost,
                estimated_duration=estimated_duration,
            )

            assignments.append(assignment)

        return assignments

    def upload_to_server(self, contacts: List[ContactInfo], user_id: str) -> bool:
        """
        上传通讯录数据到服务器

        Args:
            contacts: 联系人列表
            user_id: 用户ID

        Returns:
            bool: 上传是否成功
        """
        try:
            # 转换为字典格式
            contacts_data = [asdict(contact) for contact in contacts]

            payload = {
                "user_id": user_id,
                "contacts": contacts_data,
                "total_count": len(contacts_data),
            }

            # 发送到服务器
            response = requests.post(
                f"{self.server_url}/api/v1/contacts/upload", json=payload, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.logger.info(f"成功上传 {len(contacts)} 条通讯录数据到服务器")
                    return True
                else:
                    self.logger.error(f"服务器返回错误: {result.get('message')}")
            else:
                self.logger.error(f"上传失败，HTTP状态码: {response.status_code}")

        except Exception as e:
            self.logger.error(f"上传到服务器失败: {e}")

        return False

    def get_user_balance(self, user_id: str) -> Optional[float]:
        """
        获取用户余额

        Args:
            user_id: 用户ID

        Returns:
            Optional[float]: 用户余额，失败返回None
        """
        try:
            response = requests.get(
                f"{self.server_url}/api/v1/users/{user_id}/balance", timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return float(result.get("data", {}).get("balance", 0))

        except Exception as e:
            self.logger.error(f"获取用户余额失败: {e}")

        return None

    def calculate_task_cost(
        self, contact_count: int, platform: str, task_type: str = "follow"
    ) -> float:
        """
        计算任务费用

        Args:
            contact_count: 联系人数量
            platform: 平台
            task_type: 任务类型

        Returns:
            float: 总费用
        """
        unit_price = self.pricing_rules.get(platform, {}).get(task_type, 0.15)
        return contact_count * unit_price

    def submit_task_to_server(self, assignment: TaskAssignment, user_id: str) -> bool:
        """
        提交任务到服务器

        Args:
            assignment: 任务分配
            user_id: 用户ID

        Returns:
            bool: 提交是否成功
        """
        try:
            # 准备任务数据
            task_data = {
                "user_id": user_id,
                "device_id": assignment.device_id,
                "platform": assignment.platform,
                "task_type": assignment.task_type,
                "contacts": [asdict(contact) for contact in assignment.contact_batch],
                "estimated_cost": assignment.estimated_cost,
                "estimated_duration": assignment.estimated_duration,
            }

            # 提交到服务器
            response = requests.post(
                f"{self.server_url}/api/v1/tasks/submit", json=task_data, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.logger.info(f"成功提交任务到设备 {assignment.device_id}")
                    return True
                else:
                    self.logger.error(f"服务器返回错误: {result.get('message')}")
            else:
                self.logger.error(f"提交任务失败，HTTP状态码: {response.status_code}")

        except Exception as e:
            self.logger.error(f"提交任务到服务器失败: {e}")

        return False


# 示例使用
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)

    # 创建服务实例
    service = ContactsService()

    # 示例：导入通讯录文件
    try:
        contacts, stats = service.import_contacts_file("example_contacts.csv")
        print(f"导入成功: {stats}")

        # 创建任务分配
        devices = ["device_001", "device_002"]
        assignments = service.create_task_assignments(
            contacts, devices, "xiaohongshu", "follow"
        )

        print(f"创建了 {len(assignments)} 个任务分配")

    except Exception as e:
        print(f"操作失败: {e}")
