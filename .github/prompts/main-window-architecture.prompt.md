---
description: "创建主界面和导航架构"
mode: "edit"
tools: ["file-system"]
---

# 主界面架构开发

创建Flow Farm员工客户端的主界面框架，集成所有功能模块并提供清晰的导航体验。

## 主界面架构设计

### 1. 导航结构
```python
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition,
    FluentIcon, SplashScreen
)

class FlowFarmMainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flow Farm - 社交平台获客系统")
        self.setWindowIcon(QIcon(":/icons/logo.png"))

        # 初始化所有功能界面
        self.device_interface = DeviceManagementInterface()
        self.contact_interface = ContactManagementInterface()
        self.acquisition_interface = PrecisionAcquisitionInterface()
        self.billing_interface = BillingInterface()
        self.statistics_interface = StatisticsInterface()
        self.settings_interface = SettingsInterface()

        self.init_navigation()
        self.init_window()

    def init_navigation(self):
        """初始化导航栏"""
        # 主功能区
        self.addSubInterface(
            self.device_interface,
            FluentIcon.PHONE,
            "设备管理",
            NavigationItemPosition.TOP
        )

        self.addSubInterface(
            self.contact_interface,
            FluentIcon.CONTACT,
            "通讯录管理",
            NavigationItemPosition.TOP
        )

        self.addSubInterface(
            self.acquisition_interface,
            FluentIcon.SEARCH,
            "精准获客",
            NavigationItemPosition.TOP
        )

        self.addSubInterface(
            self.statistics_interface,
            FluentIcon.CHART,
            "数据统计",
            NavigationItemPosition.TOP
        )

        # 系统功能区
        self.addSubInterface(
            self.billing_interface,
            FluentIcon.MONEY,
            "余额管理",
            NavigationItemPosition.BOTTOM
        )

        self.addSubInterface(
            self.settings_interface,
            FluentIcon.SETTING,
            "系统设置",
            NavigationItemPosition.BOTTOM
        )
```

### 2. 主界面布局

```
┌─────────────────────────────────────────────────────┐
│ Flow Farm - 社交平台获客系统               [- □ ×]   │
├─────────────────────────────────────────────────────┤
│ 导航栏     │                主内容区                │
│           │                                      │
│ 📱 设备管理 │  ┌─────────────────────────────────┐   │
│ 📇 通讯录管理│  │                               │   │
│ 🔍 精准获客 │  │        当前界面内容             │   │
│ 📊 数据统计 │  │                               │   │
│           │  │                               │   │
│ ─────────  │  │                               │   │
│ 💰 余额管理 │  │                               │   │
│ ⚙️ 系统设置 │  │                               │   │
│           │  └─────────────────────────────────┘   │
│           │                                      │
├─────────────────────────────────────────────────────┤
│ 状态栏: 🟢 已连接服务器 | 余额: ¥1,250 | 3台设备在线 │
└─────────────────────────────────────────────────────┘
```

### 3. 状态栏信息显示
- 服务器连接状态
- 当前余额（实时更新）
- 在线设备数量
- 当前正在执行的任务
- 系统通知和警告

## 启动流程和初始化

### 1. 应用启动序列
```python
class FlowFarmApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)

        # 设置应用信息
        self.setApplicationName("Flow Farm")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Flow Farm Inc.")

        # 显示启动画面
        self.splash = SplashScreen(QPixmap(":/images/splash.png"))
        self.splash.show()

        # 初始化配置和服务
        self.init_services()

        # 创建主窗口
        self.main_window = FlowFarmMainWindow()

        # 完成启动
        self.finish_startup()

    def init_services(self):
        """初始化核心服务"""
        self.config_manager = ConfigManager()
        self.api_client = APIClient(self.config_manager)
        self.device_manager = DeviceManager()
        self.billing_manager = BillingManager(self.api_client)

        # 服务启动检查
        self.check_server_connection()
        self.load_user_preferences()
        self.init_device_scan()
```

### 2. 启动检查清单
- [ ] 配置文件完整性检查
- [ ] 服务器连接测试
- [ ] ADB环境检查
- [ ] 用户认证验证
- [ ] 余额和权限获取
- [ ] 设备扫描和连接
- [ ] 本地数据库初始化

## 系统设置界面

### 配置选项分组：

#### 1. 基础设置
- 服务器地址配置
- 用户登录信息
- 自动登录选项
- 语言和主题设置

#### 2. 设备设置
- ADB路径配置
- 设备连接超时设置
- 自动重连策略
- 设备性能监控

#### 3. 任务设置
- 默认任务间隔
- 最大并发任务数
- 失败重试次数
- 任务日志级别

#### 4. 平台设置
- 小红书APP路径
- 抖音APP路径
- 平台切换延时
- 操作随机化程度

#### 5. 安全设置
- 数据加密选项
- 日志保留天数
- 自动备份设置
- 隐私保护级别

```python
class SettingsInterface(VerticalScrollInterface):
    def __init__(self):
        super().__init__(
            object_name="settings",
            nav_text_cn="系统设置",
            nav_icon=FluentIcon.SETTING
        )
        self.create_setting_groups()

    def create_setting_groups(self):
        # 基础设置组
        basic_group = SettingCardGroup("基础设置")
        basic_group.addSettingCard(
            TextSettingCard(
                icon=FluentIcon.GLOBE,
                title="服务器地址",
                content="配置API服务器连接地址"
            )
        )

        # 设备设置组
        device_group = SettingCardGroup("设备设置")
        device_group.addSettingCard(
            ComboBoxSettingCard(
                icon=FluentIcon.PHONE,
                title="ADB连接模式",
                content="选择设备连接方式",
                options=["USB连接", "无线连接", "自动检测"]
            )
        )

        self.addWidget(basic_group)
        self.addWidget(device_group)
```

## 错误处理和用户体验

### 1. 友好的错误提示
- 网络连接失败的处理
- 设备离线时的提示
- 余额不足的引导
- 任务失败的原因说明

### 2. 操作反馈
- 按钮点击的即时反馈
- 长时间操作的进度显示
- 成功操作的确认提示
- 关键操作的二次确认

### 3. 数据保护
- 自动保存用户配置
- 任务中断的恢复机制
- 重要数据的本地备份
- 异常退出的数据恢复

参考gui-development.instructions.md中的组件使用规范和OneDragon架构模式。
