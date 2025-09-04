use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use thiserror::Error;

/// 用户认证错误类型
#[derive(Error, Debug)]
pub enum AuthError {
    #[error("网络请求失败: {0}")]
    NetworkError(#[from] reqwest::Error),
    #[error("JSON序列化错误: {0}")]
    SerializationError(#[from] serde_json::Error),
    #[error("认证失败: {0}")]
    AuthenticationFailed(String),
    #[error("用户名或密码错误")]
    InvalidCredentials,
    #[error("服务器错误: {0}")]
    ServerError(String),
}

/// 登录请求
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LoginRequest {
    pub username: String,
    pub password: String,
}

/// 用户信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserInfo {
    pub id: i32,
    pub username: String,
    pub email: Option<String>,
    pub full_name: Option<String>,
    pub phone: Option<String>,
    pub company: Option<String>,
    pub role: String,
    pub is_active: bool,
    pub is_verified: bool,
    pub current_employees: i32,
    pub max_employees: i32,
    pub parent_id: Option<i32>,
    pub created_at: String,
    pub last_login: Option<String>,
}

/// 登录响应
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LoginResponse {
    pub token: String,
    pub user: UserInfo,
}

/// API响应包装器
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub message: String,
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

/// 用户会话状态
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserSession {
    pub token: String,
    pub user: UserInfo,
    pub login_time: DateTime<Utc>,
    pub expires_at: DateTime<Utc>,
}

impl UserSession {
    pub fn new(token: String, user: UserInfo) -> Self {
        let login_time = Utc::now();
        let expires_at = login_time + chrono::Duration::hours(24); // 24小时过期

        Self {
            token,
            user,
            login_time,
            expires_at,
        }
    }

    /// 检查会话是否已过期
    pub fn is_expired(&self) -> bool {
        Utc::now() > self.expires_at
    }

    /// 检查会话是否有效（未过期且token不为空）
    pub fn is_valid(&self) -> bool {
        !self.is_expired() && !self.token.is_empty()
    }
}
