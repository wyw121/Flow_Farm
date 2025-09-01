@echo off
echo ========================================
echo Flow Farm OneDragon 依赖升级脚本
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
echo 🔄 开始升级 OneDragon 依赖...
echo.

REM 运行升级脚本
python upgrade_onedragon.py

if errorlevel 1 (
    echo.
    echo ❌ 升级失败，请检查网络连接和权限
    pause
    exit /b 1
) else (
    echo.
    echo 🎉 升级完成！
    echo.
    echo 现在可以运行: start_onedragon.bat
    echo 或直接运行: python start_onedragon.py
)

pause
