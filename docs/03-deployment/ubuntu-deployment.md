# Flow Farm Ubuntu Deployment Guide

## Docker临时容器编译方案 (最节省空间)

### 特点
- ✅ **零存储占用**: 使用`--rm`自动删除容器，不留任何Docker镜像缓存
- ✅ **一键编译**: 自动处理所有依赖和编译过程
- ✅ **跨平台**: Windows上编译Ubuntu二进制文件
- ✅ **生产就绪**: Release版本优化，性能最佳

### 使用方法

#### 方式1: 批处理脚本 (推荐)
```bash
cd d:\repositories\Flow_Farm\server-backend
compile-ubuntu.bat
```

#### 方式2: PowerShell脚本
```powershell
cd d:\repositories\Flow_Farm\server-backend
.\compile-ubuntu.ps1
```

#### 方式3: 手动Docker命令
```bash
cd d:\repositories\Flow_Farm\server-backend
docker run --rm -v "%CD%:/workspace" -w /workspace rust:1.75-slim bash -c "
    apt-get update -qq &&
    apt-get install -y -qq pkg-config libssl-dev &&
    cargo build --release
"
```

### 编译输出

编译完成后，您将得到：
- **二进制文件**: `target/release/flow-farm-backend`
- **文件大小**: 约10-20MB (优化后的Release版本)
- **目标平台**: Ubuntu Linux x86_64

### 部署到Ubuntu服务器

#### 1. 复制文件
```bash
# 使用SCP复制到服务器
scp target/release/flow-farm-backend user@your-server:/opt/flow-farm/
scp .env.production user@your-server:/opt/flow-farm/.env
```

#### 2. 服务器配置
```bash
# 在Ubuntu服务器上
cd /opt/flow-farm
chmod +x flow-farm-backend

# 创建系统服务 (可选)
sudo nano /etc/systemd/system/flow-farm.service
```

#### 3. systemd服务配置示例
```ini
[Unit]
Description=Flow Farm Backend Service
After=network.target

[Service]
Type=simple
User=flowfarm
WorkingDirectory=/opt/flow-farm
ExecStart=/opt/flow-farm/flow-farm-backend
Restart=always
RestartSec=10
Environment=RUST_LOG=info

[Install]
WantedBy=multi-user.target
```

#### 4. 启动服务
```bash
sudo systemctl daemon-reload
sudo systemctl enable flow-farm
sudo systemctl start flow-farm
sudo systemctl status flow-farm
```

### 配置文件要求

确保Ubuntu服务器上有正确的`.env`配置：

```env
# 数据库配置
DATABASE_URL=sqlite:data/flow_farm.db
DATABASE_PATH=data/flow_farm.db

# 服务器配置
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info

# 静态文件服务
STATIC_DIR=static
FRONTEND_BUILD_PATH=static

# JWT配置
JWT_SECRET=your-super-secret-jwt-key-here
JWT_EXPIRES_IN=24h

# 加密密钥
ENCRYPTION_KEY=your-32-char-encryption-key-here

# CORS配置
ALLOWED_ORIGINS=http://localhost:3000,http://your-domain.com
```

### 空间占用对比

| 方案 | Docker镜像占用 | 编译缓存 | 总空间占用 |
|------|---------------|----------|-----------|
| 临时容器 (推荐) | 0 MB | 0 MB | ~20 MB (仅二进制) |
| 持久化容器 | ~1.2 GB | ~500 MB | ~1.7 GB |
| 本地交叉编译 | 0 MB | ~800 MB | ~800 MB |

### 故障排除

#### 编译失败
1. 检查Docker是否运行: `docker --version`
2. 检查网络连接 (下载Rust镜像需要网络)
3. 检查磁盘空间是否足够

#### 运行时错误
1. 确保`.env`文件存在
2. 检查数据库文件权限
3. 确保端口8000未被占用
4. 查看系统日志: `sudo journalctl -u flow-farm -f`

### 性能优化建议

1. **使用反向代理**: 配置Nginx或Caddy作为反向代理
2. **启用HTTPS**: 使用Let's Encrypt证书
3. **数据库优化**: 考虑迁移到PostgreSQL (生产环境)
4. **监控**: 使用systemd或专业监控工具

### 自动化部署脚本

可以结合CI/CD创建自动化部署：
```yaml
# .github/workflows/deploy.yml
name: Deploy to Ubuntu
on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build with Docker
        run: |
          docker run --rm -v $PWD:/workspace -w /workspace rust:1.75-slim \
            bash -c "apt-get update && apt-get install -y pkg-config libssl-dev && cargo build --release"
      - name: Deploy to server
        run: |
          scp target/release/flow-farm-backend ${{ secrets.SERVER_USER }}@${{ secrets.SERVER_HOST }}:/opt/flow-farm/
          ssh ${{ secrets.SERVER_USER }}@${{ secrets.SERVER_HOST }} "sudo systemctl restart flow-farm"
```
