#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书完整自动关注工具 - 测试版本
修复返回键导致退出APP的问题
"""

import subprocess
import time
import xml.etree.ElementTree as ET
import re

class XiaohongshuFullAutomationTest:
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

                        found_elements.append({
                            'text': text or content_desc,
                            'bounds': bounds,
                            'clickable': clickable,
                            'target': target_text
                        })

                        if bounds and clickable == 'true':
                            coords = re.findall(r'\d+', bounds)
                            if len(coords) >= 4:
                                x1, y1, x2, y2 = map(int, coords[:4])
                                center_x = (x1 + x2) // 2
                                center_y = (y1 + y2) // 2
                                return {
                                    'found': True,
                                    'text': text or content_desc,
                                    'position': (center_x, center_y),
                                    'bounds': bounds,
                                    'all_found': found_elements
                                }

            return {
                'found': False,
                'all_found': found_elements
            }
        except Exception as e:
            print(f"    ❌ 查找元素失败: {e}")
            return {'found': False, 'all_found': []}

    def check_current_page_type(self):
        """检测当前页面类型"""
        print("    🔍 检测当前页面类型...")
        self.get_ui_info("page_detection.xml")

        # 检测不同页面的特征元素
        page_indicators = {
            '主页': ['推荐', '关注', '发现', '购物', '首页'],
            '消息页': ['新增关注', '通知', '赞和收藏', '系统通知', '消息'],
            '关注推荐页': ['关注', '已关注', '推荐用户', '可能认识的人'],
            '其他内页': ['返回', '分享', '评论', '点赞'],
            '小红书APP': ['xiaohongshu', 'RED', '小红书'],
        }

        detected_pages = []

        try:
            tree = ET.parse("page_detection.xml")
            root = tree.getroot()

            # 收集页面中的所有文本
            page_texts = []
            for elem in root.iter():
                text = elem.get('text', '')
                content_desc = elem.get('content-desc', '')
                if text:
                    page_texts.append(text)
                if content_desc:
                    page_texts.append(content_desc)

            print(f"    📱 页面中发现的文本: {page_texts[:10]}...")  # 显示前10个文本

            # 检测页面类型
            for page_type, indicators in page_indicators.items():
                found_count = 0
                for indicator in indicators:
                    if any(indicator in text for text in page_texts):
                        found_count += 1

                if found_count > 0:
                    detected_pages.append((page_type, found_count))
                    print(f"    📍 检测到 {page_type} 特征: {found_count}个指标")

            if detected_pages:
                # 按匹配数量排序，返回最可能的页面类型
                detected_pages.sort(key=lambda x: x[1], reverse=True)
                best_match = detected_pages[0]
                print(f"    ✅ 当前页面类型: {best_match[0]} (匹配度: {best_match[1]})")
                return best_match[0]
            else:
                print(f"    ⚠️ 无法确定页面类型，可能不在小红书APP内")
                return "未知页面"

        except Exception as e:
            print(f"    ❌ 页面检测失败: {e}")
            return "检测失败"

    def safe_navigate_to_homepage(self):
        """安全地导航到主页，避免退出APP"""
        print("    🛡️ 安全导航到主页...")

        current_page = self.check_current_page_type()

        if current_page == "主页":
            print("    ✅ 已经在主页，无需操作")
            return True
        elif current_page == "小红书APP":
            print("    ✅ 在小红书APP内，但可能在启动页")
            time.sleep(3)  # 等待APP完全加载
            return self.check_current_page_type() in ["主页", "消息页", "关注推荐页"]
        elif current_page == "未知页面":
            print("    ⚠️ 可能不在小红书APP内，请检查")
            return False

        # 如果在其他页面，尝试安全返回
        return self.safe_back_to_homepage(current_page)

    def safe_back_to_homepage(self, current_page):
        """安全返回主页的策略"""
        print(f"    🔄 从 {current_page} 安全返回主页...")

        max_back_attempts = 2  # 减少返回次数，避免退出APP

        for i in range(max_back_attempts):
            print(f"    ⬅️ 尝试返回 ({i+1}/{max_back_attempts})")

            # 按一次返回键
            self.run_adb_command("shell input keyevent 4")
            time.sleep(2)  # 等待页面加载

            # 立即检查是否退出了APP
            new_page_type = self.check_current_page_type()

            if new_page_type == "主页":
                print("    ✅ 成功返回主页")
                return True
            elif new_page_type == "未知页面" or new_page_type == "检测失败":
                print("    ❌ 可能已退出小红书APP，停止返回操作")
                return False
            elif new_page_type == "小红书APP":
                print("    ⏳ 在APP启动页，等待加载...")
                time.sleep(3)
                continue
            else:
                print(f"    ⏳ 当前在 {new_page_type}，继续尝试返回...")
                continue

        # 如果返回键不行，尝试点击底部首页按钮
        print("    🔄 尝试点击底部首页按钮...")
        homepage_coords = [(150, 1050), (180, 1080), (120, 1020)]

        for coord in homepage_coords:
            if self.click_coordinate(coord[0], coord[1], "首页按钮", 1):
                new_page_type = self.check_current_page_type()
                if new_page_type == "主页":
                    print("    ✅ 通过首页按钮成功返回主页")
                    return True

        print("    ❌ 无法安全返回主页")
        return False

    def step1_go_to_homepage_safe(self):
        """步骤1: 安全回到主页 (改进版)"""
        self.current_step = "安全回到主页"
        print(f"\\n📱 步骤1: {self.current_step}")
        print("=" * 40)

        try:
            success = self.safe_navigate_to_homepage()

            self.step_results['step1'] = success
            if success:
                print(f"    ✅ {self.current_step} 成功")
            else:
                print(f"    ❌ {self.current_step} 失败")

            return success

        except Exception as e:
            print(f"    ❌ {self.current_step} 异常: {e}")
            self.step_results['step1'] = False
            return False

    def step2_go_to_messages_safe(self):
        """步骤2: 安全进入消息页面"""
        self.current_step = "进入消息"
        print(f"\\n💬 步骤2: {self.current_step}")
        print("=" * 40)

        try:
            # 先检查当前是否已经在消息页面
            current_page = self.check_current_page_type()
            if current_page == "消息页":
                print("    ✅ 已经在消息页面")
                self.step_results['step2'] = True
                return True

            self.get_ui_info("step2_before.xml")

            # 查找消息按钮
            message_texts = ['消息', 'message', '聊天', 'Message']
            message_result = self.find_element_by_text(message_texts, "step2_before.xml")

            print(f"    🔍 查找消息按钮结果: {message_result}")

            if message_result['found']:
                x, y = message_result['position']
                print(f"    📍 找到消息按钮: '{message_result['text']}' 位置 ({x}, {y})")

                if self.click_coordinate(x, y, "消息按钮"):
                    # 验证是否成功进入消息页面
                    time.sleep(2)
                    new_page_type = self.check_current_page_type()
                    success = new_page_type == "消息页"

                    self.step_results['step2'] = success
                    if success:
                        print(f"    ✅ {self.current_step} 成功")
                    else:
                        print(f"    ❌ {self.current_step} 失败，当前页面: {new_page_type}")
                    return success

            # 如果找不到消息按钮，尝试常见位置
            print("    🔄 未找到消息按钮，尝试常见位置...")
            print(f"    📝 页面中找到的元素: {message_result.get('all_found', [])}")

            # 常见的消息按钮位置（底部导航栏）
            common_message_coords = [(540, 1050), (500, 1080), (580, 1020), (270, 1050), (810, 1050)]

            for i, coord in enumerate(common_message_coords):
                print(f"    🎯 尝试位置 {i+1}: ({coord[0]}, {coord[1]})")
                if self.click_coordinate(coord[0], coord[1], f"消息按钮位置{i+1}"):
                    time.sleep(2)
                    new_page_type = self.check_current_page_type()
                    if new_page_type == "消息页":
                        print(f"    ✅ 在位置{i+1}找到消息按钮")
                        self.step_results['step2'] = True
                        return True

            self.step_results['step2'] = False
            print(f"    ❌ {self.current_step} 失败")
            return False

        except Exception as e:
            print(f"    ❌ {self.current_step} 异常: {e}")
            self.step_results['step2'] = False
            return False

    def test_complete_workflow(self):
        """测试完整流程（仅前两步）"""
        print("🧪 小红书自动关注工具 - 测试模式")
        print("=" * 60)
        print("📋 测试内容:")
        print("   1. 安全回到主页 (改进版)")
        print("   2. 进入消息页面")
        print("   3. 检测当前页面状态")
        print("=" * 60)

        start_time = time.time()

        # 初始状态检测
        print("\\n🔍 初始状态检测:")
        initial_page = self.check_current_page_type()
        print(f"初始页面类型: {initial_page}")

        # 测试步骤1: 安全回到主页
        if not self.step1_go_to_homepage_safe():
            print("\\n❌ 步骤1失败，停止测试")
            return False

        # 测试步骤2: 进入消息
        if not self.step2_go_to_messages_safe():
            print("\\n❌ 步骤2失败，停止测试")
            return False

        end_time = time.time()
        duration = end_time - start_time

        print(f"\\n🎉 测试完成！")
        print(f"⏱️ 测试耗时: {duration:.1f}秒")

        # 最终状态检测
        print("\\n🔍 最终状态检测:")
        final_page = self.check_current_page_type()
        print(f"最终页面类型: {final_page}")

        self.print_test_report()
        return True

    def print_test_report(self):
        """打印测试报告"""
        print("\\n" + "=" * 60)
        print("📊 测试报告")
        print("=" * 60)

        test_steps = {
            'step1': '1. 安全回到主页',
            'step2': '2. 进入消息页面'
        }

        for step_key, step_name in test_steps.items():
            if step_key in self.step_results:
                status = "✅ 成功" if self.step_results[step_key] else "❌ 失败"
                print(f"{step_name}: {status}")
            else:
                print(f"{step_name}: ⏸️ 未测试")

        print("=" * 60)

def main():
    print("🧪 小红书自动关注工具 - 安全导航测试")
    print("💡 测试安全导航逻辑，避免退出APP")
    print("🔧 修复返回键导致的APP退出问题")
    print()

    automation = XiaohongshuFullAutomationTest()
    automation.test_complete_workflow()

if __name__ == "__main__":
    main()
