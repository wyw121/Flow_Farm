"""
Flow Farm 员工客户端 - 功能界面视图
实现关注通讯录用户、同行监控、关注数统计等核心功能
"""

import json
import logging
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List, Optional

from ..base_window import ComponentFactory, ModernTheme


class TaskStatus:
    """任务状态枚举"""

    PENDING = "待执行"
    RUNNING = "执行中"
    COMPLETED = "已完成"
    FAILED = "失败"
    PAUSED = "已暂停"


class FollowTask:
    """关注任务类"""

    def __init__(self, task_id: str, task_type: str, target_count: int):
        self.task_id = task_id
        self.task_type = task_type  # 'contacts' 或 'competitor'
        self.target_count = target_count
        self.completed_count = 0
        self.status = TaskStatus.PENDING
        self.start_time = None
        self.end_time = None
        self.error_message = ""
        self.assigned_devices = []


class FunctionView:
    """功能界面视图"""

    def __init__(self, parent: tk.Widget, main_window):
        self.parent = parent
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self.theme = ModernTheme()

        # 功能状态
        self.current_task: Optional[FollowTask] = None
        self.contacts_file = None
        self.keywords_file = None
        self.competitor_account = ""
        self.user_balance = 1000.0  # 模拟用户余额
        self.follow_cost = 0.1  # 每次关注成本

        # 统计数据
        self.total_follows = 0
        self.daily_follows = 0
        self.today_date = time.strftime("%Y-%m-%d")

        # 初始化界面
        self.setup_layout()
        self.load_statistics()

        self.logger.info("功能界面视图初始化完成")

    def setup_layout(self):
        """设置布局"""
        # 主容器
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 使用网格布局
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # 左侧：功能操作区域
        self.create_function_panel(main_frame)

        # 右侧：统计和监控区域
        self.create_statistics_panel(main_frame)

        # 底部：任务进度区域
        self.create_progress_panel(main_frame)

    def create_function_panel(self, parent):
        """创建功能操作面板"""
        function_frame = ttk.Frame(parent)
        function_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # 1. 关注通讯录用户
        self.create_contacts_follow_section(function_frame)

        # 2. 同行监控
        self.create_competitor_monitor_section(function_frame)

        # 3. 任务控制
        self.create_task_control_section(function_frame)

    def create_statistics_panel(self, parent):
        """创建统计面板"""
        stats_frame = ttk.Frame(parent)
        stats_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # 关注数统计
        self.create_follow_statistics(stats_frame)

        # 余额信息
        self.create_balance_info(stats_frame)

        # 设备状态概览
        self.create_device_overview(stats_frame)

    def create_progress_panel(self, parent):
        """创建任务进度面板"""
        progress_frame = ttk.Frame(parent)
        progress_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        # 任务进度卡片
        progress_card = ttk.LabelFrame(progress_frame, text="任务进度", padding=10)
        progress_card.pack(fill="x")

        # 当前任务信息
        task_info_frame = ttk.Frame(progress_card)
        task_info_frame.pack(fill="x", pady=(0, 10))

        self.current_task_label = ttk.Label(
            task_info_frame, text="当前无任务", style="Heading.TLabel"
        )
        self.current_task_label.pack(side="left")

        self.task_status_label = ttk.Label(
            task_info_frame, text="", style="Body.TLabel"
        )
        self.task_status_label.pack(side="right")

        # 进度条
        progress_frame_inner = ttk.Frame(progress_card)
        progress_frame_inner.pack(fill="x", pady=(0, 5))

        self.progress_bar = ttk.Progressbar(
            progress_frame_inner,
            style="Modern.Horizontal.TProgressbar",
            mode="determinate",
        )
        self.progress_bar.pack(fill="x")

        # 进度文本
        self.progress_text = ttk.Label(
            progress_card, text="0 / 0 (0%)", style="Body.TLabel"
        )
        self.progress_text.pack()

    def create_contacts_follow_section(self, parent):
        """创建通讯录关注功能区域"""
        contacts_card = ttk.LabelFrame(parent, text="📱 关注通讯录用户", padding=10)
        contacts_card.pack(fill="x", pady=(0, 10))

        # 文件选择
        file_frame = ttk.Frame(contacts_card)
        file_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(file_frame, text="通讯录文件:", style="Body.TLabel").pack(anchor="w")

        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill="x", pady=(5, 0))

        self.contacts_file_var = tk.StringVar(value="未选择文件")
        contacts_file_label = ttk.Label(
            file_select_frame,
            textvariable=self.contacts_file_var,
            style="Body.TLabel",
            relief="sunken",
            padding=5,
        )
        contacts_file_label.pack(side="left", fill="x", expand=True)

        browse_btn = ttk.Button(
            file_select_frame, text="浏览", command=self.browse_contacts_file
        )
        browse_btn.pack(side="right", padx=(5, 0))

        # 关注数量设置
        count_frame = ttk.Frame(contacts_card)
        count_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(count_frame, text="关注数量:", style="Body.TLabel").pack(side="left")

        self.contacts_count_var = tk.StringVar(value="100")
        contacts_count_entry = ttk.Entry(
            count_frame, textvariable=self.contacts_count_var, width=10
        )
        contacts_count_entry.pack(side="left", padx=(5, 0))

        ttk.Label(count_frame, text="人", style="Body.TLabel").pack(
            side="left", padx=(2, 0)
        )

        # 开始按钮
        start_contacts_btn = ttk.Button(
            contacts_card,
            text="开始关注通讯录",
            command=self.start_contacts_follow,
            style="Primary.TButton",
        )
        start_contacts_btn.pack(fill="x")

    def create_competitor_monitor_section(self, parent):
        """创建同行监控功能区域"""
        monitor_card = ttk.LabelFrame(parent, text="👁️ 同行监控", padding=10)
        monitor_card.pack(fill="x", pady=(0, 10))

        # 同行账号输入
        account_frame = ttk.Frame(monitor_card)
        account_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(account_frame, text="同行账号:", style="Body.TLabel").pack(anchor="w")

        self.competitor_account_var = tk.StringVar()
        competitor_entry = ttk.Entry(
            account_frame,
            textvariable=self.competitor_account_var,
            placeholder_text="输入要监控的同行账号",
        )
        competitor_entry.pack(fill="x", pady=(5, 0))

        # 关键词文件选择
        keywords_frame = ttk.Frame(monitor_card)
        keywords_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(keywords_frame, text="关键词文件:", style="Body.TLabel").pack(
            anchor="w"
        )

        keywords_select_frame = ttk.Frame(keywords_frame)
        keywords_select_frame.pack(fill="x", pady=(5, 0))

        self.keywords_file_var = tk.StringVar(value="未选择文件")
        keywords_file_label = ttk.Label(
            keywords_select_frame,
            textvariable=self.keywords_file_var,
            style="Body.TLabel",
            relief="sunken",
            padding=5,
        )
        keywords_file_label.pack(side="left", fill="x", expand=True)

        keywords_browse_btn = ttk.Button(
            keywords_select_frame, text="浏览", command=self.browse_keywords_file
        )
        keywords_browse_btn.pack(side="right", padx=(5, 0))

        # 目标数量设置
        target_frame = ttk.Frame(monitor_card)
        target_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(target_frame, text="目标关注数:", style="Body.TLabel").pack(
            side="left"
        )

        self.monitor_count_var = tk.StringVar(value="50")
        monitor_count_entry = ttk.Entry(
            target_frame, textvariable=self.monitor_count_var, width=10
        )
        monitor_count_entry.pack(side="left", padx=(5, 0))

        ttk.Label(target_frame, text="人", style="Body.TLabel").pack(
            side="left", padx=(2, 0)
        )

        # 开始按钮
        start_monitor_btn = ttk.Button(
            monitor_card,
            text="开始同行监控",
            command=self.start_competitor_monitor,
            style="Secondary.TButton",
        )
        start_monitor_btn.pack(fill="x")

    def create_task_control_section(self, parent):
        """创建任务控制区域"""
        control_card = ttk.LabelFrame(parent, text="⚙️ 任务控制", padding=10)
        control_card.pack(fill="x")

        button_frame = ttk.Frame(control_card)
        button_frame.pack(fill="x")

        # 暂停按钮
        self.pause_btn = ttk.Button(
            button_frame, text="⏸️ 暂停", command=self.pause_task, state="disabled"
        )
        self.pause_btn.pack(side="left", padx=(0, 5))

        # 恢复按钮
        self.resume_btn = ttk.Button(
            button_frame, text="▶️ 恢复", command=self.resume_task, state="disabled"
        )
        self.resume_btn.pack(side="left", padx=(0, 5))

        # 停止按钮
        self.stop_btn = ttk.Button(
            button_frame, text="⏹️ 停止", command=self.stop_task, state="disabled"
        )
        self.stop_btn.pack(side="left")

    def create_follow_statistics(self, parent):
        """创建关注数统计"""
        stats_card = ttk.LabelFrame(parent, text="📊 关注统计", padding=10)
        stats_card.pack(fill="x", pady=(0, 10))

        # 总关注数
        total_frame = ttk.Frame(stats_card)
        total_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(total_frame, text="总关注人数:", style="Body.TLabel").pack(
            side="left"
        )
        self.total_follows_label = ttk.Label(
            total_frame, text=f"{self.total_follows:,}", style="Heading.TLabel"
        )
        self.total_follows_label.pack(side="right")

        # 今日关注数
        daily_frame = ttk.Frame(stats_card)
        daily_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(daily_frame, text="今日新增:", style="Body.TLabel").pack(side="left")
        self.daily_follows_label = ttk.Label(
            daily_frame, text=f"{self.daily_follows:,}", style="Success.TLabel"
        )
        self.daily_follows_label.pack(side="right")

        # 关注成功率
        success_frame = ttk.Frame(stats_card)
        success_frame.pack(fill="x")

        ttk.Label(success_frame, text="关注成功率:", style="Body.TLabel").pack(
            side="left"
        )
        self.success_rate_label = ttk.Label(
            success_frame, text="95.2%", style="Success.TLabel"
        )
        self.success_rate_label.pack(side="right")

    def create_balance_info(self, parent):
        """创建余额信息"""
        balance_card = ttk.LabelFrame(parent, text="💰 账户余额", padding=10)
        balance_card.pack(fill="x", pady=(0, 10))

        # 当前余额
        balance_frame = ttk.Frame(balance_card)
        balance_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(balance_frame, text="当前余额:", style="Body.TLabel").pack(
            side="left"
        )
        self.balance_label = ttk.Label(
            balance_frame, text=f"¥{self.user_balance:.2f}", style="Heading.TLabel"
        )
        self.balance_label.pack(side="right")

        # 关注单价
        cost_frame = ttk.Frame(balance_card)
        cost_frame.pack(fill="x", pady=(0, 5))

        ttk.Label(cost_frame, text="关注单价:", style="Body.TLabel").pack(side="left")
        ttk.Label(
            cost_frame, text=f"¥{self.follow_cost:.2f}/人", style="Body.TLabel"
        ).pack(side="right")

        # 可关注数量
        available_frame = ttk.Frame(balance_card)
        available_frame.pack(fill="x")

        ttk.Label(available_frame, text="可关注数量:", style="Body.TLabel").pack(
            side="left"
        )
        available_count = int(self.user_balance / self.follow_cost)
        self.available_count_label = ttk.Label(
            available_frame, text=f"{available_count:,}人", style="Success.TLabel"
        )
        self.available_count_label.pack(side="right")

    def create_device_overview(self, parent):
        """创建设备状态概览"""
        device_card = ttk.LabelFrame(parent, text="📱 设备状态", padding=10)
        device_card.pack(fill="x")

        # 设备连接状态
        self.device_status_frame = ttk.Frame(device_card)
        self.device_status_frame.pack(fill="x")

        self.update_device_overview()

    def update_device_overview(self):
        """更新设备状态概览"""
        # 清空现有内容
        for widget in self.device_status_frame.winfo_children():
            widget.destroy()

        # 获取设备状态（从设备管理视图）
        if hasattr(self.main_window, "device_view") and self.main_window.device_view:
            connected_devices = self.main_window.device_view.get_connected_devices()

            ttk.Label(
                self.device_status_frame, text="已连接设备:", style="Body.TLabel"
            ).pack(anchor="w")

            if connected_devices:
                for device in connected_devices[:3]:  # 只显示前3个
                    device_frame = ttk.Frame(self.device_status_frame)
                    device_frame.pack(fill="x", pady=1)

                    ttk.Label(
                        device_frame, text=f"• {device.name}", style="Body.TLabel"
                    ).pack(side="left")
                    ttk.Label(
                        device_frame, text=device.status, style="Success.TLabel"
                    ).pack(side="right")

                if len(connected_devices) > 3:
                    ttk.Label(
                        self.device_status_frame,
                        text=f"...等{len(connected_devices)}台设备",
                        style="Body.TLabel",
                    ).pack(anchor="w")
            else:
                ttk.Label(
                    self.device_status_frame, text="无已连接设备", style="Error.TLabel"
                ).pack(anchor="w")
        else:
            ttk.Label(
                self.device_status_frame, text="设备信息未加载", style="Body.TLabel"
            ).pack(anchor="w")

    def browse_contacts_file(self):
        """浏览通讯录文件"""
        file_path = filedialog.askopenfilename(
            title="选择通讯录文件",
            filetypes=[
                ("文本文件", "*.txt"),
                ("CSV文件", "*.csv"),
                ("JSON文件", "*.json"),
                ("所有文件", "*.*"),
            ],
        )

        if file_path:
            self.contacts_file = file_path
            self.contacts_file_var.set(Path(file_path).name)
            self.logger.info(f"选择通讯录文件: {file_path}")

    def browse_keywords_file(self):
        """浏览关键词文件"""
        file_path = filedialog.askopenfilename(
            title="选择关键词文件",
            filetypes=[
                ("文本文件", "*.txt"),
                ("JSON文件", "*.json"),
                ("所有文件", "*.*"),
            ],
        )

        if file_path:
            self.keywords_file = file_path
            self.keywords_file_var.set(Path(file_path).name)
            self.logger.info(f"选择关键词文件: {file_path}")

    def start_contacts_follow(self):
        """开始关注通讯录用户"""
        if not self.contacts_file:
            messagebox.showerror("错误", "请先选择通讯录文件")
            return

        try:
            target_count = int(self.contacts_count_var.get())
            if target_count <= 0:
                raise ValueError("关注数量必须大于0")
        except ValueError as e:
            messagebox.showerror("错误", f"关注数量输入错误: {e}")
            return

        # 检查余额
        total_cost = target_count * self.follow_cost
        if total_cost > self.user_balance:
            messagebox.showerror(
                "余额不足",
                f"所需费用: ¥{total_cost:.2f}\n"
                f"当前余额: ¥{self.user_balance:.2f}\n"
                f"不足金额: ¥{total_cost - self.user_balance:.2f}",
            )
            return

        # 检查设备连接
        if hasattr(self.main_window, "device_view") and self.main_window.device_view:
            connected_devices = self.main_window.device_view.get_connected_devices()
            if not connected_devices:
                messagebox.showerror("错误", "没有已连接的设备，请先连接设备")
                return
        else:
            messagebox.showerror("错误", "设备管理器未初始化")
            return

        # 确认开始任务
        if messagebox.askyesno(
            "确认开始",
            f"将关注 {target_count} 人\n"
            f"预计费用: ¥{total_cost:.2f}\n"
            f"使用设备: {len(connected_devices)} 台\n"
            "确定要开始吗？",
        ):

            # 创建任务
            task = FollowTask(
                "contacts_" + str(int(time.time())), "contacts", target_count
            )
            task.assigned_devices = connected_devices.copy()

            self.start_task(task)

    def start_competitor_monitor(self):
        """开始同行监控"""
        competitor_account = self.competitor_account_var.get().strip()
        if not competitor_account:
            messagebox.showerror("错误", "请输入要监控的同行账号")
            return

        if not self.keywords_file:
            messagebox.showerror("错误", "请先选择关键词文件")
            return

        try:
            target_count = int(self.monitor_count_var.get())
            if target_count <= 0:
                raise ValueError("目标关注数必须大于0")
        except ValueError as e:
            messagebox.showerror("错误", f"目标关注数输入错误: {e}")
            return

        # 检查余额
        total_cost = target_count * self.follow_cost
        if total_cost > self.user_balance:
            messagebox.showerror(
                "余额不足",
                f"所需费用: ¥{total_cost:.2f}\n" f"当前余额: ¥{self.user_balance:.2f}",
            )
            return

        # 检查设备连接
        if hasattr(self.main_window, "device_view") and self.main_window.device_view:
            connected_devices = self.main_window.device_view.get_connected_devices()
            if not connected_devices:
                messagebox.showerror("错误", "没有已连接的设备，请先连接设备")
                return
        else:
            messagebox.showerror("错误", "设备管理器未初始化")
            return

        # 确认开始任务
        if messagebox.askyesno(
            "确认开始",
            f"监控账号: {competitor_account}\n"
            f"目标关注: {target_count} 人\n"
            f"预计费用: ¥{total_cost:.2f}\n"
            "确定要开始吗？",
        ):

            # 创建任务
            task = FollowTask(
                "competitor_" + str(int(time.time())), "competitor", target_count
            )
            task.assigned_devices = connected_devices.copy()

            self.start_task(task)

    def start_task(self, task: FollowTask):
        """开始执行任务"""
        if self.current_task and self.current_task.status == TaskStatus.RUNNING:
            messagebox.showerror("错误", "已有任务正在执行中，请先停止当前任务")
            return

        self.current_task = task
        task.status = TaskStatus.RUNNING
        task.start_time = time.time()

        # 更新界面
        self.update_task_display()
        self.update_task_buttons()

        # 在后台线程中执行任务
        threading.Thread(target=self.execute_task, args=(task,), daemon=True).start()

        self.logger.info(f"开始执行任务: {task.task_id}")

    def execute_task(self, task: FollowTask):
        """执行任务（后台线程）"""
        try:
            self.main_window.update_status(f"正在执行{task.task_type}任务...", "info")

            # 模拟任务执行过程
            for i in range(task.target_count):
                if task.status != TaskStatus.RUNNING:
                    break

                # 模拟关注一个用户
                time.sleep(0.1)  # 模拟操作时间

                # 模拟成功率
                import random

                if random.choice([True, True, True, False]):  # 75%成功率
                    task.completed_count += 1

                    # 扣费
                    self.user_balance -= self.follow_cost
                    self.total_follows += 1
                    self.daily_follows += 1

                    # 更新UI
                    self.parent.after(0, self.update_task_display)
                    self.parent.after(0, self.update_statistics)

                # 每10个更新一次进度
                if i % 10 == 0:
                    self.parent.after(0, self.update_task_display)

            # 任务完成
            if task.status == TaskStatus.RUNNING:
                task.status = TaskStatus.COMPLETED
                task.end_time = time.time()

                self.parent.after(
                    0, lambda: self.main_window.update_status("任务完成", "success")
                )
                self.parent.after(
                    0,
                    lambda: messagebox.showinfo(
                        "任务完成",
                        f"任务已完成！\n"
                        f"成功关注: {task.completed_count} 人\n"
                        f"总费用: ¥{task.completed_count * self.follow_cost:.2f}",
                    ),
                )

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            self.logger.error(f"任务执行失败: {e}")
            self.parent.after(
                0, lambda: self.main_window.update_status("任务失败", "error")
            )

        finally:
            self.parent.after(0, self.update_task_display)
            self.parent.after(0, self.update_task_buttons)

    def pause_task(self):
        """暂停任务"""
        if self.current_task and self.current_task.status == TaskStatus.RUNNING:
            self.current_task.status = TaskStatus.PAUSED
            self.update_task_display()
            self.update_task_buttons()
            self.main_window.update_status("任务已暂停", "warning")

    def resume_task(self):
        """恢复任务"""
        if self.current_task and self.current_task.status == TaskStatus.PAUSED:
            self.current_task.status = TaskStatus.RUNNING
            self.update_task_display()
            self.update_task_buttons()
            self.main_window.update_status("任务已恢复", "info")

    def stop_task(self):
        """停止任务"""
        if self.current_task and self.current_task.status in [
            TaskStatus.RUNNING,
            TaskStatus.PAUSED,
        ]:
            if messagebox.askyesno(
                "确认停止", "确定要停止当前任务吗？已完成的关注不会退费。"
            ):
                self.current_task.status = TaskStatus.FAILED
                self.current_task.end_time = time.time()
                self.update_task_display()
                self.update_task_buttons()
                self.main_window.update_status("任务已停止", "warning")

    def update_task_display(self):
        """更新任务显示"""
        if self.current_task:
            task = self.current_task

            # 更新任务信息
            task_type_name = (
                "通讯录关注" if task.task_type == "contacts" else "同行监控"
            )
            self.current_task_label.config(text=f"当前任务: {task_type_name}")
            self.task_status_label.config(text=task.status)

            # 更新进度条
            if task.target_count > 0:
                progress = int((task.completed_count / task.target_count) * 100)
                self.progress_bar["value"] = progress
                self.progress_text.config(
                    text=f"{task.completed_count} / {task.target_count} ({progress}%)"
                )

        else:
            self.current_task_label.config(text="当前无任务")
            self.task_status_label.config(text="")
            self.progress_bar["value"] = 0
            self.progress_text.config(text="0 / 0 (0%)")

    def update_task_buttons(self):
        """更新任务控制按钮状态"""
        if self.current_task:
            status = self.current_task.status

            if status == TaskStatus.RUNNING:
                self.pause_btn.config(state="normal")
                self.resume_btn.config(state="disabled")
                self.stop_btn.config(state="normal")
            elif status == TaskStatus.PAUSED:
                self.pause_btn.config(state="disabled")
                self.resume_btn.config(state="normal")
                self.stop_btn.config(state="normal")
            else:
                self.pause_btn.config(state="disabled")
                self.resume_btn.config(state="disabled")
                self.stop_btn.config(state="disabled")
        else:
            self.pause_btn.config(state="disabled")
            self.resume_btn.config(state="disabled")
            self.stop_btn.config(state="disabled")

    def update_statistics(self):
        """更新统计信息"""
        # 更新关注统计
        self.total_follows_label.config(text=f"{self.total_follows:,}")
        self.daily_follows_label.config(text=f"{self.daily_follows:,}")

        # 更新余额信息
        self.balance_label.config(text=f"¥{self.user_balance:.2f}")
        available_count = int(self.user_balance / self.follow_cost)
        self.available_count_label.config(text=f"{available_count:,}人")

        # 更新设备概览
        self.update_device_overview()

    def load_statistics(self):
        """加载统计数据"""
        # TODO: 从服务器或本地文件加载真实统计数据
        # 这里使用模拟数据
        pass

    def save_statistics(self):
        """保存统计数据"""
        # TODO: 保存统计数据到服务器或本地文件
        pass
