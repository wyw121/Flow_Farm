use axum::{
    extract::{State, Path, Query},
    response::Json as ResponseJson,
    http::StatusCode,
    Json,
};
use serde::Deserialize;

use crate::{
    Database, Config,
    models::{ApiResponse, Device, CreateDeviceRequest},
    services::device::DeviceService,
    middleware::auth::AuthContext,
};

type AppState = (Database, Config);

pub async fn list_devices(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
) -> Result<ResponseJson<ApiResponse<Vec<Device>>>, StatusCode> {
    let service = DeviceService::new(database);

    match service.list_devices(&auth_context.user).await {
        Ok(devices) => Ok(ResponseJson(ApiResponse::success(devices))),
        Err(e) => {
            tracing::error!("获取设备列表失败: {}", e);
            Ok(ResponseJson(ApiResponse::error("获取设备列表失败".to_string())))
        }
    }
}

pub async fn create_device(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Json(request): Json<CreateDeviceRequest>,
) -> Result<ResponseJson<ApiResponse<Device>>, StatusCode> {
    let service = DeviceService::new(database);

    match service.create_device(&auth_context.user, request).await {
        Ok(device) => Ok(ResponseJson(ApiResponse::success(device))),
        Err(e) => {
            tracing::error!("创建设备失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(format!("创建设备失败: {}", e))))
        }
    }
}

pub async fn get_device(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Path(device_id): Path<String>,
) -> Result<ResponseJson<ApiResponse<Device>>, StatusCode> {
    let service = DeviceService::new(database);

    match service.get_device(&auth_context.user, &device_id).await {
        Ok(device) => Ok(ResponseJson(ApiResponse::success(device))),
        Err(e) => {
            tracing::error!("获取设备失败: {}", e);
            Ok(ResponseJson(ApiResponse::error("设备不存在".to_string())))
        }
    }
}

pub async fn update_device(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Path(device_id): Path<String>,
    Json(request): Json<CreateDeviceRequest>,
) -> Result<ResponseJson<ApiResponse<Device>>, StatusCode> {
    let service = DeviceService::new(database);

    match service.update_device(&auth_context.user, &device_id, request).await {
        Ok(device) => Ok(ResponseJson(ApiResponse::success(device))),
        Err(e) => {
            tracing::error!("更新设备失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(format!("更新设备失败: {}", e))))
        }
    }
}

pub async fn delete_device(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Path(device_id): Path<String>,
) -> Result<ResponseJson<ApiResponse<()>>, StatusCode> {
    let service = DeviceService::new(database);

    match service.delete_device(&auth_context.user, &device_id).await {
        Ok(_) => Ok(ResponseJson(ApiResponse::success(()))),
        Err(e) => {
            tracing::error!("删除设备失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(format!("删除设备失败: {}", e))))
        }
    }
}
