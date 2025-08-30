"""
测试后端API的简单脚本
"""

import os
import sys

# 添加app目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

if __name__ == "__main__":
    try:
        from sqlalchemy.orm import Session

        from app.database import SessionLocal, engine
        from app.main import app
        from app.models import User

        print("✅ 导入模块成功")

        # 测试数据库连接
        db = SessionLocal()
        try:
            users = db.query(User).all()
            print(f"✅ 数据库连接成功，找到 {len(users)} 个用户")
            for user in users:
                print(f"  - {user.username} ({user.role})")
        except Exception as e:
            print(f"❌ 数据库查询失败: {e}")
        finally:
            db.close()

        print("\n🚀 尝试启动服务器...")
        import uvicorn

        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保在 server-backend 目录下运行此脚本")
    except Exception as e:
        print(f"❌ 其他错误: {e}")
