---
applyTo: "src/platforms/**/*.py"
---

# 平台自动化模块开发指令

## 抖音自动化指导原则

- 严格遵守抖音平台使用规范
- 模拟真实用户行为，添加随机延时
- 实现反检测机制，避免被识别为机器人
- 支持多种操作：关注、点赞、评论、分享

## 小红书自动化指导原则

- 遵循小红书社区规范
- 实现智能内容识别和筛选
- 支持笔记互动、用户关注等操作
- 添加内容质量评估功能

## 通用自动化标准

```python
import random
import time
from abc import ABC, abstractmethod

class BasePlatformAutomation(ABC):
    def __init__(self, device_manager):
        self.device = device_manager
        self.min_delay = 2  # 最小延时(秒)
        self.max_delay = 5  # 最大延时(秒)
    
    def random_delay(self):
        """随机延时，模拟人类操作"""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)
    
    @abstractmethod
    def follow_user(self, user_id):
        """关注用户的抽象方法"""
        pass
    
    @abstractmethod
    def like_content(self, content_id):
        """点赞内容的抽象方法"""
        pass
```

## 安全和检测规避

- 操作频率控制：每小时操作次数限制
- 行为模式随机化：避免固定的操作序列
- IP地址管理：支持代理切换（如需要）
- 异常检测：识别验证码和异常页面

## 数据收集和分析

- 记录操作结果和效果数据
- 分析用户互动反馈
- 监控账号状态变化
- 生成操作报告和统计

## 错误处理机制

- 网络连接异常重试
- 页面加载失败处理
- 元素定位失败降级
- 账号异常状态检测
