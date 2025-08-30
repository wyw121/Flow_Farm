#!/usr/bin/env python3
"""
检查数据库中的用户
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User


def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"数据库中共有 {len(users)} 个用户:")
        for user in users:
            print(
                f"- ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}, 角色: {user.role}, 激活: {user.is_active}"
            )
    finally:
        db.close()


if __name__ == "__main__":
    check_users()
