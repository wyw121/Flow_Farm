@echo off
chcp 65001 >nul
cls
echo ========================================
echo    小红书自动关注工具 - 最终版选择器
echo ========================================
echo.
echo 🚀 可用版本:
echo.
echo [1] 完整流程版 (最新推荐)
echo     └── 自动执行: 主页→消息→新增关注→智能关注
echo     └── 带界面显示，状态验证，错误处理
echo.
echo [2] 带界面版 (原版本)
echo     └── 需手动导航到关注推荐页面
echo     └── 智能关注前3个用户
echo.
echo [3] 静默运行版
echo     └── 后台运行，无界面显示
echo.
echo [4] 安全版本
echo     └── 高级加密，适合重要客户
echo.
echo ========================================
set /p choice=请选择版本 (1/2/3/4):

if "%choice%"=="1" (
    echo.
    echo 🚀 启动完整流程版...
    echo ========================================
    echo 📋 执行流程:
    echo    1. 自动回到主页
    echo    2. 进入消息页面
    echo    3. 点击新增关注
    echo    4. 智能关注前3个用户
    echo.
    echo ⚠️ 使用前请确保:
    echo    ✓ 雷电模拟器已启动
    echo    ✓ 小红书APP已打开并登录
    echo    ✓ 网络连接正常
    echo ========================================
    pause
    xiaohongshu_complete.exe
) else if "%choice%"=="2" (
    echo.
    echo 💻 启动带界面版...
    echo ========================================
    echo 📋 使用方法:
    echo    1. 手动打开小红书APP
    echo    2. 导航到推荐页面或用户列表
    echo    3. 程序将自动关注前3个用户
    echo ========================================
    pause
    xiaohongshu_tool_console.exe
) else if "%choice%"=="3" (
    echo.
    echo 🔇 启动静默版...
    echo ⚠️ 程序将在后台运行，请观察模拟器变化
    xiaohongshu_tool.exe
    echo ✅ 静默程序已完成
) else if "%choice%"=="4" (
    echo.
    echo 🛡️ 启动安全版...
    echo ========================================
    echo 📋 高级功能:
    echo    ✓ 增强加密保护
    echo    ✓ 优化性能
    echo    ✓ 完整界面显示
    echo ========================================
    pause
    xhs_automation_secure.exe
) else (
    echo.
    echo ❌ 无效选择，启动默认版本 (完整流程版)
    xiaohongshu_complete.exe
)

echo.
echo ========================================
echo 🎊 程序执行完成！
echo.
echo 💡 小贴士:
echo    - 如果遇到问题，建议使用带界面版本查看详细日志
echo    - 完整流程版适合新手和日常使用
echo    - 安全版本适合重要客户或商业环境
echo ========================================
pause
