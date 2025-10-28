use chrono::{DateTime, NaiveDate, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use std::collections::HashMap;
use validator::Validate;

/// 客户信息模型
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Customer {
    pub id: i32,
    pub company_name: String,
    pub contact_person: String,
    pub phone: String,
    pub email: Option<String>,
    pub address: String,
    pub industry: String,
    pub company_size: Option<String>,  // small, medium, large, enterprise
    pub annual_revenue: Option<f64>,
    pub latitude: Option<f64>,
    pub longitude: Option<f64>,
    pub notes: Option<String>,
    pub created_by: i32,  // research_manager ID
    pub company_id: i32,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 拜访记录模型
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct VisitRecord {
    pub id: i32,
    pub customer_id: i32,
    pub field_worker_id: i32,
    pub planned_date: NaiveDate,
    pub planned_start_time: String,  // HH:MM 格式
    pub planned_duration: i32,  // 计划拜访时长（分钟）
    pub actual_start_time: Option<DateTime<Utc>>,
    pub actual_end_time: Option<DateTime<Utc>>,
    pub arrival_lat: Option<f64>,
    pub arrival_lng: Option<f64>,
    pub departure_lat: Option<f64>,
    pub departure_lng: Option<f64>,
    pub location_accuracy: Option<f64>,  // GPS精度（米）
    pub visit_summary: Option<String>,
    pub customer_feedback: Option<serde_json::Value>,  // 客户反馈JSON
    pub business_opportunities: Option<serde_json::Value>,  // 商机信息JSON
    pub competitor_info: Option<serde_json::Value>,  // 竞争对手信息JSON
    pub follow_up_plan: Option<String>,
    pub visit_rating: Option<i32>,  // 拜访效果评分 1-5
    pub customer_satisfaction: Option<i32>,  // 客户满意度 1-5
    pub status: String,  // planned, in_progress, completed, cancelled
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 拜访附件（照片、音频、文档等）
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct VisitAttachment {
    pub id: i32,
    pub visit_id: i32,
    pub attachment_type: String,  // image, audio, video, document
    pub file_name: String,
    pub file_path: String,
    pub file_size: i64,  // 字节
    pub mime_type: String,
    pub uploaded_by: i32,  // 上传人ID
    pub upload_time: DateTime<Utc>,
}

/// 创建客户请求
#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct CreateCustomerRequest {
    #[validate(length(min = 1, max = 200))]
    pub company_name: String,
    #[validate(length(min = 1, max = 100))]
    pub contact_person: String,
    #[validate(length(min = 1, max = 20))]
    pub phone: String,
    #[validate(email)]
    pub email: Option<String>,
    #[validate(length(min = 1, max = 500))]
    pub address: String,
    #[validate(length(min = 1, max = 100))]
    pub industry: String,
    pub company_size: Option<String>,
    pub annual_revenue: Option<f64>,
    pub latitude: Option<f64>,
    pub longitude: Option<f64>,
    pub notes: Option<String>,
}

/// 更新客户请求
#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct UpdateCustomerRequest {
    #[validate(length(min = 1, max = 200))]
    pub company_name: Option<String>,
    #[validate(length(min = 1, max = 100))]
    pub contact_person: Option<String>,
    #[validate(length(min = 1, max = 20))]
    pub phone: Option<String>,
    #[validate(email)]
    pub email: Option<String>,
    #[validate(length(min = 1, max = 500))]
    pub address: Option<String>,
    #[validate(length(min = 1, max = 100))]
    pub industry: Option<String>,
    pub company_size: Option<String>,
    pub annual_revenue: Option<f64>,
    pub latitude: Option<f64>,
    pub longitude: Option<f64>,
    pub notes: Option<String>,
}

/// 创建拜访计划请求
#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct CreateVisitRequest {
    pub customer_id: i32,
    pub field_worker_id: i32,
    pub planned_date: String,  // YYYY-MM-DD 格式
    pub planned_start_time: String,  // HH:MM 格式
    #[validate(range(min = 15, max = 480))]
    pub planned_duration: i32,  // 15分钟到8小时
    pub visit_purpose: Option<String>,
    pub notes: Option<String>,
}

