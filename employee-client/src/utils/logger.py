"""
Flow Farm 员工客户端 - 日志配置
配置应用程序的日志记录
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO", log_file: Optional[str] = None, console_output: bool = True
) -> None:
    """设置日志配置"""

    # 创建日志格式器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # 清除现有处理器
    root_logger.handlers.clear()

    # 控制台输出
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)

    # 文件输出
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # 使用滚动文件处理器
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            root_logger.addHandler(file_handler)

        except Exception as e:
            # 如果文件日志设置失败，至少要有控制台输出
            print(f"警告: 无法设置文件日志 {log_file}: {e}")

    # 设置第三方库的日志级别
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # 记录日志配置完成
    logger = logging.getLogger(__name__)
    logger.info(f"日志系统初始化完成 - 级别: {log_level}")
    if log_file:
        logger.info(f"日志文件: {log_file}")


def get_default_log_file() -> str:
    """获取默认日志文件路径"""
    log_dir = Path.home() / ".flow_farm" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return str(log_dir / "employee_client.log")
