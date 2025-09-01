use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json as ResponseJson,
    Json,
};
use serde::Deserialize;

use crate::{
    middleware::auth::AuthContext,
    models::{ApiResponse, CompanyStatistics, CreateUserRequest, User, UserInfo},
    services::user::UserService,
    Config, Database,
};

type AppState = (Database, Config);

#[derive(Deserialize)]
pub struct ListUsersQuery {
    pub page: Option<i32>,
    pub limit: Option<i32>,
    pub role: Option<String>,
}

pub async fn list_users(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Query(query): Query<ListUsersQuery>,
) -> Result<ResponseJson<ApiResponse<Vec<UserInfo>>>, StatusCode> {
    let user_service = UserService::new(database);

    match user_service
        .list_users(
            &auth_context.user,
            query.page.unwrap_or(1),
            query.limit.unwrap_or(20),
            query.role.as_deref(),
        )
        .await
    {
        Ok(users) => Ok(ResponseJson(ApiResponse::success(users))),
        Err(e) => {
            tracing::error!("获取用户列表失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(
                "获取用户列表失败".to_string(),
            )))
        }
    }
}

pub async fn create_user(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Json(request): Json<CreateUserRequest>,
) -> Result<ResponseJson<ApiResponse<UserInfo>>, StatusCode> {
    // 记录请求信息用于调试
    tracing::info!("创建用户请求: {:?}", request);
    tracing::info!("请求用户: {:?}", auth_context.user);

    let user_service = UserService::new(database);

    match user_service.create_user(&auth_context.user, request).await {
        Ok(user) => {
            tracing::info!("用户创建成功: {:?}", user);
            Ok(ResponseJson(ApiResponse::success(user)))
        }
        Err(e) => {
            tracing::error!("创建用户失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(format!(
                "创建用户失败: {}",
                e
            ))))
        }
    }
}

pub async fn get_user(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Path(user_id): Path<String>,
) -> Result<ResponseJson<ApiResponse<UserInfo>>, StatusCode> {
    let user_service = UserService::new(database);

    match user_service.get_user(&auth_context.user, &user_id).await {
        Ok(user) => Ok(ResponseJson(ApiResponse::success(user))),
        Err(e) => {
            tracing::error!("获取用户失败: {}", e);
            Ok(ResponseJson(ApiResponse::error("用户不存在".to_string())))
        }
    }
}

pub async fn update_user(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Path(user_id): Path<String>,
    Json(request): Json<CreateUserRequest>,
) -> Result<ResponseJson<ApiResponse<UserInfo>>, StatusCode> {
    let user_service = UserService::new(database);

    match user_service
        .update_user(&auth_context.user, &user_id, request)
        .await
    {
        Ok(user) => Ok(ResponseJson(ApiResponse::success(user))),
        Err(e) => {
            tracing::error!("更新用户失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(format!(
                "更新用户失败: {}",
                e
            ))))
        }
    }
}

pub async fn delete_user(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Path(user_id): Path<String>,
) -> Result<ResponseJson<ApiResponse<()>>, StatusCode> {
    let user_service = UserService::new(database);

    match user_service.delete_user(&auth_context.user, &user_id).await {
        Ok(_) => Ok(ResponseJson(ApiResponse::success(()))),
        Err(e) => {
            tracing::error!("删除用户失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(format!(
                "删除用户失败: {}",
                e
            ))))
        }
    }
}

pub async fn get_company_statistics(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
) -> Result<ResponseJson<ApiResponse<Vec<CompanyStatistics>>>, StatusCode> {
    let user_service = UserService::new(database);

    match user_service
        .get_company_statistics(&auth_context.user)
        .await
    {
        Ok(statistics) => Ok(ResponseJson(ApiResponse::success(statistics))),
        Err(e) => {
            tracing::error!("获取公司统计信息失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(format!(
                "获取公司统计信息失败: {}",
                e
            ))))
        }
    }
}
