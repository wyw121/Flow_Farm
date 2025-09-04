# AI Coding Agent Instructions for Flow Farm Employee Client

## Project Context

This is the **Flow Farm Employee Client** - a desktop GUI application for employee roles built with **Rust** and **Tauri framework**. The client provides device automation management, task execution (contact management and precision customer acquisition), and social media operations primarily for Xiaohongshu and Douyin platforms.

## Core Architecture

### Technology Stack
- **Backend**: Rust 2021 + Tauri 2.0 (native desktop GUI)
- **Frontend**: Minimal HTML/CSS/JavaScript for UI only
- **Database**: SQLx + SQLite for local storage
- **API**: reqwest for server communication
- **Build**: Cargo + Tauri CLI

### Key Requirements
- **Native GUI Application**: Not a web app - uses Tauri for desktop GUI
- **Business Logic in Rust**: All core functionality implemented in Rust backend
- **Minimal Frontend**: HTML/CSS/JS only for UI rendering and user interaction
- **Employee-focused Features**: Device management, task automation, social media operations

## Development Guidelines

### Code Organization
```
src-tauri/src/          # All Rust business logic
├── main.rs            # Application entry point and Tauri setup
├── api.rs             # Server communication and HTTP client
├── device.rs          # ADB device management (1-10 devices)
├── models.rs          # Data structures and types
└── utils.rs           # Helper functions and utilities

src/                   # Frontend UI assets (minimal)
├── index.html         # Main application interface
├── styles.css         # Application styling
└── components/        # UI components (HTML/CSS/JS)
```

### Priority Features to Implement

1. **Device Management Module** (Critical)
   - Support up to 10 simultaneous device connections
   - Real-time device status monitoring (connected/disconnected)
   - ADB command integration for device control
   - Auto task assignment to connected devices

2. **Task Management System** (Critical)
   - **Contact Management**: CSV/text file upload, server data import, automated follow operations
   - **Precision Customer Acquisition**: Competitor monitoring, comment keyword scraping, user ID collection, auto-follow when threshold reached
   - Platform-specific scripts (Xiaohongshu/Douyin priority)
   - Non-duplicate task distribution algorithm

3. **Balance and Billing Integration** (Important)
   - Real-time balance display from server
   - Pre-task balance verification (block if insufficient)
   - Success-based billing (charge only after successful follow)
   - Server database synchronization

4. **User Interface** (Important)
   - Modern desktop application design
   - Platform selection (dropdown: Xiaohongshu/Douyin)
   - Real-time progress bars and status updates
   - Device list with connection status indicators
   - Task progress monitoring dashboard

### Development Workflow

#### Before Starting Any Task
1. **Read Project Instructions**: Always check `.github/copilot-instructions.md` and relevant `.instructions.md` files
2. **Run Code Check**: Execute `cargo check` to verify current state
3. **Check Build Tasks**: Use available VS Code tasks for development
4. **Understand Architecture**: This is Rust+Tauri, not React/web framework

#### Implementation Pattern
1. **Implement in Rust First**: All business logic goes in `src-tauri/src/`
2. **Create Tauri Commands**: Use `#[tauri::command]` for frontend-accessible functions
3. **Add Error Handling**: Use `Result<T, E>` and custom error types
4. **Create Minimal UI**: HTML/CSS/JS in `src/` for user interaction only
5. **Test Integration**: Ensure frontend can call Rust commands via `invoke()`

#### Code Standards
- **Rust**: Follow Rust 2021 edition standards, use `snake_case` for functions, `PascalCase` for types
- **Error Handling**: Always use `Result<T, E>`, create custom error types with `thiserror`
- **Async Operations**: Use `tokio` runtime, proper `async/await` patterns
- **Frontend**: Keep minimal - only UI and user interaction, call Rust for all business logic
- **Comments**: Document complex business logic, especially device management and task allocation

#### Build Commands (Use VS Code Tasks)
- **Development**: `cargo tauri dev` (hot reload)
- **Code Check**: `cargo check` (before changes)
- **Testing**: `cargo test`
- **Linting**: `cargo clippy --all-targets --all-features`
- **Formatting**: `cargo fmt`
- **Production**: `cargo tauri build`

### Common Pitfalls to Avoid
1. **Don't treat this as a web project** - It's a native Rust desktop app
2. **Don't put business logic in JavaScript** - All logic goes in Rust
3. **Don't forget error handling** - Use proper `Result<T, E>` patterns
4. **Don't skip the build check** - Always run `cargo check` before major changes
5. **Don't ignore the task requirements** - Focus on employee-specific functionality

### Quick Start Checklist
- [ ] Read `.github/copilot-instructions.md` and path-specific instructions
- [ ] Run `cargo check` to verify project state
- [ ] Understand this is Rust+Tauri (not React/web)
- [ ] Implement business logic in `src-tauri/src/`
- [ ] Create Tauri commands for frontend communication
- [ ] Test with `cargo tauri dev`
- [ ] Follow the available VS Code tasks for build/test operations

## Success Criteria
When implementing features, ensure:
1. **Code compiles** with `cargo check`
2. **Tests pass** with `cargo test`
3. **No clippy warnings** with `cargo clippy`
4. **UI works** with `cargo tauri dev`
5. **Follows project architecture** (Rust backend, minimal frontend)
6. **Implements employee-specific requirements** (device management, task automation, social media operations)

Trust these instructions and refer to the existing project structure. Focus on the employee client requirements and maintain the Rust+Tauri architecture throughout development.
