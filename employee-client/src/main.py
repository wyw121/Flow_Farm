"""
Flow Farm 员工客户端 - 主程序入口
员工使用的工作程序，连接服务器进行认证和数据同步
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from auth.login import LoginManager
from config.settings import ClientSettings
from gui.main_window import MainWindow
from sync.kpi_uploader import KPIUploader
from utils.logger import setup_logging


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Flow Farm 员工客户端")
    parser.add_argument(
        "--mode",
        choices=["gui", "console"],
        default="gui",
        help="运行模式: gui(图形界面) 或 console(控制台)",
    )
    parser.add_argument(
        "--server", type=str, help="服务器地址 (例如: http://192.168.1.100:8000)"
    )
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日志级别",
    )
    return parser.parse_args()


def check_dependencies():
    """检查必要的依赖"""
    try:
        # 检查ADB是否可用
        import subprocess
        import tkinter

        import requests
        import sqlalchemy

        result = subprocess.run(["adb", "version"], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError("ADB不可用")
        return True
    except ImportError as e:
        print(f"❌ 缺少必要依赖: {e}")
        return False
    except FileNotFoundError:
        print("❌ ADB工具未安装或不在PATH中")
        return False


def main():
    """主函数"""
    args = parse_arguments()

    # 设置日志
    setup_logging(level=args.log_level, debug=args.debug)
    logger = logging.getLogger(__name__)

    logger.info("🚀 Flow Farm 员工客户端启动中...")

    # 检查依赖
    if not check_dependencies():
        logger.error("❌ 依赖检查失败，程序退出")
        sys.exit(1)

    # 加载配置
    try:
        settings = ClientSettings()
        if args.server:
            settings.SERVER_URL = args.server
        logger.info(f"📡 连接服务器: {settings.SERVER_URL}")
    except Exception as e:
        logger.error(f"❌ 配置加载失败: {e}")
        sys.exit(1)

    # 初始化登录管理器
    login_manager = LoginManager(settings.SERVER_URL)

    # 检查服务器连接
    if not login_manager.check_server_connection():
        logger.error("❌ 无法连接到服务器，请检查网络和服务器地址")
        sys.exit(1)

    logger.info("✅ 服务器连接正常")

    try:
        if args.mode == "gui":
            logger.info("🖥️ 启动图形界面模式")
            app = MainWindow(login_manager, settings)
            app.run()
        else:
            logger.info("💻 启动控制台模式")
            from cli.console_interface import ConsoleInterface

            console = ConsoleInterface(login_manager, settings)
            console.run()

    except KeyboardInterrupt:
        logger.info("🛑 用户中断程序")
    except Exception as e:
        logger.error(f"❌ 程序运行出错: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)
    finally:
        logger.info("👋 Flow Farm 员工客户端已退出")


if __name__ == "__main__":
    main()
