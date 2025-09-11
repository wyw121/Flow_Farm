#!/bin/bash

# Flow Farm Ubuntu 部署脚本
# 使用方法: ./deploy.sh your-server-ip your-username

set -e

if [ $# -lt 2 ]; then
    echo "使用方法: $0 <服务器IP> <用户名> [端口(默认22)]"
    echo "示例: $0 192.168.1.100 ubuntu"
    echo "示例: $0 192.168.1.100 ubuntu 2222"
    exit 1
fi

SERVER_IP=$1
USERNAME=$2
PORT=${3:-22}

echo "================================================"
echo "Flow Farm Ubuntu 自动部署脚本"
echo "================================================"
echo "目标服务器: $USERNAME@$SERVER_IP:$PORT"
echo "本地二进制: target/release/flow-farm-backend"
echo ""

# 检查本地二进制文件
if [ ! -f "target/release/flow-farm-backend" ]; then
    echo "❌ 错误: 找不到 target/release/flow-farm-backend"
    echo "请先运行编译脚本: compile-ubuntu-latest.bat"
    exit 1
fi

echo "📊 本地二进制文件信息:"
ls -lh target/release/flow-farm-backend
echo ""

# 检查配置文件
ENV_FILE=".env.production"
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  警告: 找不到 $ENV_FILE，将使用 .env 文件"
    ENV_FILE=".env"
    if [ ! -f "$ENV_FILE" ]; then
        echo "❌ 错误: 找不到任何环境配置文件"
        exit 1
    fi
fi

echo "📁 使用配置文件: $ENV_FILE"
echo ""

# 创建远程目录
echo "🚀 创建远程目录结构..."
ssh -p $PORT $USERNAME@$SERVER_IP "
    mkdir -p /opt/flow-farm/data
    mkdir -p /opt/flow-farm/logs
    mkdir -p /opt/flow-farm/static
    echo '✅ 目录创建完成'
"

# 复制二进制文件
echo "📦 复制二进制文件..."
scp -P $PORT target/release/flow-farm-backend $USERNAME@$SERVER_IP:/opt/flow-farm/
echo "✅ 二进制文件复制完成"

# 复制配置文件
echo "⚙️  复制配置文件..."
scp -P $PORT $ENV_FILE $USERNAME@$SERVER_IP:/opt/flow-farm/.env
echo "✅ 配置文件复制完成"

# 设置权限并测试
echo "🔧 设置文件权限..."
ssh -p $PORT $USERNAME@$SERVER_IP "
    chmod +x /opt/flow-farm/flow-farm-backend
    chown -R $USERNAME:$USERNAME /opt/flow-farm
    echo '✅ 权限设置完成'
"

# 创建systemd服务
echo "📋 创建系统服务..."
ssh -p $PORT $USERNAME@$SERVER_IP "
    sudo tee /etc/systemd/system/flow-farm.service > /dev/null << 'EOF'
[Unit]
Description=Flow Farm Backend Service
After=network.target

[Service]
Type=simple
User=$USERNAME
WorkingDirectory=/opt/flow-farm
ExecStart=/opt/flow-farm/flow-farm-backend
Restart=always
RestartSec=10
Environment=RUST_LOG=info
Environment=PORT=8000

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    echo '✅ 系统服务创建完成'
"

# 启动服务
echo "🚀 启动服务..."
ssh -p $PORT $USERNAME@$SERVER_IP "
    sudo systemctl enable flow-farm
    sudo systemctl start flow-farm
    sleep 3
    sudo systemctl status flow-farm --no-pager
"

echo ""
echo "================================================"
echo "✅ 部署完成！"
echo "================================================"
echo "🌐 服务访问地址:"
echo "   http://$SERVER_IP:8000"
echo ""
echo "📋 管理命令:"
echo "   查看状态: sudo systemctl status flow-farm"
echo "   查看日志: sudo journalctl -u flow-farm -f"
echo "   重启服务: sudo systemctl restart flow-farm"
echo "   停止服务: sudo systemctl stop flow-farm"
echo ""
echo "📁 服务器文件位置:"
echo "   程序目录: /opt/flow-farm/"
echo "   日志文件: journalctl -u flow-farm"
echo "   配置文件: /opt/flow-farm/.env"
echo ""
echo "🎯 测试连接:"
echo "   curl http://$SERVER_IP:8000/health"
echo "================================================"
