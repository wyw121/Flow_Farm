#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书智能关注验证工具 - 修复版
每次关注后都验证是否成功
"""

import subprocess
import time
import xml.etree.ElementTree as ET
import re

class SmartFollowWithVerification:
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

    def click_coordinate(self, x, y, description=""):
        """点击指定坐标"""
        _, stderr = self.run_adb_command(f"shell input tap {x} {y}")
        print(f"点击 {description} 坐标 ({x}, {y})")
        if stderr:
            print(f"错误: {stderr}")
        time.sleep(1)
        return not stderr

    def get_ui_info(self, filename="current_ui.xml"):
        """获取当前UI信息"""
        self.run_adb_command(f"shell uiautomator dump /sdcard/{filename}")
        self.run_adb_command(f"pull /sdcard/{filename} {filename}")
        time.sleep(0.5)

    def find_follow_buttons(self):
        """查找所有关注按钮"""
        print("📱 分析当前界面，查找关注按钮...")
        self.get_ui_info("current_follow_page.xml")

        follow_buttons = []
        try:
            tree = ET.parse("current_follow_page.xml")
            root = tree.getroot()

            for elem in root.iter():
                text = elem.get('text', '')
                if text in ['关注', '已关注']:  # 查找关注按钮和已关注按钮
                    bounds = elem.get('bounds', '')
                    clickable = elem.get('clickable', 'false')

                    if bounds and clickable == 'true':
                        # 解析坐标
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
                            print(f"找到按钮: {status} 在位置 ({center_x}, {center_y})")

            print(f"总共找到 {len(follow_buttons)} 个关注相关按钮")
            return follow_buttons

        except Exception as e:
            print(f"❌ 解析关注按钮失败: {e}")
            return []

    def verify_follow_success(self, button_pos, expected_result="已关注"):
        """验证关注是否成功"""
        print(f"    🔍 验证关注结果...")

        # 等待界面更新
        time.sleep(1.5)

        # 获取更新后的UI
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

                            # 检查是否是我们点击的按钮位置(允许50像素误差)
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

    def follow_users_with_verification(self, max_count=5):
        """智能关注用户并验证结果"""
        print(f"\\n🚀 开始智能关注流程 (最多{max_count}个用户)")
        print("=" * 50)

        # 查找所有关注按钮
        all_buttons = self.find_follow_buttons()

        # 过滤出未关注的用户
        unfollow_buttons = [btn for btn in all_buttons if btn['status'] == '未关注']

        print(f"\\n📊 状态统计:")
        print(f"   总按钮数: {len(all_buttons)}")
        print(f"   未关注用户: {len(unfollow_buttons)}")
        print(f"   已关注用户: {len(all_buttons) - len(unfollow_buttons)}")

        if not unfollow_buttons:
            print("\\n🎉 所有用户都已关注！")
            return 0

        success_count = 0

        # 关注前几个未关注的用户
        for i, button in enumerate(unfollow_buttons[:max_count]):
            print(f"\\n👤 关注第{i+1}个用户...")
            print(f"   位置: {button['position']}")

            # 点击关注按钮
            x, y = button['position']
            if self.click_coordinate(x, y, f"第{i+1}个用户的关注按钮"):

                # 验证关注是否成功
                if self.verify_follow_success(button['position'], "已关注"):
                    success_count += 1
                    print(f"   ✅ 第{i+1}个用户关注成功!")
                else:
                    print(f"   ❌ 第{i+1}个用户关注失败!")
            else:
                print(f"   ❌ 点击第{i+1}个用户失败!")

            # 每次关注后稍微等待
            if i < len(unfollow_buttons) - 1:
                print("   ⏱️ 等待2秒...")
                time.sleep(2)

        print(f"\\n🎊 关注完成!")
        print(f"   尝试关注: {min(max_count, len(unfollow_buttons))} 个用户")
        print(f"   成功关注: {success_count} 个用户")
        print(f"   成功率: {success_count/min(max_count, len(unfollow_buttons))*100:.1f}%")

        return success_count

def main():
    automation = SmartFollowWithVerification()

    print("🎯 小红书智能关注验证工具 - 修复版")
    print("💡 每次关注后都会验证是否成功")
    print("=" * 50)

    # 执行智能关注
    automation.follow_users_with_verification(max_count=3)

if __name__ == "__main__":
    main()
