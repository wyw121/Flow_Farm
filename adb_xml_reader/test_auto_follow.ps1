# 小红书自动关注功能测试脚本
# PowerShell版本

Write-Host ""
Write-Host "========================================"
Write-Host "小红书自动关注功能测试" -ForegroundColor Cyan
Write-Host "========================================"
Write-Host ""

# 检查ADB连接
Write-Host "📱 检查设备连接状态..." -ForegroundColor Yellow
& "D:\leidian\LDPlayer9\adb.exe" devices
Write-Host ""

# 提示用户
Write-Host "⚠️  使用前请确认:" -ForegroundColor Red
Write-Host "   1. 小红书APP已打开且在主页"
Write-Host "   2. 设备屏幕保持亮屏"
Write-Host "   3. 通讯录中有好友需要关注"
Write-Host ""

$choice = Read-Host "请选择测试模式 [1=仅导航测试, 2=完整自动关注]"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🧭 开始测试导航流程（不会自动关注）..." -ForegroundColor Green
        Write-Host ""
        & ".\target\release\adb_xml_reader.exe" --auto-contact-flow
    }
    "2" {
        Write-Host ""
        Write-Host "🤖 开始完整自动关注测试..." -ForegroundColor Green
        Write-Host "   ⚠️  这将会实际关注通讯录中的好友！" -ForegroundColor Red
        Write-Host ""
        $confirm = Read-Host "确认继续？ (y/N)"
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            & ".\target\release\adb_xml_reader.exe" --auto-follow-contacts
        } else {
            Write-Host "❌ 用户取消操作" -ForegroundColor Red
        }
    }
    default {
        Write-Host "❌ 无效选择，请输入 1 或 2" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ 测试完成！" -ForegroundColor Green
Read-Host "按回车键退出"
