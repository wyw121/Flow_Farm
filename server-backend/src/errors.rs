use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde::{Deserialize, Serialize};
use thiserror::Error;

/// 统一的错误响应格式
#[derive(Debug, Serialize, Deserialize)]
pub struct ErrorResponse {
    /// 错误代码（用于前端精确处理）
    pub code: u32,
    /// 用户友好的错误消息
    pub message: String,
    /// 详细的错误信息（可选，开发环境使用）
    #[serde(skip_serializing_if = "Option::is_none")]
    pub details: Option<String>,
    /// 时间戳
    pub timestamp: i64,
}

impl ErrorResponse {
    pub fn new(code: u32, message: impl Into<String>) -> Self {
        Self {
            code,
            message: message.into(),
            details: None,
            timestamp: chrono::Utc::now().timestamp(),
        }
    }

    pub fn with_details(mut self, details: impl Into<String>) -> Self {
        self.details = Some(details.into());
        self
    }
}

/// 错误代码定义
/// - 1000-1999: 认证和授权错误
/// - 2000-2999: 数据验证错误
/// - 3000-3999: 数据库操作错误
/// - 4000-4999: 业务逻辑错误
/// - 5000-5999: 外部服务错误
/// - 9000-9999: 内部服务器错误
pub mod error_codes {
    // 认证和授权错误 (1000-1999)
    pub const AUTH_INVALID_CREDENTIALS: u32 = 1001;
    pub const AUTH_TOKEN_EXPIRED: u32 = 1002;
    pub const AUTH_TOKEN_INVALID: u32 = 1003;
    pub const AUTH_UNAUTHORIZED: u32 = 1004;
    pub const AUTH_FORBIDDEN: u32 = 1005;
    pub const AUTH_USER_NOT_FOUND: u32 = 1006;
    pub const AUTH_DUPLICATE_USERNAME: u32 = 1007;

    // 数据验证错误 (2000-2999)
    pub const VALIDATION_INVALID_INPUT: u32 = 2001;
    pub const VALIDATION_MISSING_FIELD: u32 = 2002;
    pub const VALIDATION_INVALID_FORMAT: u32 = 2003;
    pub const VALIDATION_OUT_OF_RANGE: u32 = 2004;

    // 数据库操作错误 (3000-3999)
    pub const DATABASE_CONNECTION_ERROR: u32 = 3001;
    pub const DATABASE_QUERY_ERROR: u32 = 3002;
    pub const DATABASE_NOT_FOUND: u32 = 3003;
    pub const DATABASE_CONFLICT: u32 = 3004;
    pub const DATABASE_CONSTRAINT_VIOLATION: u32 = 3005;

    // 业务逻辑错误 (4000-4999)
    pub const BUSINESS_INSUFFICIENT_BALANCE: u32 = 4001;
    pub const BUSINESS_DEVICE_LIMIT_EXCEEDED: u32 = 4002;
    pub const BUSINESS_TASK_NOT_FOUND: u32 = 4003;
    pub const BUSINESS_DEVICE_NOT_FOUND: u32 = 4004;
    pub const BUSINESS_INVALID_STATE: u32 = 4005;
    pub const BUSINESS_OPERATION_NOT_ALLOWED: u32 = 4006;

    // 外部服务错误 (5000-5999)
    pub const EXTERNAL_SERVICE_UNAVAILABLE: u32 = 5001;
    pub const EXTERNAL_API_ERROR: u32 = 5002;

    // 内部服务器错误 (9000-9999)
    pub const INTERNAL_SERVER_ERROR: u32 = 9001;
    pub const INTERNAL_UNKNOWN_ERROR: u32 = 9999;
}

/// 统一的应用错误类型
#[derive(Error, Debug)]
pub enum AppError {
    // 认证和授权错误
    #[error("用户名或密码错误")]
    InvalidCredentials,

    #[error("Token已过期")]
    TokenExpired,

    #[error("Token无效")]
    TokenInvalid,

    #[error("未授权访问")]
    Unauthorized,

