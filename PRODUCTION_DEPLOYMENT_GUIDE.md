# Flow Farm 生产环境部署指南

## 🎯 部署架构

### 推荐方案：Nginx + Rust后端 + React静态文件

```
Internet
    ↓
┌─────────────────────────────────────────────────────────┐
│                 Linux 服务器 (CentOS/Ubuntu)            │
│                                                         │
│  ┌─────────────────┐    ┌───────────────────────────┐  │
│  │      Nginx      │    │      Flow Farm 后端       │  │
│  │   (80/443)      │────│     (127.0.0.1:8000)     │  │
│  │   反向代理       │    │     Rust + Axum          │  │
│  │   SSL终结       │    │     systemd服务           │  │
│  └─────────────────┘    └───────────────────────────┘  │
│           │                        │                   │
│  ┌─────────────────┐    ┌───────────────────────────┐  │
│  │   静态文件目录   │    │      SQLite 数据库        │  │
│  │  /var/www/flow  │    │   /opt/flow-farm/data/    │  │
│  │  (React构建产物)│    │                           │  │
│  └─────────────────┘    └───────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 📋 环境要求

### 服务器配置
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **CPU**: 2核心以上
- **内存**: 4GB RAM 以上（推荐8GB）
- **存储**: 20GB 可用空间
- **网络**: 稳定的互联网连接

### 软件依赖
- Nginx 1.18+
- systemd (服务管理)
- 防火墙配置工具 (ufw/firewalld)

## 🚀 部署步骤

### 第一步：服务器环境准备

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx certbot python3-certbot-nginx ufw

# CentOS/RHEL
sudo dnf update -y
sudo dnf install -y nginx certbot python3-certbot-nginx firewalld

# 创建应用目录
sudo mkdir -p /opt/flow-farm/{bin,data,logs,config}
sudo mkdir -p /var/www/flow-farm
```

### 第二步：部署后端应用

```bash
# 1. 构建Rust应用（在开发机器上）
cd server-backend
cargo build --release

# 2. 上传到服务器
scp target/release/flow-farm-backend user@server:/opt/flow-farm/bin/
scp -r data/ user@server:/opt/flow-farm/
scp .env.production user@server:/opt/flow-farm/config/.env

# 3. 设置权限和所有者
sudo chown -R flow-farm:flow-farm /opt/flow-farm
sudo chmod +x /opt/flow-farm/bin/flow-farm-backend
```

### 第三步：创建systemd服务

```bash
sudo tee /etc/systemd/system/flow-farm.service << 'EOF'
[Unit]
Description=Flow Farm Backend Service
After=network.target
Wants=network.target

[Service]
Type=exec
User=flow-farm
Group=flow-farm
WorkingDirectory=/opt/flow-farm
EnvironmentFile=/opt/flow-farm/config/.env
ExecStart=/opt/flow-farm/bin/flow-farm-backend
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/flow-farm

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
sudo systemctl status flow-farm
```

### 第四步：部署前端静态文件

```bash
# 1. 构建前端（在开发机器上）
cd server-frontend
npm run build

# 2. 上传到服务器
scp -r dist/ user@server:/var/www/flow-farm/

# 3. 设置权限
sudo chown -R www-data:www-data /var/www/flow-farm
sudo chmod -R 644 /var/www/flow-farm
sudo find /var/www/flow-farm -type d -exec chmod 755 {} \;
```

### 第五步：配置Nginx

```bash
sudo tee /etc/nginx/sites-available/flow-farm << 'EOF'
# Flow Farm Nginx 配置
upstream flow_farm_backend {
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name flow-farm.yourdomain.com;  # 替换为您的域名

    # 重定向HTTP到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name flow-farm.yourdomain.com;  # 替换为您的域名

    # SSL配置 (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/flow-farm.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/flow-farm.yourdomain.com/privkey.pem;

    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # 静态文件根目录
    root /var/www/flow-farm;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/javascript;

    # 前端路由支持 (React Router)
    location / {
        try_files $uri $uri/ /index.html;
        expires 1h;
        add_header Cache-Control "public, no-transform";
    }

    # API 反向代理
    location /api {
        proxy_pass http://flow_farm_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;

        # WebSocket支持 (如果需要)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 健康检查
    location /health {
        proxy_pass http://flow_farm_backend;
        access_log off;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, no-transform, immutable";
    }

    # 日志配置
    access_log /var/log/nginx/flow-farm.access.log;
    error_log /var/log/nginx/flow-farm.error.log;
}
EOF

# 启用站点
sudo ln -sf /etc/nginx/sites-available/flow-farm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 第六步：SSL证书配置

```bash
# 使用 Let's Encrypt 获取免费SSL证书
sudo certbot --nginx -d flow-farm.yourdomain.com

# 自动续期设置
sudo crontab -e
# 添加以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 第七步：防火墙配置

```bash
# Ubuntu (ufw)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 🔧 生产环境配置

### 环境变量配置 (.env.production)

```bash
# 应用配置
APP_NAME="Flow Farm Production"
VERSION="1.0.0"
DEBUG=false

# 服务器配置
HOST=127.0.0.1
PORT=8000

# 数据库配置
DATABASE_URL=sqlite:/opt/flow-farm/data/flow_farm.db

# JWT配置 (请更改为强密码)
JWT_SECRET=your-super-secure-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 默认管理员 (首次启动后应立即修改)
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=ChangeThisPassword123!

# 日志配置
RUST_LOG=info
LOG_DIR=/opt/flow-farm/logs

