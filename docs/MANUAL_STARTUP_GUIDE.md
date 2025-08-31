# Flow Farm 手动启动指南

## 📋 概述

本文档提供了在不使用任何自动化脚本的情况下，手动启动 Flow Farm 系统各个组件的详细步骤。

## 🏗️ 系统架构

Flow Farm 系统包含三个主要组件：
- **服务器后端** (FastAPI) - 端口 8000
- **服务器前端** (React + Vite) - 端口 3000
- **员工客户端** (Python GUI) - 桌面应用

## ⚡ 快速启动命令（最关键）

### 1. 服务器后端启动
```powershell
# 进入后端目录
cd d:\repositories\Flow_Farm\server-backend

# 创建虚拟环境（仅首次需要）
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖（仅首次需要）
pip install -r requirements.txt

# 启动后端服务
python -m uvicorn app.main:app --reload --port 8000
```

### 2. 服务器前端启动
```powershell
# 进入前端目录
cd d:\repositories\Flow_Farm\server-frontend

# 安装依赖（仅首次需要）
npm install

# 启动前端开发服务器
npm run dev
```

### 3. 员工客户端启动
```powershell
# 进入客户端目录
cd d:\repositories\Flow_Farm\employee-client

# 创建虚拟环境（仅首次需要）
python -m venv venv

# 切换到员工客户端目录
cd employee-client

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖（仅首次需要）
pip install -r requirements.txt

# 启动GUI客户端
python src/main.py --mode gui --debug
```

## 📝 详细步骤说明

### 🎯 预准备要求

1. **Python 3.8+** 已安装
2. **Node.js 18+** 已安装
3. **Git** 已安装
4. **PowerShell 5.1+** (Windows)

### 🔧 首次环境配置

#### 步骤 1: 克隆仓库（如果还没有）
```powershell
git clone https://github.com/wyw121/Flow_Farm.git
cd Flow_Farm
```

#### 步骤 2: 验证系统要求
```powershell
# 检查Python版本
python --version  # 应该 >= 3.8

# 检查Node.js版本
node --version     # 应该 >= 18.0

# 检查npm版本
npm --version      # 应该 >= 8.0
```

## 🚀 服务器后端详细启动

### 环境准备
```powershell
# 1. 进入后端目录
cd d:\repositories\Flow_Farm\server-backend

# 2. 创建Python虚拟环境（仅首次）
python -m venv venv

# 3. 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 验证虚拟环境已激活（命令提示符前应有 (venv)）
where python  # 应该指向 venv\Scripts\python.exe
```

### 安装依赖
```powershell
# 4. 升级pip
python -m pip install --upgrade pip

# 5. 安装后端依赖
pip install -r requirements.txt

# 6. 验证关键包安装
pip show fastapi uvicorn sqlalchemy
```

### 数据库初始化
```powershell
# 7. 初始化数据库（仅首次或数据库结构变更时）
python -c "from app.init_db import create_tables; create_tables()"

# 8. 创建测试用户（可选）
python scripts/create_test_users.py
```

### 启动服务
```powershell
# 9. 启动FastAPI服务器
python -m uvicorn app.main:app --reload --port 8000

# 或者指定更多参数
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info
```

### 验证启动
- 浏览器访问: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 🌐 服务器前端详细启动

### 环境准备
```powershell
# 1. 进入前端目录
cd d:\repositories\Flow_Farm\server-frontend

# 2. 验证Node.js环境
node --version
npm --version
```

### 安装依赖
```powershell
# 3. 清理可能的缓存（如果有问题）
npm cache clean --force

# 4. 安装项目依赖
npm install

# 5. 验证安装
npm list --depth=0
```

### 启动开发服务器
```powershell
# 6. 启动开发服务器
npm run dev

# 或者指定端口
npm run dev -- --port 3000 --host 0.0.0.0
```

### 验证启动
- 浏览器访问: http://localhost:3000
- 控制台应显示: "Local: http://localhost:3000"

## 💻 员工客户端详细启动

### 环境准备
```powershell
# 1. 进入客户端目录
cd d:\repositories\Flow_Farm\employee-client

# 2. 创建虚拟环境（仅首次）
python -m venv venv

# 3. 激活虚拟环境
.\venv\Scripts\Activate.ps1
```

### 安装依赖
```powershell
# 4. 升级pip
python -m pip install --upgrade pip

# 5. 安装客户端依赖
pip install -r requirements.txt

# 6. 验证关键组件
python -c "import tkinter; print('✅ tkinter可用')"
python -c "import requests; print('✅ requests可用')"
```

### ADB环境配置（如果需要设备自动化）
```powershell
# 7. 检查ADB是否可用
adb version

# 如果ADB不可用，需要安装Android SDK Platform Tools
# 下载地址: https://developer.android.com/studio/releases/platform-tools
```

### 启动应用
```powershell
# 8. 启动GUI模式
python src/main.py --mode gui --debug

# 或者启动控制台模式
python src/main.py --mode console --debug

# 或者不带调试模式
python src/main.py --mode gui
```

## 🔍 故障排除

### 常见错误及解决方案

#### 1. 后端启动失败
```powershell
# 错误：ModuleNotFoundError
# 解决：确保在虚拟环境中且已安装依赖
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 错误：端口被占用
# 解决：查找并关闭占用端口的进程
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F

# 或者使用不同端口
python -m uvicorn app.main:app --reload --port 8001
```

#### 2. 前端启动失败
```powershell
# 错误：npm ERR!
# 解决：清理缓存重新安装
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# 错误：端口被占用
# 解决：使用不同端口
npm run dev -- --port 3001
```

#### 3. 客户端启动失败
```powershell
# 错误：tkinter not found
# 解决：重新安装Python或使用完整版Python

# 错误：ADB相关错误
# 解决：确保ADB在PATH中或配置ADB路径
where adb
```

## 🎯 启动顺序建议

推荐按以下顺序启动：

1. **首先启动后端** (端口 8000)
2. **然后启动前端** (端口 3000)
3. **最后启动客户端** (连接到后端API)

## 📊 状态验证

### 服务状态检查
```powershell
# 检查后端状态
curl http://localhost:8000/health

# 检查前端状态
curl http://localhost:3000

# 检查端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :3000
```

### 日志查看
- 后端日志：控制台输出 + `logs/app.log`
- 前端日志：浏览器控制台
- 客户端日志：应用内日志窗口 + `logs/client.log`

## 🔧 开发模式配置

### 后端开发配置
```powershell
# 启用热重载和调试模式
python -m uvicorn app.main:app --reload --debug --log-level debug
```

### 前端开发配置
```powershell
# 启用热重载和详细日志
npm run dev -- --debug --verbose
```

## 📱 生产模式启动

### 后端生产模式
```powershell
# 不使用热重载，优化性能
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 前端生产构建
```powershell
# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## ⚠️ 重要注意事项

1. **虚拟环境**: 始终在虚拟环境中工作，避免依赖冲突
2. **端口冲突**: 确保8000和3000端口未被占用
3. **防火墙**: 可能需要允许应用访问网络
4. **权限**: 某些操作可能需要管理员权限
5. **Python路径**: 确保使用正确的Python版本和解释器

## 🆘 获取帮助

如果遇到问题，可以：
1. 查看应用日志文件
2. 检查网络连接状态
3. 验证依赖版本兼容性
4. 参考项目文档：`docs/` 目录

---

**最后更新**: 2025年8月30日
**适用版本**: Flow Farm v1.0
