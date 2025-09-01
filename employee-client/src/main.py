"""
Flow Farm 员工客户端 - OneDragon风格现代化GUI
基于OneDragon架构重构的现代化界面
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import ClientSettings

# 导入 OneDragon GUI 主程序
from main_onedragon_optimized import FlowFarmApp
from main_onedragon_optimized import main as onedragon_main
from utils.logger import setup_logging


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Flow Farm 员工客户端 - OneDragon风格")
    parser.add_argument(
        "--mode",
        choices=["gui", "console"],
        default="gui",
        help="运行模式: gui(图形界面) 或 console(控制台)",
    )
    parser.add_argument(
        "--gui",
        action="store_const",
        const="gui",
        dest="mode",
        help="启动GUI模式 (等同于 --mode gui)",
    )
    parser.add_argument(
        "--console",
        action="store_const",
        const="console",
        dest="mode",
        help="启动控制台模式 (等同于 --mode console)",
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
        # 检查GUI依赖
        import PySide6  # noqa: F401

        # 检查基础依赖
        import requests  # noqa: F401

        print("✅ OneDragon GUI 依赖检查通过")
        print("✅ 基础依赖检查通过")
        return True

    except ImportError as e:
        print(f"❌ 缺少必要依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ 依赖检查错误: {e}")
        return True  # 开发模式下继续运行


def main():
    """主函数"""
    args = parse_arguments()

    # 设置日志
    log_level = "DEBUG" if args.debug else args.log_level
    setup_logging(log_level=log_level)
    logger = logging.getLogger(__name__)

    logger.info("🚀 Flow Farm 员工客户端启动中 (OneDragon风格)")

    # 检查依赖
    if not check_dependencies():
        logger.error("❌ 依赖检查失败，程序退出")
        sys.exit(1)

    # 加载配置
    try:
        settings = ClientSettings()
        if args.server:
            settings.set_server_url(args.server)
        logger.info("📡 服务器地址: %s", settings.get_server_url())
    except Exception as e:
        logger.error("❌ 配置加载失败: %s", str(e))
        sys.exit(1)

    logger.info("✅ 配置加载完成")

    try:
        if args.mode == "gui":
            logger.info("🖥️ 启动 OneDragon 风格图形界面")
            # 直接调用 OneDragon GUI 主程序
            return onedragon_main()
        else:
            logger.info("💻 启动控制台模式")
            print("控制台模式暂未实现，请使用GUI模式")

    except KeyboardInterrupt:
        logger.info("🛑 用户中断程序")
    except Exception as e:
        logger.error("❌ 程序运行出错: %s", str(e))
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)
    finally:
        logger.info("👋 Flow Farm 员工客户端已退出")


if __name__ == "__main__":
    main()
