"""
配置管理模块
管理服务器后端的所有配置项
"""

import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用程序配置"""

    # 基本配置
    APP_NAME: str = "Flow Farm 服务器后端"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库配置
    DATABASE_URL: str = "postgresql://flowfarm:password@localhost:5432/flowfarm_db"
    # 或者使用SQLite (开发环境)
    # DATABASE_URL: str = "sqlite:///./flowfarm.db"

    # JWT配置
    SECRET_KEY: str = "flow-farm-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS配置
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # 前端开发服务器
        "http://localhost:8080",  # 前端生产服务器
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]

    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/backend.log"

    # Redis配置 (可选，用于缓存)
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_REDIS: bool = False

    # 安全配置
    BCRYPT_ROUNDS: int = 12

    # KPI配置
    KPI_CALCULATION_INTERVAL: int = 3600  # 秒，KPI计算间隔
    MAX_DAILY_OPERATIONS: int = 10000  # 每日最大操作数限制

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建配置实例
settings = Settings()


# 数据库配置
def get_database_url() -> str:
    """获取数据库连接URL"""
    if settings.DEBUG:
        # 开发环境使用SQLite
        return "sqlite:///./flowfarm_dev.db"
    else:
        # 生产环境使用PostgreSQL
        return settings.DATABASE_URL


# 日志配置
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "default",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "detailed",
            "filename": settings.LOG_FILE,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": settings.LOG_LEVEL,
            "propagate": False,
        },
    },
}
