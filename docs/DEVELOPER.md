# 开发者文档

## 开发环境设置

### 必需工具
- Python 3.8+ (推荐3.9或3.10)
- Git 2.30+
- VS Code (推荐IDE)
- Android SDK Platform Tools

### 推荐VS Code扩展
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.flake8", 
    "ms-python.pylint",
    "ms-python.black-formatter",
    "github.copilot",
    "github.copilot-chat"
  ]
}
```

## 项目架构详解

### 模块依赖关系
```
GUI Layer (src/gui/)
    ↓ 依赖
Core Layer (src/core/)
    ↓ 依赖  
Platform Layer (src/platforms/)
    ↓ 依赖
Utils Layer (src/utils/)
```

### 核心模块设计

#### 设备管理器 (DeviceManager)
```python
class DeviceManager:
    """
    设备管理器负责:
    - ADB设备连接和通信
    - 设备状态监控
    - 多设备并发控制
    - 设备池管理
    """
    
    def __init__(self):
        self.devices = {}  # 设备池
        self.adb_path = self._get_adb_path()
        
    def scan_devices(self) -> List[Device]:
        """扫描可用设备"""
        
    def connect_device(self, device_id: str) -> bool:
        """连接指定设备"""
        
    def execute_command(self, device_id: str, command: str) -> str:
        """在设备上执行命令"""
```

#### 自动化引擎 (AutomationEngine)
```python
class AutomationEngine:
    """
    自动化引擎负责:
    - UI元素定位和操作
    - 页面状态检测
    - 操作序列执行
    - 错误恢复机制
    """
    
    def find_element(self, strategy: str, value: str) -> Element:
        """查找UI元素"""
        
    def click_element(self, element: Element) -> bool:
        """点击元素"""
        
    def input_text(self, element: Element, text: str) -> bool:
        """输入文本"""
```

### 平台插件架构

#### 基础平台类
```python
from abc import ABC, abstractmethod

class BasePlatform(ABC):
    """平台自动化基类"""
    
    def __init__(self, device_manager: DeviceManager):
        self.device_manager = device_manager
        self.automation_engine = AutomationEngine(device_manager)
    
    @abstractmethod
    def login(self, credentials: dict) -> bool:
        """平台登录"""
        pass
    
    @abstractmethod  
    def follow_user(self, user_id: str) -> bool:
        """关注用户"""
        pass
    
    @abstractmethod
    def like_content(self, content_id: str) -> bool:
        """点赞内容"""
        pass
```

#### 小红书平台实现
```python
class XiaohongshuPlatform(BasePlatform):
    """小红书平台自动化实现"""
    
    def __init__(self, device_manager):
        super().__init__(device_manager)
        self.ui_elements = XiaohongshuUIElements()
    
    def follow_user(self, user_id: str) -> bool:
        """实现小红书关注逻辑"""
        # 1. 导航到用户页面
        # 2. 查找关注按钮
        # 3. 点击关注
        # 4. 验证结果
        pass
```

## 编码规范

### Python代码规范
```python
# 1. 导入顺序: 标准库 -> 第三方库 -> 本地模块
import os
import sys
from typing import List, Dict, Optional

import requests
from tkinter import ttk

from src.core.device_manager import DeviceManager
from src.utils.logger import get_logger

# 2. 类型注解
def process_devices(device_list: List[str]) -> Dict[str, bool]:
    """处理设备列表
    
    Args:
        device_list: 设备ID列表
        
    Returns:
        设备处理结果字典
        
    Raises:
        DeviceError: 设备连接失败时抛出
    """
    results = {}
    for device_id in device_list:
        results[device_id] = self._process_single_device(device_id)
    return results

# 3. 错误处理
class DeviceError(Exception):
    """设备相关错误"""
    pass

try:
    device_manager.connect(device_id)
except DeviceError as e:
    logger.error(f"设备连接失败: {device_id}, 错误: {e}")
    raise
```

### 日志规范
```python
import logging
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SomeClass:
    def some_method(self):
        logger.info("开始执行操作")
        
        try:
            # 业务逻辑
            result = self._do_something()
            logger.info(f"操作完成: {result}")
            return result
        except Exception as e:
            logger.error(f"操作失败: {e}", exc_info=True)
            raise
```

### GUI代码规范
```python
class DevicePanel(BaseComponent):
    """设备管理面板"""
    
    def __init__(self, parent, device_manager: DeviceManager):
        super().__init__(parent)
        self.device_manager = device_manager
        self.setup_ui()
        self.bind_events()
    
    def setup_ui(self):
        """设置UI布局"""
        # 创建主框架
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 设备列表
        self.device_tree = ttk.Treeview(self.main_frame)
        self.device_tree.pack(fill='both', expand=True)
    
    def bind_events(self):
        """绑定事件"""
        self.device_tree.bind('<<TreeviewSelect>>', self.on_device_select)
    
    @ErrorHandler.handle_gui_error
    def on_device_select(self, event):
        """设备选择事件处理"""
        selection = self.device_tree.selection()
        if selection:
            device_id = self.device_tree.item(selection[0])['values'][0]
            self.show_device_details(device_id)
```

## 测试指南

### 单元测试示例
```python
import unittest
from unittest.mock import Mock, patch
from src.core.device_manager import DeviceManager

