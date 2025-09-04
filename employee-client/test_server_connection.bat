@echo off
echo ===========================================
echo Flow Farm 桌面客户端连接测试
echo ===========================================
echo.

echo 正在检查服务器状态...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -Method GET; if ($response.StatusCode -eq 200) { Write-Host '✅ 服务器正在运行' -ForegroundColor Green } else { Write-Host '❌ 服务器无响应' -ForegroundColor Red } } catch { Write-Host '❌ 无法连接服务器' -ForegroundColor Red }"

echo.
echo 测试登录功能...
powershell -Command "$body = '{\"username\": \"client_test\", \"password\": \"test123\"}'; try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/auth/login' -Method POST -ContentType 'application/json' -Body $body; $result = $response.Content | ConvertFrom-Json; if ($result.success) { Write-Host '✅ 用户登录成功' -ForegroundColor Green; Write-Host ('用户名: ' + $result.data.user.username) -ForegroundColor Cyan; Write-Host ('角色: ' + $result.data.user.role) -ForegroundColor Cyan } else { Write-Host ('❌ 登录失败: ' + $result.message) -ForegroundColor Red } } catch { Write-Host '❌ 登录请求失败' -ForegroundColor Red }"

echo.
echo ===========================================
echo 测试完成！
echo.
echo 测试用户信息:
echo   用户名: client_test
echo   密码: test123
echo   角色: employee
echo.
echo 现在可以使用这个账号登录桌面客户端程序
echo ===========================================
pause
