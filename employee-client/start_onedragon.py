"""
Flow Farm OneDragon 版本启动脚本
用于启动基于 OneDragon 架构的新版本 GUI
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    # 检查必要的依赖
    import PySide6

    print(f"✅ PySide6 版本: {PySide6.__version__}")

    try:
        import qfluentwidgets

        print(f"✅ qfluentwidgets 已安装")
    except ImportError:
        print("❌ qfluentwidgets 未安装，请运行: pip install qfluentwidgets==1.7.0")
        sys.exit(1)

    # 启动应用程序
    from main_onedragon import main

    print("🚀 启动 Flow Farm OneDragon 版本...")

    sys.exit(main())

except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所有必要的依赖:")
    print("pip install PySide6==6.8.0.2 qfluentwidgets==1.7.0")
    sys.exit(1)
except Exception as e:
    print(f"❌ 启动错误: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
