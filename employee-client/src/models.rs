// 数据模型定义
use serde::{Deserialize, Serialize};

pub use crate::{DeviceInfo, TaskInfo, UserSession, AppConfig};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ContactFile {
    pub path: String,
    pub contacts: Vec<Contact>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Contact {
    pub name: String,
    pub phone: String,
    pub platform_id: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct MonitorTarget {
    pub account: String,
    pub platform: String,
    pub keywords: Vec<String>,
    pub target_count: u32,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct TaskProgress {
    pub task_id: String,
    pub total: u32,
    pub completed: u32,
    pub failed: u32,
    pub current_status: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct FollowRecord {
    pub id: String,
    pub target_user: String,
    pub platform: String,
    pub status: String,
    pub device_id: String,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub completed_at: Option<chrono::DateTime<chrono::Utc>>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct BillingInfo {
    pub user_id: String,
    pub balance: f64,
    pub cost_per_follow: f64,
    pub daily_limit: u32,
    pub monthly_limit: u32,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DeviceCapability {
    pub name: String,
    pub version: String,
    pub supported: bool,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct PlatformConfig {
    pub platform: String,
    pub enabled: bool,
    pub rate_limit: u32, // 每小时操作次数限制
    pub delay_range: (u32, u32), // 操作间隔范围（秒）
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AppSettings {
    pub auto_start: bool,
    pub minimize_to_tray: bool,
    pub notification_enabled: bool,
    pub log_level: String,
    pub theme: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub data: Option<T>,
    pub message: String,
    pub code: u32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PaginatedResponse<T> {
    pub items: Vec<T>,
    pub total: u32,
    pub page: u32,
    pub page_size: u32,
    pub total_pages: u32,
}
