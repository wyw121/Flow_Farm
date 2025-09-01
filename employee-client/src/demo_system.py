"""
Flow Farm - 完整系统演示脚本
演示设备连接、通讯录管理和自动化执行的完整流程
"""

import json
import logging
import time
from pathlib import Path

from core.automation_task import XiaohongshuAutomationTask
from core.contacts_manager import Contact, ContactsManager
from core.device_manager import ADBDeviceManager


def setup_logging():
    """设置日志"""
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("demo.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def create_demo_contacts():
    """创建演示用的通讯录数据"""
    demo_contacts = {
        "metadata": {
            "version": "1.0",
            "description": "Flow Farm 演示通讯录",
            "created_time": "2024-01-01T00:00:00",
        },
        "contacts": [
            {
                "id": "demo_001",
                "platform": "xiaohongshu",
                "username": "美妆达人小王",
                "user_id": "xiaohongshu_user_001",
                "category": "美妆",
                "priority": 1,
                "notes": "专业美妆博主，粉丝10万+",
                "tags": ["美妆", "护肤", "优质"],
            },
            {
                "id": "demo_002",
                "platform": "xiaohongshu",
                "username": "旅行摄影师",
                "user_id": "xiaohongshu_user_002",
                "category": "旅行",
                "priority": 2,
                "notes": "旅行摄影师，作品精美",
                "tags": ["旅行", "摄影", "风景"],
            },
            {
                "id": "demo_003",
                "platform": "xiaohongshu",
                "username": "健身教练Lisa",
                "user_id": "xiaohongshu_user_003",
                "category": "健身",
                "priority": 1,
                "notes": "专业健身教练，减肥塑形专家",
                "tags": ["健身", "减肥", "塑形"],
            },
            {
                "id": "demo_004",
                "platform": "xiaohongshu",
                "username": "美食探店王",
                "user_id": "xiaohongshu_user_004",
                "category": "美食",
                "priority": 3,
                "notes": "美食博主，探店达人",
                "tags": ["美食", "探店", "吃播"],
            },
            {
                "id": "demo_005",
                "platform": "xiaohongshu",
                "username": "时尚穿搭师",
                "user_id": "xiaohongshu_user_005",
                "category": "时尚",
                "priority": 2,
                "notes": "时尚穿搭指导，潮流趋势分析",
                "tags": ["时尚", "穿搭", "潮流"],
            },
        ],
        "settings": {
            "max_retry": 3,
            "follow_interval": 3,
            "batch_size": 5,
            "error_threshold": 0.2,
        },
    }

    # 保存演示通讯录
    Path("data").mkdir(exist_ok=True)
    with open("data/demo_contacts.json", "w", encoding="utf-8") as f:
        json.dump(demo_contacts, f, ensure_ascii=False, indent=2)

    print("✅ 演示通讯录已创建: data/demo_contacts.json")
    return "data/demo_contacts.json"


def demo_complete_workflow():
    """演示完整的工作流程"""
    print("🚀 Flow Farm 完整系统演示")
    print("=" * 60)

    # 1. 初始化组件
    print("\n📦 1. 初始化系统组件...")
    device_manager = ADBDeviceManager()
    contacts_manager = ContactsManager()
    automation_task = XiaohongshuAutomationTask(device_manager, contacts_manager)
    print("✅ 系统组件初始化完成")

    # 2. 检查设备连接
    print("\n📱 2. 检查设备连接...")
    devices = device_manager.scan_devices()

    if not devices:
        print("❌ 没有检测到设备")
        print("请确保:")
        print("  - 设备已连接并开启USB调试")
        print("  - 模拟器已启动")
        print("  - ADB驱动正常")
        return False

    print(f"✅ 检测到 {len(devices)} 个设备: {devices}")

    # 获取设备详细信息
    for device_id in devices:
        device_info = device_manager.get_device_info(device_id)
        if device_info:
            print(f"   设备 {device_id}:")
            print(f"     分辨率: {device_info.get('resolution', 'unknown')}")
            print(f"     Android版本: {device_info.get('android_version', 'unknown')}")

            apps = device_info.get("installed_apps", [])
            if "com.xingin.xhs" in apps:
                print("     ✅ 已安装小红书")
            else:
                print("     ⚠️ 未安装小红书")

    # 3. 创建并导入通讯录
    print("\n📇 3. 创建演示通讯录...")
    demo_file = create_demo_contacts()

    print("\n📥 4. 导入通讯录...")
    if not contacts_manager.import_from_json(demo_file):
        print("❌ 通讯录导入失败")
        return False

    # 显示通讯录统计
    stats = contacts_manager.get_statistics()
    print("✅ 通讯录导入成功")
    print(f"   总联系人: {stats['total_contacts']}")
    print(f"   待处理: {stats['pending_count']}")
    print(f"   平台分布: {stats['platform_distribution']}")

    # 4. 分配任务
    print("\n📋 5. 分配任务到设备...")
    assignments = contacts_manager.assign_contacts_to_devices(devices)

    for device_id, contacts in assignments.items():
        print(f"   设备 {device_id}: {len(contacts)} 个联系人")
        for contact in contacts:
            print(
                f"     - {contact.username} ({contact.category}, 优先级{contact.priority})"
            )

    # 5. 询问是否执行
    print("\n🤖 6. 准备执行自动化任务...")
    print("⚠️  注意: 这将在真实设备上执行关注操作")

    user_input = input("是否继续执行? (y/N): ").lower().strip()
    if user_input != "y":
        print("ℹ️ 用户取消执行")
        print("\n🧪 执行模拟测试...")

        # 模拟执行统计
        total_contacts = sum(len(contacts) for contacts in assignments.values())
        success_rate = 85.0  # 模拟成功率
        success_count = int(total_contacts * success_rate / 100)
        failed_count = total_contacts - success_count

        print(f"   📊 模拟执行结果:")
        print(f"     使用设备: {len(devices)} 个")
        print(f"     处理联系人: {total_contacts} 个")
        print(f"     预期成功: {success_count} 个")
        print(f"     预期失败: {failed_count} 个")
        print(f"     预期成功率: {success_rate}%")

        return True

    # 6. 执行自动化任务
    print("\n🚀 7. 执行自动化任务...")
    try:
        results = automation_task.execute_batch_tasks()

        if "error" in results:
            print(f"❌ 执行失败: {results['error']}")
            return False

        if "info" in results:
            print(f"ℹ️ {results['info']}")
            return True

        # 显示执行结果
        print("\n🎉 任务执行完成!")
        print("=" * 40)
        print(f"使用设备: {results['devices_used']} 个")
        print(f"处理联系人: {results['total_processed']}/{results['total_contacts']}")
        print(f"成功: {results['total_success']} 个")
        print(f"失败: {results['total_failed']} 个")
        print(f"成功率: {results['success_rate']:.1f}%")

        # 显示设备详细结果
        print("\n📱 设备执行详情:")
        for device_result in results["device_results"]:
            device_id = device_result["device_id"]
            success_rate = (
                device_result["success"] / device_result["total_contacts"] * 100
                if device_result["total_contacts"] > 0
                else 0
            )
            print(f"   设备 {device_id}:")
            print(
                f"     成功率: {success_rate:.1f}% ({device_result['success']}/{device_result['total_contacts']})"
            )

            if device_result["errors"]:
                print(f"     错误: {len(device_result['errors'])} 个")

        return True

    except Exception as e:
        print(f"❌ 执行过程中发生异常: {str(e)}")
        return False


def demo_device_capabilities():
    """演示设备功能"""
    print("\n🧪 设备功能演示")
    print("=" * 30)

    device_manager = ADBDeviceManager()
    devices = device_manager.scan_devices()

    if not devices:
        print("❌ 没有可用设备")
        return

    device_id = devices[0]
    print(f"📱 使用设备: {device_id}")

    # 测试截图
    print("\n📸 测试截图功能...")
    screenshot_path = f"screenshot_{device_id}.png"
    success, _ = device_manager.take_screenshot(device_id, screenshot_path)
    if success:
        print(f"✅ 截图保存: {screenshot_path}")

    # 测试UI分析
    print("\n🔍 测试UI分析功能...")
    success, ui_xml = device_manager.get_ui_dump(device_id)
    if success:
        from core.ui_analyzer import UIAnalyzer

        analyzer = UIAnalyzer()

        elements = analyzer.parse_ui_xml(ui_xml)
        page_type = analyzer.detect_page_type(ui_xml)
        clickable_elements = analyzer.find_clickable_elements(ui_xml)

        print(f"✅ UI分析完成")
        print(f"   页面类型: {page_type}")
        print(f"   总元素: {len(elements)}")
        print(f"   可点击元素: {len(clickable_elements)}")


def main():
    """主函数"""
    setup_logging()

    print("🔥 Flow Farm 小红书自动化系统")
    print("集成设备管理、通讯录管理和自动化关注功能")
    print("=" * 60)

    try:
        # 演示设备功能
        demo_device_capabilities()

        print("\n" + "=" * 60)

        # 演示完整工作流程
        success = demo_complete_workflow()

        if success:
            print("\n🎉 演示完成!")
            print("\n💡 使用建议:")
            print("  1. 根据实际需要调整通讯录格式")
            print("  2. 设置合适的关注间隔避免被限制")
            print("  3. 定期检查设备连接状态")
            print("  4. 备份通讯录数据")
            print("  5. 监控执行日志")
        else:
            print("\n⚠️ 演示过程中发生问题，请检查日志")

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示异常: {str(e)}")
        logging.exception("演示异常")


if __name__ == "__main__":
    main()
