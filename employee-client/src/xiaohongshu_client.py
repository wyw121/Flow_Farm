"""
Flow Farm - 小红书自动化客户端主程序
提供通讯录管理和自动化关注功能
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

from core.automation_task import XiaohongshuAutomationTask
from core.contacts_manager import ContactsManager
from core.device_manager import ADBDeviceManager


class FlowFarmClient:
    """Flow Farm 客户端主程序"""

    def __init__(self):
        """初始化客户端"""
        self.setup_logging()
        self.logger = logging.getLogger(__name__)

        # 初始化组件
        self.device_manager = ADBDeviceManager()
        self.contacts_manager = ContactsManager()
        self.automation_task = XiaohongshuAutomationTask(
            self.device_manager, self.contacts_manager
        )

        self.logger.info("🚀 Flow Farm 客户端启动")

    def setup_logging(self):
        """设置日志"""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler("flow_farm_client.log", encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )

    def check_devices(self) -> Dict[str, Any]:
        """检查设备状态"""
        print("📱 正在扫描设备...")
        devices = self.device_manager.scan_devices()

        result = {"total_devices": len(devices), "devices": []}

        for device_id in devices:
            device_info = self.device_manager.get_device_info(device_id)
            if device_info:
                result["devices"].append(
                    {
                        "id": device_id,
                        "info": device_info,
                        "available": self.device_manager.is_device_available(device_id),
                    }
                )

        print(f"✅ 发现 {len(devices)} 个设备")
        for device in result["devices"]:
            status = "✅ 可用" if device["available"] else "❌ 不可用"
            print(f"   设备: {device['id']} - {status}")
            if device["info"]:
                print(f"     分辨率: {device['info'].get('resolution', 'unknown')}")
                print(
                    f"     Android: {device['info'].get('android_version', 'unknown')}"
                )
                if device["info"].get("installed_apps"):
                    apps = ", ".join(device["info"]["installed_apps"])
                    print(f"     已安装应用: {apps}")

        return result

    def import_contacts(self, file_path: str, file_type: str = "json") -> bool:
        """导入通讯录"""
        print(f"📥 导入通讯录: {file_path}")

        if not Path(file_path).exists():
            print(f"❌ 文件不存在: {file_path}")
            return False

        if file_type.lower() == "json":
            success = self.contacts_manager.import_from_json(file_path)
        elif file_type.lower() == "csv":
            success = self.contacts_manager.import_from_csv(file_path)
        else:
            print(f"❌ 不支持的文件类型: {file_type}")
            return False

        if success:
            stats = self.contacts_manager.get_statistics()
            print("✅ 通讯录导入成功")
            print(f"   总联系人数: {stats['total_contacts']}")
            print(f"   待处理: {stats['pending_count']}")
            print(f"   平台分布: {stats['platform_distribution']}")

        return success

    def create_sample_contacts(self, count: int = 10) -> bool:
        """创建示例通讯录"""
        print(f"📝 创建 {count} 个示例联系人...")

        if self.contacts_manager.create_sample_data(count):
            # 保存示例数据
            sample_file = "data/sample_contacts.json"
            Path("data").mkdir(exist_ok=True)

            if self.contacts_manager.export_to_json(sample_file):
                print(f"✅ 示例通讯录已保存: {sample_file}")
                return True

        return False

    def show_contacts_stats(self):
        """显示通讯录统计"""
        stats = self.contacts_manager.get_statistics()

        print("📊 通讯录统计信息")
        print("=" * 40)
        print(f"总联系人数: {stats['total_contacts']}")
        print(f"待处理数量: {stats['pending_count']}")
        print(f"成功率: {stats['success_rate']:.1f}%")

        print("\n平台分布:")
        for platform, count in stats["platform_distribution"].items():
            print(f"  {platform}: {count}")

        print("\n状态分布:")
        for status, count in stats["status_distribution"].items():
            print(f"  {status}: {count}")

        print("\n优先级分布:")
        for priority, count in stats["priority_distribution"].items():
            priority_name = {1: "高", 2: "中", 3: "低"}.get(priority, priority)
            print(f"  {priority_name}: {count}")

    def execute_automation(self, max_devices: int = None, dry_run: bool = False):
        """执行自动化任务"""
        print("🤖 开始执行自动化关注任务")
        print("=" * 50)

        # 检查设备
        device_info = self.check_devices()
        if device_info["total_devices"] == 0:
            print("❌ 没有可用设备，请检查设备连接")
            return False

        # 检查通讯录
        stats = self.contacts_manager.get_statistics()
        if stats["pending_count"] == 0:
            print("ℹ️ 没有待处理的联系人")
            return True

        print(f"📋 待处理联系人: {stats['pending_count']} 个")

        if dry_run:
            print("🔍 模拟执行模式（不会实际执行操作）")
            # 显示分配计划
            devices = [d["id"] for d in device_info["devices"] if d["available"]]
            if max_devices:
                devices = devices[:max_devices]

            assignments = self.contacts_manager.assign_contacts_to_devices(devices)

            print("\n📋 任务分配计划:")
            for device_id, contacts in assignments.items():
                print(f"  设备 {device_id}: {len(contacts)} 个联系人")
                for contact in contacts[:3]:  # 显示前3个
                    print(f"    - {contact.username} ({contact.category})")
                if len(contacts) > 3:
                    print(f"    ... 还有 {len(contacts) - 3} 个")

            return True

        # 执行任务
        try:
            results = self.automation_task.execute_batch_tasks(max_devices)

            if "error" in results:
                print(f"❌ 执行失败: {results['error']}")
                return False

            if "info" in results:
                print(f"ℹ️ {results['info']}")
                return True

            # 显示执行结果
            print("\n🎉 任务执行完成")
            print("=" * 30)
            print(f"使用设备: {results['devices_used']} 个")
            print(
                f"处理联系人: {results['total_processed']}/{results['total_contacts']}"
            )
            print(f"成功: {results['total_success']} 个")
            print(f"失败: {results['total_failed']} 个")
            print(f"成功率: {results['success_rate']:.1f}%")

            if results["errors"]:
                print(f"\n⚠️ 发生 {len(results['errors'])} 个错误:")
                for error in results["errors"][:5]:  # 显示前5个错误
                    print(f"  - {error}")
                if len(results["errors"]) > 5:
                    print(f"  ... 还有 {len(results['errors']) - 5} 个错误")

            return True

        except Exception as e:
            print(f"❌ 执行过程中发生异常: {str(e)}")
            return False

    def export_contacts(self, file_path: str) -> bool:
        """导出通讯录"""
        print(f"💾 导出通讯录: {file_path}")

        if self.contacts_manager.export_to_json(file_path):
            print("✅ 通讯录导出成功")
            return True
        else:
            print("❌ 通讯录导出失败")
            return False

    def show_help(self):
        """显示帮助信息"""
        help_text = """
