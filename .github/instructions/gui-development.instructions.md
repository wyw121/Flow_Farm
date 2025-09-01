---
applyTo: "src/gui/**/*.py"
---

# GUI界面开发指令 - OneDragon架构指导

## OneDragon GUI 架构学习指导

### 核心技术栈升级

基于对 OneDragon ZenlessZoneZero 项目的分析，GUI 开发必须遵循以下现代化架构：

#### 必需依赖升级
```bash
# 从当前版本升级
# PySide6==6.6.1 qtawesome==1.3.1

# 升级到目标版本
pip install PySide6==6.8.0.2
pip install qfluentwidgets==1.7.0
pip install qtawesome==1.3.1  # 保留兼容
```

#### 核心组件导入模式
```python
# 基础框架
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QFont, QIcon

# Fluent Design 组件（新增）
from qfluentwidgets import (
    # 基础容器
    VerticalScrollInterface, QWidget,

    # 按钮组件
    PrimaryPushButton, PushButton, ToolButton,

    # 设置组件
    SettingCardGroup, SettingCard,
    ComboBoxSettingCard, SwitchSettingCard,
    RangeSettingCard, TextSettingCard,

    # 输入组件
    LineEdit, TextEdit, ComboBox,

    # 信息组件
    InfoBar, MessageBox, TeachingTip,

    # 图标系统
    FluentIcon, IconWidget,

    # 主题系统
    Theme, qconfig, setTheme,

    # 布局组件
    VBoxLayout, HBoxLayout,
)
```
- **Material Design风格**: 使用现代化的卡片布局和阴影效果
- **响应式设计**: 支持窗口大小调整和不同分辨率适配
- **主题系统**: 支持亮色/暗色主题动态切换
- **国际化支持**: 预留多语言支持接口

### 权限控制界面规范
```python
# 权限级别可视化设计
PERMISSION_LEVELS = {
    "admin": {
        "color": "#FF5722",  # 红色 - 管理员
        "icon": "🔑",
        "features": ["device_manage", "user_manage", "system_config"]
    },
    "user": {
        "color": "#2196F3",  # 蓝色 - 普通用户
        "icon": "👤",
        "features": ["task_execute", "device_view", "log_view"]
    },
    "guest": {
        "color": "#757575",  # 灰色 - 访客
        "icon": "👁️",
        "features": ["readonly"]
    }
}
```

## 标准化组件基类

### BaseWindow - 窗口基类
```python
import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod

class BaseWindow(ABC):
    def __init__(self, title="Flow Farm", size=(1200, 800)):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{size[0]}x{size[1]}")
        self.setup_theme()
        self.setup_layout()
        self.bind_events()

    def setup_theme(self):
        """设置现代化主题"""
        style = ttk.Style()
        style.theme_use('clam')

        # 自定义样式
        style.configure('Card.TFrame', relief='raised', borderwidth=1)
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Status.TLabel', foreground='green')

    @abstractmethod
    def setup_layout(self):
        """子类必须实现的布局方法"""
        pass

    def bind_events(self):
        """绑定全局事件"""
        self.root.bind('<Control-q>', lambda e: self.on_quit())
        self.root.protocol("WM_DELETE_WINDOW", self.on_quit)

    def show_message(self, title, message, msg_type="info"):
        """统一的消息显示接口"""
        from tkinter import messagebox
        if msg_type == "error":
            messagebox.showerror(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)

    def on_quit(self):
        """安全退出处理"""
        # 保存用户设置、清理资源等
        self.root.quit()
        self.root.destroy()
```

### BaseComponent - 组件基类
```python
class BaseComponent(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.setup_component()
        self.setup_events()

    @abstractmethod
    def setup_component(self):
        """子类实现具体组件布局"""
        pass

    def setup_events(self):
        """设置组件事件绑定"""
        pass

    def update_data(self, data):
        """更新组件数据显示"""
        pass

    def get_data(self):
        """获取组件当前数据"""
        return {}
```

## 实时状态管理系统

