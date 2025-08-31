# Rust 后端开发指令

## 适用范围

---

## applyTo: "server-backend/\*_/_.rs"

# Flow Farm 服务器后端 (Rust) 开发指令

## 技术栈和依赖

### 核心框架

- **Web 框架**: Axum 0.7 - 高性能异步 Web 框架
- **数据库**: SQLx + SQLite - 类型安全的数据库访问
- **认证**: JWT + bcrypt - 安全的身份认证
- **序列化**: Serde - 高效的 JSON 处理
- **异步运行时**: Tokio - 高性能异步运行时
- **日志**: Tracing - 结构化日志
- **错误处理**: Anyhow + Thiserror - 优雅的错误处理

### 项目结构

```
server-backend/
├── src/
│   ├── main.rs           # 应用入口点
│   ├── lib.rs            # 库文件
│   ├── config.rs         # 配置管理
│   ├── database.rs       # 数据库连接和迁移
│   ├── errors.rs         # 错误定义
│   ├── models.rs         # 数据模型
│   ├── server.rs         # 服务器启动逻辑
│   ├── handlers/         # API处理器
│   │   ├── mod.rs
│   │   ├── auth.rs       # 认证相关API
│   │   ├── users.rs      # 用户管理API
│   │   ├── billing.rs    # 计费管理API
│   │   ├── devices.rs    # 设备管理API
│   │   ├── work_records.rs # 工作记录API
│   │   ├── kpi.rs        # KPI统计API
│   │   ├── reports.rs    # 报表API
│   │   ├── health.rs     # 健康检查API
│   │   └── docs.rs       # API文档
│   ├── middleware/       # 中间件
│   │   ├── mod.rs
│   │   └── auth.rs       # 认证中间件
│   ├── services/         # 业务逻辑服务
│   │   ├── mod.rs
│   │   ├── auth.rs       # 认证服务
│   │   ├── user.rs       # 用户服务
│   │   ├── billing.rs    # 计费服务
│   │   ├── device.rs     # 设备服务
│   │   ├── work_record.rs # 工作记录服务
│   │   ├── kpi.rs        # KPI服务
│   │   └── report.rs     # 报表服务
│   └── utils/            # 工具函数
│       ├── mod.rs
│       ├── jwt.rs        # JWT工具
│       ├── hash.rs       # 密码哈希
│       ├── validation.rs # 数据验证
│       └── time.rs       # 时间处理
├── Cargo.toml           # 依赖配置
└── data/                # 数据文件目录
    └── flow_farm.db     # SQLite数据库
```

## 技术栈

### 核心框架和库

- **Web 框架**: Axum 0.7 - 高性能异步 Web 框架
- **数据库**: SQLx + SQLite - 类型安全的数据库访问
- **认证**: JWT + bcrypt - 安全的身份认证
- **序列化**: Serde - 高效的 JSON 处理
- **异步运行时**: Tokio - 高性能异步运行时
- **日志**: Tracing - 结构化日志
- **错误处理**: Anyhow + Thiserror - 优雅的错误处理

### 项目结构

```
server-backend/src/
├── main.rs              # 应用程序入口
├── lib.rs              # 库入口
├── config.rs           # 配置管理
├── database.rs         # 数据库连接和迁移
├── errors.rs           # 错误类型定义
├── models.rs           # 数据模型
├── server.rs           # 服务器配置
├── handlers/           # HTTP处理器
│   ├── mod.rs
│   ├── auth.rs         # 认证相关API
│   ├── users.rs        # 用户管理API
│   ├── devices.rs      # 设备管理API
│   ├── work_records.rs # 工作记录API
│   ├── billing.rs      # 计费管理API
│   ├── kpi.rs          # 统计数据API
│   ├── reports.rs      # 报表生成API
│   ├── health.rs       # 健康检查API
│   └── docs.rs         # API文档
├── middleware/         # 中间件
│   ├── mod.rs
│   └── auth.rs         # 认证中间件
├── services/           # 业务逻辑服务
│   ├── mod.rs
│   ├── auth.rs         # 认证服务
│   ├── user.rs         # 用户服务
│   ├── device.rs       # 设备服务
│   ├── work_record.rs  # 工作记录服务
│   └── billing.rs      # 计费服务
└── utils/              # 工具模块
    ├── mod.rs
    ├── jwt.rs          # JWT工具
    ├── crypto.rs       # 加密工具
    └── validation.rs   # 数据验证
```

