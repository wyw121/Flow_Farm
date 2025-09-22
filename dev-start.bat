@echo off
REM Flow Farm 本地开发启动脚本 (Windows)

echo 🚀 启动 Flow Farm 本地开发环境

REM 启动后端服务器 (使用本地配置)
echo 📊 启动后端服务器...
cd server-backend
copy .env.local .env
start /b cargo run

REM 等待后端启动
timeout /t 5 /nobreak

REM 启动前端开发服务器
echo 🌐 启动前端开发服务器...
cd ..\server-frontend
copy .env.local .env
start /b npm run dev

echo ✅ 开发环境启动完成!
echo 📖 前端地址: http://localhost:3000
echo 📖 后端API: http://localhost:8000
echo 📖 API文档: http://localhost:8000/docs
echo.
echo 按任意键关闭...
pause