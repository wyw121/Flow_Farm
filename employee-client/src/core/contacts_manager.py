"""
Flow Farm - 通讯录管理器
负责通讯录的导入、验证、存储和任务分发
"""

import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class FollowStatus(Enum):
    """关注状态枚举"""

    PENDING = "pending"  # 待关注
    SUCCESS = "success"  # 关注成功
    FAILED = "failed"  # 关注失败
    SKIPPED = "skipped"  # 跳过
    ALREADY_FOLLOWED = "already_followed"  # 已关注


class ContactPriority(Enum):
    """联系人优先级"""

    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class Contact:
    """联系人数据类"""

    id: str
    platform: str
    username: str
    user_id: str
    profile_url: str = ""
    priority: int = 2
    category: str = ""
    notes: str = ""
    tags: Optional[List[str]] = None
    follow_status: str = "pending"
    retry_count: int = 0
    last_attempt: Optional[str] = None
    assigned_device: Optional[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class ContactsMetadata:
    """通讯录元数据"""

    version: str = "1.0"
    created_time: str = ""
    total_count: int = 0
    description: str = ""

    def __post_init__(self):
        if not self.created_time:
            self.created_time = datetime.now().isoformat()


@dataclass
class ContactsSettings:
    """通讯录设置"""

    max_retry: int = 3
    follow_interval: int = 2
    batch_size: int = 5
    error_threshold: float = 0.2


class ContactsManager:
    """通讯录管理器"""

    def __init__(self, data_dir: str = "data"):
        """初始化通讯录管理器

        Args:
            data_dir: 数据存储目录
        """
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.contacts: List[Contact] = []
        self.metadata: ContactsMetadata = ContactsMetadata()
        self.settings: ContactsSettings = ContactsSettings()

        self.logger.info("📇 通讯录管理器初始化完成")

    def import_from_json(self, file_path: str) -> bool:
        """从JSON文件导入通讯录

        Args:
            file_path: JSON文件路径

        Returns:
            导入是否成功
        """
        try:
            self.logger.info("📥 开始导入通讯录: %s", file_path)

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 验证JSON格式
            if not self._validate_json_format(data):
                self.logger.error("❌ JSON格式验证失败")
                return False

            # 导入元数据
            if "metadata" in data:
                self.metadata = ContactsMetadata(**data["metadata"])

            # 导入设置
            if "settings" in data:
                self.settings = ContactsSettings(**data["settings"])

            # 导入联系人
            self.contacts = []
            for contact_data in data.get("contacts", []):
                contact = Contact(**contact_data)
                self.contacts.append(contact)

            # 更新统计信息
            self.metadata.total_count = len(self.contacts)

            self.logger.info("✅ 通讯录导入成功")
            self.logger.info("   总联系人数: %d", len(self.contacts))
            self.logger.info("   平台分布: %s", self._get_platform_stats())

            return True

        except FileNotFoundError:
            self.logger.error("❌ 文件不存在: %s", file_path)
            return False
        except json.JSONDecodeError as e:
            self.logger.error("❌ JSON解析失败: %s", str(e))
            return False
        except Exception as e:
            self.logger.error("❌ 导入失败: %s", str(e))
            return False

    def _validate_json_format(self, data: Dict) -> bool:
        """验证JSON格式"""
        required_fields = ["contacts"]

        for field in required_fields:
            if field not in data:
                self.logger.error("❌ 缺少必需字段: %s", field)
                return False

        # 验证联系人格式
        contacts = data.get("contacts", [])
        if not isinstance(contacts, list):
            self.logger.error("❌ contacts字段必须是数组")
            return False

        for i, contact in enumerate(contacts):
            required_contact_fields = ["platform", "username", "user_id"]
            for field in required_contact_fields:
                if field not in contact:
                    self.logger.error("❌ 联系人 %d 缺少字段: %s", i, field)
                    return False

        return True

    def _get_platform_stats(self) -> Dict[str, int]:
        """获取平台统计"""
        stats = {}
        for contact in self.contacts:
            platform = contact.platform
            stats[platform] = stats.get(platform, 0) + 1
        return stats

    def export_to_json(self, file_path: str) -> bool:
        """导出通讯录到JSON文件

        Args:
            file_path: 导出文件路径

        Returns:
            导出是否成功
        """
        try:
            data = {
                "metadata": asdict(self.metadata),
                "contacts": [asdict(contact) for contact in self.contacts],
                "settings": asdict(self.settings),
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.logger.info("✅ 通讯录导出成功: %s", file_path)
            return True

        except Exception as e:
            self.logger.error("❌ 导出失败: %s", str(e))
            return False

    def import_from_csv(self, file_path: str) -> bool:
        """从CSV文件导入通讯录（简化格式）

        CSV格式：username,user_id,platform,category,priority,notes
        """
        try:
            import csv

            self.logger.info("📥 从CSV导入通讯录: %s", file_path)

            contacts = []
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    contact = Contact(
                        id=str(uuid.uuid4()),
                        platform=row.get("platform", "xiaohongshu"),
                        username=row.get("username", ""),
                        user_id=row.get("user_id", ""),
                        category=row.get("category", ""),
                        priority=int(row.get("priority", 2)),
                        notes=row.get("notes", ""),
                        tags=row.get("tags", "").split(",") if row.get("tags") else [],
                    )
                    contacts.append(contact)

            self.contacts = contacts
            self.metadata.total_count = len(contacts)

            self.logger.info("✅ CSV导入成功，共 %d 个联系人", len(contacts))
            return True

        except Exception as e:
            self.logger.error("❌ CSV导入失败: %s", str(e))
            return False

    def filter_contacts(
        self,
        platform: str = None,
        status: FollowStatus = None,
        priority: int = None,
        category: str = None,
    ) -> List[Contact]:
        """筛选联系人

        Args:
            platform: 平台筛选
            status: 状态筛选
            priority: 优先级筛选
            category: 分类筛选

        Returns:
            筛选后的联系人列表
        """
        filtered = self.contacts.copy()

        if platform:
            filtered = [c for c in filtered if c.platform == platform]

        if status:
            filtered = [c for c in filtered if c.follow_status == status.value]

        if priority is not None:
            filtered = [c for c in filtered if c.priority == priority]

        if category:
            filtered = [c for c in filtered if c.category == category]

        return filtered

    def get_pending_contacts(self, limit: int = None) -> List[Contact]:
        """获取待处理的联系人

        Args:
            limit: 限制数量

        Returns:
            待处理联系人列表（按优先级排序）
        """
        pending = self.filter_contacts(status=FollowStatus.PENDING)

        # 按优先级排序（优先级数字越小越重要）
        pending.sort(key=lambda x: (x.priority, x.retry_count))

        if limit:
            pending = pending[:limit]

        return pending

    def update_contact_status(
        self, contact_id: str, status: FollowStatus, device_id: str = None
    ) -> bool:
        """更新联系人状态

        Args:
            contact_id: 联系人ID
            status: 新状态
            device_id: 执行设备ID
            error_msg: 错误信息

        Returns:
            更新是否成功
        """
        for contact in self.contacts:
            if contact.id == contact_id:
                contact.follow_status = status.value
                contact.last_attempt = datetime.now().isoformat()

                if device_id:
                    contact.assigned_device = device_id

                if status == FollowStatus.FAILED:
                    contact.retry_count += 1

                self.logger.info(
                    "📝 更新联系人状态: %s -> %s", contact.username, status.value
                )
                return True

        self.logger.warning("⚠️ 未找到联系人: %s", contact_id)
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """获取通讯录统计信息"""
        total = len(self.contacts)

        status_stats = {}
        platform_stats = {}
        priority_stats = {}

        for contact in self.contacts:
            # 状态统计
            status = contact.follow_status
            status_stats[status] = status_stats.get(status, 0) + 1

            # 平台统计
            platform = contact.platform
            platform_stats[platform] = platform_stats.get(platform, 0) + 1

            # 优先级统计
            priority = contact.priority
            priority_stats[priority] = priority_stats.get(priority, 0) + 1

        return {
            "total_contacts": total,
            "status_distribution": status_stats,
            "platform_distribution": platform_stats,
            "priority_distribution": priority_stats,
            "pending_count": status_stats.get("pending", 0),
            "success_rate": (
                status_stats.get("success", 0) / total * 100 if total > 0 else 0
            ),
        }

    def assign_contacts_to_devices(
        self, device_ids: List[str]
    ) -> Dict[str, List[Contact]]:
        """将联系人分配给设备

        Args:
            device_ids: 可用设备ID列表

        Returns:
            设备ID到联系人列表的映射
        """
        if not device_ids:
            self.logger.warning("⚠️ 没有可用设备")
            return {}

        pending_contacts = self.get_pending_contacts()
        if not pending_contacts:
            self.logger.info("📝 没有待处理的联系人")
            return {}

        # 平均分配联系人到设备
        assignments = {device_id: [] for device_id in device_ids}

        for i, contact in enumerate(pending_contacts):
            device_id = device_ids[i % len(device_ids)]
            assignments[device_id].append(contact)
            contact.assigned_device = device_id

        self.logger.info("📋 联系人分配完成:")
        for device_id, contacts in assignments.items():
            self.logger.info("   设备 %s: %d 个联系人", device_id, len(contacts))

        return assignments

    def save_progress(self, file_path: str = None) -> bool:
        """保存进度

        Args:
            file_path: 保存文件路径

        Returns:
            保存是否成功
        """
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.data_dir / f"contacts_progress_{timestamp}.json"

        return self.export_to_json(str(file_path))

    def create_sample_data(self, count: int = 10) -> bool:
        """创建示例数据

        Args:
            count: 创建数量

        Returns:
            创建是否成功
        """
        try:
            sample_contacts = []

            categories = ["美妆", "美食", "旅行", "时尚", "健身", "摄影"]

            for i in range(count):
                contact = Contact(
                    id=f"sample_{i+1:03d}",
                    platform="xiaohongshu",
                    username=f"用户{i+1:03d}",
                    user_id=f"xiaohongshu_user_{i+1:03d}",
                    category=categories[i % len(categories)],
                    priority=(i % 3) + 1,
                    notes=f"示例用户{i+1}",
                    tags=[categories[i % len(categories)], "示例"],
                )
                sample_contacts.append(contact)

            self.contacts = sample_contacts
            self.metadata = ContactsMetadata(
                description=f"示例通讯录数据 - {count}个联系人", total_count=count
            )

            self.logger.info("✅ 创建了 %d 个示例联系人", count)
            return True

        except Exception as e:
            self.logger.error("❌ 创建示例数据失败: %s", str(e))
            return False


def test_contacts_manager():
    """测试通讯录管理器"""
    import logging

    logging.basicConfig(level=logging.INFO)

    print("🧪 测试通讯录管理器")
    print("=" * 50)

    # 创建管理器
    manager = ContactsManager()

    # 创建示例数据
    print("\n📝 创建示例数据...")
    manager.create_sample_data(20)

    # 显示统计信息
    print("\n📊 统计信息:")
    stats = manager.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # 测试筛选
    print("\n🔍 筛选测试:")
    pending = manager.get_pending_contacts(limit=5)
    print(f"   待处理联系人: {len(pending)} 个")

    # 测试设备分配
    print("\n📋 设备分配测试:")
    device_ids = ["emulator-5554", "emulator-5556"]
    assignments = manager.assign_contacts_to_devices(device_ids)

    for device_id, contacts in assignments.items():
        print(f"   设备 {device_id}: {len(contacts)} 个联系人")
        for contact in contacts[:3]:  # 显示前3个
            print(f"     - {contact.username} ({contact.category})")

    # 测试导出
    print("\n💾 导出测试:")
    export_path = "test_contacts.json"
    if manager.export_to_json(export_path):
        print(f"   ✅ 导出成功: {export_path}")

    return manager


if __name__ == "__main__":
    test_contacts_manager()
