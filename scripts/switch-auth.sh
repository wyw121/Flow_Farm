#!/bin/bash

# Flow Farm 认证系统切换脚本
# 用于在新旧认证系统之间切换

echo "🚀 Flow Farm 认证系统切换工具"
echo "================================"

# 检查当前状态
check_current_system() {
    if grep -q "AppNew" src/main.tsx 2>/dev/null; then
        echo "✅ 当前使用新认证系统"
        return 0
    elif grep -q "App" src/main.tsx 2>/dev/null; then
        echo "📛 当前使用旧认证系统"
        return 1
    else
        echo "❌ 无法确定当前系统状态"
        return 2
    fi
}

# 备份当前文件
backup_files() {
    echo "📦 备份当前文件..."

    backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"

    # 备份关键文件
    if [ -f "src/main.tsx" ]; then
        cp "src/main.tsx" "$backup_dir/main.tsx.backup"
    fi

    if [ -f "src/App.tsx" ]; then
        cp "src/App.tsx" "$backup_dir/App.tsx.backup"
    fi

    if [ -f "src/store/index.ts" ]; then
        cp "src/store/index.ts" "$backup_dir/store_index.ts.backup"
    fi

    echo "✅ 备份完成: $backup_dir"
}

# 切换到新认证系统
switch_to_new() {
    echo "🔄 切换到新认证系统..."

    # 更新main.tsx
    if [ -f "src/mainNew.tsx" ]; then
        cp "src/mainNew.tsx" "src/main.tsx"
        echo "✅ 更新了 main.tsx"
    else
        echo "❌ 找不到 src/mainNew.tsx"
        return 1
    fi

    # 更新App.tsx
    if [ -f "src/AppNew.tsx" ]; then
        cp "src/AppNew.tsx" "src/App.tsx"
        echo "✅ 更新了 App.tsx"
    else
        echo "❌ 找不到 src/AppNew.tsx"
        return 1
    fi

    # 更新App.css
    if [ -f "src/AppNew.css" ]; then
        cp "src/AppNew.css" "src/App.css"
        echo "✅ 更新了 App.css"
    fi

    # 更新store配置
    if [ -f "src/store/indexNew.ts" ]; then
        cp "src/store/indexNew.ts" "src/store/index.ts"
        echo "✅ 更新了 store/index.ts"
    else
        echo "❌ 找不到 src/store/indexNew.ts"
        return 1
    fi

    echo "🎉 已切换到新认证系统！"
    return 0
}

# 恢复到旧认证系统
switch_to_old() {
    echo "🔄 切换到旧认证系统..."

    # 检查备份
    latest_backup=$(ls -t backup_* 2>/dev/null | head -1)
    if [ -z "$latest_backup" ]; then
        echo "❌ 找不到备份文件"
        echo "请手动恢复或重新构建项目"
        return 1
    fi

    echo "📦 使用备份: $latest_backup"

    # 恢复文件
    if [ -f "$latest_backup/main.tsx.backup" ]; then
        cp "$latest_backup/main.tsx.backup" "src/main.tsx"
        echo "✅ 恢复了 main.tsx"
    fi

    if [ -f "$latest_backup/App.tsx.backup" ]; then
        cp "$latest_backup/App.tsx.backup" "src/App.tsx"
        echo "✅ 恢复了 App.tsx"
    fi

    if [ -f "$latest_backup/store_index.ts.backup" ]; then
        cp "$latest_backup/store_index.ts.backup" "src/store/index.ts"
        echo "✅ 恢复了 store/index.ts"
    fi

    echo "🎉 已切换回旧认证系统！"
    return 0
}

# 测试新系统
test_new_system() {
    echo "🧪 测试新认证系统..."

    # 检查必要文件
    required_files=(
        "src/services/auth/index.ts"
        "src/services/auth/AuthServiceSimplified.ts"
        "src/services/auth/ApiAdapter.ts"
        "src/store/authSliceNew.ts"
        "src/pages/LoginNew.tsx"
        "src/components/ProtectedRouteNew.tsx"
    )

    missing_files=()
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done

    if [ ${#missing_files[@]} -gt 0 ]; then
        echo "❌ 缺少以下文件:"
        printf '%s\n' "${missing_files[@]}"
        return 1
    fi

    echo "✅ 所有必要文件都存在"

    # 检查TypeScript编译
    if command -v tsc >/dev/null 2>&1; then
        echo "🔍 检查TypeScript编译..."
        if tsc --noEmit --skipLibCheck; then
            echo "✅ TypeScript编译检查通过"
        else
            echo "❌ TypeScript编译错误"
            return 1
        fi
    fi

    echo "🎉 新系统测试通过！"
    return 0
}

# 清理临时文件
cleanup() {
    echo "🧹 清理临时文件..."

    # 清理node_modules缓存
    if [ -d "node_modules" ]; then
        rm -rf node_modules/.cache 2>/dev/null
    fi

    # 清理构建缓存
    if [ -d "dist" ]; then
        rm -rf dist
    fi

    echo "✅ 清理完成"
}

# 显示帮助
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  new     切换到新认证系统"
    echo "  old     切换回旧认证系统"
    echo "  test    测试新认证系统"
    echo "  status  检查当前系统状态"
    echo "  backup  仅创建备份"
    echo "  clean   清理临时文件"
    echo "  help    显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 new      # 切换到新系统"
    echo "  $0 old      # 切换回旧系统"
    echo "  $0 test     # 测试新系统"
}

# 主函数
main() {
    case "${1:-}" in
        "new")
            backup_files
            if switch_to_new; then
                echo ""
                echo "🎯 下一步："
                echo "1. 运行 'npm run dev' 启动开发服务器"
                echo "2. 访问 http://localhost:3000 测试登录"
                echo "3. 如有问题，运行 '$0 old' 切换回旧系统"
            fi
            ;;
        "old")
            switch_to_old
            ;;
        "test")
            test_new_system
            ;;
        "status")
            check_current_system
            ;;
        "backup")
            backup_files
            ;;
        "clean")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo "❌ 无效选项: ${1:-}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
