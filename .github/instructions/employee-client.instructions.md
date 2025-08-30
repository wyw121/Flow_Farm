---
applyTo: "employee-client/**/*.py"
---

# 员工客户端开发指令

## 适用范围
本指令适用于 `employee-client/` 目录下的所有 Python 文件，专门用于构建员工使用的桌面客户端应用程序。

## 技术要求

### 核心框架和库
- 使用 tkinter 作为主要 GUI 框架
- 使用 ADB (Android Debug Bridge) 进行设备控制
- 使用 uiautomator2 进行 UI 自动化
- 使用 requests 进行 API 通信
- 使用 SQLite 进行本地数据缓存
- 使用 threading 进行多线程操作

### 员工权限系统
- 权限级别: 3 (最低)
- 只能访问数据上报和任务接收 API
- 本地存储加密的认证信息
- 实现离线模式功能
- 定期与服务器同步数据

### 设备管理功能
- 自动发现连接的 Android 设备
- 支持多设备并发操作
- 设备状态监控和健康检查
- 设备连接异常自动重连
- 设备操作日志记录

### 平台自动化支持
1. **抖音平台**
   - 自动关注用户
   - 视频点赞和评论
   - 直播间互动
   - 数据收集上报

2. **小红书平台**
   - 笔记点赞和收藏
   - 用户关注操作
   - 评论互动
   - 热门内容监控

### GUI 界面设计
- 主窗口显示设备列表和状态
- 任务管理面板显示进行中的任务
- 日志窗口实时显示操作记录
- 设置界面配置自动化参数
- 统计界面显示工作数据

## 代码示例

### 设备管理示例
```python
import adb_shell
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
import uiautomator2 as u2
from typing import List, Dict, Optional

class DeviceManager:
    def __init__(self):
        self.devices: Dict[str, u2.Device] = {}
        self.device_status: Dict[str, str] = {}
    
    def discover_devices(self) -> List[str]:
        """发现连接的设备"""
        import subprocess
        result = subprocess.run(['adb', 'devices'], 
                              capture_output=True, text=True)
        devices = []
        for line in result.stdout.split('\n')[1:]:
            if '\tdevice' in line:
                device_id = line.split('\t')[0]
                devices.append(device_id)
        return devices
    
    def connect_device(self, device_id: str) -> bool:
        """连接设备"""
        try:
            device = u2.connect(device_id)
            self.devices[device_id] = device
            self.device_status[device_id] = "connected"
            self.logger.info(f"设备 {device_id} 连接成功")
            return True
        except Exception as e:
            self.logger.error(f"设备 {device_id} 连接失败: {e}")
            self.device_status[device_id] = "error"
            return False
    
    def check_device_health(self, device_id: str) -> bool:
        """检查设备健康状态"""
        if device_id not in self.devices:
            return False
        
        try:
            device = self.devices[device_id]
            info = device.info
            return info is not None
        except Exception:
            return False
```

### 平台自动化基类示例
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import time
import random

class BasePlatform(ABC):
    def __init__(self, device: u2.Device, logger):
        self.device = device
        self.logger = logger
        self.platform_name = self.__class__.__name__
    
    @abstractmethod
    def login(self, credentials: Dict[str, str]) -> bool:
        """登录平台账户"""
        pass
    
    @abstractmethod
    def follow_user(self, user_info: Dict[str, Any]) -> bool:
        """关注用户"""
        pass
    
    @abstractmethod
    def get_follow_count(self) -> int:
        """获取关注数量"""
        pass
    
    def random_delay(self, min_seconds: int = 1, max_seconds: int = 3):
        """随机延迟，模拟人类操作"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def safe_click(self, selector: str, timeout: int = 10) -> bool:
        """安全点击，包含错误处理"""
        try:
            element = self.device(text=selector).wait(timeout=timeout)
            if element.exists:
                element.click()
                self.random_delay()
                return True
            return False
        except Exception as e:
            self.logger.error(f"点击失败: {selector}, 错误: {e}")
            return False
```

### GUI 主窗口示例
```python
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Flow Farm - 员工客户端")
        self.root.geometry("900x600")
        
        self.device_manager = DeviceManager()
        self.task_scheduler = TaskScheduler()
        
        self.setup_ui()
        self.start_background_tasks()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 设备管理面板
        device_frame = ttk.LabelFrame(main_frame, text="设备管理")
        device_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 设备列表
        self.device_tree = ttk.Treeview(device_frame, 
                                       columns=("device_id", "status", "platform"),
                                       show="headings", height=6)
        self.device_tree.heading("device_id", text="设备ID")
        self.device_tree.heading("status", text="状态")
        self.device_tree.heading("platform", text="当前平台")
        self.device_tree.pack(fill=tk.X, padx=5, pady=5)
        
        # 控制按钮
        button_frame = ttk.Frame(device_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="刷新设备", 
                  command=self.refresh_devices).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="开始任务", 
                  command=self.start_tasks).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="停止任务", 
                  command=self.stop_tasks).pack(side=tk.LEFT)
    
    def refresh_devices(self):
        """刷新设备列表"""
        def update_devices():
            devices = self.device_manager.discover_devices()
            for device_id in devices:
                if device_id not in self.device_manager.devices:
                    self.device_manager.connect_device(device_id)
            
            # 更新界面
            self.root.after(0, self.update_device_tree)
        
        threading.Thread(target=update_devices, daemon=True).start()
    
    def update_device_tree(self):
        """更新设备树显示"""
        # 清除现有项目
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)
        
        # 添加设备信息
        for device_id, status in self.device_manager.device_status.items():
            self.device_tree.insert("", tk.END, values=(device_id, status, "待分配"))
```

### 任务调度器示例
```python
import queue
import threading
from dataclasses import dataclass
from typing import Callable, Any
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    id: str
    device_id: str
    platform: str
    action: str
    parameters: Dict[str, Any]
    callback: Optional[Callable] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class TaskScheduler:
    def __init__(self, max_workers: int = 5):
        self.task_queue = queue.Queue()
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.max_workers = max_workers
        self.workers: List[threading.Thread] = []
        self.is_running = False
    
    def add_task(self, task: Task):
        """添加任务到队列"""
        self.task_queue.put(task)
        self.logger.info(f"任务已添加: {task.id}")
    
    def start(self):
        """启动任务调度器"""
        if self.is_running:
            return
        
        self.is_running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def _worker(self):
        """工作线程"""
        while self.is_running:
            try:
                task = self.task_queue.get(timeout=1)
                self._execute_task(task)
                self.task_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"任务执行异常: {e}")
```

## 重要提醒
- 实现适当的异常处理和重试机制
- 定期保存和同步数据到服务器
- 监控设备状态，避免过度使用
- 遵循平台的使用条款和限制
- 保护用户隐私和数据安全
- 实现优雅的程序退出和清理
- 提供详细的日志记录和错误报告
