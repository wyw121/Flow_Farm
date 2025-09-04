# Employee Client - GitHub Copilot 配置说明

## 工作区配置概述

### 独立工作区优势
本项目现在有两个工作区配置：

1. **主工作区** (`../employee-client.code-workspace`) - 包含完整 Flow Farm 项目
2. **独立工作区** (`employee-client-standalone.code-workspace`) - 仅包含员工客户端

### 使用独立工作区的好处

#### ✅ 优势
- **专注开发**: 只关注员工客户端相关代码，避免干扰
- **精确配置**: Rust + Tauri 专用的开发环境配置
- **独立 Copilot**: 专门针对 Rust 桌面应用的 AI 辅助
- **更快响应**: 减少不相关文件的索引，提升性能
- **清晰任务**: 专用的构建和调试任务

#### 🔧 技术配置差异
- **主工作区**: Python + FastAPI + Vue.js 多技术栈配置
- **独立工作区**: Rust + Tauri 专用配置

## GitHub Copilot 配置层级

### 配置优先级 (高到低)
1. **个人设置** - 用户全局 Copilot 设置
2. **工作区设置** - 当前工作区的 Copilot 配置
3. **仓库设置** - `.github/copilot-instructions.md`
4. **组织设置** - 组织级别的设置

### 本项目的配置架构

```
Flow_Farm/                                 # 主仓库
├── .github/copilot-instructions.md       # 主项目指令 (通用)
├── employee-client/                       # 员工客户端子目录
│   ├── .github/                          # 独立 Copilot 配置
│   │   ├── copilot-instructions.md      # 专用指令 (Rust/Tauri)
│   │   └── instructions/                 # 路径特定指令
│   │       ├── rust-backend.instructions.md
│   │       ├── frontend.instructions.md
│   │       └── configuration.instructions.md
│   ├── .prompt.md                        # 开发上下文提示
│   └── employee-client-standalone.code-workspace
```

## 冲突处理机制

### 🚫 不会产生冲突的情况
- **文件路径**: 子目录的 `.github` 配置独立于父目录
- **工作区范围**: 独立工作区只作用于当前目录
- **Copilot 指令**: 路径特定指令具有更高优先级

### ✅ 协同工作原理
1. **在主工作区工作**: 使用主项目的 Copilot 配置
2. **在独立工作区工作**: 使用员工客户端专用配置
3. **路径特定**: 编辑 Rust 文件时，自动应用 Rust 专用指令

### 🔄 切换工作区的建议

#### 使用主工作区场景
- 跨项目开发 (后端 + 前端 + 客户端)
- 项目架构调整
- 服务器相关开发

#### 使用独立工作区场景 (推荐)
- 专注员工客户端开发
- Rust/Tauri 代码编写
- 桌面应用功能开发
- 性能优化和调试

## 最佳实践建议

### 🎯 开发流程
1. **日常开发**: 使用独立工作区 (`employee-client-standalone.code-workspace`)
2. **集成测试**: 切换到主工作区测试整体系统
3. **部署准备**: 在主工作区进行最终验证

### 📝 配置维护
- **保持同步**: 重要配置更新需要同步到两个工作区
- **定期检查**: 确保独立配置与主配置不冲突
- **文档更新**: 及时更新本说明文档

### 🛠 故障排除
如果遇到 Copilot 行为异常：
1. 检查当前工作区设置
2. 确认 `.github/copilot-instructions.md` 内容
3. 重启 VS Code 刷新配置
4. 检查 Copilot 扩展状态

## 总结

通过这种双工作区配置，您可以：
- 在独立环境中专注开发员工客户端
- 享受针对 Rust + Tauri 优化的开发体验
- 避免其他项目组件的干扰
- 保持与主项目的兼容性

**推荐**: 大部分时间使用独立工作区进行开发，需要整体项目视图时切换到主工作区。
