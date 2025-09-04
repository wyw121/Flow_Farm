# Flow Farm Employee Client - GitHub Copilot Instructions

## Project Overview

Flow Farm Employee Client is a modern desktop application built with **Rust** and **Tauri framework** for native GUI development. This is a standalone employee management and automation client that provides:

- Employee authentication and authorization
- Device automation management via ADB
- Task execution and monitoring
- Real-time data synchronization with server
- Modern native GUI using Tauri (Rust + HTML/CSS/JS)

**Important**: This project uses **native Rust GUI with Tauri**, NOT React.js or web-based frameworks.

## Technology Stack

### Core Technologies

- **Language**: Rust (Edition 2021)
- **GUI Framework**: Tauri 2.0 (Native desktop application)
- **Frontend**: HTML/CSS/JavaScript (minimal, for UI only)
- **Build System**: Cargo + Tauri CLI
- **Platform**: Windows (primary), with cross-platform support

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
│   │   ├── api.rs         # API communication
│   │   ├── device.rs      # Device management
│   │   └── models.rs      # Data models
│   ├── Cargo.toml         # Rust dependencies
│   └── tauri.conf.json    # Tauri configuration
├── src/                   # Frontend assets (HTML/CSS/JS)
├── logs/                  # Application logs
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
