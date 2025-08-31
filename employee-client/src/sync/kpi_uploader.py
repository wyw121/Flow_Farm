"""
Flow Farm 员工客户端 - KPI数据上传器
负责将工作数据同步到服务器
"""

import logging
import time
from typing import Any, Dict, Optional

import requests


class KPIUploader:
    """KPI数据上传器"""

    def __init__(self, server_url: str, auth_token: str = None):
        self.server_url = server_url.rstrip("/")
        self.auth_token = auth_token
        self.logger = logging.getLogger(__name__)

        # 会话对象用于保持连接
        self.session = requests.Session()
        if auth_token:
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json",
                }
            )

    def upload_follow_data(
        self, follow_count: int, task_type: str, device_id: str = None
    ) -> bool:
        """上传关注数据"""
        try:
            data = {
                "timestamp": int(time.time()),
                "follow_count": follow_count,
                "task_type": task_type,
                "device_id": device_id,
            }

            response = self.session.post(
                f"{self.server_url}/api/kpi/follow", json=data, timeout=30
            )

            if response.status_code == 200:
                self.logger.info(f"关注数据上传成功: {follow_count}")
                return True
            else:
                self.logger.error(f"关注数据上传失败: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"上传关注数据时发生错误: {e}")
            return False

    def upload_device_status(
        self, device_id: str, status: str, tasks_completed: int = 0
    ) -> bool:
        """上传设备状态"""
        try:
            data = {
                "timestamp": int(time.time()),
                "device_id": device_id,
                "status": status,
                "tasks_completed": tasks_completed,
            }

            response = self.session.post(
                f"{self.server_url}/api/devices/status", json=data, timeout=30
            )

            if response.status_code == 200:
                self.logger.debug(f"设备状态上传成功: {device_id}")
                return True
            else:
                self.logger.error(f"设备状态上传失败: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"上传设备状态时发生错误: {e}")
            return False

    def get_user_balance(self) -> Optional[float]:
        """获取用户余额"""
        try:
            response = self.session.get(
                f"{self.server_url}/api/user/balance", timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("balance", 0.0)
            else:
                self.logger.error(f"获取余额失败: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"获取余额时发生错误: {e}")
            return None
