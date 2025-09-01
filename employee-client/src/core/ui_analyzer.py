"""
Flow Farm - UI界面识别和分析器
负责分析Android设备的UI结构，提供智能元素定位功能

功能特性:
- UI层次结构分析
- 元素智能定位
- 文本内容识别
- 图像识别辅助
- 页面状态检测
"""

import logging
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ElementType(Enum):
    """UI元素类型枚举"""

    BUTTON = "button"
    TEXT = "text"
    INPUT = "input"
    IMAGE = "image"
    LIST = "list"
    SCROLL = "scroll"
    UNKNOWN = "unknown"


@dataclass
class UIElement:
    """UI元素信息"""

    bounds: Tuple[int, int, int, int]  # (left, top, right, bottom)
    text: str = ""
    resource_id: str = ""
    class_name: str = ""
    content_desc: str = ""
    clickable: bool = False
    scrollable: bool = False
    element_type: ElementType = ElementType.UNKNOWN

    @property
    def center_x(self) -> int:
        """获取元素中心X坐标"""
        return (self.bounds[0] + self.bounds[2]) // 2

    @property
    def center_y(self) -> int:
        """获取元素中心Y坐标"""
        return (self.bounds[1] + self.bounds[3]) // 2

    @property
    def width(self) -> int:
        """获取元素宽度"""
        return self.bounds[2] - self.bounds[0]

    @property
    def height(self) -> int:
        """获取元素高度"""
        return self.bounds[3] - self.bounds[1]


