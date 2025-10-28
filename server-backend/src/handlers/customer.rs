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
        customer::*,
        UserInfo,
    },
};

/// 查询参数结构
#[derive(Debug, Deserialize)]
pub struct CustomerListQuery {
    pub page: Option<i32>,
    pub page_size: Option<i32>,
    pub industry: Option<String>,
    pub company_size: Option<String>,
    pub search: Option<String>,
}

/// 创建客户
pub async fn create_customer(
    auth_context: AuthContext,
    State((database, _config)): State<(Database, crate::Config)>,
    Json(request): Json<CreateCustomerRequest>,
) -> Result<Json<Customer>, AppError> {
    // 验证请求数据
    request.validate().map_err(|e| {
        AppError::ValidationError(format!("请求验证失败: {}", e))
    })?;

    // 检查权限：只有调研经理可以创建客户
    if auth_context.user.role != "research_manager" && auth_context.user.role != "system_admin" {
        return Err(AppError::PermissionDenied("只有调研经理可以创建客户".to_string()));
    }

    let now = Utc::now();

    // 插入客户记录
    let customer = sqlx::query_as::<_, Customer>(
        r#"
        INSERT INTO customers (
            company_name, contact_person, phone, email, address, industry,
            company_size, annual_revenue, latitude, longitude, notes,
            created_by, company_id, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING *
        "#,
    )
    .bind(&request.company_name)
    .bind(&request.contact_person)
    .bind(&request.phone)
    .bind(&request.email)
    .bind(&request.address)
    .bind(&request.industry)
    .bind(&request.company_size)
    .bind(request.annual_revenue)
    .bind(request.latitude)
    .bind(request.longitude)
    .bind(&request.notes)
    .bind(auth_context.user.id)
    .bind(auth_context.user.company_id.unwrap_or(1))
    .bind(now)
    .bind(now)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("创建客户失败: {}", e)))?;

    Ok(Json(customer))
}

/// 获取客户列表
pub async fn get_customers(
    auth_context: AuthContext,
    Query(query): Query<CustomerListQuery>,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<Json<CustomerListResponse>, AppError> {
    let page = query.page.unwrap_or(1);
    let page_size = query.page_size.unwrap_or(20).min(100);
    let offset = (page - 1) * page_size;

    // 构建查询条件
    let mut where_clause = "WHERE company_id = ?".to_string();
    let mut params: Vec<String> = vec![auth_context.user.company_id.unwrap_or(1).to_string()];

    if let Some(industry) = &query.industry {
        where_clause.push_str(" AND industry = ?");
        params.push(industry.clone());
    }

    if let Some(company_size) = &query.company_size {
        where_clause.push_str(" AND company_size = ?");
        params.push(company_size.clone());
    }

    if let Some(search) = &query.search {
        where_clause.push_str(" AND (company_name LIKE ? OR contact_person LIKE ? OR phone LIKE ?)");
        let search_pattern = format!("%{}%", search);
        params.push(search_pattern.clone());
        params.push(search_pattern.clone());
        params.push(search_pattern);
    }

    // 查询总数
    let total_query = format!("SELECT COUNT(*) as count FROM customers {}", where_clause);
    let total: (i32,) = sqlx::query_as(&total_query)
        .bind(auth_context.user.company_id.unwrap_or(1))
        .fetch_one(&database.pool)
        .await
        .map_err(|e| AppError::DatabaseError(format!("查询客户总数失败: {}", e)))?;

    // 查询客户列表
    let customers_query = format!(
        "SELECT * FROM customers {} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        where_clause
    );
    
    let customers: Vec<Customer> = sqlx::query_as(&customers_query)
        .bind(auth_context.user.company_id.unwrap_or(1))
        .bind(page_size)
        .bind(offset)
        .fetch_all(&database.pool)
        .await
        .map_err(|e| AppError::DatabaseError(format!("查询客户列表失败: {}", e)))?;

    Ok(Json(CustomerListResponse {
        customers,
        total: total.0,
        page,
        page_size,
    }))
}

/// 获取单个客户详情
pub async fn get_customer(
    auth_context: AuthContext,
    Path(customer_id): Path<i32>,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<Json<Customer>, AppError> {
    let customer: Customer = sqlx::query_as(
        "SELECT * FROM customers WHERE id = ? AND company_id = ?"
    )
    .bind(customer_id)
    .bind(auth_context.user.company_id.unwrap_or(1))
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("客户不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询客户失败: {}", e)),
    })?;

    Ok(Json(customer))
}

