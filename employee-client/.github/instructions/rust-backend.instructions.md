---
applyTo: "src-tauri/**/*.rs"
---

# Rust Backend Development Instructions

## Core Requirements

- 使用 Rust 2021 edition
- 所有业务逻辑必须在 Rust 后端实现
- 使用 Tauri 命令进行前后端通信
- 确保类型安全和内存安全

## Code Style and Standards

- 遵循标准 Rust 命名约定（snake_case 函数，PascalCase 类型）
- 最大行长度：100 字符
- 始终使用显式错误处理 `Result<T, E>`
- 使用 tokio 处理所有异步操作

## Tauri Architecture Requirements

- 所有前端可访问的函数必须使用 `#[tauri::command]` 宏
- 使用 Tauri 状态管理共享数据
- 在命令函数中正确处理所有错误
- 前端仅用于 UI 渲染，业务逻辑在 Rust 中

## Employee Client Specific Requirements

### Device Management

- 实现 ADB 设备连接管理
- 支持最多 10 台设备同时连接
- 设备状态实时监控
- 任务自动分配给已连接设备

### Task Management

- 通讯录管理：CSV/文本文件上传和处理
- 精准获客：同行监控和用户 ID 收集
- 任务不重复分配算法
- 平台特定脚本执行（小红书/抖音）

### API Communication

- 使用 reqwest 与服务器通信
- 实现余额检查和扣费机制
- 数据同步和用户认证
- 错误重试机制

## Error Handling

- 使用 thiserror crate 创建自定义错误类型
- 所有外部 API 调用必须有错误处理
- 向前端返回用户友好的错误信息

## Performance and Security

- 使用高效的 Rust 模式（borrowing, zero-copy）
- API 令牌安全存储（Tauri secure storage）
- 验证所有 ADB 命令
- 网络通信使用 HTTPS

## Security

- Validate all input from frontend
- Use Tauri's secure API access patterns
- Implement proper authentication checks
- Sanitize all external command executions

## Performance

- Use efficient data structures
- Implement proper async patterns
- Avoid blocking operations on main thread
- Use channels for inter-task communication