class TestDeviceManager(unittest.TestCase):
    
    def setUp(self):
        self.device_manager = DeviceManager()
    
    @patch('subprocess.run')
    def test_scan_devices(self, mock_run):
        """测试设备扫描功能"""
        # 模拟adb devices输出
        mock_run.return_value.stdout = "emulator-5554\tdevice\n"
        
        devices = self.device_manager.scan_devices()
        
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0].device_id, "emulator-5554")
    
    def test_device_connection(self):
        """测试设备连接"""
        with patch.object(self.device_manager, '_execute_adb') as mock_adb:
            mock_adb.return_value = ("", "")
            
            result = self.device_manager.connect_device("test-device")
            
            self.assertTrue(result)
            mock_adb.assert_called_once()

if __name__ == '__main__':
    unittest.main()
```

### 集成测试示例
```python
import pytest
from src.core.device_manager import DeviceManager
from src.platforms.xiaohongshu.automation import XiaohongshuPlatform

class TestXiaohongshuIntegration:
    
    @pytest.fixture
    def device_manager(self):
        dm = DeviceManager()
        # 使用测试设备或模拟器
        dm.connect_device("emulator-5554")
        return dm
    
    @pytest.fixture
    def xhs_platform(self, device_manager):
        return XiaohongshuPlatform(device_manager)
    
    def test_app_launch(self, xhs_platform):
        """测试应用启动"""
        result = xhs_platform.launch_app()
        assert result is True
    
    def test_navigation_flow(self, xhs_platform):
        """测试页面导航流程"""
        # 启动应用
        xhs_platform.launch_app()
        
        # 导航到关注页面
        result = xhs_platform.navigate_to_follow_page()
        
        assert result is True
```

## 性能优化指南

### 多线程处理
```python
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

class TaskExecutor:
    """任务执行器"""
    
    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_queue = queue.Queue()
    
    def submit_task(self, func, *args, **kwargs):
        """提交任务"""
        future = self.executor.submit(func, *args, **kwargs)
        return future
    
    def execute_batch(self, tasks: List[callable]):
        """批量执行任务"""
        futures = []
        for task in tasks:
            future = self.submit_task(task)
            futures.append(future)
        
        # 等待所有任务完成
        results = []
        for future in futures:
            try:
                result = future.result(timeout=30)
                results.append(result)
            except Exception as e:
                logger.error(f"任务执行失败: {e}")
                results.append(None)
        
        return results
```

### 内存优化
```python
import weakref
import gc

class ResourceManager:
    """资源管理器"""
    
    def __init__(self):
        self._resources = weakref.WeakValueDictionary()
    
    def get_resource(self, key):
        """获取资源"""
        if key in self._resources:
            return self._resources[key]
        
        # 创建新资源
        resource = self._create_resource(key)
        self._resources[key] = resource
        return resource
    
    def cleanup(self):
        """清理资源"""
        self._resources.clear()
        gc.collect()
```

## 调试技巧

### ADB调试
```bash
# 查看设备列表
adb devices

# 查看设备日志
adb logcat | grep "com.xingin.xhs"

# 截图调试
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png

# UI层次结构
adb shell uiautomator dump /sdcard/ui.xml
adb pull /sdcard/ui.xml
```

### Python调试
```python
import pdb
import logging

# 设置断点
def some_function():
    pdb.set_trace()  # 调试断点
    # 业务逻辑
    
# 日志调试
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_function():
    logger.debug("调试信息")
    logger.info("普通信息") 
    logger.warning("警告信息")
    logger.error("错误信息")
```

## 部署指南

### 开发环境部署
```bash
# 1. 克隆代码
git clone https://github.com/wyw121/Flow_Farm.git
cd Flow_Farm

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements-dev.txt

# 4. 配置环境
cp .env.example .env
# 编辑.env文件设置ADB路径等

# 5. 运行测试
python -m pytest tests/

# 6. 启动应用
python src/main.py --debug
```

### 生产环境构建
```bash
# 1. 清理环境
python scripts/clean.py

# 2. 构建应用
python scripts/build.py --mode production --encrypt

# 3. 测试构建结果
python scripts/validate_build.py

# 4. 创建分发包
python scripts/package.py --output dist/

# 5. 验证分发包
python scripts/test_package.py dist/Flow_Farm_v1.0.0.zip
```

## 常见问题解决

### ADB连接问题
```python
# 问题: 设备无法连接
# 解决方案:
1. 检查USB调试是否开启
2. 验证ADB驱动是否正确安装
3. 尝试重启ADB服务: adb kill-server && adb start-server
4. 检查USB连接模式是否为文件传输模式
```

### GUI性能问题
```python
# 问题: 界面卡顿
# 解决方案:
1. 将耗时操作移到后台线程
2. 使用after()方法更新UI
3. 减少UI更新频率
4. 使用虚拟列表处理大量数据
```

### 内存泄漏问题
```python
# 问题: 内存使用持续增长
# 解决方案:
1. 及时关闭文件和数据库连接
2. 使用弱引用避免循环引用
3. 定期调用gc.collect()
4. 监控大对象的生命周期
```

## 代码贡献流程

### 分支管理
```bash
# 主分支
main          # 稳定版本
develop       # 开发版本

# 功能分支
feature/设备管理    # 新功能开发
bugfix/修复连接     # 错误修复
hotfix/紧急修复     # 紧急修复
```

### 提交规范
```bash
# 提交消息格式
类型(范围): 简短描述

详细描述

# 示例
feat(device): 添加设备自动重连功能

实现设备断线自动检测和重连机制，提高系统稳定性
- 添加设备状态监控
- 实现自动重连逻辑
- 更新相关测试用例
```

### 代码审查清单
- [ ] 代码符合PEP 8规范
- [ ] 添加了充分的测试用例
- [ ] 更新了相关文档
- [ ] 通过了所有测试
- [ ] 性能没有明显下降
- [ ] 安全性检查通过