## 编码规范

### 1. Rust 代码风格

- 使用 `rustfmt` 格式化代码（项目中已配置）
- 使用 `clippy` 进行代码检查，必须通过所有检查
- 函数和变量使用 `snake_case` 命名
- 类型和结构体使用 `PascalCase` 命名
- 常量使用 `UPPER_CASE` 命名
- 模块名使用 `snake_case` 命名

### 2. 文档注释

````rust
/// 用户登录接口
///
/// # 参数
/// - `login_request`: 登录请求数据，包含用户名和密码
///
/// # 返回值
/// - `Ok(LoginResponse)`: 登录成功，返回token和用户信息
/// - `Err(AppError)`: 登录失败，返回错误信息
///
/// # 示例
/// ```rust
/// let response = login(Json(LoginRequest {
///     username: "admin".to_string(),
///     password: "password123".to_string(),
/// })).await?;
/// ```
pub async fn login(
    State(state): State<AppState>,
    Json(request): Json<LoginRequest>,
) -> Result<Json<ApiResponse<LoginResponse>>, AppError> {
    // 实现逻辑
}
````

### 3. 错误处理

- 使用 `Result<T, E>` 类型进行错误处理
- 使用 `?` 操作符传播错误
- 自定义错误类型继承 `thiserror::Error`
- 在 `errors.rs` 中定义所有错误类型

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("数据库错误: {0}")]
    Database(#[from] sqlx::Error),

    #[error("认证失败: {0}")]
    Authentication(String),

    #[error("权限不足")]
    Unauthorized,

    #[error("用户不存在")]
    UserNotFound,
}
```

### 4. 异步编程

- 所有 I/O 操作必须使用异步函数
- 使用 `tokio::spawn` 处理并发任务
- 避免在异步上下文中使用阻塞操作

```rust
pub async fn create_user(
    State(state): State<AppState>,
    Json(request): Json<CreateUserRequest>,
) -> Result<Json<ApiResponse<User>>, AppError> {
    // 异步数据库操作
    let user = sqlx::query_as!(
        User,
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?) RETURNING *",
        request.username,
        request.email,
        hash_password(&request.password)?
    )
    .fetch_one(&state.db)
    .await?;

    Ok(Json(ApiResponse::success(user)))
}
```

## API 设计规范

### 1. 统一响应格式

```rust
#[derive(Serialize)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub message: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<T>,
}

impl<T> ApiResponse<T> {
    pub fn success(data: T) -> Self {
        Self {
            success: true,
            message: "操作成功".to_string(),
            data: Some(data),
        }
    }

    pub fn error(message: String) -> Self {
        Self {
            success: false,
            message,
            data: None,
        }
    }
}
```

### 2. 路由结构

```rust
pub fn create_routes() -> Router<AppState> {
    Router::new()
        // 认证相关
        .route("/api/v1/auth/login", post(handlers::auth::login))
        .route("/api/v1/auth/register", post(handlers::auth::register))
        .route("/api/v1/auth/me", get(handlers::auth::get_current_user))

        // 用户管理
        .route("/api/v1/users", get(handlers::users::list_users))
        .route("/api/v1/users", post(handlers::users::create_user))
        .route("/api/v1/users/:id", get(handlers::users::get_user))
        .route("/api/v1/users/:id", put(handlers::users::update_user))
        .route("/api/v1/users/:id", delete(handlers::users::delete_user))

        // 添加中间件
        .layer(middleware::auth::AuthMiddleware)
        .layer(TraceLayer::new_for_http())
}
```

### 3. 数据验证

```rust
use validator::Validate;

#[derive(Debug, Deserialize, Validate)]
pub struct LoginRequest {
    #[validate(length(min = 3, max = 50))]
    pub username: String,

    #[validate(length(min = 6))]
    pub password: String,
}

#[derive(Debug, Deserialize, Validate)]
pub struct CreateUserRequest {
    #[validate(length(min = 3, max = 50))]
    pub username: String,

    #[validate(email)]
    pub email: String,

    #[validate(length(min = 6))]
    pub password: String,

