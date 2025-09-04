# Flow Farm 桌面客户端连接测试
Write-Host "===========================================" -ForegroundColor Yellow
Write-Host "Flow Farm 桌面客户端连接测试" -ForegroundColor Yellow
Write-Host "===========================================" -ForegroundColor Yellow
Write-Host

Write-Host "正在检查服务器状态..." -ForegroundColor Blue
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 服务器正在运行" -ForegroundColor Green
    } else {
        Write-Host "❌ 服务器无响应" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ 无法连接服务器" -ForegroundColor Red
    Write-Host "请确保服务器后端正在运行" -ForegroundColor Yellow
}

Write-Host
Write-Host "测试登录功能..." -ForegroundColor Blue
$body = '{"username": "client_test", "password": "test123"}'
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -ContentType "application/json" -Body $body
    $result = $response.Content | ConvertFrom-Json
    if ($result.success) {
        Write-Host "✅ 用户登录成功" -ForegroundColor Green
        Write-Host "用户名: $($result.data.user.username)" -ForegroundColor Cyan
        Write-Host "角色: $($result.data.user.role)" -ForegroundColor Cyan
        Write-Host "邮箱: $($result.data.user.email)" -ForegroundColor Cyan
    } else {
        Write-Host "❌ 登录失败: $($result.message)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ 登录请求失败" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host
Write-Host "===========================================" -ForegroundColor Yellow
Write-Host "测试完成！" -ForegroundColor Green
Write-Host
Write-Host "🔑 测试用户信息:" -ForegroundColor Yellow
Write-Host "   用户名: client_test" -ForegroundColor White
Write-Host "   密码: test123" -ForegroundColor White
Write-Host "   角色: employee" -ForegroundColor White
Write-Host
Write-Host "✨ 现在可以使用这个账号登录桌面客户端程序" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Yellow

Read-Host "按回车键继续"
