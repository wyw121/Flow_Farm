#!/usr/bin/env python3
"""
Flow Farm 服务器后端启动脚本
"""

import argparse
import os
import subprocess
import sys


def setup_environment():
    """设置环境"""
    # 确保必要的目录存在
    dirs = ["data", "logs", "exports", "uploads"]
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)

    print("✅ 环境目录创建完成")


def install_dependencies():
    """安装依赖"""
    print("📦 安装Python依赖...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    )
    if result.returncode == 0:
        print("✅ 依赖安装完成")
    else:
        print("❌ 依赖安装失败")
        sys.exit(1)


def init_database():
    """初始化数据库"""
    print("🗄️  初始化数据库...")
    try:
        from app.init_db import init_database

        init_database()
        print("✅ 数据库初始化完成")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        sys.exit(1)


def start_server(host="0.0.0.0", port=8000, reload=False):
    """启动服务器"""
    print(f"🚀 启动服务器 http://{host}:{port}")

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]

    if reload:
        cmd.append("--reload")

    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(description="Flow Farm 服务器后端管理")
    parser.add_argument("--setup", action="store_true", help="设置环境和安装依赖")
    parser.add_argument("--init-db", action="store_true", help="初始化数据库")
    parser.add_argument("--start", action="store_true", help="启动服务器")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口")
    parser.add_argument("--reload", action="store_true", help="开发模式（自动重载）")

    args = parser.parse_args()

    if args.setup:
        setup_environment()
        install_dependencies()

    if args.init_db:
        init_database()

    if args.start:
        start_server(args.host, args.port, args.reload)

    # 如果没有指定参数，执行完整的启动流程
    if not any([args.setup, args.init_db, args.start]):
        print("🏗️  开始完整初始化流程...")
        setup_environment()
        install_dependencies()
        init_database()
        start_server(args.host, args.port, args.reload)


if __name__ == "__main__":
    main()
