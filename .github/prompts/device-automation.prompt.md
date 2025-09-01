# 设备自动化开发 Prompt - 多平台智能引流系统

## 背景
Flow Farm 员工客户端的核心功能是多设备自动化控制，实现抖音、小红书等平台的自动化引流操作。本系统需要在保证稳定性和安全性的前提下，最大化自动化效率。

## 开发重点

### ADB 设备连接管理
```python
# 设备发现和连接
def discover_devices():
    """自动发现可用设备"""
    devices = []
    # 雷电模拟器检测
    # 真机设备检测
    # 其他模拟器检测
    return devices

def connect_device(device_id: str):
    """连接指定设备"""
    # 建立 ADB 连接
    # 验证设备状态
    # 初始化自动化环境
    pass
```

### 平台自动化模块架构
- **抖音自动化** (`src/platforms/douyin/`)
  - 关注用户操作
  - 视频点赞和评论
  - 直播间互动
  - 数据收集和上报

- **小红书自动化** (`src/platforms/xiaohongshu/`)
  - 笔记点赞和收藏
  - 用户关注操作
  - 评论互动
  - 热门内容监控

- **统一自动化接口** (`src/platforms/base_platform.py`)
  - 标准化操作接口
  - 通用错误处理
  - 平台适配层
- 人性化操作模拟

### 任务调度
- 任务队列管理
- 多线程执行
- 任务状态跟踪
- 错误处理和恢复

## 技术要求
- 使用ADB进行设备通信
- 实现设备连接池管理
- 支持设备热插拔
- 提供操作日志记录
- 实现性能监控

## 安全要求
- 遵循平台使用条款
- 实现频率限制
- 避免被检测为机器人
- 保护用户隐私数据

## 参考文件
- #file:employee-client/src/core/device_manager.py
- #file:employee-client/src/core/automation_engine.py
- #file:employee-client/src/platforms/douyin/automation.py
- #file:employee-client/src/platforms/xiaohongshu/automation.py
