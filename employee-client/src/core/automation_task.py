"""
Flow Farm - 小红书自动化任务执行器
整合设备管理、UI分析和小红书自动化功能
"""

import logging
import random
import re
import subprocess
import threading
import time
import xml.etree.ElementTree as ET
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .contacts_manager import Contact, ContactsManager, FollowStatus
from .device_manager import ADBDeviceManager
from .ui_analyzer import UIAnalyzer


class AutomationResult(Enum):
    """自动化执行结果"""

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    ALREADY_FOLLOWED = "already_followed"


class XiaohongshuAutomationTask:
    """小红书自动化任务执行器"""

    def __init__(
        self,
        device_manager: ADBDeviceManager,
        contacts_manager: ContactsManager,
        adb_path: str = r"D:\leidian\LDPlayer9\adb.exe",
    ):
        """初始化任务执行器

        Args:
            device_manager: 设备管理器
            contacts_manager: 通讯录管理器
            adb_path: ADB工具路径
        """
        self.logger = logging.getLogger(__name__)
        self.device_manager = device_manager
        self.contacts_manager = contacts_manager
        self.ui_analyzer = UIAnalyzer()
        self.adb_path = adb_path

        # 自动化配置
        self.follow_interval = (2, 5)  # 关注间隔范围(秒)
        self.operation_timeout = 30  # 操作超时时间
        self.max_retries = 3  # 最大重试次数

        # 统计信息
        self.stats = {
            "total_processed": 0,
            "success_count": 0,
            "failed_count": 0,
            "skipped_count": 0,
            "error_count": 0,
        }

        self.logger.info("🤖 小红书自动化任务执行器初始化完成")

    def execute_adb_command(self, device_id: str, command: str) -> Tuple[bool, str]:
        """执行ADB命令

        Args:
            device_id: 设备ID
            command: 命令

        Returns:
            (成功状态, 输出内容)
        """
        try:
            full_command = f'"{self.adb_path}" -s {device_id} {command}'
            self.logger.debug("🔧 执行命令: %s", full_command)

            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=self.operation_timeout,
            )

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                self.logger.warning("⚠️ 命令执行失败: %s", result.stderr)
                return False, result.stderr.strip()

        except subprocess.TimeoutExpired:
            self.logger.error("❌ 命令超时: %s", command)
            return False, "命令执行超时"
        except Exception as e:
            self.logger.error("❌ 命令执行异常: %s", str(e))
            return False, str(e)

    def click_element(self, device_id: str, x: int, y: int) -> bool:
        """点击元素

        Args:
            device_id: 设备ID
            x, y: 坐标

        Returns:
            点击是否成功
        """
        success, _ = self.execute_adb_command(device_id, f"shell input tap {x} {y}")

        if success:
            # 随机等待，模拟人工操作
            wait_time = random.uniform(0.5, 1.5)
            time.sleep(wait_time)
            self.logger.debug("👆 点击坐标: (%d, %d)", x, y)

        return success

    def input_text(self, device_id: str, text: str) -> bool:
        """输入文本

        Args:
            device_id: 设备ID
            text: 文本内容

        Returns:
            输入是否成功
        """
        # 清空输入框
        self.execute_adb_command(device_id, "shell input keyevent KEYCODE_CTRL_A")
        time.sleep(0.2)
        self.execute_adb_command(device_id, "shell input keyevent KEYCODE_DEL")
        time.sleep(0.5)

        # 输入文本
        success, _ = self.execute_adb_command(device_id, f'shell input text "{text}"')

        if success:
            time.sleep(0.5)
            self.logger.debug("⌨️ 输入文本: %s", text)

        return success

    def get_current_page_type(self, device_id: str) -> str:
        """检测当前页面类型

        Args:
            device_id: 设备ID

        Returns:
            页面类型
        """
        success, ui_xml = self.device_manager.get_ui_dump(device_id)
        if not success:
            return "unknown"

        page_type = self.ui_analyzer.detect_page_type(ui_xml)
        self.logger.debug("📱 当前页面类型: %s", page_type)
        return page_type

    def navigate_to_search(self, device_id: str) -> bool:
        """导航到搜索页面

        Args:
            device_id: 设备ID

        Returns:
            导航是否成功
        """
        try:
            self.logger.info("🔍 导航到搜索页面")

            # 获取当前页面
            current_page = self.get_current_page_type(device_id)

            if current_page == "search":
                self.logger.info("✅ 已在搜索页面")
                return True

            # 如果不在主页，先返回主页
            if current_page != "main":
                self.logger.info("🏠 返回主页")
                # 点击返回按钮或主页按钮
                self.execute_adb_command(device_id, "shell input keyevent KEYCODE_BACK")
                time.sleep(2)

            # 查找搜索按钮
            success, ui_xml = self.device_manager.get_ui_dump(device_id)
            if not success:
                return False

            search_elements = self.ui_analyzer.find_elements_by_text(
                ui_xml, ["搜索", "search", "🔍"]
            )

            if search_elements:
                element = search_elements[0]
                coords = self.ui_analyzer.parse_bounds(element.get("bounds", ""))
                if coords:
                    center_x = (coords[0] + coords[2]) // 2
                    center_y = (coords[1] + coords[3]) // 2

                    if self.click_element(device_id, center_x, center_y):
                        time.sleep(2)

                        # 验证是否进入搜索页面
                        if self.get_current_page_type(device_id) == "search":
                            self.logger.info("✅ 成功进入搜索页面")
                            return True

            self.logger.warning("⚠️ 未找到搜索入口")
            return False

        except Exception as e:
            self.logger.error("❌ 导航到搜索页面失败: %s", str(e))
            return False

    def search_user(self, device_id: str, username: str) -> bool:
        """搜索用户

        Args:
            device_id: 设备ID
            username: 用户名

        Returns:
            搜索是否成功
        """
        try:
            self.logger.info("🔍 搜索用户: %s", username)

            # 确保在搜索页面
            if not self.navigate_to_search(device_id):
                return False

            # 查找搜索输入框
            success, ui_xml = self.device_manager.get_ui_dump(device_id)
            if not success:
                return False

            # 查找输入框
            input_elements = self.ui_analyzer.find_elements_by_class(
                ui_xml, "android.widget.EditText"
            )

            if not input_elements:
                self.logger.warning("⚠️ 未找到搜索输入框")
                return False

            # 点击输入框
            element = input_elements[0]
            coords = self.ui_analyzer.parse_bounds(element.get("bounds", ""))
            if not coords:
                return False

            center_x = (coords[0] + coords[2]) // 2
            center_y = (coords[1] + coords[3]) // 2

            if not self.click_element(device_id, center_x, center_y):
                return False

            time.sleep(1)

            # 输入用户名
            if not self.input_text(device_id, username):
                return False

            # 点击搜索按钮或回车
            self.execute_adb_command(device_id, "shell input keyevent KEYCODE_ENTER")
            time.sleep(3)

            self.logger.info("✅ 用户搜索完成")
            return True

        except Exception as e:
            self.logger.error("❌ 搜索用户失败: %s", str(e))
            return False

    def find_and_follow_user(self, device_id: str, username: str) -> AutomationResult:
        """查找并关注用户

        Args:
            device_id: 设备ID
            username: 用户名

        Returns:
            执行结果
        """
        try:
            self.logger.info("👤 开始关注用户: %s", username)

            # 搜索用户
            if not self.search_user(device_id, username):
                return AutomationResult.ERROR

            # 查找用户卡片和关注按钮
            success, ui_xml = self.device_manager.get_ui_dump(device_id)
            if not success:
                return AutomationResult.ERROR

            # 分析页面内容
            follow_buttons = self.ui_analyzer.find_follow_buttons(ui_xml)

            if not follow_buttons:
                self.logger.warning("⚠️ 未找到关注按钮")
                return AutomationResult.FAILED

            # 检查是否已关注
            for button in follow_buttons:
                button_text = button.get("text", "").lower()
                if button_text in ["已关注", "following", "✓"]:
                    self.logger.info("ℹ️ 用户已关注: %s", username)
                    return AutomationResult.ALREADY_FOLLOWED

            # 点击关注按钮
            button = follow_buttons[0]
            coords = self.ui_analyzer.parse_bounds(button.get("bounds", ""))
            if not coords:
                return AutomationResult.ERROR

            center_x = (coords[0] + coords[2]) // 2
            center_y = (coords[1] + coords[3]) // 2

            if self.click_element(device_id, center_x, center_y):
                time.sleep(2)

                # 验证关注是否成功
                success, new_ui_xml = self.device_manager.get_ui_dump(device_id)
                if success:
                    new_buttons = self.ui_analyzer.find_follow_buttons(new_ui_xml)
                    for button in new_buttons:
                        button_text = button.get("text", "").lower()
                        if button_text in ["已关注", "following", "✓"]:
                            self.logger.info("✅ 关注成功: %s", username)
                            return AutomationResult.SUCCESS

                self.logger.info("✅ 关注操作已执行: %s", username)
                return AutomationResult.SUCCESS
            else:
                return AutomationResult.FAILED

        except Exception as e:
            self.logger.error("❌ 关注用户失败: %s", str(e))
            return AutomationResult.ERROR

    def process_contact(self, device_id: str, contact: Contact) -> AutomationResult:
        """处理单个联系人

        Args:
            device_id: 设备ID
            contact: 联系人信息

        Returns:
            处理结果
        """
        try:
            self.logger.info(
                "📞 处理联系人: %s (%s)", contact.username, contact.platform
            )

            # 检查平台支持
            if contact.platform.lower() != "xiaohongshu":
                self.logger.warning("⚠️ 不支持的平台: %s", contact.platform)
                return AutomationResult.SKIPPED

            # 执行关注操作
            result = self.find_and_follow_user(device_id, contact.username)

            # 更新统计
            self.stats["total_processed"] += 1
            if result == AutomationResult.SUCCESS:
                self.stats["success_count"] += 1
                status = FollowStatus.SUCCESS
            elif result == AutomationResult.ALREADY_FOLLOWED:
                self.stats["success_count"] += 1
                status = FollowStatus.ALREADY_FOLLOWED
            elif result == AutomationResult.FAILED:
                self.stats["failed_count"] += 1
                status = FollowStatus.FAILED
            elif result == AutomationResult.SKIPPED:
                self.stats["skipped_count"] += 1
                status = FollowStatus.SKIPPED
            else:
                self.stats["error_count"] += 1
                status = FollowStatus.FAILED

            # 更新联系人状态
            self.contacts_manager.update_contact_status(contact.id, status, device_id)

            # 随机等待，避免被检测
            wait_time = random.uniform(*self.follow_interval)
            self.logger.debug("⏱️ 等待 %.1f 秒", wait_time)
            time.sleep(wait_time)

            return result

        except Exception as e:
            self.logger.error("❌ 处理联系人失败: %s", str(e))
            return AutomationResult.ERROR

    def execute_device_tasks(self, device_id: str, contacts: List[Contact]) -> Dict:
        """执行设备任务

        Args:
            device_id: 设备ID
            contacts: 联系人列表

        Returns:
            执行结果统计
        """
        device_stats = {
            "device_id": device_id,
            "total_contacts": len(contacts),
            "processed": 0,
            "success": 0,
            "failed": 0,
            "errors": [],
        }

        try:
            self.logger.info(
                "🔄 设备 %s 开始处理 %d 个联系人", device_id, len(contacts)
            )

            # 检查设备状态
            if not self.device_manager.is_device_available(device_id):
                error_msg = f"设备 {device_id} 不可用"
                self.logger.error("❌ %s", error_msg)
                device_stats["errors"].append(error_msg)
                return device_stats

            # 启动小红书应用
            self.logger.info("📱 启动小红书应用")
            self.execute_adb_command(
                device_id, "shell am start -n com.xingin.xhs/.activity.SplashActivity"
            )
            time.sleep(5)

            # 处理每个联系人
            for i, contact in enumerate(contacts, 1):
                try:
                    self.logger.info("📋 处理进度: %d/%d", i, len(contacts))

                    result = self.process_contact(device_id, contact)
                    device_stats["processed"] += 1

                    if result in [
                        AutomationResult.SUCCESS,
                        AutomationResult.ALREADY_FOLLOWED,
                    ]:
                        device_stats["success"] += 1
                    else:
                        device_stats["failed"] += 1

                except Exception as e:
                    error_msg = f"处理联系人 {contact.username} 失败: {str(e)}"
                    self.logger.error("❌ %s", error_msg)
                    device_stats["errors"].append(error_msg)
                    device_stats["failed"] += 1

            success_rate = (
                device_stats["success"] / device_stats["total_contacts"] * 100
                if device_stats["total_contacts"] > 0
                else 0
            )

            self.logger.info("✅ 设备 %s 任务完成", device_id)
            self.logger.info(
                "   成功率: %.1f%% (%d/%d)",
                success_rate,
                device_stats["success"],
                device_stats["total_contacts"],
            )

        except Exception as e:
            error_msg = f"设备任务执行失败: {str(e)}"
            self.logger.error("❌ %s", error_msg)
            device_stats["errors"].append(error_msg)

        return device_stats

    def execute_batch_tasks(self, max_devices: int = None) -> Dict:
        """执行批量任务

        Args:
            max_devices: 最大设备数量限制

        Returns:
            执行结果统计
        """
        try:
            self.logger.info("🚀 开始执行批量关注任务")

            # 获取可用设备
            available_devices = self.device_manager.scan_devices()
            if not available_devices:
                self.logger.error("❌ 没有可用设备")
                return {"error": "没有可用设备"}

            if max_devices:
                available_devices = available_devices[:max_devices]

            self.logger.info(
                "📱 检测到 %d 个可用设备: %s", len(available_devices), available_devices
            )

            # 分配联系人到设备
            assignments = self.contacts_manager.assign_contacts_to_devices(
                available_devices
            )

            if not any(assignments.values()):
                self.logger.info("ℹ️ 没有待处理的联系人")
                return {"info": "没有待处理的联系人"}

            # 重置统计
            self.stats = {key: 0 for key in self.stats}

            # 并行执行设备任务
            device_results = []
            threads = []

            def worker(device_id, contacts):
                result = self.execute_device_tasks(device_id, contacts)
                device_results.append(result)

            # 启动线程
            for device_id, contacts in assignments.items():
                if contacts:  # 只处理有联系人的设备
                    thread = threading.Thread(target=worker, args=(device_id, contacts))
                    thread.start()
                    threads.append(thread)

            # 等待所有线程完成
            for thread in threads:
                thread.join()

            # 汇总结果
            total_stats = {
                "devices_used": len([r for r in device_results if r["processed"] > 0]),
                "total_contacts": sum(r["total_contacts"] for r in device_results),
                "total_processed": sum(r["processed"] for r in device_results),
                "total_success": sum(r["success"] for r in device_results),
                "total_failed": sum(r["failed"] for r in device_results),
                "success_rate": 0,
                "device_results": device_results,
                "errors": [],
            }

            # 收集错误
            for result in device_results:
                total_stats["errors"].extend(result.get("errors", []))

            # 计算成功率
            if total_stats["total_contacts"] > 0:
                total_stats["success_rate"] = (
                    total_stats["total_success"] / total_stats["total_contacts"] * 100
                )

            self.logger.info("🎉 批量任务执行完成")
            self.logger.info("   使用设备: %d 个", total_stats["devices_used"])
            self.logger.info(
                "   处理联系人: %d/%d",
                total_stats["total_processed"],
                total_stats["total_contacts"],
            )
            self.logger.info("   成功率: %.1f%%", total_stats["success_rate"])

            # 保存进度
            self.contacts_manager.save_progress()

            return total_stats

        except Exception as e:
            self.logger.error("❌ 批量任务执行失败: %s", str(e))
            return {"error": str(e)}

    def get_execution_stats(self) -> Dict:
        """获取执行统计信息"""
        return self.stats.copy()


def test_automation_task():
    """测试自动化任务执行器"""
    import logging

    logging.basicConfig(level=logging.INFO)

    print("🧪 测试小红书自动化任务执行器")
    print("=" * 50)

    # 创建组件
    device_manager = ADBDeviceManager()
    contacts_manager = ContactsManager()

    # 创建示例数据
    contacts_manager.create_sample_data(5)

    # 创建任务执行器
    automation = XiaohongshuAutomationTask(device_manager, contacts_manager)

    # 显示可用设备
    devices = device_manager.scan_devices()
    print(f"\n📱 可用设备: {devices}")

    if devices:
        # 测试单个联系人处理
        contacts = contacts_manager.get_pending_contacts(limit=1)
        if contacts:
            contact = contacts[0]
            print(f"\n🧪 测试处理联系人: {contact.username}")

            result = automation.process_contact(devices[0], contact)
            print(f"   结果: {result.value}")

    # 显示统计信息
    stats = automation.get_execution_stats()
    print(f"\n📊 执行统计: {stats}")

    return automation


if __name__ == "__main__":
    test_automation_task()
