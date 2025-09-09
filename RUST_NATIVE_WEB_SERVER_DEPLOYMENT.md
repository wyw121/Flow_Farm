# Flow Farm Rust 原生 Web 服务器部署指南

## 🚀 架构优势

使用Rust直接提供Web服务，无需Nginx等反向代理：

```
Internet → Flow Farm Rust Server (Port 8080)
                ├── API 路由 (/api/*)
                ├── 静态文件服务 (/, /assets/*)
                ├── SPA路由支持 (React Router)
                └── WebSocket支持 (可选)
```

### ✨ 核心优势

1. **极简架构**: 单一Rust二进制文件处理所有请求
2. **高性能**: 无代理层损耗，直接处理HTTP请求
3. **内存安全**: Rust的零成本抽象和内存安全保证
4. **部署简单**: 无需配置Nginx，减少运维复杂度
5. **统一日志**: 所有请求和错误都在一个地方记录
6. **自动压缩**: 内置Gzip/Brotli压缩支持
7. **智能缓存**: 根据文件类型自动设置缓存策略

## 📋 已实现的功能

### 🔧 Web服务器功能
- ✅ 静态文件服务 (HTML, CSS, JS, 图片等)
- ✅ SPA路由支持 (React Router兼容)
- ✅ API路由处理 (/api/* 路径)
- ✅ 自动压缩 (Gzip/Brotli)
- ✅ 智能缓存控制
- ✅ CORS跨域支持
- ✅ 安全头设置
- ✅ 404/错误页面处理

### 📁 文件服务策略
- **HTML文件**: 无缓存 (确保更新及时)
- **JS/CSS文件**: 长期缓存 (1年)
- **图片/字体**: 长期缓存 (1年)
- **JSON文件**: 短期缓存 (1小时)

### 🛡️ 安全特性
- ✅ X-Content-Type-Options: nosniff
- ✅ X-Frame-Options: DENY
- ✅ 路径遍历保护
- ✅ API路径隔离
- ✅ JWT认证保护

## 🏗️ 部署方案

### 方案一：直接部署 (推荐)

```
┌─────────────────────────────────────────────────────┐
│                Linux 服务器                         │
│                                                     │
│  ┌─────────────────────────────────────────────────┐│
│  │        Flow Farm Rust Server                   ││
│  │         (Port 8080)                            ││
│  │  ┌──────────────┐  ┌────────────────────────┐  ││
│  │  │  API服务     │  │     静态文件服务        │  ││
│  │  │ /api/*      │  │ /, /assets/, /static/* │  ││
│  │  └──────────────┘  └────────────────────────┘  ││
│  │           │                    │               ││
│  │  ┌──────────────┐  ┌────────────────────────┐  ││
│  │  │  数据库      │  │     日志系统           │  ││
│  │  │ SQLite      │  │   tracing + 文件       │  ││
│  │  └──────────────┘  └────────────────────────┘  ││
│  └─────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

### 方案二：负载均衡 (大型部署)

```
         ┌─── Load Balancer (HAProxy/Cloudflare)
         │
    ┌────┴───┬────────────┬──────────────┐
    │        │            │              │
┌───▼───┐┌───▼───┐ ┌─────▼─────┐ ┌──────▼──────┐
│Server1││Server2│ │  Server3  │ │   Server4   │
│:8080  ││:8080  │ │   :8080   │ │    :8080    │
└───────┘└───────┘ └───────────┘ └─────────────┘
```

## 🚀 快速部署步骤

### 第一步：构建生产版本

```bash
# 1. 构建前端
cd server-frontend
npm install
npm run build

# 2. 构建后端
cd ../server-backend
cargo build --release
```

### 第二步：配置生产环境

```bash
# 复制生产配置
cp .env.production .env

# 编辑配置文件
nano .env
```

### 第三步：部署到服务器

```bash
# 1. 创建应用目录
sudo mkdir -p /opt/flow-farm/{bin,data,logs,static}

# 2. 上传文件
scp target/release/flow-farm-backend user@server:/opt/flow-farm/bin/
scp -r ../server-frontend/dist/ user@server:/opt/flow-farm/static/
scp .env.production user@server:/opt/flow-farm/.env

# 3. 创建系统用户
sudo useradd --system --create-home --shell /bin/false flow-farm
sudo chown -R flow-farm:flow-farm /opt/flow-farm
sudo chmod +x /opt/flow-farm/bin/flow-farm-backend
```

### 第四步：创建 systemd 服务

```bash
sudo tee /etc/systemd/system/flow-farm.service << 'EOF'
[Unit]
Description=Flow Farm Web Server
Documentation=https://github.com/wyw121/Flow_Farm
After=network.target network-online.target
Requires=network-online.target

[Service]
Type=exec
User=flow-farm
Group=flow-farm
ExecStart=/opt/flow-farm/bin/flow-farm-backend
ExecReload=/bin/kill -HUP $MAINPID
WorkingDirectory=/opt/flow-farm
Environment=STATIC_DIR=/opt/flow-farm/static
EnvironmentFile=/opt/flow-farm/.env

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/flow-farm/data /opt/flow-farm/logs

# 重启策略
Restart=always
RestartSec=10
KillMode=mixed
KillSignal=SIGTERM

# 资源限制
LimitNOFILE=1048576
LimitNPROC=1048576

# 日志设置
StandardOutput=journal
StandardError=journal
SyslogIdentifier=flow-farm

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable flow-farm
sudo systemctl start flow-farm
```

### 第五步：配置防火墙

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8080/tcp  # Flow Farm
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

## ⚙️ 生产环境配置

### 完整的 .env 配置

```env
# 应用基本信息
APP_NAME="Flow Farm Production Server"
VERSION="1.0.0"
DEBUG=false

# 服务器配置
HOST=0.0.0.0
PORT=8080

# 数据库配置
DATABASE_URL=sqlite:/opt/flow-farm/data/flow_farm.db

# JWT配置 (必须更改!)
JWT_SECRET=your-super-secure-jwt-secret-key-min-32-chars-production
JWT_EXPIRES_IN=86400

# CORS配置 (指定具体域名)
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# 加密配置
BCRYPT_ROUNDS=12

# 静态文件配置
STATIC_DIR=/opt/flow-farm/static

# TLS配置 (可选)
ENABLE_TLS=false
# TLS_CERT_PATH=/opt/flow-farm/ssl/cert.pem
# TLS_KEY_PATH=/opt/flow-farm/ssl/key.pem

# 日志配置
RUST_LOG=info
RUST_BACKTRACE=1
```

## 📊 性能优化

### 系统级优化

```bash
# 优化文件描述符限制
echo "flow-farm soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "flow-farm hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# 优化内核参数
sudo tee -a /etc/sysctl.conf << 'EOF'
# 网络优化
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65535

# 内存优化
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
EOF

sudo sysctl -p
```

### 应用级优化

1. **并发连接数**: Rust默认已优化，无需额外配置
2. **内存使用**: 生产环境推荐4GB+ RAM
3. **磁盘I/O**: 使用SSD存储提升SQLite性能
4. **CPU**: 多核CPU自动利用Tokio异步优势

## 🔍 监控和运维

### 服务状态监控

```bash
# 检查服务状态
sudo systemctl status flow-farm

# 实时查看日志
sudo journalctl -u flow-farm -f

# 检查连接数
sudo netstat -tlnp | grep :8080

# 检查资源使用
sudo htop
```

### 性能监控脚本

```bash
#!/bin/bash
# /opt/flow-farm/scripts/monitor.sh

LOG_FILE="/opt/flow-farm/logs/performance.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# CPU使用率
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)

# 内存使用
MEM_USAGE=$(free | grep Mem | awk '{printf "%.2f", ($3/$2) * 100.0}')

# 磁盘使用
DISK_USAGE=$(df -h /opt/flow-farm | awk 'NR==2 {print $5}' | cut -d'%' -f1)

# 进程状态
PROCESS_STATUS=$(systemctl is-active flow-farm)

# 连接数
CONNECTIONS=$(ss -tln sport = :8080 | wc -l)

echo "$DATE,CPU:${CPU_USAGE}%,MEM:${MEM_USAGE}%,DISK:${DISK_USAGE}%,STATUS:$PROCESS_STATUS,CONN:$CONNECTIONS" >> $LOG_FILE

# 检查异常
if [[ "$PROCESS_STATUS" != "active" ]]; then
    echo "$DATE ERROR: Flow Farm service is not running!" >> $LOG_FILE
    # 发送告警 (可配置邮件或消息通知)
fi
```

### 日志轮转配置

```bash
sudo tee /etc/logrotate.d/flow-farm << 'EOF'
/opt/flow-farm/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    create 644 flow-farm flow-farm
    postrotate
        systemctl reload flow-farm > /dev/null 2>&1 || true
    endscript
}
EOF
```

## 🔄 更新部署流程

### 自动化更新脚本

```bash
#!/bin/bash
# /opt/flow-farm/scripts/update.sh

set -e

echo "开始更新 Flow Farm..."

# 1. 备份当前版本
sudo cp /opt/flow-farm/bin/flow-farm-backend /opt/flow-farm/bin/flow-farm-backend.bak.$(date +%Y%m%d)

# 2. 停止服务
sudo systemctl stop flow-farm

# 3. 更新二进制文件
sudo cp /tmp/flow-farm-backend /opt/flow-farm/bin/
sudo chown flow-farm:flow-farm /opt/flow-farm/bin/flow-farm-backend
sudo chmod +x /opt/flow-farm/bin/flow-farm-backend

# 4. 更新静态文件
sudo rm -rf /opt/flow-farm/static.bak
sudo mv /opt/flow-farm/static /opt/flow-farm/static.bak
sudo cp -r /tmp/dist /opt/flow-farm/static
sudo chown -R flow-farm:flow-farm /opt/flow-farm/static

# 5. 启动服务
sudo systemctl start flow-farm

# 6. 验证部署
sleep 5
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Flow Farm 更新成功！"
    sudo rm -f /opt/flow-farm/bin/flow-farm-backend.bak.*
else
    echo "❌ 更新失败，回滚到previous版本..."
    sudo systemctl stop flow-farm
    sudo mv /opt/flow-farm/bin/flow-farm-backend.bak.* /opt/flow-farm/bin/flow-farm-backend
    sudo systemctl start flow-farm
    exit 1
fi
```

## 🛡️ 安全最佳实践

### 1. 系统安全

```bash
# 定期系统更新
sudo apt update && sudo apt upgrade -y  # Ubuntu
sudo dnf update -y                      # CentOS

# SSH安全配置
sudo sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# 安装fail2ban防护
sudo apt install fail2ban -y
```

### 2. 应用安全

```bash
# 强制使用强JWT密钥
grep -q "your-super-secure" /opt/flow-farm/.env && echo "警告: 请修改JWT密钥!"

# 限制文件权限
sudo chmod 600 /opt/flow-farm/.env
sudo chmod 600 /opt/flow-farm/data/flow_farm.db
```

### 3. 网络安全

- 使用防火墙只开放必要端口
- 配置HTTPS (可使用Let's Encrypt)
- 设置合理的CORS策略
- 启用访问日志监控

## 📈 容量规划

### 硬件推荐

| 用户规模 | CPU | 内存 | 存储 | 网络 |
|---------|-----|------|------|------|
| 10-50人  | 2核 | 4GB  | 50GB | 100Mbps |
| 50-200人 | 4核 | 8GB  | 100GB| 1Gbps |
| 200-500人| 8核 | 16GB | 200GB| 1Gbps |
| 500+人   | 16核| 32GB | 500GB| 10Gbps |

### 数据库维护

```bash
# SQLite数据库优化
sqlite3 /opt/flow-farm/data/flow_farm.db "VACUUM;"
sqlite3 /opt/flow-farm/data/flow_farm.db "ANALYZE;"

# 定期备份脚本
#!/bin/bash
BACKUP_DIR="/opt/flow-farm/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
sqlite3 /opt/flow-farm/data/flow_farm.db ".backup $BACKUP_DIR/flow_farm_$DATE.db"
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
```

## 🎯 测试验证

### 部署后验证检查单

- [ ] 服务正常启动: `sudo systemctl status flow-farm`
- [ ] 端口正常监听: `sudo netstat -tlnp | grep :8080`
- [ ] 前端页面可访问: `curl -I http://localhost:8080/`
- [ ] API健康检查: `curl http://localhost:8080/health`
- [ ] API文档可访问: `curl -I http://localhost:8080/docs`
- [ ] 数据库连接正常: 检查日志无错误
- [ ] 静态文件正常服务: 检查CSS/JS加载
- [ ] 用户登录功能正常: 测试管理员登录
- [ ] SPA路由正常: 测试前端路由跳转

### 性能测试

```bash
# 安装测试工具
sudo apt install apache2-utils -y

# 并发测试
ab -n 1000 -c 10 http://localhost:8080/
ab -n 1000 -c 10 http://localhost:8080/health

# 静态文件测试
ab -n 1000 -c 10 http://localhost:8080/static/js/main.js
```

## ❗ 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   sudo journalctl -u flow-farm --no-pager -l
   ```

2. **静态文件404**
   - 检查 `STATIC_DIR` 配置是否正确
   - 确认前端已构建: `ls -la /opt/flow-farm/static/`

3. **数据库连接失败**
   ```bash
   ls -la /opt/flow-farm/data/
   sudo -u flow-farm sqlite3 /opt/flow-farm/data/flow_farm.db ".tables"
   ```

4. **端口占用**
   ```bash
   sudo lsof -i :8080
   sudo kill -9 [PID]
   ```

## 🎉 总结

使用Rust原生Web服务器的优势：

1. **🚀 极高性能**: 直接处理HTTP请求，无代理损耗
2. **🎛️ 简化架构**: 单一服务处理所有请求
3. **💰 降低成本**: 减少服务器资源占用
4. **🔧 易于运维**: 统一的日志和监控
5. **🛡️ 内存安全**: Rust的安全保证

这种架构特别适合中小型企业的生产环境，既保证了性能，又简化了部署和运维流程。
