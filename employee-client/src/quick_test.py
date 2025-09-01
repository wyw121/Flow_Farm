"""
Flow Farm - 快速测试脚本
测试集成系统的基本功能
"""

import json
import logging
import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.contacts_manager import ContactsManager
from core.device_manager import ADBDeviceManager
from core.ui_analyzer import UIAnalyzer


def setup_logging():
    """设置简单日志"""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def test_device_manager():
    """测试设备管理器"""
    print("🧪 测试设备管理器")
    print("-" * 30)

    device_manager = ADBDeviceManager()

    # 扫描设备
    devices = device_manager.scan_devices()
    print(
        f"发现设备: {[d.device_id if hasattr(d, 'device_id') else str(d) for d in devices]}"
    )

    if devices:
        device_info = devices[0]  # 这是一个DeviceInfo对象
        device_id = (
            device_info.device_id
            if hasattr(device_info, "device_id")
            else str(device_info)
        )
        print(f"使用设备: {device_id}")

        # 显示设备信息
        print(f"设备信息: {device_info}")

        # 测试截图
        screenshot_path = device_manager.take_screenshot(
            device_id, "test_screenshot.png"
        )
        if screenshot_path:
            print(f"截图成功: {screenshot_path}")

        # 测试UI dump
        ui_xml = device_manager.get_ui_dump(device_id)
        if ui_xml:
            print(f"UI dump成功，长度: {len(ui_xml)}")

            # 简单分析UI
            analyzer = UIAnalyzer()
            elements = analyzer.parse_ui_xml(ui_xml)
            print(f"解析到 {len(elements)} 个UI元素")

    return [d.device_id if hasattr(d, "device_id") else str(d) for d in devices]


def test_contacts_manager():
    """测试通讯录管理器"""
    print("\n🧪 测试通讯录管理器")
    print("-" * 30)

    contacts_manager = ContactsManager()

    # 创建示例数据
    print("创建示例数据...")
    contacts_manager.create_sample_data(5)

    # 显示统计
    stats = contacts_manager.get_statistics()
    print(f"统计信息: {stats}")

    # 获取待处理联系人
    pending = contacts_manager.get_pending_contacts(limit=3)
    print(f"待处理联系人: {len(pending)} 个")
    for contact in pending:
        print(f"  - {contact.username} ({contact.platform})")

    return contacts_manager


def test_task_assignment():
    """测试任务分配"""
    print("\n🧪 测试任务分配")
    print("-" * 30)

    # 创建组件
    device_manager = ADBDeviceManager()
    contacts_manager = ContactsManager()

    # 创建数据
    contacts_manager.create_sample_data(10)
    device_objects = device_manager.scan_devices()

    # 提取设备ID
    devices = [
        d.device_id if hasattr(d, "device_id") else str(d) for d in device_objects
    ]

    if devices:
        print(f"可用设备: {devices}")

        # 分配任务
        assignments = contacts_manager.assign_contacts_to_devices(devices)

        print("任务分配结果:")
        for device_id, contacts in assignments.items():
            print(f"  设备 {device_id}: {len(contacts)} 个联系人")
            for contact in contacts[:2]:  # 显示前2个
                print(f"    - {contact.username}")
    else:
        print("没有可用设备")


def create_simple_demo_data():
    """创建简单的演示数据"""
    demo_data = {
        "metadata": {"version": "1.0", "description": "简单演示数据"},
        "contacts": [
            {
                "id": "demo_001",
                "platform": "xiaohongshu",
                "username": "测试用户1",
                "user_id": "test_001",
                "category": "测试",
                "priority": 1,
            },
            {
                "id": "demo_002",
                "platform": "xiaohongshu",
                "username": "测试用户2",
                "user_id": "test_002",
                "category": "测试",
                "priority": 2,
            },
        ],
        "settings": {"follow_interval": 2, "batch_size": 5},
    }

    # 保存数据
    Path("data").mkdir(exist_ok=True)
    with open("data/simple_demo.json", "w", encoding="utf-8") as f:
        json.dump(demo_data, f, ensure_ascii=False, indent=2)

    print("✅ 简单演示数据已创建: data/simple_demo.json")


def main():
    """主测试函数"""
    setup_logging()

    print("🔥 Flow Farm 快速测试")
    print("=" * 50)

    try:
        # 1. 测试设备管理
        devices = test_device_manager()

        # 2. 测试通讯录管理
        contacts_manager = test_contacts_manager()

        # 3. 测试任务分配
        test_task_assignment()

        # 4. 创建演示数据
        print("\n📝 创建演示数据")
        print("-" * 30)
        create_simple_demo_data()

        # 5. 测试导入
        print("\n📥 测试导入功能")
        print("-" * 30)
        new_manager = ContactsManager()
        if new_manager.import_from_json("data/simple_demo.json"):
            print("✅ 导入成功")
            stats = new_manager.get_statistics()
            print(f"导入后统计: {stats}")

        print("\n🎉 所有测试完成!")

        if devices:
            print(f"\n💡 系统就绪:")
            print(f"  - 检测到 {len(devices)} 个设备")
            print(f"  - 通讯录管理正常")
            print(f"  - 任务分配正常")
            print(f"\n可以使用 xiaohongshu_client.py 开始自动化任务")
        else:
            print(f"\n⚠️ 注意:")
            print(f"  - 未检测到设备")
            print(f"  - 请启动模拟器或连接设备")
            print(f"  - 确保ADB驱动正常")

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        logging.exception("测试异常")


if __name__ == "__main__":
    main()
