@echo off
chcp 65001 >nul
cls
echo ========================================
echo    小红书自动关注工具 - 选择运行模式
echo ========================================
echo.
echo 请选择运行模式:
echo.
echo [1] 带界面版本 (推荐) - 可以看到运行过程
echo [2] 后台运行版本 - 无界面，静默运行
echo [3] 安全版本 - 高级加密版本
echo.
echo ========================================
set /p choice=请输入选择 (1/2/3):

if "%choice%"=="1" (
    echo.
    echo 启动带界面版本...
    echo ----------------------------------------
    echo 请确保:
    echo 1. 雷电模拟器已启动
    echo 2. 小红书APP已打开并登录
    echo 3. 在推荐页面或用户列表页面
    echo ----------------------------------------
    pause
    xiaohongshu_tool_console.exe
) else if "%choice%"=="2" (
    echo.
    echo 启动后台版本...
    echo 程序将在后台运行，请查看模拟器中的变化
    xiaohongshu_tool.exe
    echo 后台程序已启动完成
) else if "%choice%"=="3" (
    echo.
    echo 启动安全版本...
    echo ----------------------------------------
    echo 请确保:
    echo 1. 雷电模拟器已启动
    echo 2. 小红书APP已打开并登录
    echo 3. 在推荐页面或用户列表页面
    echo ----------------------------------------
    pause
    xhs_automation_secure.exe
) else (
    echo 无效选择，使用默认版本
    xiaohongshu_tool_console.exe
)

echo.
echo 程序执行完成！
pause