    #[error("权限不足")]
    Forbidden,

    #[error("用户不存在: {0}")]
    UserNotFound(String),

    #[error("用户名已存在: {0}")]
    DuplicateUsername(String),

    // 数据验证错误
    #[error("输入数据无效: {0}")]
    InvalidInput(String),

    #[error("缺少必填字段: {0}")]
    MissingField(String),

    #[error("数据格式错误: {0}")]
    InvalidFormat(String),

    #[error("数据超出范围: {0}")]
    OutOfRange(String),

    // 数据库操作错误
    #[error("数据库连接失败")]
    DatabaseConnection,

    #[error("数据库查询错误: {0}")]
    DatabaseQuery(String),

    #[error("资源未找到: {0}")]
    NotFound(String),

    #[error("数据冲突: {0}")]
    Conflict(String),

    #[error("约束违反: {0}")]
    ConstraintViolation(String),

    // 业务逻辑错误
    #[error("余额不足")]
    InsufficientBalance,

    #[error("设备数量已达上限")]
    DeviceLimitExceeded,

    #[error("任务不存在: {0}")]
    TaskNotFound(String),

    #[error("设备不存在: {0}")]
    DeviceNotFound(String),

    #[error("状态无效: {0}")]
    InvalidState(String),

    #[error("操作不允许: {0}")]
    OperationNotAllowed(String),

    // 外部服务错误
    #[error("外部服务不可用: {0}")]
    ServiceUnavailable(String),

    #[error("外部API调用失败: {0}")]
    ExternalApiError(String),

    // 内部错误
    #[error("内部服务器错误: {0}")]
    Internal(String),

    #[error("未知错误: {0}")]
    Unknown(String),
}

impl AppError {
    /// 获取错误代码
    pub fn error_code(&self) -> u32 {
        use error_codes::*;
        match self {
            // 认证和授权
            AppError::InvalidCredentials => AUTH_INVALID_CREDENTIALS,
            AppError::TokenExpired => AUTH_TOKEN_EXPIRED,
            AppError::TokenInvalid => AUTH_TOKEN_INVALID,
            AppError::Unauthorized => AUTH_UNAUTHORIZED,
            AppError::Forbidden => AUTH_FORBIDDEN,
            AppError::UserNotFound(_) => AUTH_USER_NOT_FOUND,
            AppError::DuplicateUsername(_) => AUTH_DUPLICATE_USERNAME,

            // 数据验证
            AppError::InvalidInput(_) => VALIDATION_INVALID_INPUT,
            AppError::MissingField(_) => VALIDATION_MISSING_FIELD,
            AppError::InvalidFormat(_) => VALIDATION_INVALID_FORMAT,
            AppError::OutOfRange(_) => VALIDATION_OUT_OF_RANGE,

            // 数据库
            AppError::DatabaseConnection => DATABASE_CONNECTION_ERROR,
            AppError::DatabaseQuery(_) => DATABASE_QUERY_ERROR,
            AppError::NotFound(_) => DATABASE_NOT_FOUND,
            AppError::Conflict(_) => DATABASE_CONFLICT,
            AppError::ConstraintViolation(_) => DATABASE_CONSTRAINT_VIOLATION,

            // 业务逻辑
            AppError::InsufficientBalance => BUSINESS_INSUFFICIENT_BALANCE,
            AppError::DeviceLimitExceeded => BUSINESS_DEVICE_LIMIT_EXCEEDED,
            AppError::TaskNotFound(_) => BUSINESS_TASK_NOT_FOUND,
            AppError::DeviceNotFound(_) => BUSINESS_DEVICE_NOT_FOUND,
            AppError::InvalidState(_) => BUSINESS_INVALID_STATE,
            AppError::OperationNotAllowed(_) => BUSINESS_OPERATION_NOT_ALLOWED,

            // 外部服务
            AppError::ServiceUnavailable(_) => EXTERNAL_SERVICE_UNAVAILABLE,
            AppError::ExternalApiError(_) => EXTERNAL_API_ERROR,

            // 内部错误
            AppError::Internal(_) => INTERNAL_SERVER_ERROR,
            AppError::Unknown(_) => INTERNAL_UNKNOWN_ERROR,
        }
    }

