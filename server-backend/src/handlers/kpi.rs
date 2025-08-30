use axum::{
    extract::{State, Query},
    response::Json as ResponseJson,
    http::StatusCode,
};
use serde::Deserialize;

use crate::{
    Database, Config,
    models::{ApiResponse, KpiStats, UserStats},
    services::kpi::KpiService,
    middleware::auth::AuthContext,
};

type AppState = (Database, Config);

#[derive(Deserialize)]
pub struct KpiQuery {
    pub start_date: Option<String>,
    pub end_date: Option<String>,
    pub platform: Option<String>,
}

pub async fn get_kpi_stats(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Query(query): Query<KpiQuery>,
) -> Result<ResponseJson<ApiResponse<KpiStats>>, StatusCode> {
    let service = KpiService::new(database);

    match service.get_kpi_stats(
        &auth_context.user,
        query.start_date.as_deref(),
        query.end_date.as_deref(),
        query.platform.as_deref(),
    ).await {
        Ok(stats) => Ok(ResponseJson(ApiResponse::success(stats))),
        Err(e) => {
            tracing::error!("获取KPI统计失败: {}", e);
            Ok(ResponseJson(ApiResponse::error("获取KPI统计失败".to_string())))
        }
    }
}

pub async fn get_user_stats(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Query(query): Query<KpiQuery>,
) -> Result<ResponseJson<ApiResponse<Vec<UserStats>>>, StatusCode> {
    let service = KpiService::new(database);

    match service.get_user_stats(
        &auth_context.user,
        query.start_date.as_deref(),
        query.end_date.as_deref(),
    ).await {
        Ok(stats) => Ok(ResponseJson(ApiResponse::success(stats))),
        Err(e) => {
            tracing::error!("获取用户统计失败: {}", e);
            Ok(ResponseJson(ApiResponse::error("获取用户统计失败".to_string())))
        }
    }
}
