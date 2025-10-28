use serde::{Deserialize, Serialize};
use tauri::State;
use std::sync::{Arc, Mutex};
use chrono::{DateTime, Utc, NaiveDate};
use crate::auth_service::AuthService;
use crate::commands::gps::{GpsLocation, GpsService};

/// 客户信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Customer {
    pub id: i32,
    pub company_name: String,
    pub contact_person: Option<String>,
    pub phone: Option<String>,
    pub email: Option<String>,
    pub address: Option<String>,
    pub industry: Option<String>,
    pub latitude: Option<f64>,
    pub longitude: Option<f64>,
}

/// 拜访记录状态
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum VisitStatus {
    Planned,
    InProgress,
    Completed,
    Cancelled,
}

/// 拜访记录
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VisitRecord {
    pub id: i32,
    pub customer_id: i32,
    pub customer: Option<Customer>,
    pub field_worker_id: i32,
    pub planned_date: NaiveDate,
    pub planned_start_time: Option<String>,
    pub planned_duration: Option<i32>, // 分钟
    pub actual_start_time: Option<DateTime<Utc>>,
    pub actual_end_time: Option<DateTime<Utc>>,
    pub arrival_location: Option<GpsLocation>,
    pub departure_location: Option<GpsLocation>,
    pub visit_summary: Option<String>,
    pub customer_feedback: Option<String>,
    pub business_opportunities: Option<String>,
    pub competitor_info: Option<String>,
    pub follow_up_plan: Option<String>,
    pub visit_rating: Option<i32>, // 1-5
    pub customer_satisfaction: Option<i32>, // 1-5
    pub status: VisitStatus,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 拜访附件
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VisitAttachment {
    pub id: i32,
    pub visit_id: i32,
    pub attachment_type: String, // image, audio, video, document
    pub file_name: String,
    pub file_path: String,
    pub file_size: i64,
    pub mime_type: String,
    pub uploaded_by: i32,
    pub upload_time: DateTime<Utc>,
}

/// 开始拜访请求
#[derive(Debug, Serialize, Deserialize)]
pub struct StartVisitRequest {
    pub arrival_lat: f64,
    pub arrival_lng: f64,
    pub location_accuracy: f64,
}

/// 结束拜访请求
#[derive(Debug, Serialize, Deserialize)]
pub struct EndVisitRequest {
    pub departure_lat: f64,
    pub departure_lng: f64,
    pub visit_summary: String,
    pub customer_feedback: Option<String>,
    pub business_opportunities: Option<String>,
    pub competitor_info: Option<String>,
    pub follow_up_plan: Option<String>,
    pub visit_rating: Option<i32>,
    pub customer_satisfaction: Option<i32>,
}

/// 拜访服务状态
pub struct VisitService {
    pub active_visit: Arc<Mutex<Option<VisitRecord>>>,
    pub api_base_url: String,
}

impl VisitService {
    pub fn new(api_base_url: String) -> Self {
        Self {
            active_visit: Arc::new(Mutex::new(None)),
            api_base_url,
        }
    }
}

/// 获取今日拜访计划
#[tauri::command]
pub async fn get_today_visits(
    visit_service: State<'_, VisitService>,
    auth_service: State<'_, AuthService>,
) -> Result<Vec<VisitRecord>, String> {
    let token = auth_service.get_token()
        .ok_or("用户未登录")?;

    let client = reqwest::Client::new();
    let today = chrono::Utc::now().format("%Y-%m-%d").to_string();

    let url = format!("{}/api/v1/visits?date_from={}&date_to={}", 
        visit_service.api_base_url, today, today);

    let response = client
        .get(&url)
        .header("Authorization", format!("Bearer {}", token))
        .send()
        .await
        .map_err(|e| format!("请求失败: {}", e))?;

    if !response.status().is_success() {
        return Err(format!("服务器错误: {}", response.status()));
    }

    #[derive(Deserialize)]
    struct VisitListResponse {
        visits: Vec<VisitRecordResponse>,
    }

    #[derive(Deserialize)]
    struct VisitRecordResponse {
        visit: VisitRecord,
        customer: Customer,
    }

    let visit_response: VisitListResponse = response.json().await
        .map_err(|e| format!("解析响应失败: {}", e))?;

    let visits: Vec<VisitRecord> = visit_response.visits
        .into_iter()
        .map(|v| VisitRecord {
            customer: Some(v.customer),
            ..v.visit
        })
        .collect();

    Ok(visits)
}

/// 开始拜访
#[tauri::command]
pub async fn start_visit(
    visit_id: i32,
    visit_service: State<'_, VisitService>,
    gps_service: State<'_, GpsService>,
    auth_service: State<'_, AuthService>,
) -> Result<VisitRecord, String> {
    let token = auth_service.get_token()
        .ok_or("用户未登录")?;

    // 获取当前位置
    let location = crate::commands::gps::get_current_location(gps_service.clone()).await?
        .ok_or("无法获取当前位置")?;

    let start_request = StartVisitRequest {
        arrival_lat: location.latitude,
        arrival_lng: location.longitude,
        location_accuracy: location.accuracy,
    };

    let client = reqwest::Client::new();
    let url = format!("{}/api/v1/visits/{}/start", visit_service.api_base_url, visit_id);

    let response = client
        .post(&url)
        .header("Authorization", format!("Bearer {}", token))
        .header("Content-Type", "application/json")
        .json(&start_request)
        .send()
        .await
        .map_err(|e| format!("请求失败: {}", e))?;

    if !response.status().is_success() {
        return Err(format!("服务器错误: {}", response.status()));
    }

    let visit: VisitRecord = response.json().await
        .map_err(|e| format!("解析响应失败: {}", e))?;

    // 设置当前活跃拜访
    let mut active_visit = visit_service.active_visit.lock()
        .map_err(|e| format!("Failed to lock active_visit: {}", e))?;
    *active_visit = Some(visit.clone());

    Ok(visit)
}

/// 结束拜访
#[tauri::command]
pub async fn end_visit(
    visit_id: i32,
    visit_summary: String,
    customer_feedback: Option<String>,
    business_opportunities: Option<String>,
    competitor_info: Option<String>,
    follow_up_plan: Option<String>,
    visit_rating: Option<i32>,
    customer_satisfaction: Option<i32>,
    visit_service: State<'_, VisitService>,
    gps_service: State<'_, GpsService>,
    auth_service: State<'_, AuthService>,
) -> Result<VisitRecord, String> {
    let token = auth_service.get_token()
        .ok_or("用户未登录")?;

    // 获取当前位置
    let location = crate::commands::gps::get_current_location(gps_service.clone()).await?
        .ok_or("无法获取当前位置")?;

    let end_request = EndVisitRequest {
        departure_lat: location.latitude,
        departure_lng: location.longitude,
        visit_summary,
        customer_feedback,
        business_opportunities,
        competitor_info,
        follow_up_plan,
        visit_rating,
        customer_satisfaction,
    };

    let client = reqwest::Client::new();
    let url = format!("{}/api/v1/visits/{}/end", visit_service.api_base_url, visit_id);

    let response = client
        .post(&url)
        .header("Authorization", format!("Bearer {}", token))
        .header("Content-Type", "application/json")
        .json(&end_request)
        .send()
        .await
        .map_err(|e| format!("请求失败: {}", e))?;

    if !response.status().is_success() {
        return Err(format!("服务器错误: {}", response.status()));
    }

    let visit: VisitRecord = response.json().await
        .map_err(|e| format!("解析响应失败: {}", e))?;

    // 清除当前活跃拜访
    let mut active_visit = visit_service.active_visit.lock()
        .map_err(|e| format!("Failed to lock active_visit: {}", e))?;
    *active_visit = None;

    Ok(visit)
}

/// 获取当前活跃拜访
#[tauri::command]
pub async fn get_active_visit(
    visit_service: State<'_, VisitService>,
) -> Result<Option<VisitRecord>, String> {
    let active_visit = visit_service.active_visit.lock()
        .map_err(|e| format!("Failed to lock active_visit: {}", e))?
        .clone();

    Ok(active_visit)
}

/// 取消拜访
#[tauri::command]
pub async fn cancel_visit(
    visit_id: i32,
    visit_service: State<'_, VisitService>,
    auth_service: State<'_, AuthService>,
) -> Result<VisitRecord, String> {
    let token = auth_service.get_token()
        .ok_or("用户未登录")?;

    let client = reqwest::Client::new();
    let url = format!("{}/api/v1/visits/{}/cancel", visit_service.api_base_url, visit_id);

    let response = client
        .post(&url)
        .header("Authorization", format!("Bearer {}", token))
        .send()
        .await
        .map_err(|e| format!("请求失败: {}", e))?;

    if !response.status().is_success() {
        return Err(format!("服务器错误: {}", response.status()));
    }

    let visit: VisitRecord = response.json().await
        .map_err(|e| format!("解析响应失败: {}", e))?;

    // 如果取消的是当前活跃拜访，清除它
    let mut active_visit = visit_service.active_visit.lock()
        .map_err(|e| format!("Failed to lock active_visit: {}", e))?;
    if let Some(ref current) = *active_visit {
        if current.id == visit_id {
            *active_visit = None;
        }
    }

    Ok(visit)
}

/// 获取拜访附件列表
#[tauri::command]
pub async fn get_visit_attachments(
    visit_id: i32,
    visit_service: State<'_, VisitService>,
    auth_service: State<'_, AuthService>,
) -> Result<Vec<VisitAttachment>, String> {
    let token = auth_service.get_token()
        .ok_or("用户未登录")?;

    let client = reqwest::Client::new();
    let url = format!("{}/api/v1/visits/{}/attachments", visit_service.api_base_url, visit_id);

    let response = client
        .get(&url)
        .header("Authorization", format!("Bearer {}", token))
        .send()
        .await
        .map_err(|e| format!("请求失败: {}", e))?;

    if !response.status().is_success() {
        return Err(format!("服务器错误: {}", response.status()));
    }

    let attachments: Vec<VisitAttachment> = response.json().await
        .map_err(|e| format!("解析响应失败: {}", e))?;

    Ok(attachments)
}