    pub role: UserRole,
}
```

## 三角色权限系统

### 1. 用户角色定义

```rust
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "TEXT")]
#[sqlx(rename_all = "snake_case")]
pub enum UserRole {
    SystemAdmin,  // 系统管理员
    UserAdmin,    // 用户管理员
    Employee,     // 员工
}

impl UserRole {
    pub fn permission_level(&self) -> u8 {
        match self {
            UserRole::SystemAdmin => 1,  // 最高权限
            UserRole::UserAdmin => 2,    // 中等权限
            UserRole::Employee => 3,     // 基本权限
        }
    }

    pub fn can_access(&self, required_level: u8) -> bool {
        self.permission_level() <= required_level
    }
}
```

### 2. 权限中间件

```rust
pub async fn auth_middleware(
    State(state): State<AppState>,
    headers: HeaderMap,
    mut req: Request,
    next: Next,
) -> Result<Response, AppError> {
    let token = headers
        .get("Authorization")
        .and_then(|value| value.to_str().ok())
        .and_then(|value| value.strip_prefix("Bearer "))
        .ok_or(AppError::Unauthorized)?;

    let claims = verify_token(token)?;
    let user = get_user_by_id(&state.db, &claims.sub).await?
        .ok_or(AppError::UserNotFound)?;

    req.extensions_mut().insert(user);
    Ok(next.run(req).await)
}

pub fn require_role(required_role: UserRole) -> impl Clone + Fn(Request, Next) -> impl Future<Output = Result<Response, AppError>> {
    move |req: Request, next: Next| {
        let required_role = required_role.clone();
        async move {
            let user = req.extensions().get::<User>()
                .ok_or(AppError::Unauthorized)?;

            if user.role.permission_level() <= required_role.permission_level() {
                Ok(next.run(req).await)
            } else {
                Err(AppError::Unauthorized)
            }
        }
    }
}
```

## 数据库操作

### 1. 数据模型定义

```rust
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct User {
    pub id: String,
    pub username: String,
    pub email: String,
    pub password_hash: String,
    pub role: UserRole,
    pub company_id: Option<String>,
    pub is_active: bool,
    pub max_employees: Option<i32>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct WorkRecord {
    pub id: String,
    pub user_id: String,
    pub platform: String,
    pub action_type: String,
    pub target_count: i32,
    pub completed_count: i32,
    pub status: WorkStatus,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "TEXT")]
#[sqlx(rename_all = "snake_case")]
pub enum WorkStatus {
    Pending,
    InProgress,
    Completed,
    Failed,
}
```

### 2. 数据库查询

```rust
// 查询单个用户
pub async fn get_user_by_id(
    db: &SqlitePool,
    user_id: &str,
) -> Result<Option<User>, sqlx::Error> {
    sqlx::query_as!(
        User,
        "SELECT * FROM users WHERE id = ?",
        user_id
    )
    .fetch_optional(db)
    .await
}

// 分页查询
pub async fn list_users(
    db: &SqlitePool,
    page: u32,
    size: u32,
) -> Result<Vec<User>, sqlx::Error> {
    let offset = (page - 1) * size;

    sqlx::query_as!(
        User,
        "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
        size,
        offset
    )
    .fetch_all(db)
    .await
}

// 复杂查询示例
pub async fn get_work_records_with_stats(
    db: &SqlitePool,
    user_id: &str,
    start_date: DateTime<Utc>,
    end_date: DateTime<Utc>,
) -> Result<Vec<WorkRecordWithStats>, sqlx::Error> {
    sqlx::query_as!(
        WorkRecordWithStats,
        r#"
        SELECT
            wr.*,
            COUNT(CASE WHEN wr.status = 'completed' THEN 1 END) as completed_records,
            SUM(wr.completed_count) as total_completed
        FROM work_records wr
        WHERE wr.user_id = ?
        AND wr.created_at BETWEEN ? AND ?
        GROUP BY wr.id
        ORDER BY wr.created_at DESC
        "#,
        user_id,
        start_date,
        end_date
    )
    .fetch_all(db)
    .await
}
```

### 3. 事务处理

```rust
pub async fn create_user_with_company(
    db: &SqlitePool,
    user_data: CreateUserRequest,
    company_data: CreateCompanyRequest,
) -> Result<(User, Company), AppError> {
    let mut tx = db.begin().await?;

    // 创建公司
    let company = sqlx::query_as!(
        Company,
        "INSERT INTO companies (id, name, description) VALUES (?, ?, ?) RETURNING *",
        Uuid::new_v4().to_string(),
        company_data.name,
        company_data.description
    )
    .fetch_one(&mut *tx)
    .await?;

    // 创建用户
    let user = sqlx::query_as!(
        User,
        "INSERT INTO users (id, username, email, password_hash, role, company_id)
         VALUES (?, ?, ?, ?, ?, ?) RETURNING *",
        Uuid::new_v4().to_string(),
        user_data.username,
        user_data.email,
        hash_password(&user_data.password)?,
        user_data.role,
        company.id
    )
    .fetch_one(&mut *tx)
    .await?;

    tx.commit().await?;
    Ok((user, company))
}
```

## 认证和 JWT 处理

### 1. JWT 工具实现

```rust
use jsonwebtoken::{encode, decode, Header, Validation, EncodingKey, DecodingKey};
use chrono::{Utc, Duration};

