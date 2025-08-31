use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use validator::Validate;

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct User {
    pub id: i32, // 匹配数据库的INTEGER类型
    pub username: String,
    pub email: Option<String>,     // 数据库中可能为空
    pub hashed_password: String,   // 匹配数据库字段名
    pub role: String,              // 暂时用String，因为数据库中是VARCHAR
    pub is_active: Option<bool>,   // 数据库中可能为空
    pub is_verified: Option<bool>, // 数据库字段
    pub parent_id: Option<i32>,    // 数据库字段
    pub full_name: Option<String>, // 数据库字段
    pub phone: Option<String>,     // 数据库字段
    pub company: Option<String>,   // 数据库字段，重命名自company_id
    pub max_employees: Option<i32>,
    pub current_employees: Option<i32>,    // 数据库字段
    pub created_at: Option<DateTime<Utc>>, // 数据库中可能为空
    pub updated_at: Option<DateTime<Utc>>, // 数据库中可能为空
    pub last_login: Option<DateTime<Utc>>, // 数据库字段
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "TEXT")]
#[sqlx(rename_all = "snake_case")]
pub enum UserRole {
    SystemAdmin,
    UserAdmin,
    Employee,
}

impl std::fmt::Display for UserRole {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            UserRole::SystemAdmin => write!(f, "system_admin"),
            UserRole::UserAdmin => write!(f, "user_admin"),
            UserRole::Employee => write!(f, "employee"),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct CreateUserRequest {
    #[validate(length(min = 3, max = 50))]
    pub username: String,
    #[validate(email)]
    pub email: String,
    #[validate(length(min = 6))]
    pub password: String,
    pub role: UserRole,
    pub company_id: Option<String>, // 这个会映射到company字段
    pub max_employees: Option<i32>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct LoginRequest {
    #[validate(length(min = 1))]
    pub username: String,
    #[validate(length(min = 1))]
    pub password: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LoginResponse {
    pub token: String,
    pub user: UserInfo,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserInfo {
    pub id: i32, // 匹配数据库类型
    pub username: String,
    pub email: Option<String>, // 可能为空
    pub full_name: Option<String>,
    pub phone: Option<String>,
    pub company: Option<String>,
    pub role: String,           // 暂时用String
    pub is_active: bool,        // 转换为非空布尔值
    pub is_verified: bool,      // 转换为非空布尔值
    pub current_employees: i32, // 默认值
    pub max_employees: i32,     // 默认值
    pub parent_id: Option<i32>,
    pub created_at: String,         // 转换为字符串
    pub last_login: Option<String>, // 转换为字符串
}

impl From<User> for UserInfo {
    fn from(user: User) -> Self {
        Self {
            id: user.id,
            username: user.username,
            email: user.email,
            full_name: user.full_name,
            phone: user.phone,
            company: user.company,
            role: user.role,
            is_active: user.is_active.unwrap_or(true),
            is_verified: user.is_verified.unwrap_or(false),
            current_employees: user.current_employees.unwrap_or(0),
            max_employees: user.max_employees.unwrap_or(10),
            parent_id: user.parent_id,
            created_at: user
                .created_at
                .map(|dt| dt.format("%Y-%m-%d %H:%M:%S").to_string())
                .unwrap_or_else(|| "".to_string()),
            last_login: user
                .last_login
                .map(|dt| dt.format("%Y-%m-%d %H:%M:%S").to_string()),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct WorkRecord {
    pub id: String,
    pub user_id: String,
    pub device_id: String,
    pub platform: String,
    pub action_type: String,
    pub target_user: Option<String>,
    pub target_content: Option<String>,
    pub success: bool,
    pub error_message: Option<String>,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct CreateWorkRecordRequest {
    pub device_id: String,
    pub platform: String,
    pub action_type: String,
    pub target_user: Option<String>,
    pub target_content: Option<String>,
    pub success: bool,
    pub error_message: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Device {
    pub id: String,
    pub user_id: String,
    pub device_name: String,
    pub device_type: String,
    pub adb_id: Option<String>,
    pub status: String,
    pub last_seen: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct CreateDeviceRequest {
    #[validate(length(min = 1))]
    pub device_name: String,
    pub device_type: String,
    pub adb_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct BillingRecord {
    pub id: String,
    pub user_id: String,
    pub amount: f64,
    pub billing_type: String,
    pub description: Option<String>,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct CreateBillingRecordRequest {
    pub user_id: String,
    pub amount: f64,
    pub billing_type: String,
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KpiStats {
    pub total_actions: i64,
    pub successful_actions: i64,
    pub failed_actions: i64,
    pub success_rate: f64,
    pub platforms: std::collections::HashMap<String, i64>,
    pub action_types: std::collections::HashMap<String, i64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserStats {
    pub user_id: String,
    pub username: String,
    pub total_actions: i64,
    pub successful_actions: i64,
    pub success_rate: f64,
    pub last_activity: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct CompanyStatistics {
    pub company_name: String,
    pub user_admin_id: i32,
    pub user_admin_name: String,
    pub total_employees: i32,
    pub total_follows: i64,
    pub today_follows: i64,
    pub total_billing_amount: f64,
    pub unpaid_amount: f64,
}

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