### 状态更新机制
```python
import threading
import queue
from enum import Enum

class StatusType(Enum):
    DEVICE_STATUS = "device_status"
    TASK_PROGRESS = "task_progress"
    SYSTEM_INFO = "system_info"
    USER_ACTION = "user_action"

class StatusManager:
    def __init__(self):
        self.status_queue = queue.Queue()
        self.observers = {}
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()

    def register_observer(self, status_type: StatusType, callback):
        """注册状态观察者"""
        if status_type not in self.observers:
            self.observers[status_type] = []
        self.observers[status_type].append(callback)

    def update_status(self, status_type: StatusType, data):
        """更新状态数据"""
        self.status_queue.put((status_type, data))

    def _update_loop(self):
        """状态更新循环"""
        while True:
            try:
                status_type, data = self.status_queue.get(timeout=1)
                if status_type in self.observers:
                    for callback in self.observers[status_type]:
                        callback(data)
            except queue.Empty:
                continue
```

## 用户体验优化规范

### 长时间操作处理
```python
import threading
from tkinter import ttk

class ProgressDialog:
    def __init__(self, parent, title="处理中...", message="请稍候"):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x120")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 居中显示
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))

        # 布局
        ttk.Label(self.dialog, text=message).pack(pady=10)
        self.progress = ttk.Progressbar(self.dialog, mode='indeterminate')
        self.progress.pack(pady=10, padx=20, fill='x')
        self.progress.start()

        self.cancel_button = ttk.Button(self.dialog, text="取消", command=self.cancel)
        self.cancel_button.pack(pady=5)

        self.cancelled = False

    def cancel(self):
        self.cancelled = True
        self.close()

    def close(self):
        self.progress.stop()
        self.dialog.destroy()

def long_operation_wrapper(func, progress_dialog=None):
    """长时间操作装饰器"""
    def wrapper(*args, **kwargs):
        if progress_dialog:
            def run_operation():
                try:
                    result = func(*args, **kwargs)
                    if not progress_dialog.cancelled:
                        progress_dialog.close()
                    return result
                except Exception as e:
                    progress_dialog.close()
                    raise e

            thread = threading.Thread(target=run_operation)
            thread.daemon = True
            thread.start()
        else:
            return func(*args, **kwargs)

    return wrapper
```

### 快捷键和无障碍支持
```python
class KeyboardManager:
    def __init__(self, window):
        self.window = window
        self.setup_shortcuts()

    def setup_shortcuts(self):
        """设置全局快捷键"""
        shortcuts = {
            '<Control-n>': self.new_task,
            '<Control-s>': self.save_config,
            '<Control-r>': self.refresh_devices,
            '<F5>': self.refresh_status,
            '<F11>': self.toggle_fullscreen,
            '<Alt-F4>': self.close_application
        }

        for key, callback in shortcuts.items():
            self.window.bind(key, callback)

    def new_task(self, event=None):
        """新建任务快捷键"""
        pass

    def save_config(self, event=None):
        """保存配置快捷键"""
        pass
```

## 错误处理和用户反馈

### 统一错误处理
```python
import traceback
import logging

class ErrorHandler:
    @staticmethod
    def handle_gui_error(func):
        """GUI操作错误处理装饰器"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(f"GUI操作错误: {func.__name__}: {str(e)}")
                logging.debug(traceback.format_exc())

                # 用户友好的错误提示
                error_msg = f"操作失败: {str(e)}\n\n请查看日志获取详细信息"
                tk.messagebox.showerror("错误", error_msg)

                return None
        return wrapper
```

### 操作确认机制
```python
class ConfirmationDialog:
    @staticmethod
    def confirm_action(parent, title, message, action_callback):
        """通用确认对话框"""
        result = tk.messagebox.askyesno(title, message, parent=parent)
        if result and action_callback:
            action_callback()
        return result

    @staticmethod
    def confirm_dangerous_action(parent, action_name, target, callback):
        """危险操作确认"""
        message = f"确定要{action_name} {target}吗?\n\n此操作不可撤销!"
        return ConfirmationDialog.confirm_action(
            parent, f"确认{action_name}", message, callback
        )
```

## 性能优化指导

### UI更新优化
- 使用虚拟化列表处理大量数据显示
- 实现懒加载机制，按需加载UI组件
- 使用after()方法进行UI线程安全更新
- 避免在主线程执行耗时操作

### 内存管理
- 及时销毁不用的窗口和组件
- 使用弱引用避免循环引用
- 定期清理缓存数据
- 监控GUI组件内存使用情况
