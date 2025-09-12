# Flow Farm Docker 编译部署脚本
# 使用临时容器编译项目并准备部署文件

# 设置变量
$PROJECT_ROOT = "d:\repositories\Flow_Farm"
$CONTAINER_NAME = "flow-farm-build-temp"
$BUILD_IMAGE = "sha256:6d69d862027f4f5fcccad17a1b952782a4e92e15d99b5e054bfabd1c3f586531"

Write-Host "🚀 开始使用Docker临时容器编译Flow Farm项目..." -ForegroundColor Green

# 清理可能存在的临时容器
Write-Host "🧹 清理临时容器..." -ForegroundColor Yellow
docker rm -f $CONTAINER_NAME 2>$null

# 创建临时容器并挂载项目目录
Write-Host "📦 创建临时编译容器..." -ForegroundColor Yellow
docker run -d --name $CONTAINER_NAME `
    -v "${PROJECT_ROOT}:/workspace" `
    -w /workspace `
    $BUILD_IMAGE `
    tail -f /dev/null

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 创建容器失败!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 容器创建成功，开始编译..." -ForegroundColor Green

# 编译前端 (本地编译，因为Docker镜像是纯Rust环境)
Write-Host "🌐 编译前端 (React + TypeScript) - 本地编译..." -ForegroundColor Cyan
Push-Location "${PROJECT_ROOT}\server-frontend"
try {
    if (!(Test-Path "node_modules")) {
        Write-Host "📦 安装前端依赖..." -ForegroundColor Yellow
        npm install
        if ($LASTEXITCODE -ne 0) {
            throw "前端依赖安装失败"
        }
    }
    
    Write-Host "🔨 构建前端..." -ForegroundColor Yellow
    npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "前端构建失败"
    }
} catch {
    Write-Host "❌ 前端编译失败: $_" -ForegroundColor Red
    Pop-Location
    docker rm -f $CONTAINER_NAME
    exit 1
}
Pop-Location

# 编译后端
Write-Host "🦀 编译后端 (Rust)..." -ForegroundColor Cyan
docker exec $CONTAINER_NAME bash -c "cd /workspace/server-backend && cargo build --release"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 后端编译失败!" -ForegroundColor Red
    docker rm -f $CONTAINER_NAME
    exit 1
}

# 创建部署目录
$DEPLOY_DIR = "${PROJECT_ROOT}\deploy"
Write-Host "📁 创建部署目录: $DEPLOY_DIR" -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $DEPLOY_DIR | Out-Null
New-Item -ItemType Directory -Force -Path "$DEPLOY_DIR\static" | Out-Null
New-Item -ItemType Directory -Force -Path "$DEPLOY_DIR\data" | Out-Null
New-Item -ItemType Directory -Force -Path "$DEPLOY_DIR\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "$DEPLOY_DIR\uploads" | Out-Null

# 复制编译产物
Write-Host "📋 复制编译产物..." -ForegroundColor Cyan

# 复制后端二进制文件
Copy-Item "${PROJECT_ROOT}\server-backend\target\release\flow-farm-backend.exe" "$DEPLOY_DIR\flow-farm-backend" -Force
if (Test-Path "${PROJECT_ROOT}\server-backend\target\release\flow-farm-backend") {
    Copy-Item "${PROJECT_ROOT}\server-backend\target\release\flow-farm-backend" "$DEPLOY_DIR\flow-farm-backend" -Force
}

# 复制前端构建文件
if (Test-Path "${PROJECT_ROOT}\server-frontend\dist") {
    Copy-Item "${PROJECT_ROOT}\server-frontend\dist\*" "$DEPLOY_DIR\static\" -Recurse -Force
    Write-Host "✅ 前端文件已复制到: $DEPLOY_DIR\static\" -ForegroundColor Green
} else {
    Write-Host "❌ 前端构建目录不存在!" -ForegroundColor Red
}

# 复制配置文件
if (Test-Path "${PROJECT_ROOT}\server-backend\data\flow_farm.db") {
    Copy-Item "${PROJECT_ROOT}\server-backend\data\flow_farm.db" "$DEPLOY_DIR\data\" -Force
    Write-Host "✅ 数据库文件已复制" -ForegroundColor Green
}

# 创建启动脚本
$START_SCRIPT = @"
#!/bin/bash
# Flow Farm 启动脚本

export RUST_LOG=info
export DATABASE_URL=sqlite:data/flow_farm.db
export STATIC_DIR=static
export PORT=8080

echo "🚀 启动 Flow Farm 服务器..."
echo "📁 静态文件目录: `$STATIC_DIR"
echo "🗄️ 数据库: `$DATABASE_URL"
echo "🌐 监听端口: `$PORT"

