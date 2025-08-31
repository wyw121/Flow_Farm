#!/usr/bin/env python3
import sqlite3
import os

db_path = "server-backend/data/flow_farm.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查表结构
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
    result = cursor.fetchone()
    if result:
        print("用户表结构:")
        print(result[0])
        print()

        # 检查数据
        cursor.execute("SELECT id, username, role FROM users LIMIT 5")
        users = cursor.fetchall()
        print("用户数据示例:")
        for user in users:
            print(f"ID: {user[0]} (类型: {type(user[0])}), 用户名: {user[1]}, 角色: {user[2]}")
    else:
        print("用户表不存在")

    conn.close()
else:
    print(f"数据库文件不存在: {db_path}")
