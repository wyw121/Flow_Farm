import os
import sys

import uvicorn

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print(f"当前工作目录: {os.getcwd()}")
    print(f"脚本目录: {current_dir}")
    print(f"Python路径: {sys.path[:3]}")

    try:
        from app.main import app

        print("✅ 成功导入应用")
        print("🚀 启动服务器在端口 8000...")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback

        traceback.print_exc()
