"""
Flow Farm 员工客户端 - 配置设置
管理客户端的配置参数和用户设置
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional


class ClientSettings:
    """客户端设置管理器"""

    def __init__(self, config_file: str = None):
        self.logger = logging.getLogger(__name__)

        # 默认配置文件路径
        if config_file is None:
            config_dir = Path.home() / ".flow_farm"
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / "employee_config.json"

        self.config_file = Path(config_file)

        # 默认配置
        self.default_config = {
            "server": {"url": "http://localhost:8000", "timeout": 30, "retry_count": 3},
            "gui": {
                "theme": "light",
                "window_size": [1400, 900],
                "auto_refresh": True,
                "refresh_interval": 10,
            },
            "device": {
                "max_devices": 10,
                "connection_timeout": 30,
                "auto_connect": False,
            },
            "task": {
                "follow_cost": 0.1,
                "max_concurrent_tasks": 1,
                "retry_failed": True,
            },
            "user": {
                "remember_login": True,
                "auto_login": False,
                "username": "",
                "server_url": "",
            },
        }

        # 加载配置
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    # 合并默认配置和用户配置
                    return self._merge_config(self.default_config, config)
            else:
                self.logger.info("配置文件不存在，使用默认配置")
                return self.default_config.copy()
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            return self.default_config.copy()

    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            self.logger.info(f"配置已保存到: {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
            return False

    def get(self, key_path: str, default=None) -> Any:
        """获取配置值，支持点分隔的路径"""
        keys = key_path.split(".")
        value = self.config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any) -> None:
        """设置配置值，支持点分隔的路径"""
        keys = key_path.split(".")
        config = self.config

        # 导航到目标字典
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # 设置值
        config[keys[-1]] = value

    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """递归合并配置字典"""
        result = default.copy()

        for key, value in user.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value

        return result

    def reset_to_default(self) -> None:
        """重置为默认配置"""
        self.config = self.default_config.copy()
        self.logger.info("配置已重置为默认值")

    def get_server_url(self) -> str:
        """获取服务器URL"""
        return self.get("server.url", "http://localhost:8000")

    def set_server_url(self, url: str) -> None:
        """设置服务器URL"""
        self.set("server.url", url)

    def get_window_size(self) -> tuple:
        """获取窗口大小"""
        size = self.get("gui.window_size", [1400, 900])
        return tuple(size)

    def set_window_size(self, width: int, height: int) -> None:
        """设置窗口大小"""
        self.set("gui.window_size", [width, height])

    def is_remember_login(self) -> bool:
        """是否记住登录信息"""
        return self.get("user.remember_login", True)

    def get_saved_username(self) -> str:
        """获取保存的用户名"""
        return self.get("user.username", "")

    def set_login_info(
        self, username: str, server_url: str, remember: bool = True
    ) -> None:
        """保存登录信息"""
        if remember:
            self.set("user.username", username)
            self.set("user.server_url", server_url)
            self.set("user.remember_login", True)
        else:
            self.set("user.username", "")
            self.set("user.server_url", "")
            self.set("user.remember_login", False)
