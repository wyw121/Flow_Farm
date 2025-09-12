# Flow Farm 快速部署指南

## 🎯 部署概览

您的项目已成功编译完成！使用静态前端 + Rust后端架构部署到Ubuntu服务器。

## 📦 编译产物位置

### 前端 (React 静态文件)
```
📁 位置: d:\repositories\Flow_Farm\deploy\static\
├── index.html          # 主页面
├── assets/             # JS/CSS/图片等资源
│   ├── index-Ctu2fTbY.js    # React应用 (1.4MB, gzipped: 442KB)
│   └── index-DjIuuV94.css   # 样式文件 (5.8KB, gzipped: 2.1KB)
└── vite.svg           # 图标
```

### 后端 (Rust 可执行文件)
```
📁 位置: d:\repositories\Flow_Farm\deploy\flow-farm-backend
📏 大小: 10.1MB (Release优化构建)
🎯 功能: 
  - Web服务器 (端口8080)
  - 静态文件服务
  - REST API接口
  - SQLite数据库操作
```

### 数据库
```
📁 位置: d:\repositories\Flow_Farm\deploy\data\flow_farm.db
🗄️ 类型: SQLite数据库
```

## 🚀 Ubuntu部署步骤

### 方式一：自动部署 (推荐)

1. **上传部署包到服务器**
   ```bash
   scp flow-farm-deploy-final.zip user@your-server:~/
   ```

2. **登录服务器并解压**
   ```bash
   ssh user@your-server
   unzip flow-farm-deploy-final.zip
   cd deploy
   ```

3. **运行自动部署脚本**
   ```bash
   chmod +x ubuntu-deploy.sh
   ./ubuntu-deploy.sh ../flow-farm-deploy-final.zip
   ```

### 方式二：手动部署

1. **解压并安装**
   ```bash
   sudo mv deploy /opt/flow-farm
   sudo chown -R www-data:www-data /opt/flow-farm
   sudo chmod +x /opt/flow-farm/flow-farm-backend
   ```

2. **安装系统服务**
   ```bash
   sudo cp /opt/flow-farm/flow-farm.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable flow-farm
   sudo systemctl start flow-farm
   ```

## 🌐 访问验证

部署完成后，访问以下地址验证：

- **前端界面**: `http://your-server-ip:8080`
- **API健康检查**: `http://your-server-ip:8080/api/health`
- **静态资源**: `http://your-server-ip:8080/assets/`

## 🔧 服务管理

```bash
# 查看服务状态
sudo systemctl status flow-farm

# 重启服务
sudo systemctl restart flow-farm

# 查看日志
sudo journalctl -u flow-farm -f

# 停止服务
sudo systemctl stop flow-farm
```

## 📋 服务配置

### 环境变量
- `RUST_LOG=info` - 日志级别
- `DATABASE_URL=sqlite:data/flow_farm.db` - 数据库连接
- `STATIC_DIR=static` - 静态文件目录
- `PORT=8080` - 监听端口

### 目录结构
```
/opt/flow-farm/
├── flow-farm-backend      # Rust后端可执行文件
├── static/               # React前端静态文件
├── data/                 # SQLite数据库
├── logs/                 # 应用日志
├── uploads/              # 文件上传目录
└── flow-farm.service     # systemd服务配置
```

## 🛠️ 故障排除

### 1. 端口冲突
```bash
# 检查端口占用
sudo netstat -tlnp | grep :8080
# 如果有冲突，停止占用进程或修改配置
```

### 2. 权限问题
```bash
# 修复文件权限
sudo chown -R www-data:www-data /opt/flow-farm
sudo chmod +x /opt/flow-farm/flow-farm-backend
```

### 3. 数据库问题
```bash
# 检查数据库文件
ls -la /opt/flow-farm/data/
# 修复数据库权限
sudo chown www-data:www-data /opt/flow-farm/data/flow_farm.db
```

### 4. 查看详细日志
```bash
# 系统日志
sudo journalctl -u flow-farm --no-pager -n 50

# 应用日志
sudo tail -f /opt/flow-farm/logs/*.log
```

## 📈 性能优化

### 前端优化
- ✅ Gzip压缩启用
- ✅ 静态资源缓存 (1年)
- ✅ 代码分割和压缩
- ✅ 构建优化 (Vite)

### 后端优化
- ✅ Release构建 (优化编译)
- ✅ 异步I/O (Tokio)
- ✅ 连接池 (SQLx)
- ✅ 内存安全 (Rust)

## 🔐 安全注意事项

1. **防火墙配置**
   ```bash
   sudo ufw allow 8080/tcp
   ```

2. **SSL证书** (生产环境推荐)
   - 使用Nginx反向代理
   - 或集成Let's Encrypt

3. **数据库备份**
   ```bash
   # 定期备份数据库
   cp /opt/flow-farm/data/flow_farm.db /backup/flow_farm_$(date +%Y%m%d).db
   ```

## 🎉 部署完成

恭喜！您的Flow Farm项目已成功部署到Ubuntu服务器。

- 🌐 前端: React静态文件，由Rust后端直接服务
- 🦀 后端: 高性能Rust Web服务器
- 🗄️ 数据库: SQLite，轻量级且高效
- 🔧 架构: 单一二进制文件，简化运维

项目将在端口8080提供完整的Web服务，包括前端界面和API接口。
