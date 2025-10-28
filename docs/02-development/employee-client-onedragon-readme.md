# Flow Farm OneDragon 架构 GUI 重构

## 🎉 全新界面设计

基于 OneDragon ZenlessZoneZero 项目的现代化界面架构，Flow Farm 的 GUI 已经完全重构！

### ✨ 新特性

- **🎨 Modern Fluent Design**: 采用 Microsoft Fluent Design 组件
- **🏗️ OneDragon 架构**: 模块化界面管理，易于扩展
- **🌓 主题支持**: 自动适应系统亮/暗主题
- **📱 响应式设计**: 支持不同分辨率和窗口大小
- **🔧 组件化**: 每个功能模块独立可复用

### 🚀 快速开始

#### 1. 升级依赖

```bash
# 自动升级到 OneDragon 兼容版本
python upgrade_onedragon.py
```

#### 2. 启动新版本 GUI

```bash
# 启动 OneDragon 架构版本
python start_onedragon.py
```

#### 3. 回退到旧版本（如需）

```bash
# 启动原版本（保留）
python src/main.py --gui --debug
```

### 🏗️ 架构说明

#### 基础架构

```
gui/
├── onedragon_base/          # OneDragon 基础架构
│   ├── app_window.py        # 主窗口类（MSFluentWindow）
│   ├── base_interface.py    # 基础界面类
│   └── vertical_scroll_interface.py  # 滚动界面基类
├── interfaces/              # 具体界面实现
│   ├── home_interface.py    # 主页界面
│   ├── device_interface.py  # 设备管理界面
│   └── task_interface.py    # 任务管理界面
└── components/              # 可复用组件（原有保留）
```

#### 界面层次

1. **FlowFarmAppWindow** (主窗口)
   - 基于 MSFluentWindow
   - 自动导航管理
   - 主题系统集成

2. **BaseInterface** (基础界面)
   - 统一生命周期管理
   - 信息提示系统
   - 日志记录

3. **VerticalScrollInterface** (滚动界面)
   - 自动滚动支持
   - 内容区域管理
   - 响应式布局

### 🎯 主要界面

#### 1. 主页界面 (HomeInterface)
- 📊 系统状态卡片
- 🚀 快捷操作按钮
- 📈 数据统计显示

#### 2. 设备管理界面 (DeviceInterface)
- 📱 设备扫描和连接
- ⚙️ 设备配置管理
- 🔄 自动重连设置

#### 3. 任务管理界面 (TaskInterface)
- 🎯 平台选择（抖音、小红书等）
- 🛠️ 任务配置（类型、数量、间隔）
- ▶️ 任务控制（开始、停止、状态）

### 🔧 技术细节

#### 依赖版本

```
PySide6==6.8.0.2          # Qt6 框架 (OneDragon 兼容)
qfluentwidgets==1.7.0      # Fluent Design 组件
qtawesome==1.3.1          # 图标库
```

#### 关键设计模式

1. **信号槽机制**: 界面间通信
2. **工厂模式**: 组件创建和管理
3. **观察者模式**: 状态更新和同步
4. **策略模式**: 不同平台的操作策略

### 🎨 界面特点

#### 主题和样式
- 跟随系统主题（亮色/暗色）
- Microsoft YaHei 字体
- 3:2 窗口比例（1095x730）
- 卡片式布局设计

#### 交互体验
- 平滑动画过渡
- 智能信息提示
- 键盘快捷键支持
- 拖拽操作支持

### 🛠️ 开发指南

#### 添加新界面

```python
from gui.onedragon_base.vertical_scroll_interface import VerticalScrollInterface
from qfluentwidgets import FluentIcon

class NewInterface(VerticalScrollInterface):
    def __init__(self, parent=None):
        content_widget = self._create_content()
        super().__init__(
            parent=parent,
            content_widget=content_widget,
            object_name="new_interface",
            nav_text_cn="新界面",
            nav_icon=FluentIcon.HOME
        )

    def _create_content(self):
        # 创建界面内容
        pass
```

#### 添加到主窗口

```python
# 在 FlowFarmApp._create_interfaces() 中添加
new_interface = NewInterface(parent=self.window)
self.window.add_sub_interface(
    new_interface,
    position=NavigationItemPosition.TOP
)
```

### 🐛 常见问题

#### Q: 界面显示异常或空白？
A: 检查 qfluentwidgets 版本是否为 1.7.0，运行 `upgrade_onedragon.py` 重新安装

#### Q: 图标不显示？
A: 确保 qtawesome 已安装，某些图标可能需要更新到最新版本

#### Q: 主题切换不生效？
A: 重启应用程序，主题切换需要重新初始化

#### Q: 界面卡顿？
A: 检查是否有大量数据加载，考虑使用分页或懒加载

### 🔄 迁移指南

#### 从旧版本迁移

1. **备份数据**: 备份配置文件和用户数据
2. **升级依赖**: 运行 `upgrade_onedragon.py`
3. **测试功能**: 使用 `start_onedragon.py` 启动测试
4. **配置迁移**: 将旧配置迁移到新界面

#### 兼容性说明

- ✅ 保留所有原有功能
- ✅ 配置文件向后兼容
- ✅ API 接口不变
- ⚠️ UI 交互方式有所变化

### 📝 更新日志

#### v2.0.0 (OneDragon 架构)
- 🎉 全新基于 OneDragon 的界面架构
- 🎨 Microsoft Fluent Design 组件库
- 🏗️ 模块化界面管理系统
- 🌓 自动主题切换支持
- 📱 响应式设计和布局

#### v1.x (传统架构)
- 保留在 `src/main.py` 中，可继续使用

### 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

- 界面 Bug 报告
- 新功能建议
- 界面优化建议
- 代码改进

### 📄 许可证

继承原项目许可证。

---

**享受全新的 Flow Farm 界面体验！** 🎉
