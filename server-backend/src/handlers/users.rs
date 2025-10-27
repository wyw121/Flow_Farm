use axum::{
    extract::{Path, Query, State},
    response::Json as ResponseJson,
    Json,
};
use serde::Deserialize;

use crate::{
    errors::AppError,
    middleware::auth::AuthContext,
    models::{ApiResponse, CompanyStatistics, CreateUserRequest, UpdateUserRequest, UserInfo},
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
) -> Result<ResponseJson<ApiResponse<Vec<UserInfo>>>, AppError> {
    let user_service = UserService::new(database);

    let users = user_service
        .list_users(
            &auth_context.user,
            query.page.unwrap_or(1),
            query.limit.unwrap_or(20),
            query.role.as_deref(),
        )
        .await?;

    Ok(ResponseJson(ApiResponse::success(users)))
}

pub async fn create_user(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Json(request): Json<CreateUserRequest>,
) -> Result<ResponseJson<ApiResponse<UserInfo>>, AppError> {
    tracing::info!("创建用户请求: {:?}", request);
    tracing::info!("请求用户: {:?}", auth_context.user);

    let user_service = UserService::new(database);
    let user = user_service.create_user(&auth_context.user, request).await?;

    tracing::info!("用户创建成功: {:?}", user);
    Ok(ResponseJson(ApiResponse::success(user)))
}

pub async fn get_user(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Path(user_id): Path<String>,
) -> Result<ResponseJson<ApiResponse<UserInfo>>, AppError> {
    let user_service = UserService::new(database);
    let user = user_service.get_user(&auth_context.user, &user_id).await?;

    Ok(ResponseJson(ApiResponse::success(user)))
}

pub async fn update_user(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
    Path(user_id): Path<String>,
    Json(request): Json<UpdateUserRequest>,
) -> Result<ResponseJson<ApiResponse<UserInfo>>, AppError> {
    let user_service = UserService::new(database);
    let user = user_service
        .update_user(&auth_context.user, &user_id, request)
        .await?;

    Ok(ResponseJson(ApiResponse::success(user)))
}

pub async fn delete_user(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Path(user_id): Path<String>,
) -> Result<ResponseJson<ApiResponse<()>>, AppError> {
    let user_service = UserService::new(database);
    user_service.delete_user(&auth_context.user, &user_id).await?;

    Ok(ResponseJson(ApiResponse::success(())))
}

pub async fn get_company_statistics(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
) -> Result<ResponseJson<ApiResponse<Vec<CompanyStatistics>>>, AppError> {
    let user_service = UserService::new(database);
    let statistics = user_service
        .get_company_statistics(&auth_context.user)
        .await?;

    Ok(ResponseJson(ApiResponse::success(statistics)))
}

pub async fn get_company_names(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
) -> Result<ResponseJson<ApiResponse<Vec<String>>>, AppError> {
    let user_service = UserService::new(database);
    let company_names = user_service.get_company_names(&auth_context.user).await?;

    Ok(ResponseJson(ApiResponse::success(company_names)))
}
