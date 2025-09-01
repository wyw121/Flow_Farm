# Flow Farm 小红书自动化客户端

🚀 **完整的小红书自动化关注系统，集成设备管理、通讯录管理和智能任务分发功能**

## 📋 功能特性

### 🔥 核心功能
- ✅ **多设备管理** - 支持同时管理多个Android设备/模拟器
- ✅ **智能设备检测** - 自动发现设备，获取详细信息
- ✅ **通讯录管理** - 支持JSON/CSV格式的联系人导入导出
- ✅ **任务智能分发** - 自动将关注任务分配给可用设备
- ✅ **自动化关注** - 集成小红书自动化逻辑，安全稳定
- ✅ **实时监控** - 设备状态监控，任务执行统计
- ✅ **错误处理** - 完善的错误处理和重试机制

### 🛠️ 技术架构
- **设备管理层** - ADB命令封装，设备状态管理
- **UI分析层** - XML解析，页面类型识别，元素定位
- **通讯录层** - 数据结构化存储，状态跟踪
- **自动化层** - 关注流程，安全策略，结果验证
- **任务调度层** - 多设备协调，负载均衡

## 🚀 快速开始

### 1. 环境准备

```bash
# 确保Python 3.8+已安装
python --version

# 安装依赖（如需要）
pip install -r requirements.txt
```

### 2. 设备准备

**Android设备/模拟器:**
- ✅ 启用USB调试
- ✅ 安装小红书APP
- ✅ ADB驱动正常

**雷电模拟器（推荐）:**
```bash
# ADB路径
D:\leidian\LDPlayer9\adb.exe

# 启动模拟器后检查连接
adb devices
```

### 3. 系统测试

```bash
# 运行快速测试
cd src
python quick_test.py
```

预期输出：
```
🔥 Flow Farm 快速测试
====================================================
🧪 测试设备管理器
发现设备: ['emulator-5554', 'emulator-5556']
使用设备: emulator-5554
设备信息: DeviceInfo(device_id='emulator-5554', ...)
截图成功: test_screenshot.png
UI dump成功，长度: 36
解析到 148 个UI元素

🧪 测试通讯录管理器
创建示例数据...
统计信息: {'total_contacts': 5, 'pending_count': 5, ...}

🧪 测试任务分配
任务分配结果:
  设备 emulator-5554: 5 个联系人
  设备 emulator-5556: 5 个联系人

🎉 所有测试完成!
💡 系统就绪:
  - 检测到 2 个设备
  - 通讯录管理正常
  - 任务分配正常
```

## 📇 通讯录格式

### JSON格式（推荐）

```json
{
  "metadata": {
    "version": "1.0",
    "description": "我的小红书通讯录",
    "created_time": "2024-01-01T00:00:00"
  },
  "contacts": [
    {
      "id": "contact_001",
      "platform": "xiaohongshu",
      "username": "美妆达人小王",
      "user_id": "xiaohongshu_user_001",
      "category": "美妆",
      "priority": 1,
      "notes": "专业美妆博主，内容优质",
      "tags": ["美妆", "护肤", "推荐"]
    },
    {
      "id": "contact_002",
      "platform": "xiaohongshu",
      "username": "旅行摄影师",
      "user_id": "xiaohongshu_user_002",
      "category": "旅行",
      "priority": 2,
      "notes": "旅行摄影师，作品精美",
      "tags": ["旅行", "摄影", "风景"]
    }
  ],
  "settings": {
    "max_retry": 3,
    "follow_interval": 3,
    "batch_size": 10,
    "error_threshold": 0.2
  }
}
```

### CSV格式（简化）

```csv
username,user_id,platform,category,priority,notes
美妆达人小王,xiaohongshu_user_001,xiaohongshu,美妆,1,专业美妆博主
旅行摄影师,xiaohongshu_user_002,xiaohongshu,旅行,2,旅行摄影师
```

## 🎮 使用指南

### 基本命令

```bash
# 检查设备状态
python xiaohongshu_client.py --check-devices

# 导入通讯录
python xiaohongshu_client.py --import contacts.json

# 创建示例数据
python xiaohongshu_client.py --create-sample 20

# 查看统计信息
python xiaohongshu_client.py --stats

# 模拟执行（安全测试）
python xiaohongshu_client.py --run --dry-run

# 执行自动化任务
python xiaohongshu_client.py --run --max-devices 2

# 导出结果
python xiaohongshu_client.py --export results.json
```

