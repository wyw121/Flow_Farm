use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
};
use chrono::Utc;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use validator::Validate;

use crate::{
    database::Database,
    errors::AppError,
    middleware::auth::AuthContext,
    models::{
        survey::*,
        UserInfo,
    },
};

/// 查询参数结构
#[derive(Debug, Deserialize)]
pub struct SurveyListQuery {
    pub page: Option<i32>,
    pub page_size: Option<i32>,
    pub status: Option<String>,
    pub search: Option<String>,
}

/// 创建问卷
pub async fn create_survey(
    auth_context: AuthContext,
    State((database, _config)): State<(Database, crate::Config)>,
    Json(request): Json<CreateSurveyRequest>,
) -> Result<Json<Survey>, AppError> {
    // 验证请求数据
    request.validate().map_err(|e| {
        AppError::ValidationError(format!("请求验证失败: {}", e))
    })?;

    // 检查权限：只有调研经理可以创建问卷
    if auth_context.user.role != "research_manager" && auth_context.user.role != "system_admin" {
        return Err(AppError::PermissionDenied("只有调研经理可以创建问卷".to_string()));
    }

    let now = Utc::now();
    
    // 解析日期
    let start_date = if let Some(date_str) = &request.start_date {
        Some(chrono::DateTime::parse_from_rfc3339(date_str)
            .map_err(|_| AppError::ValidationError("开始日期格式无效".to_string()))?
            .with_timezone(&Utc))
    } else {
        None
    };

    let end_date = if let Some(date_str) = &request.end_date {
        Some(chrono::DateTime::parse_from_rfc3339(date_str)
            .map_err(|_| AppError::ValidationError("结束日期格式无效".to_string()))?
            .with_timezone(&Utc))
    } else {
        None
    };

    // 插入问卷记录
    let survey = sqlx::query_as::<_, Survey>(
        r#"
        INSERT INTO surveys (
            title, description, created_by, company_id, structure, 
            status, target_sample_size, current_responses,
            start_date, end_date, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, 'draft', ?, 0, ?, ?, ?, ?)
        "#,
    )
    .bind(&request.title)
    .bind(&request.description)
    .bind(auth_context.user.id)
    .bind(auth_context.user.company_id.unwrap_or(1)) // 默认公司ID
    .bind(serde_json::to_string(&request.structure).unwrap())
    .bind(request.target_sample_size)
    .bind(start_date)
    .bind(end_date)
    .bind(now)
    .bind(now)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("创建问卷失败: {}", e)))?;

    Ok(Json(survey))
}

/// 获取问卷列表
pub async fn get_surveys(
    auth_context: AuthContext,
    Query(query): Query<SurveyListQuery>,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<Json<SurveyListResponse>, AppError> {
    let page = query.page.unwrap_or(1);
    let page_size = query.page_size.unwrap_or(20).min(100); // 最大100条
    let offset = (page - 1) * page_size;

    // 构建查询条件
    let mut where_clause = "WHERE company_id = ?".to_string();
    let mut params: Vec<String> = vec![auth_context.user.company_id.unwrap_or(1).to_string()];

    if let Some(status) = &query.status {
        where_clause.push_str(" AND status = ?");
        params.push(status.clone());
    }

    if let Some(search) = &query.search {
        where_clause.push_str(" AND (title LIKE ? OR description LIKE ?)");
        let search_pattern = format!("%{}%", search);
        params.push(search_pattern.clone());
        params.push(search_pattern);
    }

    // 查询总数
    let total_query = format!("SELECT COUNT(*) as count FROM surveys {}", where_clause);
    let total: (i32,) = sqlx::query_as(&total_query)
        .bind(auth_context.user.company_id.unwrap_or(1))
        .fetch_one(&database.pool)
        .await
        .map_err(|e| AppError::DatabaseError(format!("查询问卷总数失败: {}", e)))?;

    // 查询问卷列表
    let surveys_query = format!(
        "SELECT * FROM surveys {} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        where_clause
    );
    
    let surveys: Vec<Survey> = sqlx::query_as(&surveys_query)
        .bind(auth_context.user.company_id.unwrap_or(1))
        .bind(page_size)
        .bind(offset)
        .fetch_all(&database.pool)
        .await
        .map_err(|e| AppError::DatabaseError(format!("查询问卷列表失败: {}", e)))?;

    Ok(Json(SurveyListResponse {
        surveys,
        total: total.0,
        page,
        page_size,
    }))
}

/// 获取单个问卷详情
pub async fn get_survey(
    auth_context: AuthContext,
    Path(survey_id): Path<i32>,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<Json<SurveyDetailResponse>, AppError> {
    // 查询问卷基本信息
    let survey: Survey = sqlx::query_as(
        "SELECT * FROM surveys WHERE id = ? AND company_id = ?"
    )
    .bind(survey_id)
    .bind(auth_context.user.company_id.unwrap_or(1))
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("问卷不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询问卷失败: {}", e)),
    })?;

    // 解析问卷结构中的问题
    let questions: Vec<Question> = serde_json::from_value(survey.structure.clone())
        .unwrap_or_default();

    // 查询回答数量
    let response_count: (i32,) = sqlx::query_as(
        "SELECT COUNT(*) as count FROM survey_responses WHERE survey_id = ?"
    )
    .bind(survey_id)
    .fetch_one(&database.pool)
    .await
    .unwrap_or((0,));

    Ok(Json(SurveyDetailResponse {
        survey,
        questions,
        response_count: response_count.0,
        analytics: None, // 可选的分析数据
    }))
}

