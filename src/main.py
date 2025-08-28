#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flow Farm - 应用程序入口点

Author: Flow Farm Team
Date: 2023-12-01
Description: 手机流量农场自动化系统主入口
"""

import sys
import argparse
import logging
import os
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from utils.logger import setup_logging, get_logger
from core.config_manager import ConfigManager
from gui.main_window import MainWindow
from auth.session import SessionManager


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Flow Farm - 手机流量农场自动化系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                    # 启动GUI界面
  python main.py --debug            # 调试模式启动
  python main.py --gui              # 强制GUI模式
  python main.py --console          # 控制台模式
  python main.py --version          # 显示版本信息
        """
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='设置日志级别 (默认: INFO)'
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='强制启动GUI模式'
    )
    
    parser.add_argument(
        '--console',
        action='store_true', 
        help='启动控制台模式'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Flow Farm v1.0.0'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='指定配置文件路径'
    )
    
    return parser.parse_args()


def setup_environment():
    """设置运行环境"""
    # 设置工作目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # 创建必要的目录
    directories = ['logs', 'data', 'cache', 'temp', 'backups']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # 尝试加载环境变量（可选）
    try:
        from dotenv import load_dotenv
        load_dotenv('.env')
    except ImportError:
        pass  # python-dotenv不是必需的


def main():
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 设置环境
        setup_environment()
        
        # 设置日志
        log_level = logging.DEBUG if args.debug else getattr(logging, args.log_level)
        setup_logging(level=log_level, debug=args.debug)
        
        logger = get_logger(__name__)
        logger.info("="*50)
        logger.info("Flow Farm 启动中...")
        logger.info("="*50)
        
        # 加载配置
        config_manager = ConfigManager(config_path=args.config)
        config = config_manager.get_config()
        
        logger.info(f"配置加载完成: {config_manager.config_path}")
        
        # 初始化会话管理器
        session_manager = SessionManager()
        
        # 决定启动模式
        if args.console:
            # 控制台模式
            logger.info("启动控制台模式")
            from cli.console_interface import ConsoleInterface
            console = ConsoleInterface(config, session_manager)
            console.run()
            
        else:
            # GUI模式（默认）
            logger.info("启动GUI模式")
            app = MainWindow(config, session_manager)
            app.run()
        
    except KeyboardInterrupt:
        logger = get_logger(__name__)
        logger.info("用户中断程序运行")
        
    except Exception as e:
        # 确保错误能被记录
        try:
            logger = get_logger(__name__)
            logger.critical(f"程序启动失败: {e}", exc_info=True)
        except Exception:
            print(f"严重错误: {e}")
        
        sys.exit(1)
    
    finally:
        # 清理资源
        try:
            logger = get_logger(__name__)
            logger.info("程序正常退出")
            logging.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
