@echo off
:: Flow Farm 认证系统切换脚本 (Windows版)
:: 用于在新旧认证系统之间切换

title Flow Farm 认证系统切换工具

echo 🚀 Flow Farm 认证系统切换工具
echo ================================

if "%~1"=="" goto show_help
if "%~1"=="help" goto show_help
if "%~1"=="-h" goto show_help
if "%~1"=="--help" goto show_help

if "%~1"=="new" goto switch_to_new
if "%~1"=="old" goto switch_to_old
if "%~1"=="test" goto test_new_system
if "%~1"=="status" goto check_status
if "%~1"=="backup" goto backup_only
if "%~1"=="clean" goto cleanup

echo ❌ 无效选项: %~1
echo.
goto show_help

:check_status
echo 🔍 检查当前系统状态...
findstr /c:"AppNew" src\main.tsx >nul 2>&1
if %errorlevel%==0 (
    echo ✅ 当前使用新认证系统
) else (
    findstr /c:"App" src\main.tsx >nul 2>&1
    if %errorlevel%==0 (
        echo 📛 当前使用旧认证系统
    ) else (
        echo ❌ 无法确定当前系统状态
    )
)
goto end

:backup_files
echo 📦 备份当前文件...

for /f "tokens=2 delims==." %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "backup_dir=backup_%dt:~0,8%_%dt:~8,6%"
mkdir "%backup_dir%" 2>nul

if exist "src\main.tsx" copy "src\main.tsx" "%backup_dir%\main.tsx.backup" >nul
if exist "src\App.tsx" copy "src\App.tsx" "%backup_dir%\App.tsx.backup" >nul
if exist "src\store\index.ts" copy "src\store\index.ts" "%backup_dir%\store_index.ts.backup" >nul

echo ✅ 备份完成: %backup_dir%
goto :eof

:switch_to_new
echo 🔄 切换到新认证系统...

call :backup_files

:: 检查必要文件
if not exist "src\services\auth\AuthServiceSimplified.ts" (
    echo ❌ 找不到新认证系统文件
    echo 请确保已按照文档创建所有必要文件
    goto end
)

:: 更新main.tsx
if exist "src\mainNew.tsx" (
    copy "src\mainNew.tsx" "src\main.tsx" >nul
    echo ✅ 更新了 main.tsx
) else (
    echo ❌ 找不到 src\mainNew.tsx
    goto end
)

:: 更新App.tsx
if exist "src\AppNew.tsx" (
    copy "src\AppNew.tsx" "src\App.tsx" >nul
    echo ✅ 更新了 App.tsx
) else (
    echo ❌ 找不到 src\AppNew.tsx
    goto end
)

:: 更新App.css
if exist "src\AppNew.css" (
    copy "src\AppNew.css" "src\App.css" >nul
    echo ✅ 更新了 App.css
)

:: 更新store配置
if exist "src\store\indexNew.ts" (
    copy "src\store\indexNew.ts" "src\store\index.ts" >nul
    echo ✅ 更新了 store\index.ts
) else (
    echo ❌ 找不到 src\store\indexNew.ts
    goto end
)

echo.
echo 🎉 已切换到新认证系统！
echo.
echo 🎯 下一步：
echo 1. 运行 'npm run dev' 启动开发服务器
echo 2. 访问 http://localhost:3000 测试登录
echo 3. 如有问题，运行 '%~nx0 old' 切换回旧系统
goto end

:switch_to_old
echo 🔄 切换到旧认证系统...

:: 查找最新备份
for /f "delims=" %%i in ('dir backup_* /b /o-d 2^>nul ^| findstr /r "backup_.*"') do (
    set "latest_backup=%%i"
    goto found_backup
)

echo ❌ 找不到备份文件
echo 请手动恢复或重新构建项目
goto end

:found_backup
echo 📦 使用备份: %latest_backup%

if exist "%latest_backup%\main.tsx.backup" (
    copy "%latest_backup%\main.tsx.backup" "src\main.tsx" >nul
    echo ✅ 恢复了 main.tsx
)

if exist "%latest_backup%\App.tsx.backup" (
    copy "%latest_backup%\App.tsx.backup" "src\App.tsx" >nul
    echo ✅ 恢复了 App.tsx
)

if exist "%latest_backup%\store_index.ts.backup" (
    copy "%latest_backup%\store_index.ts.backup" "src\store\index.ts" >nul
    echo ✅ 恢复了 store\index.ts
)

echo 🎉 已切换回旧认证系统！
goto end

:test_new_system
echo 🧪 测试新认证系统...

:: 检查必要文件
set "missing_files="
if not exist "src\services\auth\index.ts" set "missing_files=%missing_files% src\services\auth\index.ts"
if not exist "src\services\auth\AuthServiceSimplified.ts" set "missing_files=%missing_files% src\services\auth\AuthServiceSimplified.ts"
if not exist "src\services\auth\ApiAdapter.ts" set "missing_files=%missing_files% src\services\auth\ApiAdapter.ts"
if not exist "src\store\authSliceNew.ts" set "missing_files=%missing_files% src\store\authSliceNew.ts"
if not exist "src\pages\LoginNew.tsx" set "missing_files=%missing_files% src\pages\LoginNew.tsx"
if not exist "src\components\ProtectedRouteNew.tsx" set "missing_files=%missing_files% src\components\ProtectedRouteNew.tsx"

if not "%missing_files%"=="" (
    echo ❌ 缺少以下文件:
    echo %missing_files%
    goto end
)

echo ✅ 所有必要文件都存在

:: 检查TypeScript编译
where tsc >nul 2>&1
if %errorlevel%==0 (
    echo 🔍 检查TypeScript编译...
    tsc --noEmit --skipLibCheck >nul 2>&1
    if %errorlevel%==0 (
        echo ✅ TypeScript编译检查通过
    ) else (
        echo ❌ TypeScript编译错误
        goto end
    )
)

echo 🎉 新系统测试通过！
goto end

:backup_only
call :backup_files
goto end

:cleanup
echo 🧹 清理临时文件...

if exist "node_modules\.cache" rmdir /s /q "node_modules\.cache" 2>nul
if exist "dist" rmdir /s /q "dist" 2>nul

echo ✅ 清理完成
goto end

:show_help
echo 用法: %~nx0 [选项]
echo.
echo 选项:
echo   new     切换到新认证系统
echo   old     切换回旧认证系统
echo   test    测试新认证系统
echo   status  检查当前系统状态
echo   backup  仅创建备份
echo   clean   清理临时文件
echo   help    显示此帮助信息
echo.
echo 示例:
echo   %~nx0 new      # 切换到新系统
echo   %~nx0 old      # 切换回旧系统
echo   %~nx0 test     # 测试新系统

:end
pause
