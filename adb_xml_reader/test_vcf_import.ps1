#!/usr/bin/env pwsh
# VCF联系人导入测试脚本

Write-Host "🚀 VCF联系人导入测试开始..." -ForegroundColor Green
Write-Host "=" * 50

# 检查是否存在联系人测试文件
$contactsFile = "D:\repositories\employeeGUI\test_contacts.txt"
if (!(Test-Path $contactsFile)) {
    Write-Host "❌ 联系人测试文件不存在: $contactsFile" -ForegroundColor Red
    exit 1
}

Write-Host "📋 联系人文件内容:" -ForegroundColor Yellow
Get-Content $contactsFile

Write-Host "`n🔧 开始执行VCF导入..." -ForegroundColor Green

# 运行VCF导入命令
try {
    $result = & .\target\debug\adb_xml_reader.exe --import-vcf $contactsFile 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ VCF导入命令执行成功!" -ForegroundColor Green
        Write-Host $result
    } else {
        Write-Host "❌ VCF导入命令执行失败!" -ForegroundColor Red
        Write-Host $result
    }
} catch {
    Write-Host "❌ 执行过程中出现异常: $_" -ForegroundColor Red
}

Write-Host "`n📱 下一步操作指南:" -ForegroundColor Cyan
Write-Host "1. 检查设备Downloads文件夹中的contacts_import.vcf文件"
Write-Host "2. 在联系人应用中选择 '导入/导出 > 从存储导入'"
Write-Host "3. 选择contacts_import.vcf文件完成导入"
Write-Host "4. 验证小红书应用是否可以读取导入的联系人"

Write-Host "`n🎉 测试完成!" -ForegroundColor Green
