@echo off
echo 启动Flow Farm后端服务器...
cd /d "d:\repositories\Flow_Farm\server-backend"
set RUST_LOG=info
cargo run