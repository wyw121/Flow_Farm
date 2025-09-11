# Flow Farm React Frontend Build Script (PowerShell Version)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Flow Farm React 前端编译部署脚本" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 检查Node.js环境
Write-Host "📦 检查Node.js环境..." -ForegroundColor Blue
try {
    $nodeVersion = node --version 2>$null
    Write-Host "✅ Node.js版本: $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ 错误: 找不到Node.js，请先安装Node.js" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 切换到前端目录
$frontendPath = "d:\repositories\Flow_Farm\server-frontend"
Set-Location $frontendPath
Write-Host "📁 工作目录: $frontendPath" -ForegroundColor Blue

# 安装依赖
Write-Host "📦 安装/更新依赖..." -ForegroundColor Blue
try {
    npm install
    Write-Host "✅ 依赖安装完成" -ForegroundColor Green
}
catch {
    Write-Host "❌ 依赖安装失败" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 编译项目
Write-Host "🏗️ 编译React项目 (生产模式)..." -ForegroundColor Magenta
try {
    npm run build
    Write-Host "✅ 编译完成" -ForegroundColor Green
}
catch {
    Write-Host "❌ 编译失败，请检查代码错误" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 检查编译产物
Write-Host "📊 编译产物信息:" -ForegroundColor Blue
$distPath = Join-Path $frontendPath "dist"
if (Test-Path $distPath) {
    $files = Get-ChildItem $distPath -Recurse | Measure-Object
    Write-Host "📁 总文件数: $($files.Count) 个" -ForegroundColor Cyan

    if (Test-Path (Join-Path $distPath "index.html")) {
        Write-Host "✅ index.html 存在" -ForegroundColor Green
    }
    else {
        Write-Host "❌ index.html 未找到" -ForegroundColor Red
    }
}
else {
    Write-Host "❌ 找不到构建产物 dist/ 目录" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 准备后端静态文件目录
$backendPath = "d:\repositories\Flow_Farm\server-backend"
$staticPath = Join-Path $backendPath "static"

Write-Host "📁 准备静态文件目录..." -ForegroundColor Blue
Set-Location $backendPath

if (!(Test-Path $staticPath)) {
    New-Item -ItemType Directory -Path $staticPath -Force | Out-Null
    Write-Host "✅ 创建静态目录: $staticPath" -ForegroundColor Green
}

# 复制静态文件
Write-Host "🚀 复制静态文件到Rust后端..." -ForegroundColor Magenta
try {
    # 清空目标目录
    if (Test-Path $staticPath) {
        Remove-Item "$staticPath\*" -Recurse -Force -ErrorAction SilentlyContinue
    }

    # 复制文件
    Copy-Item "$distPath\*" -Destination $staticPath -Recurse -Force
    Write-Host "✅ 文件复制完成" -ForegroundColor Green
}
catch {
    Write-Host "❌ 文件复制失败: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 验证部署结果
Write-Host "✅ 验证部署结果..." -ForegroundColor Blue
$indexFile = Join-Path $staticPath "index.html"
$assetsDir = Join-Path $staticPath "assets"

if (Test-Path $indexFile) {
    Write-Host "✅ index.html 存在" -ForegroundColor Green
}
else {
    Write-Host "❌ index.html 未找到" -ForegroundColor Red
}

if (Test-Path $assetsDir) {
    $jsFiles = Get-ChildItem $assetsDir -Filter "*.js" | Measure-Object
    $cssFiles = Get-ChildItem $assetsDir -Filter "*.css" | Measure-Object
    Write-Host "✅ assets 目录存在 (JS: $($jsFiles.Count), CSS: $($cssFiles.Count))" -ForegroundColor Green
}
else {
    Write-Host "❌ assets 目录未找到" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "✅ React前端编译部署完成！" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "📁 静态文件位置: $staticPath" -ForegroundColor Blue
Write-Host "🚀 启动命令:" -ForegroundColor Yellow
Write-Host "   cd server-backend" -ForegroundColor White
Write-Host "   cargo run --release" -ForegroundColor White
Write-Host ""
Write-Host "🌐 访问地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📋 API文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Green

# 询问是否启动后端
Write-Host "🤔 是否现在启动Rust后端服务器? (y/n): " -ForegroundColor Yellow -NoNewline
$choice = Read-Host

if ($choice -eq 'y' -or $choice -eq 'Y') {
    Write-Host "🚀 启动Rust后端..." -ForegroundColor Magenta
    try {
        cargo run --release
    }
    catch {
        Write-Host "❌ 启动失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}
else {
    Write-Host "💡 您可以稍后手动启动:" -ForegroundColor Yellow
    Write-Host "   cd server-backend" -ForegroundColor White
    Write-Host "   cargo run --release" -ForegroundColor White
}

Write-Host "按任意键继续..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