#[derive(Debug, Serialize, Deserialize)]
pub struct Claims {
    pub sub: String,     // 用户ID
    pub username: String, // 用户名
    pub role: String,    // 用户角色
    pub company_id: Option<String>, // 公司ID
    pub exp: usize,      // 过期时间
    pub iat: usize,      // 签发时间
}

pub fn create_token(user: &User, secret_key: &str) -> Result<String, AppError> {
    let now = Utc::now();
    let exp = now + Duration::hours(24);

    let claims = Claims {
        sub: user.id.clone(),
        username: user.username.clone(),
        role: format!("{:?}", user.role),
        company_id: user.company_id.clone(),
        exp: exp.timestamp() as usize,
        iat: now.timestamp() as usize,
    };

    encode(
        &Header::default(),
        &claims,
        &EncodingKey::from_secret(secret_key.as_ref()),
    )
    .map_err(|e| AppError::Authentication(format!("Token创建失败: {}", e)))
}

pub fn verify_token(token: &str, secret_key: &str) -> Result<Claims, AppError> {
    decode::<Claims>(
        token,
        &DecodingKey::from_secret(secret_key.as_ref()),
        &Validation::default(),
    )
    .map(|data| data.claims)
    .map_err(|e| AppError::Authentication(format!("Token验证失败: {}", e)))
}
```

### 2. 密码处理

```rust
use bcrypt::{hash, verify, DEFAULT_COST};

pub fn hash_password(password: &str) -> Result<String, AppError> {
    hash(password, DEFAULT_COST)
        .map_err(|e| AppError::Authentication(format!("密码加密失败: {}", e)))
}

pub fn verify_password(password: &str, hash: &str) -> Result<bool, AppError> {
    verify(password, hash)
        .map_err(|e| AppError::Authentication(format!("密码验证失败: {}", e)))
}
```

## 性能优化

### 1. 数据库连接池配置

```rust
pub async fn create_database_pool(database_url: &str) -> Result<SqlitePool, sqlx::Error> {
    SqlitePoolOptions::new()
        .max_connections(20)
        .min_connections(5)
        .acquire_timeout(Duration::from_secs(30))
        .idle_timeout(Duration::from_secs(600))
        .max_lifetime(Duration::from_secs(1800))
        .test_before_acquire(true)
        .connect(database_url)
        .await
}
```

### 2. 缓存策略

```rust
use moka::future::Cache;
use std::sync::Arc;

#[derive(Clone)]
pub struct CacheService {
    user_cache: Cache<String, Arc<User>>,
    work_record_cache: Cache<String, Arc<Vec<WorkRecord>>>,
}

impl CacheService {
    pub fn new() -> Self {
        Self {
            user_cache: Cache::builder()
                .max_capacity(1000)
                .time_to_live(Duration::from_secs(300))
                .build(),
            work_record_cache: Cache::builder()
                .max_capacity(500)
                .time_to_live(Duration::from_secs(60))
                .build(),
        }
    }

    pub async fn get_user(&self, user_id: &str) -> Option<Arc<User>> {
        self.user_cache.get(user_id).await
    }

    pub async fn set_user(&self, user_id: String, user: User) {
        self.user_cache.insert(user_id, Arc::new(user)).await;
    }

