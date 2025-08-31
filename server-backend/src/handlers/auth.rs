use axum::{
    extract::{State, Json},
    http::StatusCode,
    response::Json as ResponseJson,
};
use serde_json::{json, Value};
use validator::Validate;

use crate::{
    Database, Config,
    models::{LoginRequest, CreateUserRequest, ApiResponse, LoginResponse, UserInfo},
    services::auth::AuthService,
    utils::jwt::Claims,
    middleware::auth::AuthContext,
};

type AppState = (Database, Config);

pub async fn login(
    State((database, config)): State<AppState>,
    Json(request): Json<LoginRequest>,
) -> Result<ResponseJson<ApiResponse<LoginResponse>>, StatusCode> {
    // 验证输入
    if let Err(_) = request.validate() {
        return Ok(ResponseJson(ApiResponse::error("输入数据无效".to_string())));
    }

    let auth_service = AuthService::new(database, config);

    match auth_service.login(&request.username, &request.password).await {
        Ok(response) => Ok(ResponseJson(ApiResponse::success(response))),
        Err(e) => {
            tracing::error!("登录失败: {}", e);
            Ok(ResponseJson(ApiResponse::error("用户名或密码错误".to_string())))
        }
    }
}

pub async fn register(
    State((database, config)): State<AppState>,
    Json(request): Json<CreateUserRequest>,
) -> Result<ResponseJson<ApiResponse<UserInfo>>, StatusCode> {
    // 验证输入
    if let Err(_) = request.validate() {
        return Ok(ResponseJson(ApiResponse::error("输入数据无效".to_string())));
    }

    let auth_service = AuthService::new(database, config);

    match auth_service.register(request).await {
        Ok(user) => Ok(ResponseJson(ApiResponse::success(user))),
        Err(e) => {
            tracing::error!("注册失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(format!("注册失败: {}", e))))
        }
    }
}

pub async fn get_current_user(
    auth_context: AuthContext,
) -> Result<ResponseJson<ApiResponse<UserInfo>>, StatusCode> {
    Ok(ResponseJson(ApiResponse::success(auth_context.user)))
}

pub async fn refresh_token(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
) -> Result<ResponseJson<ApiResponse<String>>, StatusCode> {
    let auth_service = AuthService::new(database, config);

    match auth_service.refresh_token(&auth_context.user.id.to_string()).await {
        Ok(token) => Ok(ResponseJson(ApiResponse::success(token))),
        Err(e) => {
            tracing::error!("刷新token失败: {}", e);
            Ok(ResponseJson(ApiResponse::error("刷新token失败".to_string())))
        }
    }
}
