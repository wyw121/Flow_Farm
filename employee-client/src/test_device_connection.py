#!/usr/bin/env python3
"""
Flow Farm - 设备连接和界面识别测试脚本
综合测试ADB设备管理和UI界面分析功能

使用方法:
python test_device_connection.py
"""

import logging
import os
import sys
import time
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.device_manager import ADBDeviceManager
from core.ui_analyzer import UIAnalyzer


def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("device_test.log", encoding="utf-8"),
        ],
    )


def test_adb_connection():
    """测试ADB连接功能"""
    print("\n" + "=" * 60)
    print("🔧 ADB设备连接测试")
    print("=" * 60)

    # 创建设备管理器
    device_manager = ADBDeviceManager()

    # 测试ADB命令执行
    print("\n📡 测试ADB基础功能...")
    stdout, stderr = device_manager.execute_adb_command("version")

    if stdout:
        print(f"✅ ADB版本信息:")
        for line in stdout.split("\n"):
            if line.strip():
                print(f"   {line}")
    else:
        print(f"❌ ADB命令执行失败: {stderr}")
        return None

    # 扫描设备
    print("\n🔍 扫描连接的设备...")
    devices = device_manager.scan_devices()

    if not devices:
        print("❌ 未发现设备，请检查：")
        print("   1. 设备是否已连接并启用USB调试")
        print("   2. 是否已授权此计算机进行调试")
        print("   3. USB线是否支持数据传输")
        print("   4. 尝试运行: adb devices")
        return None

    print(f"✅ 发现 {len(devices)} 台设备:")
    for i, device in enumerate(devices, 1):
        print(f"\n📱 设备 {i}:")
        print(f"   ID: {device.device_id}")
        print(f"   型号: {device.model}")
        print(f"   Android版本: {device.android_version}")
        print(f"   分辨率: {device.screen_resolution}")
        print(f"   电池电量: {device.battery_level}%")
        print(f"   状态: {device.status.value}")

        if device.capabilities:
            print(f"   已安装应用:")
            for app in device.capabilities:
                app_name = {
                    "com.ss.android.ugc.aweme": "抖音",
                    "com.xingin.xhs": "小红书",
                }.get(app, app)
                print(f"     - {app_name}")
        else:
            print(f"   未发现目标应用")

    return device_manager, devices


