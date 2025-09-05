@echo off
echo ============================================
echo      ADB XML Reader - 快速操作脚本
echo ============================================

:: 设置变量
set ADB_PATH="D:\leidian\LDPlayer9\adb.exe"
set TOOL_PATH=".\target\release\adb_xml_reader.exe"

echo.
echo 1. 检查连接的设备...
%ADB_PATH% devices

echo.
echo 2. 获取第一个设备的UI信息...
%TOOL_PATH% --device "127.0.0.1:5555" --output ui_analysis.json --screenshot ui_screenshot.png

echo.
echo 3. 搜索关注相关元素...
%TOOL_PATH% --device "127.0.0.1:5555" --search "关注" --output follow_elements.json

echo.
echo 4. 搜索点赞相关元素...
%TOOL_PATH% --device "127.0.0.1:5555" --search "赞" --output like_elements.json

echo.
echo 5. 搜索发布相关元素...
%TOOL_PATH% --device "127.0.0.1:5555" --search "发布" --output publish_elements.json

echo.
echo ============================================
echo           操作完成！
echo ============================================
echo 生成的文件:
echo   - ui_analysis.json      (完整UI结构)
echo   - ui_screenshot.png     (屏幕截图)
echo   - follow_elements.json  (关注元素)
echo   - like_elements.json    (点赞元素)
echo   - publish_elements.json (发布元素)
echo ============================================

pause
