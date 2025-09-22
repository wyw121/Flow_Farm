# Flow Farm 开发和部署指南

## 🏗️ 架构说明

### 两种运行模式

#### 1. 开发模式（双端口）
- **前端**: localhost:3000 (热重载开发)
- **后端**: localhost:8000 (API服务)
- **数据库**: 本地SQLite `data/flow_farm_dev.db`
- **用途**: 日常开发、调试、新功能开发

#### 2. 生产模式（单端口）
- **服务**: 8080端口 (API + 静态文件)
- **数据库**: 生产SQLite `data/flow_farm_production.db`
- **用途**: 服务器部署、生产环境

## 🚀 快速开始

### 本地开发环境

```bash
# Windows
dev-start.bat

# Linux/Mac
chmod +x dev-start.sh
./dev-start.sh
```

**访问地址:**
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 手动启动开发环境

```bash
# 1. 启动后端 (终端1)
cd server-backend
cp .env.local .env
cargo run

# 2. 启动前端 (终端2)
cd server-frontend  
cp .env.local .env
npm run dev
```

## 📦 生产环境构建

### 自动构建

```bash
# Windows
build-production.bat

# Linux/Mac
chmod +x build-production.sh
./build-production.sh
```

### 手动构建

```bash
# 1. 构建前端
cd server-frontend
cp .env.production .env
npm run build

# 2. 构建后端
cd ../server-backend
cp .env.production .env
cp -r ../server-frontend/dist/* static/
cargo build --release
```

## 🗄️ 数据库管理

### 数据库文件位置
- **开发**: `server-backend/data/flow_farm_dev.db`
- **测试**: `server-backend/data/flow_farm_test.db`  
- **生产**: `server-backend/data/flow_farm_production.db`

### 重置开发数据库
```bash
cd server-backend
rm data/flow_farm_dev.db
cargo run  # 会自动创建并初始化
```

### 查看数据库内容
```bash
cd server-backend/data
sqlite3 flow_farm_dev.db
.tables
SELECT * FROM users;
.quit
```

## ⚙️ 环境配置

### 环境变量文件
- `.env.local` - 本地开发
- `.env.test` - 测试环境
- `.env.production` - 生产环境

### 关键配置项
- `DATABASE_URL` - 数据库连接字符串
- `HOST/PORT` - 服务器监听地址
- `JWT_SECRET` - JWT签名密钥
- `ALLOWED_ORIGINS` - CORS允许的源

## 🚢 部署到服务器

### 1. 构建部署包
```bash
./build-production.sh
# 生成: flow-farm-deploy-YYYYMMDD-HHMMSS.tar.gz
```

### 2. 上传到服务器
```bash
scp flow-farm-deploy-*.tar.gz user@server:/opt/
```

### 3. 服务器部署
```bash
ssh user@server
cd /opt
tar -xzf flow-farm-deploy-*.tar.gz
cd flow-farm-deploy-*
./start.sh
```

### 4. 配置系统服务 (可选)
```bash
# 创建systemd服务文件
sudo tee /etc/systemd/system/flow-farm.service << EOF
[Unit]
Description=Flow Farm Server
After=network.target

[Service]
Type=simple
User=flowfarm
WorkingDirectory=/opt/flow-farm-deploy
ExecStart=/opt/flow-farm-deploy/flow-farm-backend
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable flow-farm
sudo systemctl start flow-farm
```

## 🔧 故障排查

### 常见问题

1. **前端连接不到后端**
   - 检查 `.env` 文件中的 `VITE_API_BASE_URL`
   - 确认后端服务已启动

2. **数据库连接失败**
   - 检查 `DATABASE_URL` 配置
   - 确认数据库文件权限

3. **CORS错误**
   - 检查后端 `ALLOWED_ORIGINS` 配置
   - 确认前端域名在允许列表中

4. **JWT认证失败**
   - 检查 `JWT_SECRET` 配置
   - 清除浏览器localStorage中的token

### 日志查看
```bash
# 开发环境 - 控制台输出
cargo run

# 生产环境 - 后台运行
nohup ./flow-farm-backend > flow-farm.log 2>&1 &
tail -f flow-farm.log
```

## 📝 最佳实践

### 开发流程
1. 使用 `dev-start.bat` 启动开发环境
2. 修改代码后自动热重载
3. 测试完成后使用测试环境验证
4. 构建生产版本进行部署

### 数据安全
- 开发环境使用独立数据库
- 定期备份生产数据库
- 不要在开发时连接生产数据库

### 环境隔离
- 开发、测试、生产使用不同配置
- 敏感信息通过环境变量管理
- 生产环境使用强密码和HTTPS