def test_screenshot_and_ui(device_manager, devices):
    """测试截图和UI获取功能"""
    if not devices:
        return None, None

    test_device = devices[0]
    print(f"\n📸 使用设备 {test_device.device_id} 进行截图和UI测试...")

    # 测试截图
    print("\n📷 测试截图功能...")
    screenshot_path = device_manager.take_screenshot(
        test_device.device_id, f"test_screenshot_{int(time.time())}.png"
    )

    if screenshot_path and os.path.exists(screenshot_path):
        print(f"✅ 截图成功: {screenshot_path}")
        file_size = os.path.getsize(screenshot_path) / 1024  # KB
        print(f"   文件大小: {file_size:.1f} KB")
    else:
        print("❌ 截图失败")
        screenshot_path = None

    # 测试UI dump
    print("\n📋 测试UI结构获取...")
    ui_xml_path = device_manager.get_ui_dump(
        test_device.device_id, f"test_ui_dump_{int(time.time())}.xml"
    )

    if ui_xml_path and os.path.exists(ui_xml_path):
        print(f"✅ UI dump成功: {ui_xml_path}")
        file_size = os.path.getsize(ui_xml_path) / 1024  # KB
        print(f"   文件大小: {file_size:.1f} KB")

        # 快速检查XML内容
        try:
            with open(ui_xml_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "hierarchy" in content:
                    print("   ✅ XML结构正常")
                else:
                    print("   ⚠️ XML结构可能有问题")
        except Exception as e:
            print(f"   ❌ XML读取失败: {e}")
    else:
        print("❌ UI dump失败")
        ui_xml_path = None

    return screenshot_path, ui_xml_path


def test_ui_analysis(ui_xml_path):
    """测试UI分析功能"""
    if not ui_xml_path:
        print("\n⚠️ 跳过UI分析测试 - 无UI XML文件")
        return None

    print(f"\n🔍 测试UI界面分析...")
    print("=" * 40)

    # 创建UI分析器
    analyzer = UIAnalyzer()

    # 解析UI XML
    elements = analyzer.parse_ui_xml(ui_xml_path)

    if not elements:
        print("❌ UI解析失败")
        return None

    print(f"✅ 解析成功，发现 {len(elements)} 个UI元素")

    # 获取元素统计
    summary = analyzer.get_element_summary()
    print(f"\n📊 元素统计:")
    for key, value in summary.items():
        print(f"   {key}: {value}")

    # 检测页面类型
    print(f"\n📱 页面类型检测:")
    page_info = analyzer.detect_page_type()
    print(f"   应用: {page_info['app']}")
    print(f"   页面类型: {page_info['type']}")
    print(f"   特征: {page_info['features']}")

    # 查找可点击元素
    clickable_elements = analyzer.find_clickable_elements()
    print(f"\n👆 可点击元素: {len(clickable_elements)} 个")

    # 显示前5个可点击元素的信息
    for i, element in enumerate(clickable_elements[:5]):
        print(f"   {i+1}. {element.text or element.content_desc or '无文本'}")
        print(f"      位置: ({element.center_x}, {element.center_y})")
        print(f"      大小: {element.width}x{element.height}")

    # 查找关注按钮（如果是社交媒体应用）
    if page_info["app"] in ["douyin", "xiaohongshu"]:
        follow_buttons = analyzer.find_follow_buttons()
        print(f"\n🎯 关注按钮: {len(follow_buttons)} 个")

        for i, button in enumerate(follow_buttons):
            print(f"   {i+1}. '{button.text}'")
            print(f"      位置: ({button.center_x}, {button.center_y})")

    # 导出详细分析报告
    report_path = f"ui_analysis_report_{int(time.time())}.txt"
    analyzer.export_element_info(report_path)
    print(f"\n📄 详细报告已保存: {report_path}")

    return analyzer


def test_device_interaction(device_manager, devices):
    """测试设备交互功能"""
    if not devices:
        return

    test_device = devices[0]
    print(f"\n🎮 测试设备交互功能...")
    print("=" * 40)

    # 获取屏幕分辨率用于安全点击测试
    resolution = test_device.screen_resolution
    if resolution and "x" in resolution:
        try:
            width, height = map(int, resolution.split("x"))

            # 点击屏幕中心（相对安全的位置）
            center_x = width // 2
            center_y = height // 2

            print(f"📱 屏幕分辨率: {width}x{height}")
            print(f"🎯 测试点击屏幕中心: ({center_x}, {center_y})")

            # 询问用户是否进行交互测试
            response = input(
                "\n⚠️  是否进行点击测试？这会在设备屏幕中心点击一次 (y/N): "
            )

            if response.lower() == "y":
                success = device_manager.click_coordinate(
                    test_device.device_id, center_x, center_y
                )

                if success:
                    print("✅ 点击测试成功")
                else:
                    print("❌ 点击测试失败")
            else:
                print("⏭️ 跳过交互测试")

        except ValueError:
            print("⚠️ 无法解析屏幕分辨率，跳过交互测试")
    else:
        print("⚠️ 未获取到屏幕分辨率，跳过交互测试")


def main():
    """主测试函数"""
    import time

    print("🚀 Flow Farm 设备连接和界面识别测试")
    print("=" * 60)
    print("本测试将验证以下功能:")
    print("1. ADB设备连接和管理")
    print("2. 设备截图功能")
    print("3. UI结构获取")
    print("4. UI界面分析")
    print("5. 设备交互测试")
    print()

    # 设置日志
    setup_logging()

    try:
        # 1. 测试ADB连接
        result = test_adb_connection()
        if result is None:
            print("\n❌ ADB连接测试失败，无法继续")
            return 1

        device_manager, devices = result

        # 2. 测试截图和UI获取
        screenshot_path, ui_xml_path = test_screenshot_and_ui(device_manager, devices)

        # 3. 测试UI分析
        analyzer = test_ui_analysis(ui_xml_path)

        # 4. 测试设备交互
        test_device_interaction(device_manager, devices)

        # 5. 显示测试结果摘要
        print("\n" + "=" * 60)
        print("📊 测试结果摘要")
        print("=" * 60)

        status_summary = device_manager.get_device_status_summary()
        print(f"设备状态: {status_summary}")

        print(f"\n测试文件:")
        if screenshot_path:
            print(f"  📸 截图: {screenshot_path}")
        if ui_xml_path:
            print(f"  📋 UI XML: {ui_xml_path}")
        if analyzer:
            print(f"  📄 分析报告: ui_analysis_report_*.txt")

        print(f"\n✅ 测试完成！")
        return 0

    except KeyboardInterrupt:
        print("\n\n🛑 用户中断测试")
        return 1
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        # 清理资源
        if "device_manager" in locals():
            device_manager.stop_monitoring()


if __name__ == "__main__":
    sys.exit(main())
