# Flow Farm Copilot 配置文档

这个目录包含了Flow Farm项目的GitHub Copilot配置文件，采用模块化设计以提供更精确和上下文相关的AI辅助。

## 文件结构

```
.github/
├── copilot-instructions.md          # 主要配置文件
├── instructions/                    # 模块化指令文件
│   ├── server-backend.instructions.md      # Rust后端开发
│   ├── server-frontend.instructions.md     # React前端开发
│   ├── employee-client.instructions.md     # Python客户端开发
│   ├── auth-system.instructions.md         # 认证系统
│   ├── core-modules.instructions.md        # 核心模块
│   ├── gui-development.instructions.md     # GUI开发
│   ├── platform-automation.instructions.md # 平台自动化
│   └── build-scripts.instructions.md       # 构建脚本
├── prompts/                         # 专用prompt文件
│   ├── server-optimization.prompt.md       # 服务器优化
│   ├── api-development.prompt.md          # API开发
│   ├── rbac-system.prompt.md              # 权限系统
│   └── device-automation.prompt.md        # 设备自动化
└── workflows/                       # GitHub Actions
    └── update-docs.yml             # 文档自动更新
```

## 使用指南

### 1. 自动应用的指令

项目的模块化指令会根据你编辑的文件自动应用：

- 编辑 `server-backend/**/*.rs` 时，自动应用Rust后端指令
- 编辑 `server-frontend/**/*.tsx` 时，自动应用React前端指令
- 编辑 `employee-client/**/*.py` 时，自动应用Python客户端指令

### 2. 手动使用Prompt文件

对于特定的开发任务，可以在Copilot Chat中手动附加prompt文件：

1. 打开Copilot Chat
2. 点击附件图标 📎
3. 选择 "Prompt..."
4. 选择相应的prompt文件

### 3. 常用命令

```bash
# 查看所有指令文件
find .github/instructions -name "*.instructions.md"

# 查看所有prompt文件
find .github/prompts -name "*.prompt.md"

# 验证配置文件语法
markdown-cli .github/copilot-instructions.md
```

## 配置文件说明

### 主配置文件 (copilot-instructions.md)

包含项目的整体架构、技术栈、构建指令和通用规范。这是Copilot了解项目的起点。

### 指令文件 (.instructions.md)

每个指令文件都有 `applyTo` 前置元数据，指定应用的文件模式：

```yaml
---
applyTo: "server-backend/**/*.rs"
---
```

### Prompt文件 (.prompt.md)

专门为特定开发任务设计的提示文件，包含：
- 任务背景和目标
- 技术要求和约束
- 开发流程指导
- 最佳实践建议

## 最佳实践

### 1. 编写指令文件

- **明确性**: 使用具体、明确的语言
- **上下文**: 提供足够的背景信息
- **示例**: 包含代码示例和模板
- **更新**: 保持与项目同步更新

### 2. 使用Copilot

- **引用文件**: 使用 `#file:path/to/file` 引用特定文件
- **指定模块**: 明确说明要修改的模块
- **遵循规范**: 确保生成的代码符合项目规范

### 3. 维护配置

- **定期审查**: 检查指令是否仍然准确
- **版本控制**: 所有配置文件都纳入版本控制
- **团队协作**: 确保团队成员都了解配置结构

## 配置验证

项目包含自动化检查来确保配置质量：

1. **语法验证**: 检查Markdown语法
2. **完整性检查**: 验证指令文件的applyTo配置
3. **文档生成**: 自动生成文档索引
4. **同步检查**: 确保文档与代码同步

## 问题排查

### 常见问题

1. **指令不生效**: 检查文件路径是否匹配applyTo模式
2. **权限错误**: 确保有读取.github目录的权限
3. **配置冲突**: 避免多个指令文件的applyTo模式重叠

### 调试方法

1. 查看Copilot Chat的引用列表，确认使用了哪些指令文件
2. 检查VS Code设置中的 `chat.promptFiles` 是否启用
3. 验证指令文件的前置元数据格式是否正确

## 贡献指南

修改配置文件时请遵循以下流程：

1. 创建feature分支
2. 修改相应的指令或prompt文件
3. 测试配置是否正确应用
4. 提交Pull Request
5. 等待自动化检查通过

更多详细信息，请参考[项目文档](../docs/README.md)。