/// 开始拜访请求
#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct StartVisitRequest {
    pub arrival_lat: f64,
    pub arrival_lng: f64,
    pub location_accuracy: Option<f64>,
    pub notes: Option<String>,
}

/// 结束拜访请求
#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct EndVisitRequest {
    pub departure_lat: f64,
    pub departure_lng: f64,
    pub location_accuracy: Option<f64>,
    #[validate(length(min = 1, max = 2000))]
    pub visit_summary: String,
    pub customer_feedback: Option<serde_json::Value>,
    pub business_opportunities: Option<serde_json::Value>,
    pub competitor_info: Option<serde_json::Value>,
    pub follow_up_plan: Option<String>,
    #[validate(range(min = 1, max = 5))]
    pub visit_rating: Option<i32>,
    #[validate(range(min = 1, max = 5))]
    pub customer_satisfaction: Option<i32>,
}

/// 客户列表响应
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CustomerListResponse {
    pub customers: Vec<Customer>,
    pub total: i32,
    pub page: i32,
    pub page_size: i32,
}

/// 拜访记录列表响应
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VisitRecordListResponse {
    pub visits: Vec<VisitRecordWithCustomer>,
    pub total: i32,
    pub page: i32,
    pub page_size: i32,
}

/// 带客户信息的拜访记录
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VisitRecordWithCustomer {
    #[serde(flatten)]
    pub visit: VisitRecord,
    pub customer: Customer,
    pub field_worker_name: String,
    pub attachments: Vec<VisitAttachment>,
}

/// 拜访统计数据
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VisitStatistics {
    pub total_visits: i32,
    pub completed_visits: i32,
    pub completion_rate: f64,
    pub average_duration: i32,  // 平均拜访时长（分钟）
    pub total_customers: i32,
    pub active_customers: i32,  // 近30天有拜访的客户
    pub monthly_visits: HashMap<String, i32>,  // 按月统计
    pub top_industries: Vec<IndustryStats>,
    pub geographic_distribution: HashMap<String, i32>,
}

/// 行业统计
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IndustryStats {
    pub industry: String,
    pub customer_count: i32,
    pub visit_count: i32,
    pub avg_satisfaction: f64,
}

/// GPS轨迹点
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpsTrackPoint {
    pub latitude: f64,
    pub longitude: f64,
    pub accuracy: f64,
    pub timestamp: DateTime<Utc>,
    pub speed: Option<f64>,  // 移动速度（米/秒）
    pub heading: Option<f64>,  // 方向角（度）
}

/// 上传附件请求
#[derive(Debug, Clone, Serialize, Deserialize, Validate)]
pub struct UploadAttachmentRequest {
    pub visit_id: i32,
    pub file_type: String,  // photo, audio, document
    pub file_name: String,
    pub description: Option<String>,
    pub gps_lat: Option<f64>,
    pub gps_lng: Option<f64>,
    pub metadata: Option<serde_json::Value>,
}

/// 拜访状态枚举
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum VisitStatus {
    Planned,     // 已计划
    InProgress,  // 进行中
    Completed,   // 已完成
    Cancelled,   // 已取消
}

impl VisitStatus {
    pub fn as_str(&self) -> &'static str {
        match self {
            VisitStatus::Planned => "planned",
            VisitStatus::InProgress => "in_progress",
            VisitStatus::Completed => "completed",
            VisitStatus::Cancelled => "cancelled",
        }
    }
}

/// 公司规模枚举
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum CompanySize {
    Small,      // 小型（<50人）
    Medium,     // 中型（50-500人）
    Large,      // 大型（500-5000人）
    Enterprise, // 企业级（>5000人）
}

impl CompanySize {
    pub fn as_str(&self) -> &'static str {
        match self {
            CompanySize::Small => "small",
            CompanySize::Medium => "medium",
            CompanySize::Large => "large",
            CompanySize::Enterprise => "enterprise",
        }
    }
}