🔥 Flow Farm 小红书自动化客户端

主要功能:
  📱 设备管理 - 检测和管理Android设备/模拟器
  📇 通讯录管理 - 导入、管理、导出联系人信息
  🤖 自动化关注 - 批量关注小红书用户

支持的通讯录格式:
  📄 JSON格式 - 完整的联系人信息（推荐）
  📄 CSV格式 - 简化的联系人信息

常用命令:
  python xiaohongshu_client.py --check-devices
  python xiaohongshu_client.py --import contacts.json
  python xiaohongshu_client.py --create-sample 20
  python xiaohongshu_client.py --stats
  python xiaohongshu_client.py --run --max-devices 2
  python xiaohongshu_client.py --run --dry-run

通讯录格式示例:
  {
    "metadata": {
      "version": "1.0",
      "description": "我的小红书通讯录"
    },
    "contacts": [
      {
        "platform": "xiaohongshu",
        "username": "美妆达人小王",
        "user_id": "xiaohongshu_user_001",
        "category": "美妆",
        "priority": 1,
        "notes": "优质美妆博主"
      }
    ],
    "settings": {
      "follow_interval": 3,
      "batch_size": 10
    }
  }
        """.strip()

        print(help_text)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Flow Farm 小红书自动化客户端",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # 设备管理
    parser.add_argument("--check-devices", action="store_true", help="检查设备状态")

    # 通讯录管理
    parser.add_argument(
        "--import", dest="import_file", metavar="FILE", help="导入通讯录文件 (JSON/CSV)"
    )
    parser.add_argument(
        "--file-type",
        choices=["json", "csv"],
        default="json",
        help="文件类型 (default: json)",
    )
    parser.add_argument(
        "--export", dest="export_file", metavar="FILE", help="导出通讯录文件"
    )
    parser.add_argument(
        "--create-sample", type=int, metavar="COUNT", help="创建示例通讯录"
    )
    parser.add_argument("--stats", action="store_true", help="显示通讯录统计")

    # 任务执行
    parser.add_argument("--run", action="store_true", help="执行自动化任务")
    parser.add_argument("--max-devices", type=int, metavar="N", help="最大使用设备数量")
    parser.add_argument("--dry-run", action="store_true", help="模拟执行（不实际操作）")

    # 其他
    parser.add_argument("--help-detailed", action="store_true", help="显示详细帮助")

    args = parser.parse_args()

    # 创建客户端
    client = FlowFarmClient()

    # 执行命令
    try:
        if args.help_detailed:
            client.show_help()
        elif args.check_devices:
            client.check_devices()
        elif args.import_file:
            client.import_contacts(args.import_file, args.file_type)
        elif args.export_file:
            client.export_contacts(args.export_file)
        elif args.create_sample:
            client.create_sample_contacts(args.create_sample)
        elif args.stats:
            client.show_contacts_stats()
        elif args.run:
            client.execute_automation(args.max_devices, args.dry_run)
        else:
            # 默认显示设备状态和统计
            print("👋 欢迎使用 Flow Farm 小红书自动化客户端")
            print("使用 --help 查看所有选项，--help-detailed 查看详细帮助\n")

            client.check_devices()
            print()
            client.show_contacts_stats()

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"❌ 程序异常: {str(e)}")
        client.logger.exception("程序异常")


if __name__ == "__main__":
    main()
