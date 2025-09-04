# Rust Development Prompts for Tauri

## Tauri Command Development

### Basic Command Structure
```prompt
创建 Tauri 命令，遵循以下模式：
```rust
#[tauri::command]
async fn command_name(param: Type) -> Result<ReturnType, String> {
    // 实现逻辑
    // 错误处理
    // 返回结果
}
```
要求：
1. 使用 Result 类型进行错误处理
2. 异步操作使用 async/await
3. 错误信息对用户友好
4. 添加适当的日志记录
```

### State Management
```prompt
实现 Tauri 状态管理：
```rust
#[derive(Default)]
struct AppState {
    // 状态字段
}

// 在 main.rs 中注册状态
fn main() {
    tauri::Builder::default()
        .manage(AppState::default())
        .invoke_handler(tauri::generate_handler![command_name])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```
包括状态更新、并发访问控制、状态持久化
```

## Error Handling Patterns

### Custom Error Types
```prompt
使用 thiserror 创建自定义错误类型：
```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("设备连接失败: {0}")]
    DeviceConnectionError(String),

    #[error("API 调用失败: {0}")]
    ApiError(String),

    #[error("数据库操作失败: {0}")]
    DatabaseError(String),

    #[error("文件操作失败: {0}")]
    FileError(String),
}

impl From<AppError> for String {
    fn from(error: AppError) -> Self {
        error.to_string()
    }
}
```
```

## Async Programming Patterns

### HTTP Client with Error Handling
```prompt
实现带有错误处理的 HTTP 客户端：
```rust
use reqwest;
use serde::{Deserialize, Serialize};

async fn api_call<T: for<'de> Deserialize<'de>>(
    endpoint: &str,
    payload: Option<&impl Serialize>
) -> Result<T, AppError> {
    let client = reqwest::Client::new();
    let mut request = client.post(&format!("{}{}", BASE_URL, endpoint));

    if let Some(data) = payload {
        request = request.json(data);
    }

    let response = request.send().await
        .map_err(|e| AppError::ApiError(e.to_string()))?;

    if response.status().is_success() {
        response.json().await
            .map_err(|e| AppError::ApiError(e.to_string()))
    } else {
        Err(AppError::ApiError(response.status().to_string()))
    }
}
```
```

## Database Integration

### SQLx Pattern
```prompt
使用 SQLx 进行数据库操作：
```rust
use sqlx::{SqlitePool, Row};

pub async fn setup_database() -> Result<SqlitePool, AppError> {
    let pool = SqlitePool::connect("sqlite:app.db").await
        .map_err(|e| AppError::DatabaseError(e.to_string()))?;

    // 运行迁移
    sqlx::migrate!("./migrations").run(&pool).await
        .map_err(|e| AppError::DatabaseError(e.to_string()))?;

    Ok(pool)
}

pub async fn insert_record(
    pool: &SqlitePool,
    data: &RecordData
) -> Result<i64, AppError> {
    let row = sqlx::query!(
        "INSERT INTO table_name (field1, field2) VALUES (?, ?) RETURNING id",
        data.field1,
        data.field2
    )
    .fetch_one(pool)
    .await
    .map_err(|e| AppError::DatabaseError(e.to_string()))?;

    Ok(row.id)
}
```
```