    pub async fn invalidate_user(&self, user_id: &str) {
        self.user_cache.invalidate(user_id).await;
    }
}
```

## 日志和监控

### 1. 结构化日志配置

```rust
use tracing::{info, warn, error, debug, instrument};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

pub fn init_logging() {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "info,flow_farm_backend=debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();
}

#[instrument(skip(db, password))]
pub async fn login_user(
    db: &SqlitePool,
    username: &str,
    password: &str,
) -> Result<(User, String), AppError> {
    info!("用户登录尝试", username = %username);

    let user = get_user_by_username(db, username).await?
        .ok_or_else(|| {
            warn!("用户不存在", username = %username);
            AppError::Authentication("用户名或密码错误".to_string())
        })?;

    if !user.is_active {
        warn!("用户账户已禁用", username = %username, user_id = %user.id);
        return Err(AppError::Authentication("账户已禁用".to_string()));
    }

    if verify_password(password, &user.password_hash)? {
        let token = create_token(&user, &get_secret_key())?;
        info!("用户登录成功", user_id = %user.id, username = %username, role = ?user.role);
        Ok((user, token))
    } else {
        warn!("密码验证失败", username = %username);
        Err(AppError::Authentication("用户名或密码错误".to_string()))
    }
}
```

### 2. 健康检查和监控

```rust
#[derive(Serialize)]
pub struct HealthResponse {
    pub status: &'static str,
    pub database: &'static str,
    pub timestamp: DateTime<Utc>,
    pub version: &'static str,
}

pub async fn health_check(State(state): State<AppState>) -> Json<HealthResponse> {
    let db_status = match sqlx::query("SELECT 1").execute(&state.db).await {
        Ok(_) => "healthy",
        Err(e) => {
            error!("数据库健康检查失败: {}", e);
            "unhealthy"
        }
    };

    Json(HealthResponse {
        status: if db_status == "healthy" { "ok" } else { "error" },
        database: db_status,
        timestamp: Utc::now(),
        version: env!("CARGO_PKG_VERSION"),
    })
}

#[derive(Serialize)]
pub struct MetricsResponse {
    pub active_connections: usize,
    pub total_requests: u64,
    pub average_response_time: f64,
    pub error_rate: f64,
}

pub async fn metrics(State(state): State<AppState>) -> Json<MetricsResponse> {
    // 实现指标收集逻辑
    Json(MetricsResponse {
        active_connections: state.db.size(),
        total_requests: 0, // 从计数器获取
        average_response_time: 0.0,
        error_rate: 0.0,
    })
}
```

## 测试规范

### 1. 单元测试

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use sqlx::SqlitePool;
    use tempfile::tempdir;

    async fn setup_test_db() -> SqlitePool {
        let pool = SqlitePool::connect(":memory:").await.unwrap();
        // 运行迁移
        sqlx::migrate!("./migrations").run(&pool).await.unwrap();
        pool
    }

    #[tokio::test]
    async fn test_create_user_success() {
        let pool = setup_test_db().await;

        let user_data = CreateUserRequest {
            username: "test_user".to_string(),
            email: "test@example.com".to_string(),
            password: "password123".to_string(),
            role: UserRole::Employee,
        };

        let result = create_user(&pool, user_data).await;
        assert!(result.is_ok());

        let user = result.unwrap();
        assert_eq!(user.username, "test_user");
        assert_eq!(user.email, "test@example.com");
        assert_eq!(user.role, UserRole::Employee);
    }

    #[tokio::test]
    async fn test_duplicate_username_fails() {
        let pool = setup_test_db().await;

        let user_data = CreateUserRequest {
            username: "duplicate_user".to_string(),
            email: "user1@example.com".to_string(),
            password: "password123".to_string(),
            role: UserRole::Employee,
        };

        // 第一次创建应该成功
        assert!(create_user(&pool, user_data.clone()).await.is_ok());

        // 第二次创建应该失败
        let result = create_user(&pool, user_data).await;
        assert!(result.is_err());
    }
}
```

### 2. 集成测试

