#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书状态检测和导航测试
"""

import subprocess
import time
import xml.etree.ElementTree as ET
import re

class XiaohongshuNavigationTest:
    def __init__(self):
        self.adb_path = r"D:\leidian\LDPlayer9\adb.exe"

    def run_adb_command(self, command):
        """执行ADB命令"""
        try:
            full_command = f'"{self.adb_path}" {command}'
            result = subprocess.run(full_command, shell=True, capture_output=True, text=True, encoding='utf-8')
            return result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return "", str(e)

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
            print(f"❌ 查找元素失败: {e}")
            return []

    def click_coordinate(self, x, y, description=""):
        """点击指定坐标"""
        _, stderr = self.run_adb_command(f"shell input tap {x} {y}")
        print(f"🖱️ 点击 {description} 坐标 ({x}, {y})")
        if stderr:
            print(f"❌ 点击错误: {stderr}")
            return False
        time.sleep(2)
        return True

    def test_current_state(self):
        """测试当前页面状态"""
        print("🔍 检查当前小红书页面状态...")
        self.get_ui_info("test_current_state.xml")

        # 检查关注推荐页面 (优先检查，因为这是我们的目标)
        follow_elements = self.find_element_by_text(['关注', '已关注'], "test_current_state.xml")
        if follow_elements:
            # 进一步检查是否真的在关注推荐页面（应该有多个关注按钮）
            follow_count = len([elem for elem in follow_elements if elem['clickable'] == 'true' and elem['text'] in ['关注', '已关注']])
            if follow_count >= 2:  # 至少有2个关注相关按钮
                print("✅ 检测到关注推荐页面元素:")
                for elem in follow_elements[:3]:  # 只显示前3个
                    print(f"   - {elem['text']} 位置: {elem['position']} (可点击: {elem['clickable']})")
                return "follow_page"

        # 检查消息页面元素
        message_elements = self.find_element_by_text(['新增关注', '通知', '赞和收藏'], "test_current_state.xml")
        if message_elements:
            print("✅ 检测到消息页面元素:")
            for elem in message_elements:
                print(f"   - {elem['text']} 位置: {elem['position']} (可点击: {elem['clickable']})")
            return "message_page"

        # 检查主页元素
        homepage_elements = self.find_element_by_text(['推荐', '关注', '发现', '购物'], "test_current_state.xml")
        if homepage_elements:
            # 检查是否有底部导航的"消息"按钮，如果有说明在主页
            bottom_nav = self.find_element_by_text(['消息'], "test_current_state.xml")
            if bottom_nav:
                print("✅ 检测到主页元素:")
                for elem in homepage_elements[:3]:  # 只显示前3个
                    print(f"   - {elem['text']} 位置: {elem['position']} (可点击: {elem['clickable']})")
                return "homepage"

        print("❓ 未识别的页面状态")
        return "unknown"

    def test_navigation_to_message(self):
        """测试导航到消息页面"""
        print("\n💬 测试导航到消息页面...")

        current_state = self.test_current_state()

        if current_state == "message_page":
            print("✅ 已在消息页面，无需导航")
            return True

        if current_state == "homepage":
            print("📱 从主页导航到消息页面...")
            self.get_ui_info("before_click_message.xml")

            # 查找消息按钮
            message_buttons = self.find_element_by_text(['消息'], "before_click_message.xml")
            if message_buttons:
                for btn in message_buttons:
                    if btn['clickable'] == 'true':
                        x, y = btn['position']
                        print(f"📍 找到消息按钮: '{btn['text']}' 位置 ({x}, {y})")

                        if self.click_coordinate(x, y, "消息按钮"):
                            # 验证是否成功进入消息页面
                            time.sleep(2)
                            new_state = self.test_current_state()
                            if new_state == "message_page":
                                print("✅ 成功进入消息页面")
                                return True
                            else:
                                print("❌ 进入消息页面失败")
                                return False

            print("❌ 未找到消息按钮")
            return False

        print(f"❌ 当前状态 '{current_state}' 无法导航到消息页面")
        return False

    def test_navigation_to_follow_page(self):
        """测试导航到关注推荐页面"""
        print("\n➕ 测试导航到关注推荐页面...")

        # 先确保在消息页面
        if not self.test_navigation_to_message():
            print("❌ 无法进入消息页面，停止测试")
            return False

        print("📱 从消息页面导航到关注推荐页面...")
        self.get_ui_info("before_click_follow.xml")

        # 查找新增关注按钮
        follow_buttons = self.find_element_by_text(['新增关注', '新关注'], "before_click_follow.xml")
        if follow_buttons:
            for btn in follow_buttons:
                if btn['clickable'] == 'true':
                    x, y = btn['position']
                    print(f"📍 找到新增关注按钮: '{btn['text']}' 位置 ({x}, {y})")

                    if self.click_coordinate(x, y, "新增关注按钮"):
                        # 验证是否成功进入关注推荐页面
                        time.sleep(3)
                        new_state = self.test_current_state()
                        if new_state == "follow_page":
                            print("✅ 成功进入关注推荐页面")
                            return True
                        else:
                            print("❌ 进入关注推荐页面失败")
                            return False

        print("❌ 未找到新增关注按钮")
        return False

def main():
    test = XiaohongshuNavigationTest()

    print("🎯 小红书导航流程测试")
    print("=" * 50)

    # 测试当前状态
    current_state = test.test_current_state()
    print(f"\n📊 当前页面状态: {current_state}")

    # 测试完整导航流程
    print("\n🚀 开始测试完整导航流程...")

    if test.test_navigation_to_follow_page():
        print("\n🎉 导航测试成功！可以进行关注操作")
    else:
        print("\n❌ 导航测试失败，需要调整流程")

if __name__ == "__main__":
    main()