    /// 获取HTTP状态码
    pub fn status_code(&self) -> StatusCode {
        match self {
            // 认证和授权 - 401/403
            AppError::InvalidCredentials
            | AppError::TokenExpired
            | AppError::TokenInvalid
            | AppError::Unauthorized => StatusCode::UNAUTHORIZED,

            AppError::Forbidden => StatusCode::FORBIDDEN,

            // 数据验证 - 400
            AppError::InvalidInput(_)
            | AppError::MissingField(_)
            | AppError::InvalidFormat(_)
            | AppError::OutOfRange(_)
            | AppError::InvalidState(_)
            | AppError::OperationNotAllowed(_) => StatusCode::BAD_REQUEST,

            // 未找到 - 404
            AppError::NotFound(_)
            | AppError::UserNotFound(_)
            | AppError::TaskNotFound(_)
            | AppError::DeviceNotFound(_) => StatusCode::NOT_FOUND,

            // 冲突 - 409
            AppError::Conflict(_)
            | AppError::DuplicateUsername(_)
            | AppError::DeviceLimitExceeded => StatusCode::CONFLICT,

            // 业务逻辑错误 - 422
            AppError::InsufficientBalance | AppError::ConstraintViolation(_) => {
                StatusCode::UNPROCESSABLE_ENTITY
            }

            // 外部服务 - 503
            AppError::ServiceUnavailable(_) => StatusCode::SERVICE_UNAVAILABLE,

            // 内部错误 - 500
            AppError::DatabaseConnection
            | AppError::DatabaseQuery(_)
            | AppError::Internal(_)
            | AppError::Unknown(_)
            | AppError::ExternalApiError(_) => StatusCode::INTERNAL_SERVER_ERROR,
        }
    }

    /// 转换为错误响应
    pub fn to_error_response(&self) -> ErrorResponse {
        ErrorResponse::new(self.error_code(), self.to_string())
    }

    /// 转换为带详细信息的错误响应（开发环境使用）
    pub fn to_error_response_with_details(&self, details: impl Into<String>) -> ErrorResponse {
        ErrorResponse::new(self.error_code(), self.to_string()).with_details(details)
    }
}

// 实现 IntoResponse，使 AppError 可以直接作为 Axum handler 的返回值
impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let status_code = self.status_code();
        let error_response = self.to_error_response();

        (status_code, Json(error_response)).into_response()
    }
}

// 为常见错误类型实现 From trait，方便自动转换
impl From<sqlx::Error> for AppError {
    fn from(err: sqlx::Error) -> Self {
        match err {
            sqlx::Error::RowNotFound => AppError::NotFound("数据不存在".to_string()),
            sqlx::Error::Database(db_err) => {
                // 检查是否是唯一性约束违反
                if let Some(code) = db_err.code() {
                    if code == "2067" || code == "UNIQUE constraint failed" {
                        return AppError::Conflict("数据已存在".to_string());
                    }
                }
                AppError::DatabaseQuery(db_err.to_string())
            }
            sqlx::Error::PoolTimedOut => AppError::DatabaseConnection,
            _ => AppError::DatabaseQuery(err.to_string()),
        }
    }
}

impl From<anyhow::Error> for AppError {
    fn from(err: anyhow::Error) -> Self {
        AppError::Internal(err.to_string())
    }
}

impl From<validator::ValidationErrors> for AppError {
    fn from(err: validator::ValidationErrors) -> Self {
        AppError::InvalidInput(err.to_string())
    }
}

impl From<std::io::Error> for AppError {
    fn from(err: std::io::Error) -> Self {
        AppError::Internal(err.to_string())
    }
}

/// Result type alias，使用 AppError 作为错误类型
pub type AppResult<T> = Result<T, AppError>;