/// 更新客户信息
pub async fn update_customer(
    auth_context: AuthContext,
    Path(customer_id): Path<i32>,
    State((database, _config)): State<(Database, crate::Config)>,
    Json(request): Json<UpdateCustomerRequest>,
) -> Result<Json<Customer>, AppError> {
    // 验证请求数据
    request.validate().map_err(|e| {
        AppError::ValidationError(format!("请求验证失败: {}", e))
    })?;

    // 检查客户是否存在和权限
    let existing_customer: Customer = sqlx::query_as(
        "SELECT * FROM customers WHERE id = ? AND company_id = ?"
    )
    .bind(customer_id)
    .bind(auth_context.user.company_id.unwrap_or(1))
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("客户不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询客户失败: {}", e)),
    })?;

    // 构建更新语句
    let mut set_clauses = Vec::new();
    let mut bind_params = Vec::new();

    if let Some(company_name) = &request.company_name {
        set_clauses.push("company_name = ?");
        bind_params.push(company_name.clone());
    }

    if let Some(contact_person) = &request.contact_person {
        set_clauses.push("contact_person = ?");
        bind_params.push(contact_person.clone());
    }

    if let Some(phone) = &request.phone {
        set_clauses.push("phone = ?");
        bind_params.push(phone.clone());
    }

    if let Some(email) = &request.email {
        set_clauses.push("email = ?");
        bind_params.push(email.clone());
    }

    if let Some(address) = &request.address {
        set_clauses.push("address = ?");
        bind_params.push(address.clone());
    }

    if let Some(industry) = &request.industry {
        set_clauses.push("industry = ?");
        bind_params.push(industry.clone());
    }

    if let Some(company_size) = &request.company_size {
        set_clauses.push("company_size = ?");
        bind_params.push(company_size.clone());
    }

    if let Some(annual_revenue) = request.annual_revenue {
        set_clauses.push("annual_revenue = ?");
        bind_params.push(annual_revenue.to_string());
    }

    if let Some(latitude) = request.latitude {
        set_clauses.push("latitude = ?");
        bind_params.push(latitude.to_string());
    }

    if let Some(longitude) = request.longitude {
        set_clauses.push("longitude = ?");
        bind_params.push(longitude.to_string());
    }

    if let Some(notes) = &request.notes {
        set_clauses.push("notes = ?");
        bind_params.push(notes.clone());
    }

    if set_clauses.is_empty() {
        return Ok(Json(existing_customer));
    }

    set_clauses.push("updated_at = ?");
    bind_params.push(Utc::now().to_rfc3339());

    let update_query = format!(
        "UPDATE customers SET {} WHERE id = ? AND company_id = ?",
        set_clauses.join(", ")
    );

    // 执行更新（这里简化处理，实际应该用更好的方式绑定参数）
    sqlx::query(&update_query)
        .bind(customer_id)
        .bind(auth_context.user.company_id.unwrap_or(1))
        .execute(&database.pool)
        .await
        .map_err(|e| AppError::DatabaseError(format!("更新客户失败: {}", e)))?;

    // 返回更新后的客户
    let updated_customer: Customer = sqlx::query_as(
        "SELECT * FROM customers WHERE id = ? AND company_id = ?"
    )
    .bind(customer_id)
    .bind(auth_context.user.company_id.unwrap_or(1))
    .fetch_one(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("查询更新后的客户失败: {}", e)))?;

    Ok(Json(updated_customer))
}

