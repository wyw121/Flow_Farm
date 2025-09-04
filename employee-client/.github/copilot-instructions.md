# Flow Farm Employee Client - GitHub Copilot Instructions

## Project Overview

Flow Farm Employee Client 是一个用于员工角色的现代化桌面 GUI 应用程序，使用 **Rust** 和 **Tauri 框架** 构建。这是一个独立的员工管理和自动化客户端，提供以下功能：

- 员工身份验证和授权
- 设备自动化管理（通过 ADB）
- 任务执行和监控（重点：通讯录管理、精准获客）
- 与服务器实时数据同步
- 支持多平台社交媒体操作（小红书优先，抖音紧随，未来扩展快手、B 站等）
- 设备管理（最多支持 10 台设备）
- 余额检查和扣费机制
- 关注统计和进度显示

**重要提醒**: 本项目使用 **Tauri 原生 GUI（Rust + HTML/CSS/JS）**，而不是 React.js 或纯 Web 框架。

## 核心模块架构

### 设备管理模块

- 设备编号管理（1-10）
- 设备连接状态监控
- ADB 自动化控制
- 任务分配到已连接设备

### 任务管理模块（重点）

1. **通讯录管理**：

   - 文件上传（CSV/文本）
   - 数据导入到服务器
   - 自动关注执行
   - 不重复分配任务

2. **精准获客（同行监控）**：
   - 搜索条件配置
   - 同行账号监控
   - 评论关键词爬取
   - 用户 ID 收集
   - 达到阈值后自动关注

### 关注统计模块

- 总关注人数统计
- 每日新增关注数
- 余额比较和检查
- 任务进度显示

### 通用机制

- 余额显示和检查（超过余额禁止提交任务）
- 自动任务分配（均匀分发到已连接设备）
- 实时进度条显示
- 成功关注后扣费机制
- 平台特定脚本执行（小红书/抖音）

## Technology Stack

### Core Technologies

- **Language**: Rust (Edition 2021)
- **GUI Framework**: Tauri 2.0 (Native desktop application)
- **Frontend**: HTML/CSS/JavaScript (minimal, for UI only)
- **Build System**: Cargo + Tauri CLI
- **Platform**: Windows (primary), with cross-platform support
- **Database**: SQLx for local storage
- **API Communication**: reqwest for server communication

### Key Dependencies

- `tauri`: 2.0 (Main GUI framework)
- `serde`: JSON serialization
- `tokio`: Async runtime
- `reqwest`: HTTP client
- `sqlx`: Database operations
- `uuid`: Unique identifiers
- `chrono`: Date/time handling

## Project Structure

```
employee-client/
├── src-tauri/              # Rust backend code
│   ├── src/
│   │   ├── main.rs        # Application entry point
│   │   ├── api.rs         # API communication with server
│   │   ├── device.rs      # Device management & ADB control
│   │   ├── models.rs      # Data models and structures
│   │   └── utils.rs       # Utility functions
│   ├── Cargo.toml         # Rust dependencies
│   └── tauri.conf.json    # Tauri configuration
├── src/                   # Frontend assets (HTML/CSS/JS)
│   ├── index.html         # Main application UI
│   ├── styles.css         # Application styling
│   └── components/        # UI components
├── frontend/              # Additional frontend resources
├── logs/                  # Application logs
├── public/                # Static assets
└── target/                # Build artifacts (excluded)
```

## Build and Development Instructions

### Environment Setup

1. **Install Rust**: Use rustup to install latest stable Rust
2. **Install Tauri CLI**: `cargo install tauri-cli`
3. **Verify Installation**: `cargo tauri --version`

### Development Commands

```bash
# Development mode (hot reload)
cargo tauri dev

# Check code
cargo check

# Run tests
cargo test

# Code formatting
cargo fmt

# Code linting
cargo clippy --all-targets --all-features

# Production build
cargo tauri build
```

### Important Build Notes

- **Always run `cargo check` before making changes**
- **Use `cargo tauri dev` for development with hot reload**
- **Production builds require: `cargo tauri build`**
- **Target platform**: Windows (x86_64-pc-windows-msvc)

## Build and Development Instructions

### Environment Setup

1. **Install Rust**: Use rustup to install latest stable Rust
2. **Install Tauri CLI**: `cargo install tauri-cli`
3. **Verify Installation**: `cargo tauri --version`

