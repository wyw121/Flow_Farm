use axum::{extract::{Json, State}, response::Json as ResponseJson};
use validator::Validate;

use crate::{
    errors::AppError,
    middleware::auth::AuthContext,
    models::{ApiResponse, CreateUserRequest, LoginRequest, LoginResponse, UserInfo},
    services::auth::AuthService,
    Config, Database,
};

type AppState = (Database, Config);

pub async fn login(
    State((database, config)): State<AppState>,
    Json(request): Json<LoginRequest>,
) -> Result<ResponseJson<ApiResponse<LoginResponse>>, AppError> {
    // 验证输入
    request.validate()?;

    let auth_service = AuthService::new(database, config);
    let response = auth_service
        .login(&request.username, &request.password)
        .await?;

    Ok(ResponseJson(ApiResponse::success(response)))
}

pub async fn register(
    State((database, config)): State<AppState>,
    Json(request): Json<CreateUserRequest>,
) -> Result<ResponseJson<ApiResponse<UserInfo>>, AppError> {
    // 验证输入
    request.validate()?;

    let auth_service = AuthService::new(database, config);
    let user = auth_service.register(request).await?;

    Ok(ResponseJson(ApiResponse::success(user)))
}

pub async fn get_current_user(
    auth_context: AuthContext,
) -> Result<ResponseJson<ApiResponse<UserInfo>>, AppError> {
    Ok(ResponseJson(ApiResponse::success(auth_context.user)))
}

pub async fn refresh_token(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
) -> Result<ResponseJson<ApiResponse<String>>, AppError> {
    let auth_service = AuthService::new(database, config);
    let token = auth_service
        .refresh_token(&auth_context.user.id.to_string())
        .await?;

    Ok(ResponseJson(ApiResponse::success(token)))
}

pub async fn logout(
    State((_database, _config)): State<AppState>,
) -> Result<ResponseJson<ApiResponse<String>>, AppError> {
    // 对于JWT token，logout通常在前端处理（删除token）
    // 这里只是返回成功响应
    Ok(ResponseJson(ApiResponse::success("注销成功".to_string())))
}
