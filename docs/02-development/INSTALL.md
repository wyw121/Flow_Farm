# Flow Farm 安装指南

## 系统要求

Flow Farm 是一个企业级三角色权限管理系统，包含：

- **服务器后端**: Rust + Axum + SQLx + SQLite
- **服务器前端**: React.js + TypeScript + Vite
- **员工客户端**: Python + tkinter + ADB

### 服务器端要求
- **Rust**: 1.75+
- **Node.js**: 18+
- **SQLite**: 3.0+

### 员工客户端要求
- **Python**: 3.8+ (推荐 Python 3.9-3.11)
- **Android SDK**: Platform Tools (ADB)

### 硬件要求
- CPU: 双核 2.0GHz 以上
- 内存: 4GB RAM 以上 (推荐 8GB)
- 存储: 2GB 可用空间
- USB 接口: 用于连接Android设备

## 安装步骤

### 1. 克隆项目
```bash
git clone https://github.com/wyw121/Flow_Farm.git
cd Flow_Farm
```

### 2. 创建虚拟环境（推荐）
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 安装ADB工具
#### Windows
1. 下载 [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools)
2. 解压到 `C:\adb\` 目录
3. 将 `C:\adb\` 添加到系统PATH环境变量

#### macOS
```bash
# 使用Homebrew
brew install android-platform-tools
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install android-tools-adb
```

### 5. 验证安装
```bash
cd src
python main.py --help
```

## 初次设置

### 1. 设备准备
1. 在Android设备上启用"开发者选项"
2. 启用"USB调试"
3. 连接设备到电脑
4. 授权USB调试权限

### 2. 验证设备连接
```bash
cd src
python main.py --console
# 在控制台中输入: devices
```

### 3. 启动应用
```bash
# GUI模式（默认）
python main.py

# 控制台模式
python main.py --console

# 调试模式
python main.py --debug
```

## 常见问题

### Q: ADB设备未找到
**A:** 检查以下项目：
1. 设备是否开启USB调试
2. USB线缆是否支持数据传输
3. 是否已授权调试权限
4. 尝试切换USB连接模式（文件传输、MTP等）

### Q: GUI界面无法启动
**A:** 可能原因：
1. 缺少tkinter库（部分Linux发行版需要单独安装）
2. 显示权限问题（远程连接时）
3. 使用控制台模式替代：`python main.py --console`

### Q: 权限被拒绝错误
**A:** 确保：
1. 以管理员权限运行（Windows）
2. 设备已正确授权USB调试
3. 检查防火墙设置

### Q: 模块导入错误
**A:** 解决方法：
1. 确保在src目录下运行
2. 检查虚拟环境是否激活
3. 重新安装依赖：`pip install -r requirements.txt`

## 性能优化

### 1. 多设备管理
- 推荐同时连接不超过10台设备
- 使用USB HUB时注意供电充足
- 定期重启设备管理器

### 2. 内存使用
- 长时间运行时定期重启应用
- 关闭不必要的后台程序
- 监控系统资源使用情况

### 3. 网络优化
- 使用稳定的网络连接
- 避免在高峰期执行大量操作
- 设置合理的请求间隔

## 更新维护

### 更新代码
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### 备份数据
重要文件：
- `config/app_config.json` - 应用配置
- `data/` - 用户数据
- `logs/` - 日志文件

### 清理缓存
```bash
# 清理日志文件
rm -rf logs/*

# 清理缓存目录
rm -rf cache/*
rm -rf temp/*
```

## 技术支持

如遇到问题：
1. 查看日志文件：`logs/app.log`
2. 开启调试模式：`python main.py --debug`
3. 提交Issue到GitHub仓库
4. 联系技术支持团队

---

更多详细信息请参阅：
- [用户指南](USER_GUIDE.md)
- [开发文档](DEVELOPER.md)
- [API文档](docs/api/)
- [FAQ常见问题](docs/FAQ.md)
