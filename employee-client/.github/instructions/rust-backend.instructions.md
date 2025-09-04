---
applyTo: "src-tauri/**/*.rs"
---

# Rust Backend Development Instructions

## Code Style

- Use Rust 2021 edition features
- Implement proper error handling with custom error types
- Use `async/await` with tokio runtime
- Follow Rust naming conventions strictly

## Tauri Specific

- Define all frontend-accessible functions as Tauri commands
- Use `#[tauri::command]` macro for exported functions
- Handle all errors properly in command functions
- Use Tauri's state management for shared data

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
