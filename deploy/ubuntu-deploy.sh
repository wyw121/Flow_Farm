#!/bin/bash
# Flow Farm Ubuntu 服务器自动部署脚本
# 使用方法: ./ubuntu-deploy.sh [zip文件路径]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色信息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "请不要使用root用户运行此脚本！请使用sudo权限的普通用户。"
        exit 1
    fi
}

# 检查sudo权限
check_sudo() {
    if ! sudo -n true 2>/dev/null; then
        print_warning "需要sudo权限，请输入密码："
        sudo -v
    fi
}

# 安装依赖
install_dependencies() {
    print_info "检查并安装依赖..."
    
    # 更新包列表
    sudo apt update
    
    # 安装必要的包
    sudo apt install -y unzip curl wget systemctl
    
    print_success "依赖安装完成"
}

# 停止现有服务
stop_existing_service() {
    if systemctl is-active --quiet flow-farm; then
        print_info "停止现有的Flow Farm服务..."
        sudo systemctl stop flow-farm
        print_success "服务已停止"
    fi
}

# 备份现有安装
backup_existing() {
    if [ -d "/opt/flow-farm" ]; then
        print_info "备份现有安装..."
        BACKUP_DIR="/opt/flow-farm-backup-$(date +%Y%m%d-%H%M%S)"
        sudo mv /opt/flow-farm "$BACKUP_DIR"
        print_success "备份完成: $BACKUP_DIR"
    fi
}

# 部署新版本
deploy_new_version() {
    local zip_file="$1"
    
    print_info "部署新版本..."
    
    # 创建临时目录
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # 解压部署包
    print_info "解压部署包..."
    unzip -q "$zip_file"
    
    # 移动到系统目录
    print_info "安装到系统目录..."
    sudo mkdir -p /opt/flow-farm
    sudo cp -r * /opt/flow-farm/
    
    # 设置权限
    print_info "设置文件权限..."
    sudo chown -R www-data:www-data /opt/flow-farm
    sudo chmod +x /opt/flow-farm/flow-farm-backend
    sudo chmod +x /opt/flow-farm/start.sh
    
    # 创建必要的目录
    sudo mkdir -p /opt/flow-farm/logs
    sudo mkdir -p /opt/flow-farm/uploads
    sudo chown -R www-data:www-data /opt/flow-farm/logs
    sudo chown -R www-data:www-data /opt/flow-farm/uploads
    
    # 清理临时目录
    cd /
    rm -rf "$TEMP_DIR"
    
    print_success "新版本部署完成"
}

# 安装系统服务
install_service() {
    print_info "安装系统服务..."
    
    # 复制服务文件
    sudo cp /opt/flow-farm/flow-farm.service /etc/systemd/system/
    
    # 重载systemd
    sudo systemctl daemon-reload
    
    # 启用服务
    sudo systemctl enable flow-farm
    
    print_success "系统服务安装完成"
}

# 启动服务
start_service() {
    print_info "启动Flow Farm服务..."
    
    sudo systemctl start flow-farm
    
    # 等待服务启动
    sleep 3
    
    # 检查服务状态
    if systemctl is-active --quiet flow-farm; then
        print_success "服务启动成功！"
    else
        print_error "服务启动失败！"
        print_info "查看服务日志:"
        sudo journalctl -u flow-farm --no-pager -n 20
        exit 1
    fi
}

# 检查服务健康状态
check_health() {
    print_info "检查服务健康状态..."
    
    # 等待服务完全启动
    sleep 5
    
    # 测试HTTP响应
    local health_url="http://localhost:8080"
    if curl -s -f "$health_url" > /dev/null; then
        print_success "Web服务正常运行！"
        print_info "访问地址: http://$(hostname -I | awk '{print $1}'):8080"
    else
        print_warning "Web服务可能未完全启动，请稍后检查"
        print_info "手动测试: curl http://localhost:8080"
    fi
    
    # 显示服务状态
    print_info "服务状态:"
    sudo systemctl status flow-farm --no-pager -l
}

# 显示部署后信息
show_post_deploy_info() {
    echo
    print_success "🎉 Flow Farm 部署完成！"
    echo
    print_info "📋 部署信息:"
    echo "  📁 安装目录: /opt/flow-farm"
    echo "  🌐 访问地址: http://$(hostname -I | awk '{print $1}'):8080"
    echo "  🗄️ 数据库: /opt/flow-farm/data/flow_farm.db"
    echo "  📝 日志目录: /opt/flow-farm/logs"
    echo
    print_info "🔧 常用命令:"
    echo "  查看服务状态: sudo systemctl status flow-farm"
    echo "  重启服务:     sudo systemctl restart flow-farm"
    echo "  停止服务:     sudo systemctl stop flow-farm"
    echo "  查看日志:     sudo journalctl -u flow-farm -f"
    echo
    print_info "🌐 测试访问:"
    echo "  curl http://localhost:8080"
    echo "  curl http://localhost:8080/api/health"
    echo
}

# 主函数
main() {
    local zip_file="$1"
    
    # 检查参数
    if [ -z "$zip_file" ]; then
        print_error "用法: $0 <部署包zip文件路径>"
        print_info "示例: $0 flow-farm-deploy-20250912-072227.zip"
        exit 1
    fi
    
    # 检查文件是否存在
    if [ ! -f "$zip_file" ]; then
        print_error "文件不存在: $zip_file"
        exit 1
    fi
    
    print_info "🚀 开始部署 Flow Farm..."
    echo
    
    # 执行部署步骤
    check_root
    check_sudo
    install_dependencies
    stop_existing_service
    backup_existing
    deploy_new_version "$zip_file"
    install_service
    start_service
    check_health
    show_post_deploy_info
    
    print_success "🎉 部署完成！"
}

# 运行主函数
main "$@"
