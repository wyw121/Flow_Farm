@echo off
chcp 65001 >nul
echo 启动小红书自动关注工具...
echo.
echo 请确保：
echo 1. 雷电模拟器已启动
echo 2. 小红书APP已打开并在主页
echo 3. 模拟器分辨率为1920x1080，DPI为280
echo.
pause
python smart_follow_fixed.py
pause
