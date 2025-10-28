# Flow Farm 部署包

## 📁 目录结构
`
deploy/
├── flow-farm-backend      # 后端可执行文件
├── static/               # 前端静态文件 (React 构建产物)
│   ├── index.html       # 主页面
│   ├── assets/          # JS/CSS 等资源文件
│   └── ...
├── data/                # 数据目录
│   └── flow_farm.db     # SQLite 数据库
├── logs/                # 日志目录
├── uploads/             # 上传文件目录
├── start.sh             # Linux 启动脚本
├── start.bat            # Windows 启动脚本
└── flow-farm.service    # systemd 服务文件
`

## 🚀 Ubuntu 服务器部署步骤

### 1. 上传文件
`ash
# 将整个 deploy 目录上传到服务器
scp -r deploy/ user@your-server:/tmp/flow-farm-deploy
`

### 2. 安装到系统目录
`ash
# 登录服务器
ssh user@your-server

# 移动到系统目录
sudo mv /tmp/flow-farm-deploy /opt/flow-farm
sudo chown -R www-data:www-data /opt/flow-farm
sudo chmod +x /opt/flow-farm/flow-farm-backend
sudo chmod +x /opt/flow-farm/start.sh
`

### 3. 安装系统服务
`ash
# 复制服务文件
sudo cp /opt/flow-farm/flow-farm.service /etc/systemd/system/

# 重载 systemd 并启动服务
sudo systemctl daemon-reload
sudo systemctl enable flow-farm
sudo systemctl start flow-farm
`

### 4. 检查服务状态
`ash
# 查看服务状态
sudo systemctl status flow-farm

# 查看日志
sudo journalctl -u flow-farm -f

# 测试访问
curl http://localhost:8080
curl http://localhost:8080/api/health
`

## 🌐 访问地址

- **前端界面**: http://your-server:8080
- **API 接口**: http://your-server:8080/api/*
- **健康检查**: http://your-server:8080/api/health

## 🔧 配置说明

服务器会自动：
- 在 8080 端口提供 Web 服务
- 服务前端静态文件 (React SPA)
- 提供 API 接口
- 使用 SQLite 数据库存储数据
- 记录日志到 logs/ 目录

## 🛠️ 故障排除

### 端口被占用
`ash
sudo netstat -tlnp | grep :8080
sudo systemctl stop flow-farm
`

### 权限问题
`ash
sudo chown -R www-data:www-data /opt/flow-farm
sudo chmod +x /opt/flow-farm/flow-farm-backend
`

### 数据库问题
`ash
# 检查数据库文件权限
ls -la /opt/flow-farm/data/flow_farm.db
sudo chown www-data:www-data /opt/flow-farm/data/flow_farm.db
`
