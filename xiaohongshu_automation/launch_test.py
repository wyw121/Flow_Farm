#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书自动关注工具 - 启动测试版本
先启动小红书APP，然后进行安全导航测试
"""

import subprocess
import time
import xml.etree.ElementTree as ET
import re

class XiaohongshuLaunchTest:
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

    def click_coordinate(self, x, y, description="", wait_time=2):
        """点击指定坐标并等待"""
        _, stderr = self.run_adb_command(f"shell input tap {x} {y}")
        print(f"🖱️ 点击 {description} 坐标 ({x}, {y})")
        if stderr:
            print(f"❌ 点击错误: {stderr}")
            return False
        time.sleep(wait_time)
        return True

    def get_ui_info(self, filename="current_ui.xml"):
        """获取当前UI信息"""
        self.run_adb_command(f"shell uiautomator dump /sdcard/{filename}")
        self.run_adb_command(f"pull /sdcard/{filename} {filename}")
        time.sleep(0.5)

    def launch_xiaohongshu_app(self):
        """启动小红书APP"""
        print("🚀 启动小红书APP...")

        # 方法1: 使用adb启动命令
        print("📱 尝试使用ADB命令启动小红书...")
        stdout, stderr = self.run_adb_command("shell am start -n com.xingin.xhs/.activity.SplashActivity")

        if not stderr:
            print("✅ ADB启动命令执行成功")
            time.sleep(5)  # 等待APP启动
            return True
        else:
            print(f"⚠️ ADB启动失败: {stderr}")

        # 方法2: 点击桌面图标
        print("🖱️ 尝试点击桌面小红书图标...")
        self.get_ui_info("desktop.xml")

        # 查找小红书图标
        try:
            tree = ET.parse("desktop.xml")
            root = tree.getroot()

            for elem in root.iter():
                text = elem.get('text', '')
                content_desc = elem.get('content-desc', '')

                if '小红书' in text or '小红书' in content_desc:
                    bounds = elem.get('bounds', '')
                    if bounds:
                        coords = re.findall(r'\\d+', bounds)
                        if len(coords) >= 4:
                            x1, y1, x2, y2 = map(int, coords[:4])
                            center_x = (x1 + x2) // 2
                            center_y = (y1 + y2) // 2

                            print(f"📍 找到小红书图标: '{text or content_desc}' 位置 ({center_x}, {center_y})")

                            if self.click_coordinate(center_x, center_y, "小红书图标", 5):
                                print("✅ 点击小红书图标成功")
                                return True

        except Exception as e:
            print(f"❌ 查找小红书图标失败: {e}")

        # 方法3: 尝试常见的小红书图标位置
        print("🎯 尝试常见的小红书图标位置...")
        common_positions = [
            (400, 300),   # 屏幕上部中央
            (200, 400),   # 屏幕左侧
            (600, 400),   # 屏幕右侧
            (400, 500),   # 屏幕中央
            (400, 700),   # 屏幕下部
        ]

        for i, (x, y) in enumerate(common_positions):
            print(f"🎯 尝试位置 {i+1}: ({x}, {y})")
            if self.click_coordinate(x, y, f"可能的小红书位置{i+1}", 3):
                # 检查是否启动了小红书
                self.get_ui_info("after_click.xml")

                try:
                    tree = ET.parse("after_click.xml")
                    root = tree.getroot()
                    page_text = ""

                    for elem in root.iter():
                        text = elem.get('text', '')
                        if text:
                            page_text += text + " "

                    if '小红书' in page_text or 'RED' in page_text or '推荐' in page_text:
                        print(f"✅ 在位置{i+1}成功启动小红书")
                        return True

                except Exception as e:
                    print(f"⚠️ 检查启动结果失败: {e}")

        print("❌ 无法启动小红书APP")
        return False

    def check_app_status(self):
        """检查APP状态"""
        print("🔍 检查当前APP状态...")

        self.get_ui_info("app_status.xml")

        try:
            tree = ET.parse("app_status.xml")
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

            print(f"📱 当前页面元素: {page_texts[:15]}...")

            # 检查是否在小红书内
            xiaohongshu_indicators = ['推荐', '关注', '发现', '购物', '消息', '小红书', 'RED', '登录', '注册']
            found_indicators = [indicator for indicator in xiaohongshu_indicators if any(indicator in text for text in page_texts)]

            if found_indicators:
                print(f"✅ 检测到小红书APP元素: {found_indicators}")
                return True
            else:
                print("❌ 未检测到小红书APP元素")
                return False

        except Exception as e:
            print(f"❌ 检查APP状态失败: {e}")
            return False

def main():
    print("🧪 小红书APP启动测试")
    print("=" * 50)

    launcher = XiaohongshuLaunchTest()

    # 检查初始状态
    print("\\n1. 检查初始状态")
    launcher.check_app_status()

    # 尝试启动小红书
    print("\\n2. 启动小红书APP")
    if launcher.launch_xiaohongshu_app():
        print("\\n3. 验证启动结果")
        time.sleep(3)
        if launcher.check_app_status():
            print("\\n🎉 小红书APP启动成功！现在可以进行后续测试")
        else:
            print("\\n❌ 小红书APP启动失败或未正确加载")
    else:
        print("\\n❌ 无法启动小红书APP")

    print("\\n💡 提示:")
    print("- 如果启动成功，可以运行 smart_follow_test.py 进行导航测试")
    print("- 如果启动失败，请手动打开小红书APP后再运行测试")

if __name__ == "__main__":
    main()