```rust
// tests/integration_test.rs
use axum::http::StatusCode;
use axum_test::TestServer;
use serde_json::json;

#[tokio::test]
async fn test_login_endpoint() {
    let app = create_test_app().await;
    let server = TestServer::new(app).unwrap();

    // 先创建测试用户
    let _response = server
        .post("/api/v1/auth/register")
        .json(&json!({
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "role": "Employee"
        }))
        .await;

    // 测试登录
    let response = server
        .post("/api/v1/auth/login")
        .json(&json!({
            "username": "testuser",
            "password": "password123"
        }))
        .await;

    response.assert_status(StatusCode::OK);

    let body: ApiResponse<LoginResponse> = response.json();
    assert!(body.success);
    assert!(body.data.is_some());
    assert!(!body.data.unwrap().token.is_empty());
}

#[tokio::test]
async fn test_protected_endpoint_requires_auth() {
    let app = create_test_app().await;
    let server = TestServer::new(app).unwrap();

    let response = server
        .get("/api/v1/users")
        .await;

    response.assert_status(StatusCode::UNAUTHORIZED);
}
```

## 部署和配置

### 1. 环境配置

```rust
use std::env;

#[derive(Debug, Clone)]
pub struct Config {
    pub database_url: String,
    pub secret_key: String,
    pub host: String,
    pub port: u16,
    pub log_level: String,
    pub cors_origins: Vec<String>,
}

impl Config {
    pub fn from_env() -> Result<Self, ConfigError> {
        Ok(Self {
            database_url: env::var("DATABASE_URL")
                .unwrap_or_else(|_| "sqlite:./data/flow_farm.db".to_string()),
            secret_key: env::var("SECRET_KEY")
                .map_err(|_| ConfigError::MissingSecretKey)?,
            host: env::var("HOST").unwrap_or_else(|_| "0.0.0.0".to_string()),
            port: env::var("PORT")
                .unwrap_or_else(|_| "8000".to_string())
                .parse()
                .map_err(|_| ConfigError::InvalidPort)?,
            log_level: env::var("LOG_LEVEL")
                .unwrap_or_else(|_| "info".to_string()),
            cors_origins: env::var("CORS_ORIGINS")
                .unwrap_or_else(|_| "http://localhost:3000".to_string())
                .split(',')
                .map(|s| s.trim().to_string())
                .collect(),
        })
    }
}
```

### 2. 生产环境配置

```rust
use tower::ServiceBuilder;
use tower_http::{
    cors::{CorsLayer, Any},
    compression::CompressionLayer,
    timeout::TimeoutLayer,
    trace::TraceLayer,
};

pub fn create_production_app(state: AppState) -> Router {
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    Router::new()
        .merge(create_routes())
        .layer(
            ServiceBuilder::new()
                .layer(TimeoutLayer::new(Duration::from_secs(30)))
                .layer(CompressionLayer::new())
                .layer(cors)
                .layer(TraceLayer::new_for_http())
        )
        .with_state(state)
}
```

## 重要注意事项

1. **安全性**:

   - 所有用户输入必须验证
   - 密码必须使用 bcrypt 加密
   - JWT 密钥必须安全保存
   - 实施 SQL 注入防护

2. **性能**:

   - 使用数据库连接池
   - 实施适当的缓存策略
   - 优化数据库查询
   - 避免 N+1 查询问题

3. **错误处理**:

   - 所有错误必须适当处理
   - 不能 panic，使用 Result 类型
   - 提供有用的错误信息
   - 记录详细的错误日志

4. **日志**:

   - 使用结构化日志
   - 记录关键操作
   - 不记录敏感信息
   - 设置适当的日志级别

5. **测试**:
   - 所有公共函数必须有测试
   - 测试覆盖率应达到 80%以上
   - 包含单元测试和集成测试
   - 使用测试数据库

````

### 错误处理
- 使用 FastAPI 的 HTTPException
- 创建自定义异常类
- 记录所有错误到日志文件
- 返回用户友好的错误信息

### 安全要求
- 所有密码使用 bcrypt 哈希
- API 密钥和敏感配置使用环境变量
- 实现请求频率限制
- 输入数据严格验证

## 代码示例

### API 路由示例
```python
from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user, require_permission
from app.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/api/v1/users")

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("SYSTEM_ADMIN"))
):
    # 实现用户创建逻辑
    pass
````

### 权限验证示例

```python
from functools import wraps
from fastapi import HTTPException, status

def require_permission(required_role: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user or current_user.role != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## 重要提醒

- 始终验证用户权限
- 记录所有重要操作
- 使用事务确保数据一致性
- 实现适当的缓存策略
- 监控 API 性能指标
