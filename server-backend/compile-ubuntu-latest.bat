@echo off
chcp 65001 >nul
echo ================================================
echo Flow Farm Rust Ubuntu 编译脚本
echo 使用Docker临时容器，不占用额外存储空间
echo ================================================
echo.

set "PROJECT_PATH=%CD%"
set "OUTPUT_DIR=%CD%\target\ubuntu-release"

echo 📁 当前项目路径: %PROJECT_PATH%
echo 📦 编译输出路径: %OUTPUT_DIR%
echo.

REM 创建输出目录
if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
    echo ✅ 创建输出目录: %OUTPUT_DIR%
)

echo 🐳 启动Docker临时容器编译...
echo 🚀 使用最新的Rust版本解决依赖兼容性问题...
echo.

REM 使用最新Rust版本
docker run --rm ^
    -v "%PROJECT_PATH%:/workspace" ^
    -w /workspace ^
    rust:latest ^
    bash -c "apt-get update -qq && apt-get install -y -qq pkg-config libssl-dev && echo '📋 安装完成系统依赖' && cargo --version && rustc --version && echo '🦀 开始编译 Rust 项目...' && cargo build --release && echo '✅ 编译完成！' && echo '📊 二进制文件信息:' && ls -lh /workspace/target/release/"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================
    echo ✅ 编译成功！
    echo ================================================
    echo 📁 Ubuntu二进制文件位置:
    echo    %PROJECT_PATH%\target\release\flow-farm-backend
    echo.
    if exist "%PROJECT_PATH%\target\release\flow-farm-backend" (
        echo 📊 文件大小:
        dir "%PROJECT_PATH%\target\release\flow-farm-backend" | findstr "flow-farm-backend"
    )
    echo.
    echo 💡 使用说明:
    echo    1. 将二进制文件复制到Ubuntu服务器
    echo    2. 确保服务器上有相同的.env配置文件
    echo    3. 在Ubuntu上运行: ./flow-farm-backend
    echo.
    echo 🚀 部署命令示例:
    echo    scp target/release/flow-farm-backend user@server:/opt/flow-farm/
    echo    scp .env.production user@server:/opt/flow-farm/.env
    echo.
) else (
    echo.
    echo ❌ 编译失败！请检查错误信息。
    echo.
)

pause