/// 更新问卷
pub async fn update_survey(
    auth_context: AuthContext,
    Path(survey_id): Path<i32>,
    State((database, _config)): State<(Database, crate::Config)>,
    Json(request): Json<UpdateSurveyRequest>,
) -> Result<Json<Survey>, AppError> {
    // 验证请求数据
    request.validate().map_err(|e| {
        AppError::ValidationError(format!("请求验证失败: {}", e))
    })?;

    // 检查问卷是否存在和权限
    let existing_survey: Survey = sqlx::query_as(
        "SELECT * FROM surveys WHERE id = ? AND company_id = ?"
    )
    .bind(survey_id)
    .bind(auth_context.user.company_id.unwrap_or(1))
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("问卷不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询问卷失败: {}", e)),
    })?;

    // 检查权限：只有创建者或系统管理员可以修改
    if existing_survey.created_by != auth_context.user.id && auth_context.user.role != "system_admin" {
        return Err(AppError::PermissionDenied("无权修改此问卷".to_string()));
    }

    // 构建更新语句
    let mut set_clauses = Vec::new();
    let mut params: Vec<serde_json::Value> = Vec::new();

    if let Some(title) = &request.title {
        set_clauses.push("title = ?");
        params.push(serde_json::Value::String(title.clone()));
    }

    if let Some(description) = &request.description {
        set_clauses.push("description = ?");
        params.push(serde_json::Value::String(description.clone()));
    }

    if let Some(structure) = &request.structure {
        set_clauses.push("structure = ?");
        params.push(structure.clone());
    }

    if let Some(target_sample_size) = request.target_sample_size {
        set_clauses.push("target_sample_size = ?");
        params.push(serde_json::Value::Number(target_sample_size.into()));
    }

    if set_clauses.is_empty() {
        return Ok(Json(existing_survey));
    }

    set_clauses.push("updated_at = ?");
    params.push(serde_json::Value::String(Utc::now().to_rfc3339()));

    let update_query = format!(
        "UPDATE surveys SET {} WHERE id = ? AND company_id = ?",
        set_clauses.join(", ")
    );

    sqlx::query(&update_query)
        .bind(serde_json::to_string(&params).unwrap())
        .bind(survey_id)
        .bind(auth_context.user.company_id.unwrap_or(1))
        .execute(&database.pool)
        .await
        .map_err(|e| AppError::DatabaseError(format!("更新问卷失败: {}", e)))?;

    // 返回更新后的问卷
    let updated_survey: Survey = sqlx::query_as(
        "SELECT * FROM surveys WHERE id = ? AND company_id = ?"
    )
    .bind(survey_id)
    .bind(auth_context.user.company_id.unwrap_or(1))
    .fetch_one(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("查询更新后的问卷失败: {}", e)))?;

    Ok(Json(updated_survey))
}

/// 发布问卷
pub async fn publish_survey(
    auth_context: AuthContext,
    Path(survey_id): Path<i32>,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<Json<Survey>, AppError> {
    // 检查问卷是否存在和权限
    let survey: Survey = sqlx::query_as(
        "SELECT * FROM surveys WHERE id = ? AND company_id = ?"
    )
    .bind(survey_id)
    .bind(auth_context.user.company_id.unwrap_or(1))
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("问卷不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询问卷失败: {}", e)),
    })?;

    // 检查权限
    if survey.created_by != auth_context.user.id && auth_context.user.role != "system_admin" {
        return Err(AppError::PermissionDenied("无权发布此问卷".to_string()));
    }

    // 检查问卷状态
    if survey.status != "draft" {
        return Err(AppError::ValidationError("只能发布草稿状态的问卷".to_string()));
    }

    // 更新状态为已发布
    sqlx::query(
        "UPDATE surveys SET status = 'published', updated_at = ? WHERE id = ?"
    )
    .bind(Utc::now())
    .bind(survey_id)
    .execute(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("发布问卷失败: {}", e)))?;

    // 返回更新后的问卷
    let updated_survey: Survey = sqlx::query_as(
        "SELECT * FROM surveys WHERE id = ?"
    )
    .bind(survey_id)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("查询更新后的问卷失败: {}", e)))?;

    Ok(Json(updated_survey))
}