### Development Commands

```bash
# Development mode (hot reload)
cargo tauri dev

# Check code
cargo check

# Run tests
cargo test

# Code formatting
cargo fmt

# Code linting
cargo clippy --all-targets --all-features

# Production build
cargo tauri build
```

### Important Build Notes

- **Always run `cargo check` before making changes**
- **Use `cargo tauri dev` for development with hot reload**
- **Production builds require: `cargo tauri build`**
- **Target platform**: Windows (x86_64-pc-windows-msvc)

## Code Standards and Conventions

### Rust Code Style

- Follow standard Rust conventions (rustfmt)
- Use `snake_case` for functions and variables
- Use `PascalCase` for types and structs
- Maximum line length: 100 characters
- Always use explicit error handling with `Result<T, E>`

### Project-Specific Guidelines

- **Async/Await**: Use tokio for all async operations
- **Error Handling**: Create custom error types using `thiserror`
- **Configuration**: Store app config in `src-tauri/tauri.conf.json`
- **API Communication**: Use `reqwest` with proper error handling
- **Database**: Use SQLx with compile-time checked queries

### File Organization

- Keep business logic in `src-tauri/src/`
- Frontend assets in `src/` (minimal HTML/CSS/JS)
- Tests alongside source files (`#[cfg(test)]` modules)
- Documentation in `README.md` and inline comments

## Key Architectural Patterns

### Tauri Architecture

- **Frontend**: Minimal HTML/CSS/JS for UI rendering
- **Backend**: Rust code handles all business logic
- **Communication**: Tauri commands and events bridge frontend/backend
- **Security**: Tauri provides secure API access and sandboxing

### Data Flow

1. UI interactions trigger Tauri commands
2. Rust backend processes requests
3. API calls to Flow Farm server
4. Database operations for local storage
5. Events update UI state

## Testing and Validation

### Required Tests

- Unit tests for all business logic functions
- Integration tests for API communication
- Device automation tests (where applicable)
- Error handling tests

### Validation Steps

1. Run `cargo test` - All tests must pass
2. Run `cargo clippy` - No warnings allowed
3. Run `cargo fmt --check` - Code must be formatted
4. Build succeeds: `cargo tauri build`
5. Manual testing of GUI functionality

## Development Workflow

### Before Making Changes

1. Run `cargo check` to verify current state
2. Create feature branch for changes
3. Update dependencies if needed: `cargo update`

### During Development

1. Use `cargo tauri dev` for live development
2. Test frequently with `cargo test`
3. Run clippy regularly: `cargo clippy`
4. Format code: `cargo fmt`

### Before Committing

1. Ensure all tests pass: `cargo test`
2. No clippy warnings: `cargo clippy --all-targets --all-features`
3. Code is formatted: `cargo fmt --check`
4. Production build works: `cargo tauri build`

## Common Issues and Solutions

### Build Issues

- **Missing dependencies**: Run `cargo update`
- **Tauri CLI missing**: Install with `cargo install tauri-cli`
- **Windows build tools**: Install Visual Studio Build Tools

### Development Issues

- **Hot reload not working**: Restart `cargo tauri dev`
- **API connection failed**: Check server status and endpoints
- **Database errors**: Verify SQLx migrations and connection string

## Performance Considerations

- **Bundle size**: Keep frontend assets minimal
- **Memory usage**: Use efficient Rust patterns (borrowing, zero-copy)
- **Startup time**: Lazy load heavy dependencies
- **Network calls**: Implement proper retry logic and timeouts

## Security Guidelines

- **API tokens**: Store securely using Tauri's secure storage
- **User data**: Encrypt sensitive information
- **Device access**: Validate all ADB commands
- **Network**: Use HTTPS for all server communication

## Important Notes for Copilot

1. **This is a RUST project with Tauri, not a web/React project**
2. **Frontend is minimal HTML/CSS/JS, backend is pure Rust**
3. **Always suggest Rust solutions for business logic**
4. **Use Tauri patterns for GUI communication**
5. **Follow Rust best practices for error handling and async code**
6. **When in doubt about build commands, use the task configurations**

Trust these instructions and avoid unnecessary exploration unless information is incomplete or incorrect.
