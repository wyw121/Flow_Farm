use axum::{
    extract::{State, Query},
    response::Response,
    http::{StatusCode, header},
    body::Body,
};
use serde::Deserialize;

use crate::{
    Database, Config,
    services::report::ReportService,
    middleware::auth::AuthContext,
};

type AppState = (Database, Config);

#[derive(Deserialize)]
pub struct ExportQuery {
    pub format: Option<String>, // csv, json
    pub start_date: Option<String>,
    pub end_date: Option<String>,
    pub user_id: Option<String>,
}

pub async fn export_data(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Query(query): Query<ExportQuery>,
) -> Result<Response<Body>, StatusCode> {
    let service = ReportService::new(database);

    let format = query.format.as_deref().unwrap_or("json");

    match service.export_data(
        &auth_context.user,
        format,
        query.start_date.as_deref(),
        query.end_date.as_deref(),
        query.user_id.as_deref(),
    ).await {
        Ok((content, content_type, filename)) => {
            let response = Response::builder()
                .status(StatusCode::OK)
                .header(header::CONTENT_TYPE, content_type)
                .header(
                    header::CONTENT_DISPOSITION,
                    format!("attachment; filename=\"{}\"", filename),
                )
                .body(Body::from(content))
                .unwrap();

            Ok(response)
        }
        Err(e) => {
            tracing::error!("导出数据失败: {}", e);
            let error_json = serde_json::json!({
                "success": false,
                "message": "导出数据失败",
                "data": serde_json::Value::Null
            });
            let response = Response::builder()
                .status(StatusCode::INTERNAL_SERVER_ERROR)
                .header(header::CONTENT_TYPE, "application/json")
                .body(Body::from(serde_json::to_string(&error_json).unwrap()))
                .unwrap();

            Ok(response)
        }
    }
}
