---
applyTo: "**/*.toml"
---

# Configuration and Build Instructions

## Cargo.toml Management

### Dependency Management

- 固定主要版本号以确保稳定性
- 使用 `serde = { version = "1.0", features = ["derive"] }` 形式
- 开发依赖与运行时依赖分离
- 文档化所有可选特性

### Employee Client Required Dependencies

```toml
[dependencies]
tauri = { version = "2.0", features = ["api-all"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tokio = { version = "1.0", features = ["full"] }
reqwest = { version = "0.11", features = ["json"] }
sqlx = { version = "0.7", features = ["sqlite", "runtime-tokio-rustls", "uuid", "chrono"] }
uuid = { version = "1.0", features = ["v4", "serde"] }
chrono = { version = "0.4", features = ["serde"] }
thiserror = "1.0"
```

## Tauri Configuration (tauri.conf.json)

### 应用程序设置

- **应用名称**: "Flow Farm Employee Client"
- **版本管理**: 使用语义化版本
- **图标和元数据**: 设置适当的应用图标和描述

### 窗口属性

```json
{
  "tauri": {
    "windows": [
      {
        "title": "Flow Farm Employee Client",
        "width": 1200,
        "height": 800,
        "minWidth": 1000,
        "minHeight": 600,
        "resizable": true,
        "fullscreen": false
      }
    ]
  }
}
```

### 安全设置

- 启用 CSP (Content Security Policy)
- 限制外部资源访问
- 配置允许的 API 调用
- 设置适当的权限级别

### Build Configuration

- **目标平台**: Windows (x86_64-pc-windows-msvc)
- **图标路径**: 设置正确的应用图标
- **资源文件**: 包含必要的静态资源
- **签名配置**: 生产环境的代码签名

## Development vs Production Settings

### Development

- 启用开发者工具
- 详细错误信息
- 热重载支持

### Production

- 优化构建大小
- 禁用调试输出
- 启用所有安全特性
- 代码签名和分发配置

## Build Optimization

- Use release profile optimizations
- Configure proper target platforms
- Set up incremental compilation
- Optimize bundle size settings
