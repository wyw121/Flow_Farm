#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书完整自动关注工具 - 模块化版本
包含完整流程：回到主页 → 消息 → 新增关注 → 智能关注
每个步骤都有状态验证和错误处理
"""

import subprocess
import time
import xml.etree.ElementTree as ET
import re

class XiaohongshuFullAutomation:
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

            for elem in root.iter():
                text = elem.get('text', '')
                content_desc = elem.get('content-desc', '')

                for target_text in text_list:
                    if target_text in text or target_text in content_desc:
                        bounds = elem.get('bounds', '')
                        clickable = elem.get('clickable', 'false')

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
                                    'bounds': bounds
                                }
            return {'found': False}
        except Exception as e:
            print(f"    ❌ 查找元素失败: {e}")
            return {'found': False}

    def verify_page_state(self, expected_elements, step_name, max_attempts=3):
        """验证页面状态"""
        print(f"    🔍 验证{step_name}页面状态...")

        for attempt in range(max_attempts):
            self.get_ui_info(f"verify_{step_name}_{attempt}.xml")

            for element_text in expected_elements:
                result = self.find_element_by_text([element_text], f"verify_{step_name}_{attempt}.xml")
                if result['found']:
                    print(f"    ✅ 找到预期元素: '{element_text}'")
                    return True

            if attempt < max_attempts - 1:
                print(f"    ⏳ 第{attempt + 1}次验证失败，等待2秒后重试...")
                time.sleep(2)

        print(f"    ❌ {step_name}页面验证失败")
        return False

    def step1_go_to_homepage(self):
        """步骤1: 回到主页"""
        self.current_step = "回到主页"
        print(f"\\n📱 步骤1: {self.current_step}")
        print("=" * 40)

        try:
            # 多次按返回键确保回到主页
            for i in range(3):
                print(f"    ⬅️ 按返回键 ({i+1}/3)")
                self.run_adb_command("shell input keyevent 4")
                time.sleep(1)

            # 验证是否在主页
            success = self.verify_page_state(['推荐', '关注', '发现', '购物'], '主页')

            if not success:
                # 尝试点击底部导航的首页按钮
                print("    🔄 尝试点击首页按钮...")
                homepage_coords = [(150, 1050), (180, 1080), (120, 1020)]  # 常见的首页按钮位置

                for coord in homepage_coords:
                    self.click_coordinate(coord[0], coord[1], "首页按钮", 1)
                    success = self.verify_page_state(['推荐', '关注'], '主页')
                    if success:
                        break

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

    def step2_go_to_messages(self):
        """步骤2: 进入消息页面"""
        self.current_step = "进入消息"
        print(f"\\n💬 步骤2: {self.current_step}")
        print("=" * 40)

        try:
            self.get_ui_info("step2_before.xml")

            # 查找消息按钮 (可能的文本)
            message_texts = ['消息', 'message', '聊天', 'Message']
            message_result = self.find_element_by_text(message_texts, "step2_before.xml")

            if message_result['found']:
                x, y = message_result['position']
                print(f"    📍 找到消息按钮: '{message_result['text']}' 位置 ({x}, {y})")

                if self.click_coordinate(x, y, "消息按钮"):
                    # 验证是否成功进入消息页面
                    success = self.verify_page_state(['新增关注', '通知', '赞和收藏', '系统通知'], '消息页面')

                    self.step_results['step2'] = success
                    if success:
                        print(f"    ✅ {self.current_step} 成功")
                    else:
                        print(f"    ❌ {self.current_step} 失败")
                    return success

            # 如果找不到消息按钮，尝试常见位置
            print("    🔄 未找到消息按钮，尝试常见位置...")
            common_message_coords = [(540, 1050), (500, 1080), (580, 1020)]

            for coord in common_message_coords:
                if self.click_coordinate(coord[0], coord[1], "消息按钮(常见位置)"):
                    success = self.verify_page_state(['新增关注', '通知'], '消息页面')
                    if success:
                        self.step_results['step2'] = True
                        print(f"    ✅ {self.current_step} 成功")
                        return True

            self.step_results['step2'] = False
            print(f"    ❌ {self.current_step} 失败")
            return False

        except Exception as e:
            print(f"    ❌ {self.current_step} 异常: {e}")
            self.step_results['step2'] = False
            return False

    def step3_click_new_follow(self):
        """步骤3: 点击新增关注"""
        self.current_step = "点击新增关注"
        print(f"\\n➕ 步骤3: {self.current_step}")
        print("=" * 40)

        try:
            self.get_ui_info("step3_before.xml")

            # 查找新增关注按钮
            follow_texts = ['新增关注', '新关注', 'new follow', '关注推荐']
            follow_result = self.find_element_by_text(follow_texts, "step3_before.xml")

            if follow_result['found']:
                x, y = follow_result['position']
                print(f"    📍 找到新增关注按钮: '{follow_result['text']}' 位置 ({x}, {y})")

                if self.click_coordinate(x, y, "新增关注按钮"):
                    # 验证是否进入关注推荐页面
                    success = self.verify_page_state(['关注', '已关注', '推荐用户'], '关注推荐页面')

                    self.step_results['step3'] = success
                    if success:
                        print(f"    ✅ {self.current_step} 成功")
                    else:
                        print(f"    ❌ {self.current_step} 失败")
                    return success

            # 如果找不到，尝试滑动查找
            print("    🔄 未找到新增关注按钮，尝试向下滑动查找...")
            self.run_adb_command("shell input swipe 400 600 400 300 500")
            time.sleep(2)

            self.get_ui_info("step3_after_scroll.xml")
            follow_result = self.find_element_by_text(follow_texts, "step3_after_scroll.xml")

            if follow_result['found']:
                x, y = follow_result['position']
                print(f"    📍 滑动后找到新增关注按钮: '{follow_result['text']}' 位置 ({x}, {y})")

                if self.click_coordinate(x, y, "新增关注按钮"):
                    success = self.verify_page_state(['关注', '已关注'], '关注推荐页面')
                    self.step_results['step3'] = success
                    if success:
                        print(f"    ✅ {self.current_step} 成功")
                        return True

            self.step_results['step3'] = False
            print(f"    ❌ {self.current_step} 失败")
            return False

        except Exception as e:
            print(f"    ❌ {self.current_step} 异常: {e}")
            self.step_results['step3'] = False
            return False

    def find_follow_buttons(self):
        """查找所有关注按钮 (原有逻辑)"""
        print("    📱 分析当前界面，查找关注按钮...")
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
        """验证关注是否成功 (原有逻辑)"""
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

    def step4_smart_follow(self, max_count=3):
        """步骤4: 智能关注用户"""
        self.current_step = "智能关注用户"
        print(f"\\n🎯 步骤4: {self.current_step} (最多{max_count}个)")
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
                self.step_results['step4'] = True
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

            # 成功率超过50%视为成功
            step_success = success_rate >= 50
            self.step_results['step4'] = step_success

            if step_success:
                print(f"    ✅ {self.current_step} 成功")
            else:
                print(f"    ❌ {self.current_step} 失败 (成功率过低)")

            return step_success

        except Exception as e:
            print(f"    ❌ {self.current_step} 异常: {e}")
            self.step_results['step4'] = False
            return False

    def run_complete_workflow(self):
        """运行完整的自动关注流程"""
        print("🚀 小红书完整自动关注流程启动")
        print("=" * 60)
        print("📋 流程概览:")
        print("   1. 回到主页")
        print("   2. 进入消息")
        print("   3. 点击新增关注")
        print("   4. 智能关注前3个用户")
        print("=" * 60)

        start_time = time.time()

        # 执行完整流程
        steps = [
            ("步骤1", self.step1_go_to_homepage),
            ("步骤2", self.step2_go_to_messages),
            ("步骤3", self.step3_click_new_follow),
            ("步骤4", lambda: self.step4_smart_follow(3))
        ]

        for step_name, step_func in steps:
            try:
                if not step_func():
                    print(f"\\n❌ {step_name} 失败，流程中断")
                    self.print_final_report(False)
                    return False

                print(f"    ⏳ {step_name} 完成，等待1秒...")
                time.sleep(1)

            except Exception as e:
                print(f"\\n💥 {step_name} 发生异常: {e}")
                self.print_final_report(False)
                return False

        end_time = time.time()
        duration = end_time - start_time

        print(f"\\n🎉 完整流程执行成功！")
        print(f"⏱️ 总耗时: {duration:.1f}秒")
        self.print_final_report(True)
        return True

    def print_final_report(self, overall_success):
        """打印最终执行报告"""
        print("\\n" + "=" * 60)
        print("📊 执行报告")
        print("=" * 60)

        step_names = {
            'step1': '1. 回到主页',
            'step2': '2. 进入消息',
            'step3': '3. 点击新增关注',
            'step4': '4. 智能关注用户'
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
    automation = XiaohongshuFullAutomation()

    print("🎯 小红书完整自动关注工具 - 模块化版本")
    print("💡 包含完整流程和状态验证")
    print("🔧 每个步骤都有错误处理和重试机制")
    print()

    # 执行完整流程
    automation.run_complete_workflow()

if __name__ == "__main__":
    main()
