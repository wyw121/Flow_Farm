@echo off
echo =================================
echo Flow Farm 项目重构 - 快速启动
echo =================================
echo.

echo 🏗️ 正在初始化项目模块...
echo.

echo 📦 初始化服务器后端...
cd server-backend
if not exist "venv" (
    python -m venv venv
    echo ✅ 后端虚拟环境已创建
) else (
    echo ✅ 后端虚拟环境已存在
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
deactivate
cd ..

echo.
echo 📦 初始化服务器前端...
cd server-frontend
if not exist "node_modules" (
    npm install
    echo ✅ 前端依赖已安装
) else (
    echo ✅ 前端依赖已存在
)
cd ..

echo.
echo 📦 初始化员工客户端...
cd employee-client
if not exist "venv" (
    python -m venv venv
    echo ✅ 客户端虚拟环境已创建
) else (
    echo ✅ 客户端虚拟环境已存在
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
deactivate
cd ..

echo.
echo 🎉 项目初始化完成！
echo.
echo 📋 下一步操作：
echo   1. 打开VS Code工作区: Flow_Farm.code-workspace
echo   2. 启动服务器后端: 运行任务 "🚀 启动服务器后端"
echo   3. 启动服务器前端: 运行任务 "🌐 启动服务器前端开发"
echo   4. 启动员工客户端: 运行任务 "💻 启动员工客户端GUI"
echo.
echo 📖 详细说明请查看: PROJECT_RESTRUCTURE.md
echo.
pause