### 高级用法

```bash
# 导入CSV格式通讯录
python xiaohongshu_client.py --import contacts.csv --file-type csv

# 限制使用设备数量
python xiaohongshu_client.py --run --max-devices 1

# 查看详细帮助
python xiaohongshu_client.py --help-detailed
```

## 📊 执行流程

### 1. 设备检测
```
📱 正在扫描设备...
✅ 发现 2 个设备
   设备: emulator-5554 - ✅ 可用
     分辨率: 1920x1080
     Android: 9
     已安装应用: com.xingin.xhs
```

### 2. 通讯录处理
```
📥 导入通讯录: contacts.json
✅ 通讯录导入成功
   总联系人数: 50
   待处理: 50
   平台分布: {'xiaohongshu': 50}
```

### 3. 任务分配
```
📋 联系人分配完成:
   设备 emulator-5554: 25 个联系人
   设备 emulator-5556: 25 个联系人
```

### 4. 执行结果
```
🎉 任务执行完成
使用设备: 2 个
处理联系人: 50/50
成功: 43 个
失败: 7 个
成功率: 86.0%
```

## 🔧 配置说明

### 自动化设置

```python
# 关注间隔（秒）
follow_interval = (2, 5)  # 随机2-5秒

# 操作超时
operation_timeout = 30

# 最大重试次数
max_retries = 3

# 批处理大小
batch_size = 10
```

### 安全策略

- 🛡️ **随机延迟** - 避免被检测为机器操作
- 🛡️ **错误处理** - 遇到异常自动恢复
- 🛡️ **重试机制** - 失败自动重试
- 🛡️ **状态验证** - 确认操作成功
- 🛡️ **设备轮换** - 分散操作负载

## 📈 监控统计

### 设备统计
```json
{
  "total_devices": 2,
  "active_devices": 2,
  "device_status": {
    "emulator-5554": "working",
    "emulator-5556": "working"
  }
}
```

### 执行统计
```json
{
  "total_processed": 50,
  "success_count": 43,
  "failed_count": 7,
  "success_rate": 86.0,
  "average_time_per_contact": 3.2
}
```

## 🐛 常见问题

### 设备连接问题

**Q: 找不到设备**
```bash
# 检查ADB连接
adb devices

# 重启ADB服务
adb kill-server
adb start-server

# 检查USB调试
# 设置 -> 开发者选项 -> USB调试
```

**Q: 设备离线**
```bash
# 重连设备
adb reconnect

# 检查设备状态
adb get-state
```

### 应用相关问题

**Q: 找不到小红书**
```bash
# 检查应用安装
adb shell pm list packages | grep xhs

# 如未安装，请先安装小红书APP
```

**Q: 权限问题**
```bash
# 确保小红书有以下权限：
# - 存储权限
# - 网络权限
# - 设备权限
```

### 执行相关问题

**Q: 关注操作失败**
- 检查网络连接
- 确认账号未被限制
- 调整操作间隔
- 检查目标用户是否存在

**Q: 解析UI失败**
- 检查设备屏幕是否正常显示
- 确认小红书版本兼容性
- 重启应用重试

## 🔄 更新记录

### v1.0.0 (2024-01-01)
- ✅ 完整的设备管理功能
- ✅ 通讯录导入导出
- ✅ 自动化关注流程
- ✅ 多设备任务分发
- ✅ 实时监控统计

### 功能特性
- 🔥 **设备热插拔支持**
- 🔥 **智能任务调度**
- 🔥 **完善错误处理**
- 🔥 **安全策略保护**
- 🔥 **详细日志记录**

## 🤝 技术支持

### 日志查看
```bash
# 查看运行日志
tail -f flow_farm_client.log

# 查看设备日志
tail -f demo.log
```

### 问题排查
1. 检查设备连接状态
2. 查看日志文件
3. 验证通讯录格式
4. 确认网络连接
5. 重启相关服务

### 性能优化
- 根据设备性能调整并发数
- 优化关注间隔设置
- 定期清理日志文件
- 监控内存使用情况

---

**🎉 恭喜！您已成功集成了Flow Farm小红书自动化系统！**

现在您可以：
1. 📱 管理多个设备
2. 📇 导入通讯录数据
3. 🤖 执行自动化关注
4. 📊 监控执行结果
5. 🔄 持续优化流程

开始您的自动化之旅吧！🚀
