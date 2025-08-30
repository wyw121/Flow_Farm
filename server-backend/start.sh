#!/bin/bash

echo "=========================================="
echo " Flow Farm Rust 后端服务器启动脚本"
echo "=========================================="
echo

# 检查Rust是否安装
if ! command -v cargo &> /dev/null; then
    echo "[错误] 未找到 Cargo，请先安装 Rust"
    echo "请访问 https://rustup.rs/ 安装 Rust"
    exit 1
fi

echo "[信息] 检测到 Rust 环境"
cargo --version

echo
echo "[信息] 准备环境..."

# 复制环境配置文件
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "[信息] 已创建 .env 配置文件"
    else
        echo "[警告] 未找到 .env.example 配置文件"
    fi
fi

# 创建数据目录
if [ ! -d data ]; then
    mkdir -p data
    echo "[信息] 已创建 data 目录"
fi

echo
echo "[信息] 编译和启动服务器..."
echo "[提示] 首次运行可能需要较长时间下载依赖"

# 启动服务器
cargo run

if [ $? -ne 0 ]; then
    echo
    echo "[错误] 服务器启动失败"
    echo "[建议] 检查依赖是否完整：cargo check"
    exit 1
fi

echo
echo "[信息] 服务器已关闭"