class UIAnalyzer:
    """UI界面分析器

    提供UI界面的解析、分析和元素定位功能
    """

    def __init__(self):
        """初始化UI分析器"""
        self.logger = logging.getLogger(__name__)
        self.current_ui_elements: List[UIElement] = []
        self.current_xml_path: Optional[str] = None

    def parse_ui_xml(self, xml_path: str) -> List[UIElement]:
        """解析UI XML文件

        Args:
            xml_path: UI XML文件路径

        Returns:
            UI元素列表
        """
        self.logger.info("🔍 解析UI XML文件: %s", xml_path)

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            elements = []
            self._parse_node(root, elements)

            self.current_ui_elements = elements
            self.current_xml_path = xml_path

            self.logger.info("✅ 解析完成，找到 %d 个UI元素", len(elements))
            return elements

        except ET.ParseError as e:
            self.logger.error("❌ XML解析失败: %s", str(e))
            return []
        except FileNotFoundError:
            self.logger.error("❌ 文件不存在: %s", xml_path)
            return []
        except Exception as e:
            self.logger.error("❌ UI解析异常: %s", str(e))
            return []

    def _parse_node(self, node: ET.Element, elements: List[UIElement]):
        """递归解析XML节点"""
        # 解析节点属性
        bounds_str = node.get("bounds", "")
        if bounds_str:
            # 解析bounds格式：[left,top][right,bottom]
            bounds_match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
            if bounds_match:
                bounds = tuple(map(int, bounds_match.groups()))

                element = UIElement(
                    bounds=bounds,
                    text=node.get("text", ""),
                    resource_id=node.get("resource-id", ""),
                    class_name=node.get("class", ""),
                    content_desc=node.get("content-desc", ""),
                    clickable=node.get("clickable", "false").lower() == "true",
                    scrollable=node.get("scrollable", "false").lower() == "true",
                )

                # 推断元素类型
                element.element_type = self._infer_element_type(element)

                elements.append(element)

        # 递归处理子节点
        for child in node:
            self._parse_node(child, elements)

    def _infer_element_type(self, element: UIElement) -> ElementType:
        """推断UI元素类型"""
        class_name = element.class_name.lower()

        if "button" in class_name or element.clickable:
            return ElementType.BUTTON
        elif "edit" in class_name or "input" in class_name:
            return ElementType.INPUT
        elif "text" in class_name and element.text:
            return ElementType.TEXT
        elif "image" in class_name:
            return ElementType.IMAGE
        elif "list" in class_name or element.scrollable:
            return ElementType.LIST
        elif "scroll" in class_name:
            return ElementType.SCROLL
        else:
            return ElementType.UNKNOWN

    def find_elements_by_text(
        self, target_texts: List[str], exact_match: bool = False
    ) -> List[UIElement]:
        """根据文本查找元素

        Args:
            target_texts: 目标文本列表
            exact_match: 是否精确匹配

        Returns:
            匹配的元素列表
        """
        matches = []

        for element in self.current_ui_elements:
            element_text = element.text.strip()
            content_desc = element.content_desc.strip()

            for target_text in target_texts:
                if exact_match:
                    if target_text == element_text or target_text == content_desc:
                        matches.append(element)
                        break
                else:
                    if target_text in element_text or target_text in content_desc:
                        matches.append(element)
                        break

        self.logger.debug(
            "🔍 文本搜索 '%s'，找到 %d 个匹配元素", target_texts, len(matches)
        )
        return matches

    def find_elements_by_resource_id(self, resource_id: str) -> List[UIElement]:
        """根据resource-id查找元素"""
        matches = [
            element
            for element in self.current_ui_elements
            if resource_id in element.resource_id
        ]

        self.logger.debug(
            "🔍 Resource ID搜索 '%s'，找到 %d 个匹配元素", resource_id, len(matches)
        )
        return matches

    def find_clickable_elements(self) -> List[UIElement]:
        """查找所有可点击元素"""
        clickable = [
            element
            for element in self.current_ui_elements
            if element.clickable and element.width > 0 and element.height > 0
        ]

        self.logger.debug("🔍 找到 %d 个可点击元素", len(clickable))
        return clickable

    def find_buttons_by_keywords(self, keywords: List[str]) -> List[UIElement]:
        """根据关键词查找按钮"""
        buttons = []

        for element in self.current_ui_elements:
            if element.element_type == ElementType.BUTTON or element.clickable:
                for keyword in keywords:
                    if (
                        keyword in element.text
                        or keyword in element.content_desc
                        or keyword in element.resource_id
                    ):
                        buttons.append(element)
                        break

        self.logger.debug(
            "🔍 按钮关键词搜索 '%s'，找到 %d 个按钮", keywords, len(buttons)
        )
        return buttons

    def detect_page_type(self) -> Dict[str, Any]:
        """检测当前页面类型

        Returns:
            页面信息字典，包含页面类型、特征元素等
        """
        page_info = {
            "type": "unknown",
            "app": "unknown",
            "features": [],
            "navigation_elements": [],
            "action_elements": [],
        }

        # 检测应用类型
        app_indicators = {
            "douyin": ["抖音", "推荐", "关注", "我", "首页"],
            "xiaohongshu": ["小红书", "首页", "商城", "消息", "我"],
            "wechat": ["微信", "聊天", "通讯录", "发现", "我"],
            "system": ["设置", "返回", "主页", "任务"],
        }

        for app_name, indicators in app_indicators.items():
            for indicator in indicators:
                elements = self.find_elements_by_text([indicator])
                if elements:
                    page_info["app"] = app_name
                    page_info["features"].extend([indicator])
                    break
            if page_info["app"] != "unknown":
                break

        # 检测导航元素
        nav_keywords = ["返回", "back", "首页", "home", "菜单", "menu"]
        nav_elements = self.find_buttons_by_keywords(nav_keywords)
        page_info["navigation_elements"] = [
            {"text": elem.text, "bounds": elem.bounds} for elem in nav_elements
        ]

        # 检测操作元素
        action_keywords = ["关注", "点赞", "分享", "评论", "发布", "搜索"]
        action_elements = self.find_buttons_by_keywords(action_keywords)
        page_info["action_elements"] = [
            {"text": elem.text, "bounds": elem.bounds} for elem in action_elements
        ]

        # 推断页面类型
        if "首页" in page_info["features"] or "推荐" in page_info["features"]:
            page_info["type"] = "home"
        elif "消息" in page_info["features"]:
            page_info["type"] = "message"
        elif "我" in page_info["features"] or "个人" in page_info["features"]:
            page_info["type"] = "profile"
        elif "设置" in page_info["features"]:
            page_info["type"] = "settings"

        self.logger.info("📱 页面检测结果: %s", page_info)
        return page_info

    def find_follow_buttons(self) -> List[UIElement]:
        """查找关注按钮（专门用于社交媒体自动化）"""
        follow_keywords = ["关注", "follow", "+关注", "Follow"]
        follow_buttons = []

        # 查找包含关注关键词的按钮
        for keyword in follow_keywords:
            elements = self.find_elements_by_text([keyword])
            for element in elements:
                if element.clickable and element.width > 50 and element.height > 20:
                    follow_buttons.append(element)

        # 去重
        unique_buttons = []
        for button in follow_buttons:
            is_duplicate = False
            for existing in unique_buttons:
                if (
                    abs(button.center_x - existing.center_x) < 10
                    and abs(button.center_y - existing.center_y) < 10
                ):
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_buttons.append(button)

        self.logger.info("🎯 找到 %d 个关注按钮", len(unique_buttons))
        return unique_buttons

    def get_element_summary(self) -> Dict[str, int]:
        """获取元素统计摘要"""
        summary = {
            "total": len(self.current_ui_elements),
            "clickable": 0,
            "buttons": 0,
            "texts": 0,
            "inputs": 0,
            "images": 0,
        }

        for element in self.current_ui_elements:
            if element.clickable:
                summary["clickable"] += 1

            if element.element_type == ElementType.BUTTON:
                summary["buttons"] += 1
            elif element.element_type == ElementType.TEXT:
                summary["texts"] += 1
            elif element.element_type == ElementType.INPUT:
                summary["inputs"] += 1
            elif element.element_type == ElementType.IMAGE:
                summary["images"] += 1

        return summary

    def export_element_info(self, output_path: str):
        """导出元素信息到文件"""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("UI元素分析报告\n")
                f.write("=" * 50 + "\n\n")

                summary = self.get_element_summary()
                f.write(f"元素统计:\n")
                for key, value in summary.items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")

                f.write("详细元素列表:\n")
                f.write("-" * 30 + "\n")

                for i, element in enumerate(self.current_ui_elements):
                    f.write(f"{i+1}. {element.class_name}\n")
                    f.write(f"   文本: {element.text}\n")
                    f.write(f"   位置: {element.bounds}\n")
                    f.write(f"   可点击: {element.clickable}\n")
                    f.write(f"   类型: {element.element_type.value}\n")
                    f.write("\n")

            self.logger.info("📄 元素信息已导出到: %s", output_path)

        except Exception as e:
            self.logger.error("❌ 导出失败: %s", str(e))


def test_ui_analyzer():
    """测试UI分析器功能"""
    import logging

    logging.basicConfig(level=logging.DEBUG)

    print("🔍 测试UI界面分析器")
    print("=" * 50)

    # 创建分析器
    analyzer = UIAnalyzer()

    # 这里需要一个实际的UI XML文件来测试
    # 如果没有，会创建一个模拟的测试
    print("⚠️ 需要实际的UI XML文件来测试完整功能")
    print("可以通过以下步骤获取UI XML:")
    print("1. 连接Android设备")
    print("2. 执行: adb shell uiautomator dump /sdcard/ui.xml")
    print("3. 执行: adb pull /sdcard/ui.xml ./test_ui.xml")
    print("4. 然后调用: analyzer.parse_ui_xml('./test_ui.xml')")

    return analyzer


if __name__ == "__main__":
    test_ui_analyzer()