./flow-farm-backend
"@

$START_SCRIPT | Out-File -FilePath "$DEPLOY_DIR\start.sh" -Encoding UTF8
$START_SCRIPT | Out-File -FilePath "$DEPLOY_DIR\start.bat" -Encoding UTF8

# 创建系统服务文件
$SERVICE_FILE = @"
[Unit]
Description=Flow Farm Backend Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/flow-farm
ExecStart=/opt/flow-farm/flow-farm-backend
Restart=always
RestartSec=5
Environment=RUST_LOG=info
Environment=DATABASE_URL=sqlite:data/flow_farm.db
Environment=STATIC_DIR=static
Environment=PORT=8080

[Install]
WantedBy=multi-user.target
"@

$SERVICE_FILE | Out-File -FilePath "$DEPLOY_DIR\flow-farm.service" -Encoding UTF8

# 创建部署说明
$DEPLOY_README = @"
# Flow Farm 部署包

## 📁 目录结构
```
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
```

## 🚀 Ubuntu 服务器部署步骤

### 1. 上传文件
```bash
# 将整个 deploy 目录上传到服务器
scp -r deploy/ user@your-server:/tmp/flow-farm-deploy
```

### 2. 安装到系统目录
```bash
# 登录服务器
ssh user@your-server

# 移动到系统目录
sudo mv /tmp/flow-farm-deploy /opt/flow-farm
sudo chown -R www-data:www-data /opt/flow-farm
sudo chmod +x /opt/flow-farm/flow-farm-backend
sudo chmod +x /opt/flow-farm/start.sh
```

### 3. 安装系统服务
```bash
# 复制服务文件
sudo cp /opt/flow-farm/flow-farm.service /etc/systemd/system/

# 重载 systemd 并启动服务
sudo systemctl daemon-reload
sudo systemctl enable flow-farm
sudo systemctl start flow-farm
```

### 4. 检查服务状态
```bash
# 查看服务状态
sudo systemctl status flow-farm

# 查看日志
sudo journalctl -u flow-farm -f

# 测试访问
curl http://localhost:8080
curl http://localhost:8080/api/health
```

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
```bash
sudo netstat -tlnp | grep :8080
sudo systemctl stop flow-farm
```

### 权限问题
```bash
sudo chown -R www-data:www-data /opt/flow-farm
sudo chmod +x /opt/flow-farm/flow-farm-backend
```

### 数据库问题
```bash
# 检查数据库文件权限
ls -la /opt/flow-farm/data/flow_farm.db
sudo chown www-data:www-data /opt/flow-farm/data/flow_farm.db
```
"@

$DEPLOY_README | Out-File -FilePath "$DEPLOY_DIR\README.md" -Encoding UTF8

# 清理临时容器
Write-Host "🧹 清理临时容器..." -ForegroundColor Yellow
docker rm -f $CONTAINER_NAME

# 创建部署压缩包
Write-Host "📦 创建部署压缩包..." -ForegroundColor Cyan
$TIMESTAMP = Get-Date -Format "yyyyMMdd-HHmmss"
$ZIP_NAME = "flow-farm-deploy-$TIMESTAMP.zip"

if (Get-Command Compress-Archive -ErrorAction SilentlyContinue) {
    Compress-Archive -Path "$DEPLOY_DIR\*" -DestinationPath "${PROJECT_ROOT}\$ZIP_NAME" -Force
    Write-Host "✅ 部署包已创建: $ZIP_NAME" -ForegroundColor Green
}

Write-Host "" -ForegroundColor White
Write-Host "🎉 编译完成！部署文件位置:" -ForegroundColor Green
Write-Host "📁 部署目录: $DEPLOY_DIR" -ForegroundColor Cyan
Write-Host "🗜️ 部署压缩包: ${PROJECT_ROOT}\$ZIP_NAME" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White
Write-Host "🚀 部署组件说明:" -ForegroundColor Yellow
Write-Host "  🦀 后端: $DEPLOY_DIR\flow-farm-backend" -ForegroundColor Cyan
Write-Host "  🌐 前端: $DEPLOY_DIR\static\" -ForegroundColor Cyan
Write-Host "  🗄️ 数据库: $DEPLOY_DIR\data\flow_farm.db" -ForegroundColor Cyan
Write-Host "  📋 部署说明: $DEPLOY_DIR\README.md" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White
Write-Host "💡 接下来:" -ForegroundColor Yellow
Write-Host "  1. 上传 $ZIP_NAME 到 Ubuntu 服务器" -ForegroundColor White
Write-Host "  2. 解压并按照 README.md 中的步骤部署" -ForegroundColor White
Write-Host "  3. 访问 http://your-server:8080 查看效果" -ForegroundColor White
