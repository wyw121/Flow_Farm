@echo off
echo ================================================
echo Flow Farm Rust 原生 Web 服务器启动脚本
echo ================================================
echo.

REM 检查前端构建
if not exist "..\server-frontend\dist" (
    echo ⚠️  前端未构建，正在构建...
    cd ..\server-frontend
    call npm install
    call npm run build
    cd ..\server-backend
    echo ✅ 前端构建完成
) else (
    echo ✅ 前端已构建
)

echo.
echo 🚀 启动 Flow Farm Rust Web 服务器...
echo.
echo 📋 服务信息:
echo    - 前端界面: http://localhost:8000
echo    - API接口: http://localhost:8000/api
echo    - API文档: http://localhost:8000/docs
echo    - 健康检查: http://localhost:8000/health
echo.
echo 💡 按 Ctrl+C 停止服务器
echo.

REM 启动服务器
cargo run

pause
