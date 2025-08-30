use axum::{
    response::Json as ResponseJson,
    http::StatusCode,
};
use serde_json::{json, Value};

pub async fn health_check() -> Result<ResponseJson<Value>, StatusCode> {
    Ok(ResponseJson(json!({
        "status": "healthy",
        "service": "Flow Farm 服务器后端",
        "version": "1.0.0",
        "timestamp": chrono::Utc::now()
    })))
}
