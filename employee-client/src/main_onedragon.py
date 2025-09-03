"""
Flow Farm 主应用程序 - OneDragon 架构版本
完全基于 OneDragon 设计的新版本主程序
"""

import logging
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from qfluentwidgets import NavigationItemPosition

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from gui.interfaces.device_interface import DeviceInterface
from gui.interfaces.home_interface import HomeInterface
from gui.interfaces.task_interface import TaskInterface
from gui.onedragon_base.app_window import FlowFarmAppWindow


class FlowFarmApp:
    """Flow Farm 主应用程序类"""

    def __init__(self):
        """初始化应用程序"""
        self.app = QApplication(sys.argv)
        self.window = None
        self.logger = self._setup_logging()

        # 设置应用程序属性
        self.app.setApplicationName("Flow Farm")
        self.app.setApplicationVersion("2.0.0")
        self.app.setOrganizationName("Flow Farm Team")

        self.logger.info("Flow Farm 应用程序初始化完成")

    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("logs/flow_farm.log"),
            ],
        )
        return logging.getLogger(__name__)

    def create_window(self):
        """创建主窗口"""
        self.window = FlowFarmAppWindow()

        # 创建和添加界面
        self._create_interfaces()

        self.logger.info("主窗口创建完成")
        return self.window

    def _create_interfaces(self):
        """创建所有界面"""
        # 主页界面
        self.home_interface = HomeInterface(parent=self.window)
        self.window.add_sub_interface(
            self.home_interface, position=NavigationItemPosition.TOP
        )

        # 设备管理界面
        self.device_interface = DeviceInterface(parent=self.window)
        self.window.add_sub_interface(
            self.device_interface, position=NavigationItemPosition.TOP
        )

        # 任务管理界面
        self.task_interface = TaskInterface(parent=self.window)
        self.window.add_sub_interface(
            self.task_interface, position=NavigationItemPosition.TOP
        )

        # 可以添加更多界面...

        self.logger.info("所有界面创建完成")

    def _connect_signals(self):
        """连接信号槽"""
        # 暂时简化，先不连接信号，等系统稳定后再添加
        self.logger.info("信号连接完成")

        # 可以添加更多信号连接...

        self.logger.info("信号槽连接完成")

    def run(self):
        """运行应用程序"""
        if not self.window:
            self.create_window()

        # 显示窗口
        self.window.show()

        # 在窗口显示后连接信号
        self._connect_signals()

        # 设置默认显示主页
        self.window.switch_to_interface("home_interface")

        self.logger.info("Flow Farm 应用程序启动")

        # 运行事件循环
        return self.app.exec()


def main():
    """主函数"""
    # 启用高DPI支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    # 创建并运行应用程序
    app = FlowFarmApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
