---
applyTo: "**/*.json"
---

# JSON Configuration Instructions

## Tauri Configuration (tauri.conf.json)

### 应用程序标识

- **应用名称**: "Flow Farm Employee Client"
- **标识符**: "com.flowfarm.employee-client"
- **版本**: 遵循语义化版本控制

### 窗口配置

```json
{
  "windows": [
    {
      "title": "Flow Farm Employee Client",
      "width": 1200,
      "height": 800,
      "minWidth": 1000,
      "minHeight": 600,
      "resizable": true,
      "fullscreen": false,
      "center": true,
      "decorations": true
    }
  ]
}
```

### 安全和权限

- 启用必要的 API 权限
- 配置 CSP (Content Security Policy)
- 设置允许的外部域名
- 启用文件系统访问权限（用于 CSV 上传）

### 构建配置

- 设置正确的应用图标路径
- 配置资源文件包含规则
- 设置目标平台为 Windows
- 启用代码签名（生产环境）

## Package.json (如果存在)

### 开发脚本

```json
{
  "scripts": {
    "tauri": "tauri",
    "tauri:dev": "tauri dev",
    "tauri:build": "tauri build",
    "tauri:icon": "tauri icon"
  }
}
```

### 前端依赖管理

- 保持依赖最小化
- 避免重型框架
- 仅使用必要的工具库

## VS Code 配置

### tasks.json 任务配置

确保包含所有必要的构建和开发任务：

- Rust 环境初始化
- Cargo check/build/test
- Tauri 开发和构建命令
- 代码格式化和检查
