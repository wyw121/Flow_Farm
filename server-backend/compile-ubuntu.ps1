# Flow Farm Rust Ubuntu 编译脚本 (PowerShell版)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Flow Farm Rust Ubuntu 编译脚本" -ForegroundColor Yellow
Write-Host "使用Docker临时容器，不占用额外存储空间" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$ProjectPath = Get-Location
$OutputDir = Join-Path $ProjectPath "target\ubuntu-release"

Write-Host "📁 当前项目路径: $ProjectPath" -ForegroundColor Blue
Write-Host "📦 编译输出路径: $OutputDir" -ForegroundColor Blue
Write-Host ""

# 创建输出目录
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "✅ 创建输出目录: $OutputDir" -ForegroundColor Green
}

Write-Host "🐳 启动Docker临时容器编译..." -ForegroundColor Magenta
Write-Host ""

# 执行简化的Docker命令
try {
    $WorkspaceMount = "$($ProjectPath.Path -replace '\\', '/'):/workspace"

    Write-Host "🐳 执行Docker命令..." -ForegroundColor Yellow
    docker run --rm -v $WorkspaceMount -w /workspace rust:1.78-slim bash -c "apt-get update -qq && apt-get install -y -qq pkg-config libssl-dev && cargo build --release && ls -lh /workspace/target/release/"

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "================================================" -ForegroundColor Green
        Write-Host "✅ 编译成功！" -ForegroundColor Green
        Write-Host "================================================" -ForegroundColor Green
        Write-Host "📁 Ubuntu二进制文件位置:" -ForegroundColor Blue
        Write-Host "   $ProjectPath\target\release\flow-farm-backend" -ForegroundColor White
        Write-Host ""

        $BinaryPath = Join-Path $ProjectPath "target\release\flow-farm-backend"
        if (Test-Path $BinaryPath) {
            $FileInfo = Get-ItemProperty $BinaryPath
            Write-Host "📊 文件大小: $([math]::Round($FileInfo.Length / 1MB, 2)) MB" -ForegroundColor Cyan
        }

        Write-Host ""
        Write-Host "💡 使用说明:" -ForegroundColor Yellow
        Write-Host "   1. 将二进制文件复制到Ubuntu服务器" -ForegroundColor White
        Write-Host "   2. 确保服务器上有相同的.env配置文件" -ForegroundColor White
        Write-Host "   3. 在Ubuntu上运行: ./flow-farm-backend" -ForegroundColor White
        Write-Host ""
    }
    else {
        Write-Host ""
        Write-Host "❌ 编译失败！请检查错误信息。" -ForegroundColor Red
        Write-Host ""
    }
}
catch {
    Write-Host "❌ Docker执行出错: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "按任意键继续..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