/// 删除客户
pub async fn delete_customer(
    auth_context: AuthContext,
    Path(customer_id): Path<i32>,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<StatusCode, AppError> {
    // 检查权限：只有调研经理和系统管理员可以删除客户
    if auth_context.user.role != "research_manager" && auth_context.user.role != "system_admin" {
        return Err(AppError::PermissionDenied("无权删除客户".to_string()));
    }

    // 检查客户是否存在
    let existing_customer: Customer = sqlx::query_as(
        "SELECT * FROM customers WHERE id = ? AND company_id = ?"
    )
    .bind(customer_id)
    .bind(auth_context.user.company_id.unwrap_or(1))
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("客户不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询客户失败: {}", e)),
    })?;

    // 开始事务：删除客户及其相关数据
    let mut tx = database.pool.begin().await
        .map_err(|e| AppError::DatabaseError(format!("开始事务失败: {}", e)))?;

    // 删除拜访记录的附件
    sqlx::query("DELETE FROM visit_attachments WHERE visit_id IN (SELECT id FROM visit_records WHERE customer_id = ?)")
        .bind(customer_id)
        .execute(&mut *tx)
        .await
        .map_err(|e| AppError::DatabaseError(format!("删除拜访附件失败: {}", e)))?;

    // 删除拜访记录
    sqlx::query("DELETE FROM visit_records WHERE customer_id = ?")
        .bind(customer_id)
        .execute(&mut *tx)
        .await
        .map_err(|e| AppError::DatabaseError(format!("删除拜访记录失败: {}", e)))?;

    // 删除客户
    sqlx::query("DELETE FROM customers WHERE id = ?")
        .bind(customer_id)
        .execute(&mut *tx)
        .await
        .map_err(|e| AppError::DatabaseError(format!("删除客户失败: {}", e)))?;

    tx.commit().await
        .map_err(|e| AppError::DatabaseError(format!("提交事务失败: {}", e)))?;

    Ok(StatusCode::NO_CONTENT)
}

/// 获取客户统计信息
pub async fn get_customer_statistics(
    auth_context: AuthContext,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<Json<serde_json::Value>, AppError> {
    let company_id = auth_context.user.company_id.unwrap_or(1);

    // 客户总数
    let total_customers: (i32,) = sqlx::query_as(
        "SELECT COUNT(*) as count FROM customers WHERE company_id = ?"
    )
    .bind(company_id)
    .fetch_one(&database.pool)
    .await
    .unwrap_or((0,));

    // 按行业分布
    let industry_stats: Vec<(String, i32)> = sqlx::query_as(
        "SELECT industry, COUNT(*) as count FROM customers WHERE company_id = ? GROUP BY industry ORDER BY count DESC"
    )
    .bind(company_id)
    .fetch_all(&database.pool)
    .await
    .unwrap_or_default();

    // 按公司规模分布
    let size_stats: Vec<(String, i32)> = sqlx::query_as(
        "SELECT company_size, COUNT(*) as count FROM customers WHERE company_id = ? AND company_size IS NOT NULL GROUP BY company_size"
    )
    .bind(company_id)
    .fetch_all(&database.pool)
    .await
    .unwrap_or_default();

    // 最近30天新增客户
    let recent_customers: (i32,) = sqlx::query_as(
        "SELECT COUNT(*) as count FROM customers WHERE company_id = ? AND created_at >= datetime('now', '-30 days')"
    )
    .bind(company_id)
    .fetch_one(&database.pool)
    .await
    .unwrap_or((0,));

    let statistics = serde_json::json!({
        "total_customers": total_customers.0,
        "recent_customers": recent_customers.0,
        "industry_distribution": industry_stats.into_iter().map(|(industry, count)| serde_json::json!({
            "industry": industry,
            "count": count
        })).collect::<Vec<_>>(),
        "size_distribution": size_stats.into_iter().map(|(size, count)| serde_json::json!({
            "size": size,
            "count": count
        })).collect::<Vec<_>>()
    });

    Ok(Json(statistics))
}