# ADB XML Reader - PowerShell Auto Analysis Script

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "      ADB XML Reader - Auto Analysis" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Set variables
$AdbPath = "D:\leidian\LDPlayer9\adb.exe"
$ToolPath = ".\target\release\adb_xml_reader.exe"

Write-Host "`n1. Checking connected devices..." -ForegroundColor Yellow
& $AdbPath devices

# Get device list
$DeviceOutput = & $AdbPath devices
$Devices = @()
$DeviceOutput | ForEach-Object {
    if ($_ -match "^([0-9\.:\-\w]+)\s+device$") {
        $Devices += $Matches[1]
    }
}

if ($Devices.Count -eq 0) {
    Write-Host "No devices found. Please check if virtual machine is running" -ForegroundColor Red
    pause
    exit
}

Write-Host "Found $($Devices.Count) devices" -ForegroundColor Green
$SelectedDevice = $Devices[0]
Write-Host "Using device: $SelectedDevice" -ForegroundColor Green

# Create output directory
$OutputDir = "analysis_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Name $OutputDir -Force | Out-Null
Write-Host "Created output directory: $OutputDir" -ForegroundColor Green

# Analysis function
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
        Write-Host "Completed: $Description" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed: $Description - $_" -ForegroundColor Red
    }
}

# Execute analysis tasks
Run-Analysis "2. Getting full UI structure" @("--screenshot", "$OutputDir\full_screenshot.png") "full_ui_structure.json"

Run-Analysis "3. Searching follow elements" @("--search", "关注") "follow_elements.json"

Run-Analysis "4. Searching like elements" @("--search", "赞") "like_elements.json"

Run-Analysis "5. Searching publish elements" @("--search", "发布") "publish_elements.json"

Run-Analysis "6. Searching comment elements" @("--search", "评论") "comment_elements.json"

Run-Analysis "7. Searching share elements" @("--search", "分享") "share_elements.json"

# Create analysis report
$ReportFile = "$OutputDir\analysis_report.txt"
$ReportContent = @"
ADB XML Reader Analysis Report
==============================
Analysis Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Device: $SelectedDevice
Output Directory: $OutputDir

Generated Files:
- full_ui_structure.json  : Complete UI structure
- full_screenshot.png     : Full screenshot
- follow_elements.json    : Follow related elements
- like_elements.json      : Like related elements
- publish_elements.json   : Publish related elements
- comment_elements.json   : Comment related elements
- share_elements.json     : Share related elements

Usage Tips:
1. Check full_ui_structure.json for complete page structure
2. Use screenshot to understand element positions
3. Search results can be used for automation scripts
4. Element coordinates can be used for auto-click operations

Technical Notes:
- bounds format: [left,top][right,bottom]
- clickable: true means element can be clicked
- Coordinate system origin (0,0) is at top-left corner
"@

$ReportContent | Out-File -FilePath $ReportFile -Encoding UTF8

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "           Analysis Complete!" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Output directory: $OutputDir" -ForegroundColor Green
Write-Host "Analysis report: $ReportFile" -ForegroundColor Green

# Show file list
Write-Host "`nGenerated files:" -ForegroundColor Yellow
Get-ChildItem $OutputDir | ForEach-Object {
    $Size = if ($_.Length -gt 1MB) { "{0:N1} MB" -f ($_.Length / 1MB) }
            elseif ($_.Length -gt 1KB) { "{0:N1} KB" -f ($_.Length / 1KB) }
            else { "{0} B" -f $_.Length }
    Write-Host "  $($_.Name) ($Size)" -ForegroundColor White
}

Write-Host "`nUse notepad $ReportFile to view detailed report" -ForegroundColor Cyan
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
