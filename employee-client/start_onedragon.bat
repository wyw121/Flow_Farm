@echo off
echo ========================================
echo Flow Farm OneDragon 架构版本启动脚本
echo ========================================
echo.

REM 检查是否在正确的目录
if not exist "src" (
    echo ❌ 错误: 请在 employee-client 目录下运行此脚本
    pause
    exit /b 1
)

echo 🔍 检查 Python 环境...

REM 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: Python 未安装或不在 PATH 中
    echo 请安装 Python 3.8+ 并添加到 PATH
    pause
    exit /b 1
)

echo ✅ Python 环境检查通过

echo.
echo 🚀 启动 Flow Farm OneDragon 版本...
echo.

REM 启动应用程序
python start_onedragon.py

if errorlevel 1 (
    echo.
    echo ❌ 启动失败，可能的原因:
    echo    1. 依赖未安装，请运行: python upgrade_onedragon.py
    echo    2. Python 版本过低，需要 Python 3.8+
    echo    3. 虚拟环境未激活
    echo.
    echo 💡 提示: 运行 upgrade_onedragon.py 自动安装依赖
    pause
)

pause
