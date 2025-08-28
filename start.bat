@echo off
REM Flow Farm 快速启动脚本
REM 自动检测并启动Flow Farm应用程序

echo.
echo ==========================================
echo       Flow Farm 启动助手 v1.0
echo ==========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python环境
    echo 请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] Python环境检测通过

REM 检查是否在正确目录
if not exist "src\main.py" (
    echo [错误] 未找到主程序文件
    echo 请确保在Flow_Farm项目根目录运行此脚本
    pause
    exit /b 1
)

echo [信息] 程序文件检测通过

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo [信息] 检测到虚拟环境，正在激活...
    call venv\Scripts\activate.bat
    echo [信息] 虚拟环境已激活
) else (
    echo [警告] 未检测到虚拟环境
    echo 建议创建虚拟环境以避免依赖冲突
)

REM 进入源代码目录
cd src

echo.
echo 请选择启动模式:
echo [1] GUI模式 (图形界面，推荐)
echo [2] 控制台模式 (命令行界面)
echo [3] 调试模式 (开发调试)
echo [0] 退出
echo.

set /p choice="请输入选择 (1-3): "

if "%choice%"=="1" goto gui_mode
if "%choice%"=="2" goto console_mode  
if "%choice%"=="3" goto debug_mode
if "%choice%"=="0" goto exit
goto invalid_choice

:gui_mode
echo.
echo [启动] GUI模式启动中...
python main.py --gui
goto end

:console_mode
echo.
echo [启动] 控制台模式启动中...
python main.py --console
goto end

:debug_mode
echo.
echo [启动] 调试模式启动中...
python main.py --debug --gui
goto end

:invalid_choice
echo.
echo [错误] 无效选择，请输入1-3之间的数字
pause
goto end

:exit
echo.
echo 感谢使用Flow Farm！
goto end

:end
echo.
echo ==========================================
echo          程序运行结束
echo ==========================================
pause
