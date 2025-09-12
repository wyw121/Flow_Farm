#!/bin/bash
# Flow Farm 启动脚本

export RUST_LOG=info
export DATABASE_URL=sqlite:data/flow_farm.db
export STATIC_DIR=static
export PORT=8080

echo "🚀 启动 Flow Farm 服务器..."
echo "📁 静态文件目录: $STATIC_DIR"
echo "🗄️ 数据库: $DATABASE_URL"
echo "🌐 监听端口: $PORT"

./flow-farm-backend
