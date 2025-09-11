use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use validator::Validate;

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct User {
    pub id: i32,
    pub username: String,
    pub email: Option<String>,
    pub hashed_password: String,
    pub role: String,
    pub is_active: Option<bool>,
    pub is_verified: Option<bool>,
    pub parent_id: Option<i32>,
    pub full_name: Option<String>,
    pub phone: Option<String>,
    pub company: Option<String>,
    pub max_employees: Option<i32>,
    pub current_employees: Option<i32>,
    pub created_at: Option<DateTime<Utc>>,
    pub updated_at: Option<DateTime<Utc>>,
    pub last_login: Option<DateTime<Utc>>,
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
    pub email: Option<String>,
    #[validate(length(min = 6))]
    pub password: String,
    pub role: String,
    pub phone: Option<String>,
    pub full_name: Option<String>,
    pub company: Option<String>,
    pub max_employees: Option<i32>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct UpdateUserRequest {
    #[validate(length(min = 3, max = 50))]
    pub username: Option<String>,
    #[validate(email)]
    pub email: Option<String>,
    pub password: Option<String>, // 可选，只有提供时才更新
    pub phone: Option<String>,
    pub full_name: Option<String>,
    pub company: Option<String>,
    pub max_employees: Option<i32>,
    pub is_active: Option<bool>,
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
            max_employees: user.max_employees.unwrap_or(0),
            parent_id: user.parent_id,
            created_at: user
                .created_at
                .map(|dt| dt.format("%Y-%m-%d %H:%M:%S").to_string())
                .unwrap_or_default(),
            last_login: user
                .last_login
                .map(|dt| dt.format("%Y-%m-%d %H:%M:%S").to_string()),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Device {
    pub id: String,
    pub device_name: String,
    pub device_type: String,
    pub adb_id: Option<String>,
    pub status: String,
    pub user_id: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct CreateDeviceRequest {
    #[validate(length(min = 1))]
    pub device_name: String,
    pub device_type: String,
    pub adb_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct WorkRecord {
    pub id: String,
    pub user_id: String,
    pub device_id: String,
    pub platform: String,
    pub action_type: String,
    pub target_count: i32,
    pub completed_count: i32,
    pub status: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct CreateWorkRecordRequest {
    pub device_id: String,
    pub platform: String,
    pub action_type: String,
    pub target_count: i32,
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

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct PricingRule {
    pub id: i32,
    pub rule_name: String,
    pub billing_type: String,
    pub unit_price: f64,
    pub is_active: bool,
    pub created_at: Option<DateTime<Utc>>,
    pub updated_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct CreatePricingRuleRequest {
    #[validate(length(min = 1, max = 100))]
    pub rule_name: String,
    #[validate(length(min = 1, max = 50))]
    pub billing_type: String,
    #[validate(range(min = 0.0))]
    pub unit_price: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct KpiStats {
    pub total_actions: i64,
    pub successful_actions: i64,
    pub failed_actions: i64,
    pub success_rate: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
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
