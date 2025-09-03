"""
Flow Farm 员工客户端 - 多界面版本系统
支持多种不同风格的用户界面
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
from utils.logger import setup_logging

# 可用的界面版本配置
AVAILABLE_INTERFACES = {
    "onedragon": {
        "name": "OneDragon 任务管理界面",
        "description": "专门针对任务管理优化的界面",
        "module": "main_onedragon_optimized",
        "main_func": "main",
    },
    "onedragon_full": {
        "name": "OneDragon 完整系统",
        "description": "完整的设备管理+任务管理+系统设置界面 - 包含所有功能模块",
        "module": "main_onedragon",
        "main_func": "main",
    },
}


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Flow Farm 员工客户端 - 多界面系统")
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
        "--interface",
        choices=list(AVAILABLE_INTERFACES.keys()),
        default="onedragon",
        help="选择界面版本: " + ", ".join(AVAILABLE_INTERFACES.keys()),
    )
    parser.add_argument(
        "--list-interfaces", action="store_true", help="列出所有可用的界面版本"
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


def list_available_interfaces():
    """列出所有可用的界面版本"""
    print("\n🎨 Flow Farm 可用界面版本:")
    print("=" * 60)
    for key, info in AVAILABLE_INTERFACES.items():
        print(f"🖥️  {key:12} - {info['name']}")
        print(f"   {'':12}   {info['description']}")
        print()
    print("使用方法: python src/main.py --interface <界面名称>")
    print("例如: python src/main.py --interface professional")


def load_interface(interface_name: str):
    """动态加载指定的界面模块"""
    if interface_name not in AVAILABLE_INTERFACES:
        raise ValueError(f"未知的界面版本: {interface_name}")

    interface_info = AVAILABLE_INTERFACES[interface_name]
    module_name = interface_info["module"]
    main_func_name = interface_info["main_func"]

    try:
        # 动态导入模块
        module = __import__(module_name, fromlist=[main_func_name])
        main_func = getattr(module, main_func_name)
        return main_func, interface_info
    except ImportError as e:
        raise ImportError(f"无法导入界面模块 {module_name}: {e}")
    except AttributeError as e:
        raise AttributeError(f"模块 {module_name} 中找不到函数 {main_func_name}: {e}")


def check_dependencies():
    """检查必要的依赖"""
    try:
        # 检查GUI依赖
        import PySide6  # noqa: F401

        # 检查基础依赖
        import requests  # noqa: F401

        print("✅ GUI 依赖检查通过")
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

    # 如果用户要求列出界面，则显示后退出
    if args.list_interfaces:
        list_available_interfaces()
        return 0

    # 设置日志
    log_level = "DEBUG" if args.debug else args.log_level
    setup_logging(log_level=log_level)
    logger = logging.getLogger(__name__)

    logger.info("🚀 Flow Farm 员工客户端启动中 (多界面系统)")
    logger.info(f"🎨 选择的界面: {args.interface}")

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
            # 加载指定的界面
            interface_main, interface_info = load_interface(args.interface)
            logger.info(f"🖥️ 启动界面: {interface_info['name']}")
            logger.info(f"📝 界面描述: {interface_info['description']}")

            # 运行界面
            return interface_main()
        else:
            logger.info("💻 启动控制台模式")
            print("控制台模式暂未实现，请使用GUI模式")

    except KeyboardInterrupt:
        logger.info("🛑 用户中断程序")
    except ImportError as e:
        logger.error("❌ 界面加载失败: %s", str(e))
        logger.info("💡 提示: 使用 --list-interfaces 查看可用界面")
        sys.exit(1)
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
