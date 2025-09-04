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
            if ($line -match "🆔|👤|📧|👨‍💼|🟢|✅|📝|📞|🏢|👥|👷|📅|🔄|🕐") {
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
        Write-Host "=== 用户账号统计信息 ==="
        Write-Host "总用户数："
        & sqlite3 $dbPath "SELECT COUNT(*) FROM users;"

        Write-Host "`n按角色统计："
        & sqlite3 $dbPath "SELECT role, COUNT(*) FROM users GROUP BY role;"

        Write-Host "`n活跃用户数："
        & sqlite3 $dbPath "SELECT COUNT(*) FROM users WHERE is_active = 1;"

        Write-Host "`n用户详细信息："
        & sqlite3 $dbPath -header -column "SELECT id, username, email, role, company, is_active, created_at FROM users ORDER BY created_at;"
    }
    else {
        Write-Host "请手动安装 SQLite3 以查看详细统计"
    }
}
catch {
    Write-Host "查询失败: $($_.Exception.Message)"
}
