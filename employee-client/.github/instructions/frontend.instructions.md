---
applyTo: "src/**/*.{html,css,js}"
---

# Frontend Development Instructions

## Tauri Frontend Architecture

- **最小化前端代码**：仅用于 UI 渲染和用户交互
- **所有业务逻辑在 Rust 后端**：通过 Tauri 命令调用
- 使用原生 HTML/CSS/JavaScript，避免重框架
- 通过 `invoke()` 与 Rust 后端通信

## Employee Client UI Requirements

### Layout and Design

- 现代桌面应用程序界面设计
- 响应式布局适配不同窗口大小
- 清晰的模块分区（设备管理、任务管理、统计）
- 一致的视觉风格和交互模式

### Core UI Components

- **设备管理界面**：列表显示设备状态（1-10 台）
- **任务管理界面**：选项卡切换通讯录管理和精准获客
- **平台选择**：下拉菜单选择小红书/抖音
- **进度显示**：实时进度条和任务状态
- **余额显示**：当前余额和扣费提醒

### User Interaction Patterns

- 文件上传控件（支持 CSV/文本）
- 多选设备列表（全选功能）
- 实时状态更新（连接状态、任务进度）
- 错误提示和确认对话框
- 键盘导航支持

## Tauri Integration Best Practices

### Command Invocation

- 使用 `window.__TAURI__.invoke()` 调用 Rust 命令
- 实现加载状态和错误处理
- 异步操作的用户反馈
- 命令失败时的重试机制

### Event Handling

- 监听 Tauri 事件获取后端更新
- 实时更新 UI 状态（设备连接、任务进度）
- 处理窗口生命周期事件

## Performance and Optimization

- 最小化 JavaScript 代码量
- 避免不必要的 DOM 操作
- 使用事件委托处理动态内容
- 懒加载非关键 UI 组件

## Error Handling and User Experience

- 友好的错误信息显示
- 网络连接状态提示
- 操作确认和撤销功能
- 加载状态和进度指示器
- Use efficient DOM manipulation
- Implement virtual scrolling for large lists
- Optimize CSS for smooth animations
