@echo off
chcp 65001 >nul
echo ================================================
echo Flow Farm React 前端编译部署脚本
echo ================================================

cd /d "d:\repositories\Flow_Farm\server-frontend"

echo 📦 检查Node.js环境...
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 错误: 找不到Node.js，请先安装Node.js
    pause
    exit /b 1
)

echo 📦 安装/更新依赖...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo 🏗️ 编译React项目 (生产模式)...
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 编译失败，请检查代码错误
    pause
    exit /b 1
)

echo 📊 编译产物信息:
if exist "dist" (
    dir "dist" | findstr /C:"index.html"
    for /f %%i in ('dir "dist" /s /b ^| find /c /v ""') do echo 📁 总文件数: %%i 个
) else (
    echo ❌ 找不到构建产物 dist/ 目录
    pause
    exit /b 1
)

echo 📁 准备静态文件目录...
cd /d "d:\repositories\Flow_Farm\server-backend"
if not exist "static" mkdir "static"

echo 🚀 复制静态文件到Rust后端...
xcopy /E /Y /I "..\server-frontend\dist\*" "static\"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 文件复制失败
    pause
    exit /b 1
)

echo ✅ 验证部署结果...
if exist "static\index.html" (
    echo ✅ index.html 存在
) else (
    echo ❌ index.html 未找到
)

if exist "static\assets" (
    echo ✅ assets 目录存在
    dir "static\assets" | findstr /C:".js .css"
) else (
    echo ❌ assets 目录未找到
)

echo.
echo ================================================
echo ✅ React前端编译部署完成！
echo ================================================
echo 📁 静态文件位置: server-backend\static\
echo 🚀 启动命令:
echo    cd server-backend
echo    cargo run --release
echo.
echo 🌐 访问地址: http://localhost:8000
echo 📋 API文档: http://localhost:8000/docs
echo ================================================

echo 🚀 启动Rust后端...
cd /d "d:\repositories\Flow_Farm\server-backend"
start "Flow Farm Server" /D "d:\repositories\Flow_Farm\server-backend" cmd /k "target\release\flow-farm-backend.exe"
timeout /t 3 /nobreak >nul
echo.
echo 🌐 正在浏览器中打开应用...
start "" "http://localhost:8000"
echo.
echo ================================================
echo ✅ 部署完成！应用已启动
echo ================================================
echo 🌐 前端地址: http://localhost:8000
echo 📋 API文档: http://localhost:8000/docs
echo 🔌 API接口: http://localhost:8000/api/v1/*
echo.
echo 💡 管理:
echo    - 关闭服务器: 在新打开的窗口中按 Ctrl+C
echo    - 重新编译前端: 重新运行此脚本
echo    - 查看日志: 在服务器窗口中查看
echo ================================================

pause
