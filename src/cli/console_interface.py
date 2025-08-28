#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 控制台界面模块 - 提供命令行交互界面

import cmd
import sys
from typing import Dict, Any

from utils.logger import get_logger
from auth.session import SessionManager


class ConsoleInterface(cmd.Cmd):
    """控制台交互界面"""
    
    intro = '''
    ==================================================
    欢迎使用 Flow Farm 控制台模式
    ==================================================
    输入 'help' 或 '?' 查看可用命令
    输入 'quit' 或 'exit' 退出程序
    ==================================================
    '''
    
    prompt = 'Flow Farm> '
    
    def __init__(self, config: Dict[str, Any], session_manager: SessionManager):
        """
        初始化控制台界面
        
        Args:
            config: 配置信息
            session_manager: 会话管理器
        """
        super().__init__()
        self.logger = get_logger(__name__)
        self.config = config
        self.session_manager = session_manager
        
        self.logger.info("控制台界面初始化完成")
    
    def run(self):
        """运行控制台界面"""
        self.logger.info("启动控制台交互模式")
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            print("\n用户中断操作")
            self.do_quit("")
        except Exception as e:
            self.logger.error(f"控制台运行错误: {e}", exc_info=True)
            print(f"错误: {e}")
    
    def do_status(self, _):
        """显示系统状态"""
        print("系统状态:")
        print("  配置文件: 已加载")
        print(f"  会话状态: {'已认证' if self.session_manager.is_authenticated() else '未认证'}")
        
        if self.session_manager.is_authenticated():
            user_info = self.session_manager.get_current_user_info()
            print(f"  当前用户: {user_info.get('username', 'unknown')}")
            print(f"  用户角色: {user_info.get('role', 'unknown')}")
    
    def do_devices(self, _):
        """显示设备信息"""
        print("设备管理功能正在开发中...")
    
    def do_tasks(self, _):
        """显示任务信息"""
        print("任务管理功能正在开发中...")
    
    def do_config(self, _):
        """显示配置信息"""
        print("配置管理功能正在开发中...")
    
    def do_logs(self, _):
        """显示日志信息"""
        print("日志查看功能正在开发中...")
    
    def do_quit(self, _):
        """退出程序"""
        print("正在退出...")
        self.logger.info("用户通过控制台退出程序")
        return True
    
    def do_exit(self, _):
        """退出程序（别名）"""
        return self.do_quit(_)
    
    def do_EOF(self, _):
        """处理Ctrl+D"""
        print("\n再见!")
        return True
    
    def emptyline(self):
        """处理空行输入"""
        pass
    
    def default(self, line):
        """处理未知命令"""
        print(f"未知命令: {line}")
        print("输入 'help' 查看可用命令")
    
    def help_status(self):
        """status命令帮助"""
        print("显示系统当前状态信息")
    
    def help_devices(self):
        """devices命令帮助"""
        print("显示和管理设备信息")
    
    def help_tasks(self):
        """tasks命令帮助"""
        print("显示和管理任务信息")
    
    def help_config(self):
        """config命令帮助"""
        print("显示和修改配置信息")
    
    def help_logs(self):
        """logs命令帮助"""
        print("查看系统日志")
    
    def help_quit(self):
        """quit命令帮助"""
        print("退出程序")
        
    def help_exit(self):
        """exit命令帮助"""
        print("退出程序（与quit相同）")