/// 关闭问卷
pub async fn close_survey(
    auth_context: AuthContext,
    Path(survey_id): Path<i32>,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<Json<Survey>, AppError> {
    // 检查问卷是否存在和权限
    let survey: Survey = sqlx::query_as(
        "SELECT * FROM surveys WHERE id = ? AND company_id = ?"
    )
    .bind(survey_id)
    .bind(auth_context.user.company_id.unwrap_or(1))
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("问卷不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询问卷失败: {}", e)),
    })?;

    // 检查权限
    if survey.created_by != auth_context.user.id && auth_context.user.role != "system_admin" {
        return Err(AppError::PermissionDenied("无权关闭此问卷".to_string()));
    }

    // 更新状态为已关闭
    sqlx::query(
        "UPDATE surveys SET status = 'closed', updated_at = ? WHERE id = ?"
    )
    .bind(Utc::now())
    .bind(survey_id)
    .execute(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("关闭问卷失败: {}", e)))?;

    // 返回更新后的问卷
    let updated_survey: Survey = sqlx::query_as(
        "SELECT * FROM surveys WHERE id = ?"
    )
    .bind(survey_id)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("查询更新后的问卷失败: {}", e)))?;

    Ok(Json(updated_survey))
}

/// 删除问卷
pub async fn delete_survey(
    auth_context: AuthContext,
    Path(survey_id): Path<i32>,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<StatusCode, AppError> {
    // 检查问卷是否存在和权限
    let survey: Survey = sqlx::query_as(
        "SELECT * FROM surveys WHERE id = ? AND company_id = ?"
    )
    .bind(survey_id)
    .bind(auth_context.user.company_id.unwrap_or(1))
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("问卷不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询问卷失败: {}", e)),
    })?;

    // 检查权限
    if survey.created_by != auth_context.user.id && auth_context.user.role != "system_admin" {
        return Err(AppError::PermissionDenied("无权删除此问卷".to_string()));
    }

    // 开始事务：删除问卷及其相关数据
    let mut tx = database.pool.begin().await
        .map_err(|e| AppError::DatabaseError(format!("开始事务失败: {}", e)))?;

    // 删除问卷回答
    sqlx::query("DELETE FROM survey_responses WHERE survey_id = ?")
        .bind(survey_id)
        .execute(&mut *tx)
        .await
        .map_err(|e| AppError::DatabaseError(format!("删除问卷回答失败: {}", e)))?;

    // 删除问卷
    sqlx::query("DELETE FROM surveys WHERE id = ?")
        .bind(survey_id)
        .execute(&mut *tx)
        .await
        .map_err(|e| AppError::DatabaseError(format!("删除问卷失败: {}", e)))?;

    tx.commit().await
        .map_err(|e| AppError::DatabaseError(format!("提交事务失败: {}", e)))?;

    Ok(StatusCode::NO_CONTENT)
}

/// 提交问卷回答
pub async fn submit_survey_response(
    Path(survey_id): Path<i32>,
    State((database, _config)): State<(Database, crate::Config)>,
    Json(request): Json<SubmitSurveyResponseRequest>,
) -> Result<Json<SurveyResponse>, AppError> {
    // 验证请求数据
    request.validate().map_err(|e| {
        AppError::ValidationError(format!("请求验证失败: {}", e))
    })?;

    // 检查问卷是否存在且已发布
    let survey: Survey = sqlx::query_as(
        "SELECT * FROM surveys WHERE id = ? AND status = 'published'"
    )
    .bind(survey_id)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("问卷不存在或未发布".to_string()),
        _ => AppError::DatabaseError(format!("查询问卷失败: {}", e)),
    })?;

    // 检查是否超过截止日期
    if let Some(end_date) = survey.end_date {
        if Utc::now() > end_date {
            return Err(AppError::ValidationError("问卷已过期".to_string()));
        }
    }

    let now = Utc::now();

    // 插入回答记录
    let response = sqlx::query_as::<_, SurveyResponse>(
        r#"
        INSERT INTO survey_responses (
            survey_id, respondent_info, answers, location, 
            device_info, submitted_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(survey_id)
    .bind(serde_json::to_string(&request.respondent_info).unwrap())
    .bind(serde_json::to_string(&request.answers).unwrap())
    .bind(&request.location)
    .bind(&request.device_info)
    .bind(now)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("提交回答失败: {}", e)))?;

    // 更新问卷的回答计数
    sqlx::query(
        "UPDATE surveys SET current_responses = current_responses + 1, updated_at = ? WHERE id = ?"
    )
    .bind(now)
    .bind(survey_id)
    .execute(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("更新回答计数失败: {}", e)))?;

    Ok(Json(response))
}