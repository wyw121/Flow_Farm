# ADB XML Reader - PowerShell 自动化脚本

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "      ADB XML Reader - 自动化分析脚本" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# 设置变量
$AdbPath = "D:\leidian\LDPlayer9\adb.exe"
$ToolPath = ".\target\release\adb_xml_reader.exe"

Write-Host "`n1. 检查连接的设备..." -ForegroundColor Yellow
& $AdbPath devices

# 获取设备列表
$DeviceOutput = & $AdbPath devices
$Devices = @()
$DeviceOutput | ForEach-Object {
    if ($_ -match "^([^\s]+)\s+device$") {
        $Devices += $Matches[1]
    }
}

if ($Devices.Count -eq 0) {
    Write-Host "❌ 未发现连接的设备，请检查虚拟机是否启动" -ForegroundColor Red
    pause
    exit
}

Write-Host "✅ 发现 $($Devices.Count) 个设备" -ForegroundColor Green
$SelectedDevice = $Devices[0]
Write-Host "使用设备: $SelectedDevice" -ForegroundColor Green

# 创建输出目录
$OutputDir = "analysis_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Name $OutputDir -Force | Out-Null
Write-Host "📁 创建输出目录: $OutputDir" -ForegroundColor Green

# 功能函数
function Run-Analysis {
    param(
        [string]$Description,
        [string[]]$Arguments,
        [string]$OutputFile = ""
    )

    Write-Host "`n$Description..." -ForegroundColor Yellow

    $AllArgs = @("--device", $SelectedDevice) + $Arguments
    if ($OutputFile) {
        $AllArgs += @("--output", "$OutputDir\$OutputFile")
    }

    try {
        & $ToolPath $AllArgs
        Write-Host "✅ $Description 完成" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ $Description 失败: $_" -ForegroundColor Red
    }
}

# 执行分析任务
Run-Analysis "2. 获取完整UI结构" @("--screenshot", "$OutputDir\full_screenshot.png") "full_ui_structure.json"

Run-Analysis "3. 搜索关注相关元素" @("--search", "关注") "follow_elements.json"

Run-Analysis "4. 搜索点赞相关元素" @("--search", "赞") "like_elements.json"

Run-Analysis "5. 搜索发布相关元素" @("--search", "发布") "publish_elements.json"

Run-Analysis "6. 搜索评论相关元素" @("--search", "评论") "comment_elements.json"

Run-Analysis "7. 搜索分享相关元素" @("--search", "分享") "share_elements.json"

# 创建分析报告
$ReportFile = "$OutputDir\analysis_report.txt"
$Report = @"
ADB XML Reader 分析报告
======================
分析时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
设备信息: $SelectedDevice
输出目录: $OutputDir

生成的文件:
- full_ui_structure.json  : 完整UI结构
- full_screenshot.png     : 完整屏幕截图
- follow_elements.json    : 关注相关元素
- like_elements.json      : 点赞相关元素
- publish_elements.json   : 发布相关元素
- comment_elements.json   : 评论相关元素
- share_elements.json     : 分享相关元素

使用建议:
1. 查看 full_ui_structure.json 了解页面完整结构
2. 使用截图对照JSON文件理解元素位置
3. 搜索结果可用于自动化脚本开发
4. 元素坐标可用于自动点击操作

技术说明:
- bounds 格式: [左,上][右,下]
- clickable: true 表示元素可点击
- 坐标系以屏幕左上角为原点(0,0)
"@

$Report | Out-File -FilePath $ReportFile -Encoding UTF8

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "           分析完成！" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "📊 输出目录: $OutputDir" -ForegroundColor Green
Write-Host "📄 分析报告: $ReportFile" -ForegroundColor Green

# 显示文件列表
Write-Host "`n📁 生成的文件:" -ForegroundColor Yellow
Get-ChildItem $OutputDir | ForEach-Object {
    $Size = if ($_.Length -gt 1MB) { "{0:N1} MB" -f ($_.Length / 1MB) }
            elseif ($_.Length -gt 1KB) { "{0:N1} KB" -f ($_.Length / 1KB) }
            else { "{0} B" -f $_.Length }
    Write-Host "  $($_.Name) ($Size)" -ForegroundColor White
}

Write-Host "`n💡 使用 notepad $ReportFile 查看详细报告" -ForegroundColor Cyan
Write-Host "按任意键继续..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
