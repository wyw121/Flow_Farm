"""
Flow Farm 员工客户端 - 登录管理器
负责用户认证和会话管理
"""

import logging
import time
from typing import Any, Dict, Optional

import requests


class LoginManager:
    """登录管理器"""

    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip("/")
        self.logger = logging.getLogger(__name__)
        self.auth_token: Optional[str] = None
        self.user_info: Optional[Dict[str, Any]] = None
        self.session = requests.Session()

    def login(self, username: str, password: str) -> bool:
        """执行登录"""
        try:
            login_data = {
                "username": username,
                "password": password,
                "client_type": "employee",
            }

            response = self.session.post(
                f"{self.server_url}/api/auth/login", json=login_data, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_info = data.get("user_info", {})

                # 更新会话头部
                self.session.headers.update(
                    {"Authorization": f"Bearer {self.auth_token}"}
                )

                self.logger.info(f"用户 {username} 登录成功")
                return True
            else:
                self.logger.error(f"登录失败: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"登录时发生错误: {e}")
            return False

    def logout(self) -> bool:
        """执行登出"""
        try:
            if self.auth_token:
                response = self.session.post(
                    f"{self.server_url}/api/auth/logout", timeout=30
                )

                if response.status_code == 200:
                    self.logger.info("登出成功")
                else:
                    self.logger.warning(f"登出请求失败: {response.status_code}")

            # 清除本地状态
            self.auth_token = None
            self.user_info = None
            self.session.headers.pop("Authorization", None)

            return True

        except Exception as e:
            self.logger.error(f"登出时发生错误: {e}")
            return False

    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self.auth_token is not None

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        return self.user_info

    def get_auth_token(self) -> Optional[str]:
        """获取认证令牌"""
        return self.auth_token

    def validate_token(self) -> bool:
        """验证令牌有效性"""
        if not self.auth_token:
            return False

        try:
            response = self.session.get(
                f"{self.server_url}/api/auth/validate", timeout=10
            )

            return response.status_code == 200

        except Exception as e:
            self.logger.error(f"验证令牌时发生错误: {e}")
            return False
