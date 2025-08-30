use axum::{
    extract::{State, Path, Query},
    response::Json as ResponseJson,
    http::StatusCode,
    Json,
};
use serde::Deserialize;

use crate::{
    Database, Config,
    models::{ApiResponse, WorkRecord, CreateWorkRecordRequest},
    services::work_record::WorkRecordService,
    middleware::auth::AuthContext,
};

type AppState = (Database, Config);

#[derive(Deserialize)]
pub struct ListWorkRecordsQuery {
    pub page: Option<i32>,
    pub limit: Option<i32>,
    pub platform: Option<String>,
    pub success: Option<bool>,
}

pub async fn list_work_records(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Query(query): Query<ListWorkRecordsQuery>,
) -> Result<ResponseJson<ApiResponse<Vec<WorkRecord>>>, StatusCode> {
    let service = WorkRecordService::new(database);

    match service.list_work_records(
        &auth_context.user,
        query.page.unwrap_or(1),
        query.limit.unwrap_or(20),
        query.platform.as_deref(),
        query.success,
    ).await {
        Ok(records) => Ok(ResponseJson(ApiResponse::success(records))),
        Err(e) => {
            tracing::error!("获取工作记录失败: {}", e);
            Ok(ResponseJson(ApiResponse::error("获取工作记录失败".to_string())))
        }
    }
}

pub async fn create_work_record(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Json(request): Json<CreateWorkRecordRequest>,
) -> Result<ResponseJson<ApiResponse<WorkRecord>>, StatusCode> {
    let service = WorkRecordService::new(database);

    match service.create_work_record(&auth_context.user, request).await {
        Ok(record) => Ok(ResponseJson(ApiResponse::success(record))),
        Err(e) => {
            tracing::error!("创建工作记录失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(format!("创建工作记录失败: {}", e))))
        }
    }
}

pub async fn get_work_record(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Path(record_id): Path<String>,
) -> Result<ResponseJson<ApiResponse<WorkRecord>>, StatusCode> {
    let service = WorkRecordService::new(database);

    match service.get_work_record(&auth_context.user, &record_id).await {
        Ok(record) => Ok(ResponseJson(ApiResponse::success(record))),
        Err(e) => {
            tracing::error!("获取工作记录失败: {}", e);
            Ok(ResponseJson(ApiResponse::error("工作记录不存在".to_string())))
        }
    }
}
