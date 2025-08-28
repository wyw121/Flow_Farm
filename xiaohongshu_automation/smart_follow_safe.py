#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书安全自动关注工具 - 修正版本
避免返回键退出APP，直接从当前页面开始导航
"""

import subprocess
import time
import xml.etree.ElementTree as ET
import re

class XiaohongshuSafeAutomation:
    def __init__(self):
        self.adb_path = r"D:\leidian\LDPlayer9\adb.exe"
        self.current_step = "初始化"
        self.step_results = {}

    def run_adb_command(self, command):
        """执行ADB命令"""
        try:
            full_command = f'"{self.adb_path}" {command}'
            result = subprocess.run(full_command, shell=True, capture_output=True, text=True, encoding='utf-8')
            return result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return "", str(e)

    def click_coordinate(self, x, y, description="", wait_time=2):
        """点击指定坐标并等待"""
        _, stderr = self.run_adb_command(f"shell input tap {x} {y}")
        print(f"    🖱️ 点击 {description} 坐标 ({x}, {y})")
        if stderr:
            print(f"    ❌ 点击错误: {stderr}")
            return False
        time.sleep(wait_time)
        return True

    def get_ui_info(self, filename="current_ui.xml"):
        """获取当前UI信息"""
        self.run_adb_command(f"shell uiautomator dump /sdcard/{filename}")
        self.run_adb_command(f"pull /sdcard/{filename} {filename}")
        time.sleep(0.5)

    def find_element_by_text(self, text_list, ui_file="current_ui.xml"):
        """根据文本查找UI元素"""
        try:
            tree = ET.parse(ui_file)
            root = tree.getroot()

            found_elements = []
            for elem in root.iter():
                text = elem.get('text', '')
                content_desc = elem.get('content-desc', '')

                for target_text in text_list:
                    if target_text in text or target_text in content_desc:
                        bounds = elem.get('bounds', '')
                        clickable = elem.get('clickable', 'false')

                        if bounds:
                            coords = re.findall(r'\d+', bounds)
                            if len(coords) >= 4:
                                x1, y1, x2, y2 = map(int, coords[:4])
                                center_x = (x1 + x2) // 2
                                center_y = (y1 + y2) // 2
                                found_elements.append({
                                    'text': text or content_desc,
                                    'position': (center_x, center_y),
                                    'clickable': clickable
                                })

            return found_elements
        except Exception as e:
            print(f"    ❌ 查找元素失败: {e}")
            return []

    def detect_current_page(self):
        """智能检测当前页面类型"""
        print("🔍 智能检测当前页面状态...")
        self.get_ui_info("detect_page.xml")

        # 检查关注推荐页面 (优先检查，因为这是我们的目标)
        follow_elements = self.find_element_by_text(['关注', '已关注'], "detect_page.xml")
        if follow_elements:
            follow_count = len([elem for elem in follow_elements if elem['clickable'] == 'true' and elem['text'] in ['关注', '已关注']])
            if follow_count >= 2:
                print("✅ 当前在关注推荐页面")
                return "follow_page"

        # 检查消息页面
        message_elements = self.find_element_by_text(['新增关注', '通知', '赞和收藏'], "detect_page.xml")
        if message_elements:
            print("✅ 当前在消息页面")
            return "message_page"

        # 检查主页
        homepage_elements = self.find_element_by_text(['推荐', '关注', '发现'], "detect_page.xml")
        bottom_nav = self.find_element_by_text(['消息'], "detect_page.xml")
        if homepage_elements and bottom_nav:
            print("✅ 当前在主页")
            return "homepage"

        print("❓ 未识别的页面，尝试智能导航...")
        return "unknown"

    def safe_navigate_to_message(self):
        """安全导航到消息页面"""
        print(f"\\n💬 步骤1: 安全导航到消息页面")
        print("=" * 40)

        current_page = self.detect_current_page()

        if current_page == "message_page":
            print("    ✅ 已在消息页面，无需导航")
            self.step_results['step1'] = True
            return True

        if current_page == "follow_page":
            print("    ✅ 已在关注推荐页面，跳过导航")
            self.step_results['step1'] = True
            return True

        if current_page == "homepage":
            print("    📱 从主页导航到消息页面...")
            message_buttons = self.find_element_by_text(['消息'], "detect_page.xml")

            for btn in message_buttons:
                if btn['clickable'] == 'true':
                    x, y = btn['position']
                    print(f"    📍 找到消息按钮: '{btn['text']}' 位置 ({x}, {y})")

                    if self.click_coordinate(x, y, "消息按钮"):
                        # 验证导航结果
                        if self.detect_current_page() in ["message_page", "follow_page"]:
                            print("    ✅ 成功导航到消息相关页面")
                            self.step_results['step1'] = True
                            return True

            print("    ❌ 消息按钮点击失败")
            self.step_results['step1'] = False
            return False

        # 未知页面，尝试通用方法
        print("    🔄 未知页面，尝试查找消息入口...")
        all_message_buttons = self.find_element_by_text(['消息', 'Message', '聊天'], "detect_page.xml")

        for btn in all_message_buttons:
            if btn['clickable'] == 'true':
                x, y = btn['position']
                print(f"    📍 尝试点击: '{btn['text']}' 位置 ({x}, {y})")

                if self.click_coordinate(x, y, f"消息入口-{btn['text']}"):
                    if self.detect_current_page() in ["message_page", "follow_page"]:
                        print("    ✅ 成功找到消息入口")
                        self.step_results['step1'] = True
                        return True

        print("    ❌ 无法找到消息入口")
        self.step_results['step1'] = False
        return False

    def navigate_to_follow_page(self):
        """导航到关注推荐页面"""
        print(f"\\n➕ 步骤2: 导航到关注推荐页面")
        print("=" * 40)

        current_page = self.detect_current_page()

        if current_page == "follow_page":
            print("    ✅ 已在关注推荐页面")
            self.step_results['step2'] = True
            return True

        if current_page in ["message_page", "homepage"]:
            print("    📱 查找新增关注按钮...")
            self.get_ui_info("before_follow.xml")

            follow_buttons = self.find_element_by_text(['新增关注', '新关注', '关注推荐'], "before_follow.xml")

            for btn in follow_buttons:
                if btn['clickable'] == 'true':
                    x, y = btn['position']
                    print(f"    📍 找到新增关注按钮: '{btn['text']}' 位置 ({x}, {y})")

                    if self.click_coordinate(x, y, "新增关注按钮", 3):
                        # 验证是否成功进入关注页面
                        if self.detect_current_page() == "follow_page":
                            print("    ✅ 成功进入关注推荐页面")
                            self.step_results['step2'] = True
                            return True
                        else:
                            print("    ⚠️ 点击后页面未变化，可能需要滑动")

        print("    ❌ 无法进入关注推荐页面")
        self.step_results['step2'] = False
        return False

    def find_follow_buttons(self):
        """查找所有关注按钮"""
        print("    📱 分析关注推荐页面，查找关注按钮...")
        self.get_ui_info("current_follow_page.xml")

        follow_buttons = []
        try:
            tree = ET.parse("current_follow_page.xml")
            root = tree.getroot()

            for elem in root.iter():
                text = elem.get('text', '')
                if text in ['关注', '已关注']:
                    bounds = elem.get('bounds', '')
                    clickable = elem.get('clickable', 'false')

                    if bounds and clickable == 'true':
                        coords = re.findall(r'\d+', bounds)
                        if len(coords) >= 4:
                            x1, y1, x2, y2 = map(int, coords[:4])
                            center_x = (x1 + x2) // 2
                            center_y = (y1 + y2) // 2

                            status = "未关注" if text == "关注" else "已关注"
                            follow_buttons.append({
                                'position': (center_x, center_y),
                                'status': status,
                                'text': text,
                                'bounds': bounds
                            })
                            print(f"    找到按钮: {status} 在位置 ({center_x}, {center_y})")

            print(f"    总共找到 {len(follow_buttons)} 个关注相关按钮")
            return follow_buttons

        except Exception as e:
            print(f"    ❌ 解析关注按钮失败: {e}")
            return []

    def verify_follow_success(self, button_pos, expected_result="已关注"):
        """验证关注是否成功"""
        print(f"    🔍 验证关注结果...")
        time.sleep(1.5)
        self.get_ui_info("verify_result.xml")

        try:
            tree = ET.parse("verify_result.xml")
            root = tree.getroot()
            x, y = button_pos

            for elem in root.iter():
                text = elem.get('text', '')
                if text in ['关注', '已关注']:
                    bounds = elem.get('bounds', '')
                    if bounds:
                        coords = re.findall(r'\d+', bounds)
                        if len(coords) >= 4:
                            elem_x1, elem_y1, elem_x2, elem_y2 = map(int, coords[:4])
                            elem_center_x = (elem_x1 + elem_x2) // 2
                            elem_center_y = (elem_y1 + elem_y2) // 2

                            if abs(elem_center_x - x) < 50 and abs(elem_center_y - y) < 50:
                                print(f"    📍 找到对应按钮: '{text}' 在位置 ({elem_center_x}, {elem_center_y})")

                                if text == expected_result:
                                    print(f"    ✅ 关注成功! 按钮已变为'{text}'")
                                    return True
                                else:
                                    print(f"    ❌ 关注失败! 按钮仍显示'{text}'")
                                    return False

            print(f"    ⚠️ 无法找到对应位置的按钮")
            return False

        except Exception as e:
            print(f"    ❌ 验证关注状态时出错: {e}")
            return False

    def smart_follow_users(self, max_count=3):
        """智能关注用户"""
        print(f"\\n🎯 步骤3: 智能关注用户 (最多{max_count}个)")
        print("=" * 40)

        try:
            all_buttons = self.find_follow_buttons()
            unfollow_buttons = [btn for btn in all_buttons if btn['status'] == '未关注']

            print(f"\\n    📊 状态统计:")
            print(f"       总按钮数: {len(all_buttons)}")
            print(f"       未关注用户: {len(unfollow_buttons)}")
            print(f"       已关注用户: {len(all_buttons) - len(unfollow_buttons)}")

            if not unfollow_buttons:
                print("    🎉 所有用户都已关注！")
                self.step_results['step3'] = True
                return True

            success_count = 0

            for i, button in enumerate(unfollow_buttons[:max_count]):
                print(f"\\n    👤 关注第{i+1}个用户...")
                print(f"       位置: {button['position']}")

                x, y = button['position']
                if self.click_coordinate(x, y, f"第{i+1}个用户的关注按钮", 1):
                    if self.verify_follow_success(button['position'], "已关注"):
                        success_count += 1
                        print(f"       ✅ 第{i+1}个用户关注成功!")
                    else:
                        print(f"       ❌ 第{i+1}个用户关注失败!")
                else:
                    print(f"       ❌ 点击第{i+1}个用户失败!")

                if i < len(unfollow_buttons) - 1:
                    print("       ⏱️ 等待2秒...")
                    time.sleep(2)

            total_attempts = min(max_count, len(unfollow_buttons))
            success_rate = success_count / total_attempts * 100 if total_attempts > 0 else 0

            print(f"\\n    🎊 关注完成!")
            print(f"       尝试关注: {total_attempts} 个用户")
            print(f"       成功关注: {success_count} 个用户")
            print(f"       成功率: {success_rate:.1f}%")

            step_success = success_rate >= 50
            self.step_results['step3'] = step_success

            if step_success:
                print(f"    ✅ 智能关注 成功")
            else:
                print(f"    ❌ 智能关注 失败 (成功率过低)")

            return step_success

        except Exception as e:
            print(f"    ❌ 智能关注异常: {e}")
            self.step_results['step3'] = False
            return False

    def run_safe_workflow(self):
        """运行安全的自动关注流程"""
        print("🚀 小红书安全自动关注流程启动")
        print("=" * 60)
        print("📋 安全流程概览:")
        print("   1. 智能检测当前页面状态")
        print("   2. 安全导航到消息/关注页面")
        print("   3. 进入关注推荐页面")
        print("   4. 智能关注前3个用户")
        print("   ⚠️ 避免使用返回键，防止退出APP")
        print("=" * 60)

        start_time = time.time()

        # 执行安全流程
        steps = [
            ("安全导航", self.safe_navigate_to_message),
            ("进入关注页面", self.navigate_to_follow_page),
            ("智能关注", lambda: self.smart_follow_users(3))
        ]

        for step_name, step_func in steps:
            try:
                print(f"\\n⏳ 执行{step_name}...")
                if not step_func():
                    print(f"\\n❌ {step_name} 失败，流程中断")
                    self.print_final_report(False)
                    return False

                print(f"    ✅ {step_name} 完成")
                time.sleep(1)

            except Exception as e:
                print(f"\\n💥 {step_name} 发生异常: {e}")
                self.print_final_report(False)
                return False

        end_time = time.time()
        duration = end_time - start_time

        print(f"\\n🎉 安全流程执行成功！")
        print(f"⏱️ 总耗时: {duration:.1f}秒")
        self.print_final_report(True)
        return True

    def print_final_report(self, overall_success):
        """打印最终执行报告"""
        print("\\n" + "=" * 60)
        print("📊 执行报告")
        print("=" * 60)

        step_names = {
            'step1': '1. 安全导航到消息页面',
            'step2': '2. 进入关注推荐页面',
            'step3': '3. 智能关注用户'
        }

        for step_key, step_name in step_names.items():
            if step_key in self.step_results:
                status = "✅ 成功" if self.step_results[step_key] else "❌ 失败"
                print(f"{step_name}: {status}")
            else:
                print(f"{step_name}: ⏸️ 未执行")

        print("-" * 60)
        overall_status = "🎉 整体成功" if overall_success else "💥 整体失败"
        print(f"整体结果: {overall_status}")
        print("=" * 60)

def main():
    automation = XiaohongshuSafeAutomation()

    print("🎯 小红书安全自动关注工具")
    print("💡 智能检测页面状态，避免误操作")
    print("🔧 不使用返回键，防止退出APP")
    print()

    automation.run_safe_workflow()

if __name__ == "__main__":
    main()
