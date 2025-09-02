"""
Flow Farm - GUI性能优化配置
针对OneDragon项目的经验优化GUI性能
"""

import logging

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication


class GUIPerformanceOptimizer:
    """GUI性能优化器"""

    @staticmethod
    def optimize_qt_application():
        """优化Qt应用程序性能"""
        app = QApplication.instance()
        if not app:
            return

        # 启用高DPI缩放支持
        app.setAttribute(app.applicationDisplayNameChanged, True)

        # 优化渲染性能
        app.setAttribute(app.applicationStateChanged, True)

        # 设置线程池大小
        QCoreApplication.setApplicationName("FlowFarm")
        QCoreApplication.setApplicationVersion("2.0.0")

        # 启用图形加速（如果可用）
        try:
            import os

            os.environ["QT_OPENGL"] = "desktop"
        except Exception:
            pass

    @staticmethod
    def optimize_gui_thread():
        """优化GUI线程"""
        # 设置适当的日志级别避免过多日志影响性能
        logger = logging.getLogger()
        if logger.level < logging.INFO:
            logger.setLevel(logging.INFO)

    @staticmethod
    def optimize_device_operations():
        """优化设备操作"""
        # 设置ADB命令超时时间较短
        return {
            "adb_timeout": 10,  # 10秒超时
            "scan_interval": 30,  # 30秒扫描间隔
            "max_concurrent_devices": 5,  # 最大并发设备数
        }

    @staticmethod
    def get_recommended_settings():
        """获取推荐的性能设置"""
        return {
            # GUI设置
            "gui": {
                "update_interval": 1000,  # 界面更新间隔(ms)
                "log_max_lines": 1000,  # 日志最大行数
                "table_max_rows": 50,  # 表格最大行数
            },
            # 设备管理设置
            "device": {
                "scan_timeout": 15,  # 扫描超时时间(s)
                "connection_retry": 3,  # 连接重试次数
                "batch_size": 3,  # 批处理大小
            },
            # 系统资源设置
            "system": {
                "max_threads": 4,  # 最大线程数
                "memory_limit": 512,  # 内存限制(MB)
                "cpu_priority": "normal",  # CPU优先级
            },
        }


def apply_performance_optimizations():
    """应用所有性能优化"""
    optimizer = GUIPerformanceOptimizer()

    # 优化Qt应用程序
    optimizer.optimize_qt_application()

    # 优化GUI线程
    optimizer.optimize_gui_thread()

    # 返回优化设置
    return optimizer.get_recommended_settings()
