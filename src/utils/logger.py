#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理模块

提供统一的日志配置和管理功能
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import os


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record):
        # 添加颜色
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logging(
    level: int = logging.INFO,
    log_dir: str = "logs",
    app_name: str = "flow_farm",
    debug: bool = False,
    max_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    设置日志配置
    
    Args:
        level: 日志级别
        log_dir: 日志目录
        app_name: 应用名称
        debug: 是否调试模式
        max_size: 单个日志文件最大大小
        backup_count: 备份文件数量
    """
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # 根记录器配置
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 日志格式
    if debug:
        log_format = (
            '%(asctime)s - %(name)s - %(levelname)s - '
            '%(filename)s:%(lineno)d - %(funcName)s - %(message)s'
        )
    else:
        log_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    
    formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
    colored_formatter = ColoredFormatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(colored_formatter)
    root_logger.addHandler(console_handler)
    
    # 应用主日志文件
    app_log_file = log_path / f"{app_name}.log"
    app_handler = logging.handlers.RotatingFileHandler(
        app_log_file,
        maxBytes=max_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    app_handler.setLevel(level)
    app_handler.setFormatter(formatter)
    root_logger.addHandler(app_handler)
    
    # 错误日志文件
    error_log_file = log_path / f"{app_name}_error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=max_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # 设备操作日志文件
    device_log_file = log_path / f"{app_name}_device.log"
    device_handler = logging.handlers.RotatingFileHandler(
        device_log_file,
        maxBytes=max_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    device_handler.setLevel(logging.INFO)
    device_handler.setFormatter(formatter)
    
    # 为设备日志创建特定的记录器
    device_logger = logging.getLogger('device')
    device_logger.addHandler(device_handler)
    device_logger.setLevel(logging.INFO)
    device_logger.propagate = False  # 不传播到根记录器
    
    # 设置第三方库日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('appium').setLevel(logging.INFO)
    
    # 记录启动信息
    logger = logging.getLogger(__name__)
    logger.info(f"日志系统初始化完成 - 级别: {logging.getLevelName(level)}")
    logger.info(f"日志目录: {log_path.absolute()}")


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的记录器
    
    Args:
        name: 记录器名称，通常使用 __name__
        
    Returns:
        logging.Logger: 配置好的记录器实例
    """
    return logging.getLogger(name)


def get_device_logger() -> logging.Logger:
    """
    获取设备操作专用记录器
    
    Returns:
        logging.Logger: 设备记录器实例
    """
    return logging.getLogger('device')


class LoggerMixin:
    """日志混入类，为其他类提供日志功能"""
    
    @property
    def logger(self) -> logging.Logger:
        """获取当前类的记录器"""
        return get_logger(self.__class__.__module__ + '.' + self.__class__.__name__)


def log_execution_time(func):
    """装饰器：记录函数执行时间"""
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} 执行完成，耗时: {execution_time:.3f}秒")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} 执行失败，耗时: {execution_time:.3f}秒，错误: {e}")
            raise
            
    return wrapper


def log_method_calls(cls):
    """类装饰器：记录类方法调用"""
    import functools
    
    def decorate_methods(cls):
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and not attr_name.startswith('_'):
                decorated = log_execution_time(attr)
                setattr(cls, attr_name, decorated)
        return cls
    
    return decorate_methods(cls)


# 设置默认日志配置（如果直接导入此模块）
if not logging.getLogger().handlers:
    setup_logging()
