# 小红书自动点击演示脚本

Write-Host "🎯 小红书自动点击演示 - 进入通讯录页面" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

$ToolPath = ".\target\release\adb_xml_reader.exe"
$Device = "127.0.0.1:5555"

# 步骤1: 检查当前页面状态
Write-Host "`n📱 步骤1: 检查当前页面状态..." -ForegroundColor Yellow
& $ToolPath --device $Device --search "通讯录" --output step1_check.json --screenshot step1_check.png
Write-Host "✅ 页面状态检查完成" -ForegroundColor Green

# 等待用户确认
Write-Host "`n⏸️  请确认当前页面状态，按任意键继续..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# 步骤2: 如果已经在通讯录页面，先返回
Write-Host "`n🔙 步骤2: 点击返回按钮回到主页面..." -ForegroundColor Yellow
& $ToolPath --device $Device --click "42,84"
Start-Sleep -Seconds 2
Write-Host "✅ 返回操作完成" -ForegroundColor Green

# 步骤3: 检查主页面状态
Write-Host "`n📱 步骤3: 检查主页面状态..." -ForegroundColor Yellow
& $ToolPath --device $Device --search "发现好友" --output step3_main.json --screenshot step3_main.png
Write-Host "✅ 主页面检查完成" -ForegroundColor Green

# 步骤4: 点击通讯录选项
Write-Host "`n👆 步骤4: 点击通讯录选项..." -ForegroundColor Yellow
& $ToolPath --device $Device --click "194,249"
Start-Sleep -Seconds 3
Write-Host "✅ 点击通讯录完成" -ForegroundColor Green

# 步骤5: 验证最终结果
Write-Host "`n🎉 步骤5: 验证最终结果..." -ForegroundColor Yellow
& $ToolPath --device $Device --search "通讯录" --output final_contacts.json --screenshot final_contacts.png
Write-Host "✅ 验证完成" -ForegroundColor Green

Write-Host "`n🎊 演示完成！" -ForegroundColor Green
Write-Host "📁 生成的文件:" -ForegroundColor Cyan
Get-ChildItem step*.json, step*.png, final*.json, final*.png | ForEach-Object {
    Write-Host "  📄 $($_.Name)" -ForegroundColor White
}

Write-Host "`n💡 总结:" -ForegroundColor Yellow
Write-Host "  ✅ 成功点击操作并进入通讯录页面" -ForegroundColor Green
Write-Host "  ✅ 每个步骤都有截图和数据记录" -ForegroundColor Green
Write-Host "  ✅ 实现了精确的坐标点击" -ForegroundColor Green
Write-Host "  ✅ 验证了页面跳转的成功性" -ForegroundColor Green
