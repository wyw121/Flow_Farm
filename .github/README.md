# Flow Farm - GitHub Copilot 配置指南

本项目采用最新的GitHub Copilot和VS Code配置最佳实践（2025年版），为开发团队提供智能化的编程辅助。

**项目定位**: 垂直行业工具 - 市场调研与客户拜访管理平台

## 技术栈概览

| 模块 | 技术栈 | 业务角色 |
|------|--------|----------|
| 业务后端 | **Rust + Axum + SQLx + SQLite** | 核心数据处理与业务逻辑 |
| 管理后台 | **React 19 + TypeScript + Ant Design 5 + Vite** | 调研经理管理界面 |
| 外勤客户端 | **Rust + Tauri 2.0 + HTML/CSS/JS** | 外勤人员移动应用 |

## 配置文件结构

```
.github/
├── instructions/                    # 路径特定指令
│   ├── server-backend.instructions.md       # Rust 业务后端指令
│   ├── server-frontend.instructions.md      # React 管理后台指令
│   ├── employee-client.instructions.md      # Tauri 外勤客户端指令
│   ├── platform-automation.instructions.md  # 业务自动化指令（已废弃）
│   ├── core-modules.instructions.md         # 核心模块指令
│   ├── auth-system.instructions.md          # 认证系统指令
│   └── build-scripts.instructions.md        # 构建脚本指令
├── prompts/                         # 可复用提示文件（垂直行业场景）
│   ├── market-research.prompt.md            # 市场调研功能
│   ├── client-visit.prompt.md               # 客户拜访管理
│   ├── survey-design.prompt.md              # 问卷设计
│   ├── data-analysis.prompt.md              # 数据分析引擎
│   ├── expense-management.prompt.md         # 费用报销管理
│   ├── api-development.prompt.md            # API 开发
│   ├── rbac-system.prompt.md                # 权限管理
│   ├── server-optimization.prompt.md        # 服务器优化
│   └── project-setup.prompt.md              # 项目设置
└── README.md                        # 本文件
```

## 如何使用

### 1. 确认VS Code设置

确保您的VS Code workspace settings包含：

```json
{
    "chat.promptFiles": true,
    "copilot.chat.useInstructionFiles": true,
    "github.copilot.enable": {
        "*": true,
        "rust": true,
        "javascript": true,
        "typescript": true,
        "toml": true
    },
    "rust-analyzer.checkOnSave.command": "clippy",
    "typescript.tsdk": "server-frontend/node_modules/typescript/lib"
}
```

### 2. 使用自定义指令

#### 路径特定指令（智能匹配）
当您在特定路径下工作时，相应的指令文件会自动应用：

- `server-backend/**/*.rs` → `server-backend.instructions.md`
- `server-frontend/**/*.{tsx,ts}` → `server-frontend.instructions.md`
- `employee-client/src-tauri/**/*.rs` → `employee-client.instructions.md`

### 3. 使用提示文件

#### 通过聊天附件使用
1. 在Copilot Chat中点击📎附件按钮
2. 选择"Prompt..."
3. 选择相应的 `.prompt.md` 文件

#### 通过命令运行
在聊天框中输入：
```
/market-research       # 市场调研功能开发
/client-visit          # 客户拜访管理
/survey-design         # 问卷设计模块
/data-analysis         # 数据分析引擎
/expense-management    # 费用报销管理
```

| 提示文件 | 使用场景 | 推荐时机 |
|---------|----------|---------|
| `market-research` | 市场调研功能开发 | 实现问卷设计、数据采集功能 |
| `client-visit` | 客户拜访跟踪 | 开发拜访计划和记录功能 |
| `survey-design` | 问卷设计模块 | 创建调研问卷设计界面 |
| `data-analysis` | 数据分析引擎 | 实现市场洞察和客户画像 |
| `expense-management` | 费用报销管理 | 处理外勤费用报销逻辑 |
| `statistics-dashboard` | 数据可视化 | 创建统计图表和报表 |

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