# CORS配置
CORS_ORIGINS=https://flow-farm.yourdomain.com
```

### 数据库备份脚本

```bash
sudo tee /opt/flow-farm/scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/flow-farm/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="flow_farm_backup_${DATE}.db"

mkdir -p $BACKUP_DIR

# SQLite数据库备份
sqlite3 /opt/flow-farm/data/flow_farm.db ".backup $BACKUP_DIR/$BACKUP_FILE"

# 保留最近7天的备份
find $BACKUP_DIR -name "flow_farm_backup_*.db" -mtime +7 -delete

echo "数据库备份完成: $BACKUP_FILE"
EOF

chmod +x /opt/flow-farm/scripts/backup.sh

# 设置定期备份 (每天凌晨2点)
sudo crontab -e
# 添加：0 2 * * * /opt/flow-farm/scripts/backup.sh >> /opt/flow-farm/logs/backup.log 2>&1
```

## 📊 监控和运维

### 系统监控

```bash
# 查看服务状态
sudo systemctl status flow-farm
sudo systemctl status nginx

# 查看日志
sudo journalctl -u flow-farm -f
sudo tail -f /var/log/nginx/flow-farm.error.log
sudo tail -f /opt/flow-farm/logs/app.log

# 性能监控
htop
df -h
free -m
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
        systemctl reload flow-farm
    endscript
}
EOF
```

## 🔄 更新部署

### 应用更新流程

```bash
#!/bin/bash
# update_flow_farm.sh

echo "开始更新 Flow Farm..."

# 1. 备份当前版本
sudo cp /opt/flow-farm/bin/flow-farm-backend /opt/flow-farm/bin/flow-farm-backend.bak
sudo cp -r /var/www/flow-farm /var/www/flow-farm.bak

# 2. 停止服务
sudo systemctl stop flow-farm

# 3. 更新后端
scp target/release/flow-farm-backend user@server:/opt/flow-farm/bin/
sudo chown flow-farm:flow-farm /opt/flow-farm/bin/flow-farm-backend
sudo chmod +x /opt/flow-farm/bin/flow-farm-backend

# 4. 更新前端
scp -r dist/ user@server:/var/www/flow-farm/
sudo chown -R www-data:www-data /var/www/flow-farm

# 5. 启动服务
sudo systemctl start flow-farm
sudo systemctl reload nginx

# 6. 验证部署
sleep 5
curl -f http://localhost:8000/health && echo "后端健康检查通过"

echo "Flow Farm 更新完成！"
```

## 🎯 性能优化建议

### 1. 数据库优化
```sql
-- 创建索引优化查询性能
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_work_records_date ON work_records(created_at);
CREATE INDEX idx_work_records_employee ON work_records(employee_id);
```

### 2. Nginx 缓存优化
```nginx
# 在 http 块中添加
proxy_cache_path /var/cache/nginx/flow-farm levels=1:2 keys_zone=flow_farm:10m max_size=100m;

# 在 location /api 中添加
proxy_cache flow_farm;
proxy_cache_valid 200 5m;
proxy_cache_key "$scheme$request_method$host$request_uri";
```

### 3. 系统资源优化
```bash
# 优化文件描述符限制
echo "flow-farm soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "flow-farm hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# 优化内核参数
echo "net.core.somaxconn = 65535" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## ⚠️ 安全建议

1. **定期安全更新**
   ```bash
   sudo apt update && sudo apt upgrade -y  # Ubuntu
   sudo dnf update -y                       # CentOS
   ```

2. **防火墙配置**
   - 只开放必要端口 (80, 443, 22)
   - 配置SSH密钥登录
   - 禁用root远程登录

3. **应用安全**
   - 修改默认管理员密码
   - 使用强JWT密钥
   - 定期备份数据库
   - 监控异常访问日志

4. **SSL/TLS 配置**
   - 使用强加密套件
   - 启用HSTS
   - 定期更新证书

## 📞 故障排查

### 常见问题

1. **服务启动失败**
   ```bash
   sudo journalctl -u flow-farm --no-pager
   sudo systemctl status flow-farm
   ```

2. **数据库连接失败**
   ```bash
   ls -la /opt/flow-farm/data/
   sudo -u flow-farm sqlite3 /opt/flow-farm/data/flow_farm.db ".tables"
   ```

3. **Nginx 502 错误**
   ```bash
   sudo nginx -t
   curl http://localhost:8000/health
   sudo systemctl status flow-farm
   ```

4. **SSL 证书问题**
   ```bash
   sudo certbot certificates
   sudo certbot renew --dry-run
   ```

## 🎉 部署验证

部署完成后，请验证以下功能：

1. ✅ 访问 https://your-domain.com 显示登录页面
2. ✅ 使用默认管理员账号登录成功
3. ✅ API 健康检查：https://your-domain.com/api/health
4. ✅ 员工客户端能够正常连接服务器
5. ✅ SSL 证书正常工作
6. ✅ 日志正常写入

---

**🎯 推荐这种部署方案的原因：**
- ✨ **高性能**: Rust原生性能 + Nginx反向代理
- 🔒 **安全性**: SSL终结 + 防火墙 + 权限控制
- 🎛️ **可维护**: systemd服务管理 + 结构化日志
- 💰 **成本低**: 无需容器化，资源占用少
- 📈 **可扩展**: 支持负载均衡和横向扩展

这个方案特别适合中小企业的生产环境，既保证了性能和安全性，又降低了运维复杂度。
