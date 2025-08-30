"""
设备管理相关API路由
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..api.auth import get_current_user
from ..database import get_db
from ..models import User

router = APIRouter()


@router.get("/")
async def get_devices(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """获取设备列表"""
    # TODO: 实现设备管理功能
    return {"message": "设备管理功能待实现"}


@router.get("/status")
async def get_device_status(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """获取设备状态"""
    # TODO: 实现设备状态查询
    return {"message": "设备状态查询功能待实现"}
