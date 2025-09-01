# GUI 现代化重构 Prompt

## 背景
基于 OneDragon ZenlessZoneZero 项目的成功实践，将 Flow Farm 员工客户端的 GUI 框架从原生 PySide6 升级到 PySide6 + qfluentwidgets 现代化架构。

## 重构目标

### 技术栈升级
- **从**: PySide6 6.6.1 + qtawesome + 自定义样式
- **到**: PySide6 6.8.0.2 + qfluentwidgets 1.7.0 + FluentIcon

### 视觉效果提升
- Microsoft Fluent Design 设计语言
- 自动深色/浅色主题切换
- 现代化圆角、阴影、动画效果
- 响应式布局和平滑滚动

## 重构计划

### 阶段一：依赖升级和基础架构
```bash
# 安装新依赖
pip install qfluentwidgets==1.7.0
pip install PySide6==6.8.0.2

# 保留兼容依赖
# qtawesome 用于过渡期图标兼容
```

### 阶段二：主窗口重构
将 `src/gui/main_window.py` 的 `MainWindow` 类重构为：

```python
from qfluentwidgets import VerticalScrollInterface, FluentIcon

class MainWindow(VerticalScrollInterface):
    """现代化主窗口 - 继承 VerticalScrollInterface"""

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            object_name="main_window",
            nav_text_cn="Flow Farm 工作台",
            nav_icon=FluentIcon.HOME
        )
        self.setup_modern_ui()
```

### 阶段三：组件替换对照

| 当前组件 | 新组件 | 替换原因 |
|---------|--------|----------|
| QPushButton | PrimaryPushButton | 现代化按钮样式 |
| QComboBox | ComboBox | Fluent Design 风格 |
| QLineEdit | LineEdit | 统一输入框样式 |
| QGroupBox | SettingCardGroup | 卡片化设计 |
| QCheckBox | SwitchSettingCard | 现代化开关 |
| QMessageBox | MessageBox | Fluent 消息框 |

### 阶段四：设置界面卡片化
重构设置界面使用 SettingCard 模式：

```python
# 设备设置卡片
device_group = SettingCardGroup("设备管理")

# 平台选择卡片
platform_card = ComboBoxSettingCard(
    FluentIcon.APPLICATION,
    "目标平台",
    "选择要操作的社交媒体平台",
    texts=["抖音", "小红书", "微博"]
)

device_group.addSettingCard(platform_card)
```

## 具体重构要求

### 1. 主窗口重构 (main_window.py)
- 继承 `VerticalScrollInterface` 替代 `BaseWindow`
- 使用 `SettingCardGroup` 组织界面布局
- 实现自动主题切换支持

### 2. 组件重构 (components/)
- `console_widget.py`: 使用 `TextEdit` 替代 `QTextEdit`
- `contacts_widget.py`: 使用 `PrimaryPushButton` 替代 `QPushButton`
- 设备管理界面使用 `SettingCard` 系列组件

### 3. 对话框重构 (dialogs/)
- 登录对话框使用 `MessageBox` 基类
- 设备配置对话框使用 `ComboBoxSettingCard`
- 所有确认对话框统一使用 `MessageBox`

### 4. 主题和图标
- 配置自动主题切换: `qconfig.theme = Theme.AUTO`
- 替换 qtawesome 图标为 FluentIcon
- 保留 qtawesome 作为兼容方案

## 重构步骤

### Step 1: 环境准备
```python
# 在 main.py 中添加主题配置
from qfluentwidgets import qconfig, Theme, setTheme

# 应用启动时配置主题
qconfig.theme = Theme.AUTO  # 自动跟随系统
```

### Step 2: 基类重构
```python
# 重构 BaseWindow 为兼容层
class BaseWindow(VerticalScrollInterface):
    """兼容层 - 保持现有接口"""

    def __init__(self, title: str, size: tuple, parent=None):
        super().__init__(
            parent=parent,
            object_name="base_window",
            nav_text_cn=title,
            nav_icon=FluentIcon.APPLICATION
        )
        self.resize(*size)
```

### Step 3: 组件工厂升级
```python
# 升级 ComponentFactory
class ModernComponentFactory:
    @staticmethod
    def create_primary_button(text: str) -> PrimaryPushButton:
        return PrimaryPushButton(text)

    @staticmethod
    def create_setting_card(icon, title, content) -> SettingCard:
        return SettingCard(icon, title, content)
```

### Step 4: 信息反馈系统
```python
# 统一消息反馈
def show_success(self, message: str):
    InfoBar.success(
        title="操作成功",
        content=message,
        duration=3000,
        parent=self
    )

def show_error(self, message: str):
    InfoBar.error(
        title="操作失败",
        content=message,
        duration=5000,
        parent=self
    )
```

## 兼容性保证

### 保留现有接口
- `ComponentFactory` 类保持向后兼容
- `ModernTheme` 配色方案继续可用
- 现有的业务逻辑代码无需修改

### 渐进式迁移
1. 先升级主窗口架构
2. 逐步替换子组件
3. 最后优化细节样式

## 质量保证

### 测试要求
- 所有功能必须在新架构下正常工作
- 主题切换测试（深色/浅色）
- 响应式布局测试
- 性能回归测试

### 代码规范
- 新组件必须使用 qfluentwidgets
- 图标优先使用 FluentIcon
- 布局必须支持响应式设计
- 所有界面支持主题切换

## 风险控制

### 回滚方案
- 保留原有 base_window.py 作为备份
- 新旧组件共存的过渡期
- 版本控制确保可快速回退

### 性能考虑
- qfluentwidgets 可能增加内存占用
- 启动时间可能略有增加
- 需要性能基准测试

## 预期效果

### 用户体验提升
- 现代化的 Microsoft Fluent Design 外观
- 自动适配系统主题（深色/浅色）
- 更流畅的动画和交互效果
- 更好的响应式布局

### 开发体验提升
- 组件化设计提高复用性
- 统一的设计语言减少样式定制
- 更好的代码组织和维护性
