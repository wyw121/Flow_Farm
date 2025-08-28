#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主GUI窗口模块

Flow Farm主应用程序窗口，负责整个应用的用户界面入口
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from utils.logger import get_logger
from auth.session import SessionManager


class MainWindow:
    """主应用程序窗口"""
    
    def __init__(self, config: Dict[str, Any], session_manager: SessionManager):
        """
        初始化主窗口
        
        Args:
            config: 应用程序配置
            session_manager: 会话管理器
        """
        self.logger = get_logger(__name__)
        self.config = config
        self.session_manager = session_manager
        
        # GUI组件
        self.root = None
        self.main_frame = None
        self.status_bar = None
        
        # 初始化GUI
        self._init_gui()
        self._setup_menu()
        self._setup_layout()
        self._setup_status_bar()
        
        self.logger.info("主窗口初始化完成")
    
    def _init_gui(self):
        """初始化GUI基础组件"""
        self.root = tk.Tk()
        self.root.title(f"{self.config.get('app.name', 'Flow Farm')} v{self.config.get('app.version', '1.0.0')}")
        
        # 窗口大小和位置
        width = self.config.get('gui.window_width', 1200)
        height = self.config.get('gui.window_height', 800)
        
        # 居中显示
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(800, 600)
        
        # 设置图标（如果存在）
        try:
            icon_path = Path("assets/icon.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception as e:
            self.logger.debug(f"无法设置窗口图标: {e}")
        
        # 设置主题
        self._setup_theme()
        
        # 绑定窗口事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_theme(self):
        """设置主题样式"""
        style = ttk.Style()
        
        # 根据配置选择主题
        theme_mode = self.config.get('gui.theme', 'system')
        
        if theme_mode == 'dark':
            # 暗色主题（如果支持）
            try:
                style.theme_use('clam')
                # 这里可以添加自定义暗色主题配置
            except tk.TclError:
                style.theme_use('default')
        elif theme_mode == 'light':
            # 亮色主题
            style.theme_use('clam')
        else:
            # 系统主题
            try:
                style.theme_use('vista')  # Windows
            except tk.TclError:
                try:
                    style.theme_use('aqua')  # macOS
                except tk.TclError:
                    style.theme_use('clam')  # Linux/其他
        
        # 自定义样式
        style.configure('Title.TLabel', font=(self.config.get('gui.font_family', '微软雅黑'), 16, 'bold'))
        style.configure('Heading.TLabel', font=(self.config.get('gui.font_family', '微软雅黑'), 12, 'bold'))
    
    def _setup_menu(self):
        """设置菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建任务", command=self._new_task, accelerator="Ctrl+N")
        file_menu.add_command(label="打开配置", command=self._open_config)
        file_menu.add_command(label="保存配置", command=self._save_config, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_closing, accelerator="Ctrl+Q")
        
        # 设备菜单
        device_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设备", menu=device_menu)
        device_menu.add_command(label="扫描设备", command=self._scan_devices, accelerator="F5")
        device_menu.add_command(label="设备管理", command=self._show_device_manager)
        device_menu.add_command(label="连接测试", command=self._test_connections)
        
        # 任务菜单
        task_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="任务", menu=task_menu)
        task_menu.add_command(label="任务管理", command=self._show_task_manager)
        task_menu.add_command(label="开始执行", command=self._start_tasks)
        task_menu.add_command(label="停止执行", command=self._stop_tasks)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="系统设置", command=self._show_settings)
        tools_menu.add_command(label="日志查看", command=self._show_logs)
        tools_menu.add_command(label="数据导出", command=self._export_data)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="用户指南", command=self._show_user_guide)
        help_menu.add_command(label="关于", command=self._show_about)
        
        # 绑定快捷键
        self.root.bind('<Control-n>', lambda e: self._new_task())
        self.root.bind('<Control-s>', lambda e: self._save_config())
        self.root.bind('<Control-q>', lambda e: self._on_closing())
        self.root.bind('<F5>', lambda e: self._scan_devices())
    
    def _setup_layout(self):
        """设置主布局"""
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 欢迎标题
        title_label = ttk.Label(
            self.main_frame,
            text="Flow Farm - 手机流量农场自动化系统",
            style='Title.TLabel'
        )
        title_label.pack(pady=20)
        
        # 创建笔记本组件（标签页）
        notebook = ttk.Notebook(self.main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 设备管理标签页
        device_frame = ttk.Frame(notebook)
        notebook.add(device_frame, text="设备管理")
        self._setup_device_tab(device_frame)
        
        # 任务管理标签页
        task_frame = ttk.Frame(notebook)
        notebook.add(task_frame, text="任务管理")
        self._setup_task_tab(task_frame)
        
        # 监控统计标签页
        monitor_frame = ttk.Frame(notebook)
        notebook.add(monitor_frame, text="监控统计")
        self._setup_monitor_tab(monitor_frame)
        
        # 系统日志标签页
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="系统日志")
        self._setup_log_tab(log_frame)
    
    def _setup_device_tab(self, parent):
        """设置设备管理标签页"""
        # 工具栏
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="扫描设备", command=self._scan_devices).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="连接测试", command=self._test_connections).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="设备详情", command=self._show_device_details).pack(side=tk.LEFT, padx=(0, 5))
        
        # 设备列表
        list_frame = ttk.LabelFrame(parent, text="设备列表")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview
        columns = ('ID', '设备名', '状态', '平台', '最后连接')
        device_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        # 设置列标题
        for col in columns:
            device_tree.heading(col, text=col)
            device_tree.column(col, width=120)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=device_tree.yview)
        device_tree.configure(yscrollcommand=scrollbar.set)
        
        device_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 示例数据
        device_tree.insert('', 'end', values=('device-001', 'Mi 11', '在线', 'Android 12', '2023-12-01 14:30'))
        device_tree.insert('', 'end', values=('device-002', 'OPPO R15', '离线', 'Android 10', '2023-12-01 12:15'))
    
    def _setup_task_tab(self, parent):
        """设置任务管理标签页"""
        # 任务控制面板
        control_frame = ttk.LabelFrame(parent, text="任务控制")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 控制按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="新建任务", command=self._new_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="开始执行", command=self._start_tasks).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="暂停任务", command=self._pause_tasks).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="停止任务", command=self._stop_tasks).pack(side=tk.LEFT, padx=(0, 5))
        
        # 任务列表
        task_list_frame = ttk.LabelFrame(parent, text="任务列表")
        task_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 任务Treeview
        task_columns = ('任务名', '平台', '设备', '状态', '进度', '创建时间')
        task_tree = ttk.Treeview(task_list_frame, columns=task_columns, show='headings', height=8)
        
        for col in task_columns:
            task_tree.heading(col, text=col)
            task_tree.column(col, width=100)
        
        task_scrollbar = ttk.Scrollbar(task_list_frame, orient=tk.VERTICAL, command=task_tree.yview)
        task_tree.configure(yscrollcommand=task_scrollbar.set)
        
        task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        task_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 示例数据
        task_tree.insert('', 'end', values=('小红书关注', '小红书', 'device-001', '执行中', '65%', '2023-12-01 14:00'))
        task_tree.insert('', 'end', values=('抖音点赞', '抖音', 'device-002', '等待中', '0%', '2023-12-01 14:15'))
    
    def _setup_monitor_tab(self, parent):
        """设置监控统计标签页"""
        # 统计卡片
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 创建统计卡片
        cards = [
            ("在线设备", "5/10", "🟢"),
            ("执行任务", "3", "🔄"),
            ("今日操作", "1,245", "📊"),
            ("成功率", "94.5%", "✅")
        ]
        
        for i, (title, value, icon) in enumerate(cards):
            card = ttk.LabelFrame(stats_frame, text=title)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            value_label = ttk.Label(card, text=f"{icon} {value}", font=('Arial', 14, 'bold'))
            value_label.pack(pady=10)
        
        # 图表区域（占位）
        chart_frame = ttk.LabelFrame(parent, text="执行统计图表")
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        chart_placeholder = ttk.Label(chart_frame, text="📈 图表功能正在开发中...", font=('Arial', 12))
        chart_placeholder.pack(expand=True)
    
    def _setup_log_tab(self, parent):
        """设置系统日志标签页"""
        # 日志工具栏
        log_toolbar = ttk.Frame(parent)
        log_toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(log_toolbar, text="日志级别:").pack(side=tk.LEFT, padx=(0, 5))
        
        log_level_var = tk.StringVar(value="INFO")
        log_level_combo = ttk.Combobox(log_toolbar, textvariable=log_level_var, 
                                       values=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                                       state='readonly', width=10)
        log_level_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(log_toolbar, text="刷新", command=self._refresh_logs).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(log_toolbar, text="清空", command=self._clear_logs).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(log_toolbar, text="导出", command=self._export_logs).pack(side=tk.LEFT, padx=(0, 5))
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(parent, text="系统日志")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文本框和滚动条
        log_text = tk.Text(log_frame, wrap=tk.WORD, height=15)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=log_text.yview)
        log_text.configure(yscrollcommand=log_scrollbar.set)
        
        log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 插入示例日志
        sample_logs = [
            "2023-12-01 14:30:25 - INFO - 应用程序启动",
            "2023-12-01 14:30:26 - INFO - 配置文件加载成功",
            "2023-12-01 14:30:27 - INFO - 设备扫描开始",
            "2023-12-01 14:30:28 - INFO - 发现设备: device-001",
            "2023-12-01 14:30:29 - WARNING - 设备 device-002 连接失败",
            "2023-12-01 14:30:30 - INFO - 任务调度器启动",
        ]
        
        for log in sample_logs:
            log_text.insert(tk.END, log + "\n")
        
        log_text.config(state=tk.DISABLED)  # 设置为只读
    
    def _setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 状态标签
        self.status_label = ttk.Label(self.status_bar, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # 时间标签
        self.time_label = ttk.Label(self.status_bar, text="")
        self.time_label.pack(side=tk.RIGHT, padx=10)
        
        # 更新时间
        self._update_time()
    
    def _update_time(self):
        """更新状态栏时间"""
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self._update_time)  # 每秒更新
    
    # 菜单事件处理函数
    def _new_task(self):
        """新建任务"""
        messagebox.showinfo("新建任务", "新建任务功能正在开发中...")
    
    def _open_config(self):
        """打开配置"""
        messagebox.showinfo("打开配置", "配置管理功能正在开发中...")
    
    def _save_config(self):
        """保存配置"""
        messagebox.showinfo("保存配置", "配置已保存")
    
    def _scan_devices(self):
        """扫描设备"""
        self.status_label.config(text="正在扫描设备...")
        messagebox.showinfo("扫描设备", "设备扫描功能正在开发中...")
        self.status_label.config(text="就绪")
    
    def _show_device_manager(self):
        """显示设备管理器"""
        messagebox.showinfo("设备管理", "设备管理功能正在开发中...")
    
    def _test_connections(self):
        """测试连接"""
        messagebox.showinfo("连接测试", "连接测试功能正在开发中...")
    
    def _show_device_details(self):
        """显示设备详情"""
        messagebox.showinfo("设备详情", "设备详情功能正在开发中...")
    
    def _show_task_manager(self):
        """显示任务管理器"""
        messagebox.showinfo("任务管理", "任务管理功能正在开发中...")
    
    def _start_tasks(self):
        """开始任务"""
        messagebox.showinfo("开始任务", "任务执行功能正在开发中...")
    
    def _pause_tasks(self):
        """暂停任务"""
        messagebox.showinfo("暂停任务", "任务已暂停")
    
    def _stop_tasks(self):
        """停止任务"""
        messagebox.showinfo("停止任务", "任务已停止")
    
    def _show_settings(self):
        """显示设置"""
        messagebox.showinfo("系统设置", "系统设置功能正在开发中...")
    
    def _show_logs(self):
        """显示日志"""
        messagebox.showinfo("日志查看", "您已在日志标签页中")
    
    def _export_data(self):
        """导出数据"""
        messagebox.showinfo("数据导出", "数据导出功能正在开发中...")
    
    def _refresh_logs(self):
        """刷新日志"""
        messagebox.showinfo("刷新日志", "日志已刷新")
    
    def _clear_logs(self):
        """清空日志"""
        if messagebox.askyesno("清空日志", "确定要清空所有日志吗？"):
            messagebox.showinfo("清空日志", "日志已清空")
    
    def _export_logs(self):
        """导出日志"""
        messagebox.showinfo("导出日志", "日志导出功能正在开发中...")
    
    def _show_user_guide(self):
        """显示用户指南"""
        messagebox.showinfo("用户指南", "用户指南功能正在开发中...")
    
    def _show_about(self):
        """显示关于对话框"""
        about_text = f"""
Flow Farm - 手机流量农场自动化系统
版本: {self.config.get('app.version', '1.0.0')}

这是一个企业级手机流量农场自动化系统，
专为批量设备管理和社交媒体自动化操作而设计。

© 2023 Flow Farm Team
        """
        messagebox.showinfo("关于", about_text.strip())
    
    def _on_closing(self):
        """窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出Flow Farm吗？"):
            self.logger.info("用户关闭应用程序")
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """运行主窗口"""
        self.logger.info("启动GUI主循环")
        try:
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"GUI运行错误: {e}", exc_info=True)
            raise
        finally:
            self.logger.info("GUI主循环结束")
