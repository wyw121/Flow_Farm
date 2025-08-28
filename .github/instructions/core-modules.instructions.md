---
applyTo: "src/core/**/*.py"
---

# 核心模块开发指令

## 设备管理模块指导原则

- 使用ADB命令进行设备通信
- 实现设备连接池管理，避免频繁连接断开
- 添加设备健康检查机制
- 支持设备热插拔检测
- 实现设备锁机制，避免并发冲突

## 自动化引擎指导原则

- 使用Appium WebDriver进行UI自动化
- 实现智能等待机制，避免硬编码延时
- 添加截图和日志记录功能
- 支持多种定位策略（ID、XPath、图像识别）
- 实现操作失败重试机制

## 任务调度器指导原则

- 使用队列管理任务执行
- 支持任务优先级设置
- 实现任务依赖关系处理
- 添加任务执行状态监控
- 支持任务暂停和恢复功能

## 错误处理标准

```python
import logging
import traceback

def handle_device_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"设备操作失败: {str(e)}")
            logging.debug(traceback.format_exc())
            # 实现重试逻辑
            return None
    return wrapper
```

## 日志记录标准

- 设备连接/断开事件必须记录
- 任务执行开始/结束必须记录
- 异常情况必须记录详细堆栈信息
- 性能关键点需要记录执行时间
