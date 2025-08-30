use axum::{
    extract::{State, Query},
    response::Json as ResponseJson,
    http::StatusCode,
    Json,
};
use serde::Deserialize;

use crate::{
    Database, Config,
    models::{ApiResponse, BillingRecord, CreateBillingRecordRequest},
    services::billing::BillingService,
    middleware::auth::AuthContext,
};

type AppState = (Database, Config);

#[derive(Deserialize)]
pub struct BillingQuery {
    pub page: Option<i32>,
    pub limit: Option<i32>,
    pub user_id: Option<String>,
}

pub async fn list_billing_records(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Query(query): Query<BillingQuery>,
) -> Result<ResponseJson<ApiResponse<Vec<BillingRecord>>>, StatusCode> {
    let service = BillingService::new(database);

    match service.list_billing_records(
        &auth_context.user,
        query.page.unwrap_or(1),
        query.limit.unwrap_or(20),
        query.user_id.as_deref(),
    ).await {
        Ok(records) => Ok(ResponseJson(ApiResponse::success(records))),
        Err(e) => {
            tracing::error!("获取计费记录失败: {}", e);
            Ok(ResponseJson(ApiResponse::error("获取计费记录失败".to_string())))
        }
    }
}

pub async fn create_billing_record(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Json(request): Json<CreateBillingRecordRequest>,
) -> Result<ResponseJson<ApiResponse<BillingRecord>>, StatusCode> {
    let service = BillingService::new(database);

    match service.create_billing_record(&auth_context.user, request).await {
        Ok(record) => Ok(ResponseJson(ApiResponse::success(record))),
        Err(e) => {
            tracing::error!("创建计费记录失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(format!("创建计费记录失败: {}", e))))
        }
    }
}
