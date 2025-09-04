# Flow Farm 用户查询脚本
# 查询数据库中所有用户账号信息

Write-Host "========================================" -ForegroundColor Green
Write-Host "     Flow Farm 用户账号查询工具" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

try {
    Write-Host "正在连接数据库并查询用户信息..." -ForegroundColor Yellow
    Write-Host ""

    # 运行查询程序
    $output = & cargo run --bin query_users 2>&1

    # 过滤并显示输出
    $lines = $output -split "`r`n|`n"
    $inUserSection = $false

    foreach ($line in $lines) {
        # 跳过编译警告
        if ($line -match "warning:|Compiling|Building|Finished|Running") {
            continue
        }

        # 显示连接信息
        if ($line -match "连接到数据库") {
            Write-Host $line -ForegroundColor Cyan
            continue
        }

        # 显示表列表
        if ($line -match "数据库中的表:") {
            Write-Host $line -ForegroundColor Yellow
            $inUserSection = $false
            continue
        }

        # 显示表名
        if ($line -match "^- ") {
            Write-Host $line -ForegroundColor White
            continue
        }

        # 显示用户统计
        if ($line -match "表.*users.*中的记录数量:") {
            Write-Host $line -ForegroundColor Green
            continue
        }

        # 开始显示用户详情
        if ($line -match "所有用户账号详情:") {
            Write-Host $line -ForegroundColor Green
            $inUserSection = $true
            continue
        }

        # 显示用户分隔线
        if ($line -match "=== 用户 \d+ ===") {
            Write-Host ""
            Write-Host $line -ForegroundColor Magenta
            $inUserSection = $true
            continue
        }

        # 显示用户详细信息
        if ($inUserSection) {
            if ($line -match "ID:|用户名:|邮箱:|角色:|账号状态:|验证状态:|全名:|电话:|公司:|最大员工数:|当前员工数:|创建时间:|更新时间:|最后登录:") {
                Write-Host $line -ForegroundColor Cyan
                continue
            }
            elseif ($line.Trim() -eq "" -or $line -match "PS D:\\") {
                # 遇到空行或提示符，结束用户信息显示
                break
            }
        }
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "查询完成！" -ForegroundColor Green
}
catch {
    Write-Host "查询过程中出现错误: $_" -ForegroundColor Red
}
