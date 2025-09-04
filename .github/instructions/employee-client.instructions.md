# 员工客户端开发指令 - Rust + Tauri 架构

## 适用范围
这些指令适用于 `employee-client/src-tauri/**/*.rs` 路径下的所有 Rust 代码文件。

## 技术栈规范

### 核心框架和库
- **GUI框架**: Tauri 2.0 (原生桌面应用)
- **后端语言**: Rust (Edition 2021)
- **前端技术**: HTML/CSS/JavaScript (最小化，仅用于UI渲染)
- **构建系统**: Cargo + Tauri CLI
- **HTTP客户端**: reqwest
- **序列化**: serde + serde_json
- **异步运行时**: tokio
- **设备通信**: Android Debug Bridge (ADB)
- **数据存储**: SQLite (本地缓存) + REST API
- **任务调度**: 基于tokio的异步任务管理
- **日志记录**: log + env_logger

### Tauri架构规范
```rust
// Tauri命令模式
use tauri::command;

#[command]
async fn connect_device(device_id: String) -> Result<String, String> {
    // 设备连接逻辑
    Ok("Device connected".to_string())
}

// 主程序入口
fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            connect_device,
            // 其他命令...
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### 项目结构
```
employee-client/
├── src-tauri/              # Rust 后端代码
│   ├── src/
│   │   ├── main.rs        # 应用程序入口点
│   │   ├── api.rs         # API 通信模块
│   │   ├── device.rs      # 设备管理 (ADB连接和控制)
│   │   ├── models.rs      # 数据模型和类型定义
│   │   └── utils.rs       # 工具函数和辅助模块
│   ├── Cargo.toml         # Rust 依赖配置
│   └── tauri.conf.json    # Tauri 应用配置
├── src/                   # 前端资源 (HTML/CSS/JS)
├── logs/                  # 日志文件
└── target/                # 构建产物 (git ignore)
```
│   └── config_manager.py   # 配置管理器
├── gui/                    # GUI界面模块 (用户交互)
│   ├── main_window.py      # 主窗口 (应用程序主界面)
│   ├── components/         # 可复用组件
│   │   ├── device_panel.py # 设备状态面板
│   │   ├── task_panel.py   # 任务控制面板
│   │   └── log_panel.py    # 日志显示面板
│   ├── windows/            # 独立窗口
│   │   ├── settings_window.py # 设置窗口
│   │   └── device_config_window.py # 设备配置窗口
│   └── dialogs/            # 对话框
│       ├── login_dialog.py # 登录对话框
│       └── device_dialog.py # 设备选择对话框
├── platforms/              # 平台特定自动化模块
│   ├── base_platform.py    # 平台基类 (抽象接口)
│   ├── xiaohongshu/        # 小红书自动化
│   │   ├── automation.py   # 小红书自动化逻辑
│   │   ├── ui_elements.py  # UI元素定义
│   │   └── strategies.py   # 操作策略
│   └── douyin/             # 抖音自动化
│       ├── automation.py   # 抖音自动化逻辑
│       ├── ui_elements.py  # UI元素定义
│       └── strategies.py   # 操作策略
├── auth/                   # 权限认证系统
│   ├── user_manager.py     # 用户管理 (CRUD操作)
│   ├── permission.py       # 权限控制 (RBAC实现)
│   ├── session.py          # 会话管理
│   └── crypto.py           # 加密工具
└── utils/                  # 工具类和帮助函数
    ├── logger.py           # 日志配置
    ├── adb_helper.py       # ADB命令封装
    ├── ui_parser.py        # UI XML解析
    └── validator.py        # 数据验证
```
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
