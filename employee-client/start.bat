@echo off
chcp 65001 > nul
title Flow Farm 小红书自动化客户端

echo.
echo 🔥 Flow Farm 小红书自动化客户端
echo ==========================================
echo.

cd /d "%~dp0src"

:menu
echo 请选择操作:
echo.
echo 1. 🧪 快速系统测试
echo 2. 📱 检查设备状态
echo 3. 📇 创建示例通讯录
echo 4. 📊 查看统计信息
echo 5. 🔍 模拟执行测试
echo 6. 🚀 执行自动化任务
echo 7. 📋 查看详细帮助
echo 8. ❌ 退出
echo.

set /p choice=请输入选项 (1-8):

if "%choice%"=="1" (
    echo.
    echo 🧪 正在运行系统测试...
    python quick_test.py
    echo.
    pause
    goto menu
)

if "%choice%"=="2" (
    echo.
    echo 📱 检查设备状态...
    python xiaohongshu_client.py --check-devices
    echo.
    pause
    goto menu
)

if "%choice%"=="3" (
    echo.
    set /p count=请输入要创建的联系人数量 (默认10):
    if "%count%"=="" set count=10
    echo 📇 创建 %count% 个示例联系人...
    python xiaohongshu_client.py --create-sample %count%
    echo.
    pause
    goto menu
)

if "%choice%"=="4" (
    echo.
    echo 📊 查看统计信息...
    python xiaohongshu_client.py --stats
    echo.
    pause
    goto menu
)

if "%choice%"=="5" (
    echo.
    echo 🔍 模拟执行测试（不会实际操作）...
    python xiaohongshu_client.py --run --dry-run
    echo.
    pause
    goto menu
)

if "%choice%"=="6" (
    echo.
    echo ⚠️  警告: 这将在真实设备上执行关注操作!
    set /p confirm=确认执行? (y/N):
    if /i "%confirm%"=="y" (
        set /p devices=最大使用设备数 (默认2):
        if "%devices%"=="" set devices=2
        echo 🚀 执行自动化任务，最多使用 %devices% 个设备...
        python xiaohongshu_client.py --run --max-devices %devices%
    ) else (
        echo 操作已取消
    )
    echo.
    pause
    goto menu
)

if "%choice%"=="7" (
    echo.
    echo 📋 详细帮助信息...
    python xiaohongshu_client.py --help-detailed
    echo.
    pause
    goto menu
)

if "%choice%"=="8" (
    echo.
    echo 👋 感谢使用 Flow Farm!
    echo.
    exit /b 0
)

echo 无效选项，请重新选择
echo.
goto menu
