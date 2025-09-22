#!/bin/bash
# Flow Farm 本地开发启动脚本

echo "🚀 启动 Flow Farm 本地开发环境"

# 设置环境变量
export NODE_ENV=development

# 启动后端服务器 (使用本地配置)
echo "📊 启动后端服务器..."
cd server-backend
cp .env.local .env
cargo run &
BACKEND_PID=$!

# 等待后端启动
sleep 5

# 启动前端开发服务器
echo "🌐 启动前端开发服务器..."
cd ../server-frontend
cp .env.local .env
npm run dev &
FRONTEND_PID=$!

echo "✅ 开发环境启动完成!"
echo "📖 前端地址: http://localhost:3000"
echo "📖 后端API: http://localhost:8000"
echo "📖 API文档: http://localhost:8000/docs"

# 等待用户中断
trap "echo '🛑 停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait