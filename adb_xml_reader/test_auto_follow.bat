@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 小红书自动关注功能测试
echo ========================================
echo.

:: 检查ADB连接
echo 📱 检查设备连接状态...
D:\leidian\LDPlayer9\adb.exe devices
echo.

:: 提示用户
echo ⚠️  使用前请确认:
echo    1. 小红书APP已打开且在主页
echo    2. 设备屏幕保持亮屏
echo    3. 通讯录中有好友需要关注
echo.

set /p choice="请选择测试模式 [1=仅导航测试, 2=完整自动关注]: "

if "%choice%"=="1" (
    echo.
    echo 🧭 开始测试导航流程（不会自动关注）...
    echo.
    target\release\adb_xml_reader.exe --auto-contact-flow
) else if "%choice%"=="2" (
    echo.
    echo 🤖 开始完整自动关注测试...
    echo    ⚠️  这将会实际关注通讯录中的好友！
    echo.
    set /p confirm="确认继续？ (y/N): "
    if /i "!confirm!"=="y" (
        target\release\adb_xml_reader.exe --auto-follow-contacts
    ) else (
        echo ❌ 用户取消操作
    )
) else (
    echo ❌ 无效选择，请输入 1 或 2
)

echo.
echo ✅ 测试完成！
pause
