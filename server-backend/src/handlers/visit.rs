use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
};
use chrono::{NaiveDate, Utc};
use serde::{Deserialize, Serialize};
use sqlx::Row;
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

/// 拜访查询参数
#[derive(Debug, Deserialize)]
pub struct VisitListQuery {
    pub page: Option<i32>,
    pub page_size: Option<i32>,
    pub status: Option<String>,
    pub customer_id: Option<i32>,
    pub field_worker_id: Option<i32>,
    pub date_from: Option<String>,
    pub date_to: Option<String>,
}

/// 创建拜访计划
pub async fn create_visit(
    auth_context: AuthContext,
    State((database, _config)): State<(Database, crate::Config)>,
    Json(request): Json<CreateVisitRequest>,
) -> Result<Json<VisitRecord>, AppError> {
    // 验证请求数据
    request.validate().map_err(|e| {
        AppError::ValidationError(format!("请求验证失败: {}", e))
    })?;

    // 检查权限：只有调研经理可以创建拜访计划
    if auth_context.user.role != "research_manager" && auth_context.user.role != "system_admin" {
        return Err(AppError::PermissionDenied("只有调研经理可以创建拜访计划".to_string()));
    }

    // 验证客户是否存在
    let _customer: Customer = sqlx::query_as(
        "SELECT * FROM customers WHERE id = ? AND company_id = ?"
    )
    .bind(request.customer_id)
    .bind(auth_context.user.company_id.unwrap_or(1))
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("客户不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询客户失败: {}", e)),
    })?;

    // 解析计划日期
    let planned_date = NaiveDate::parse_from_str(&request.planned_date, "%Y-%m-%d")
        .map_err(|_| AppError::ValidationError("日期格式无效，应为 YYYY-MM-DD".to_string()))?;

    let now = Utc::now();

    // 插入拜访记录
    let visit = sqlx::query_as::<_, VisitRecord>(
        r#"
        INSERT INTO visit_records (
            customer_id, field_worker_id, planned_date, planned_start_time,
            planned_duration, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, 'planned', ?, ?)
        RETURNING *
        "#,
    )
    .bind(request.customer_id)
    .bind(request.field_worker_id)
    .bind(planned_date)
    .bind(&request.planned_start_time)
    .bind(request.planned_duration)
    .bind(now)
    .bind(now)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("创建拜访记录失败: {}", e)))?;

    Ok(Json(visit))
}

/// 开始拜访
pub async fn start_visit(
    auth_context: AuthContext,
    Path(visit_id): Path<i32>,
    State((database, _config)): State<(Database, crate::Config)>,
    Json(request): Json<StartVisitRequest>,
) -> Result<Json<VisitRecord>, AppError> {
    // 验证请求数据
    request.validate().map_err(|e| {
        AppError::ValidationError(format!("请求验证失败: {}", e))
    })?;

    // 检查拜访记录是否存在
    let visit: VisitRecord = sqlx::query_as(
        "SELECT * FROM visit_records WHERE id = ?"
    )
    .bind(visit_id)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("拜访记录不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询拜访记录失败: {}", e)),
    })?;

    // 检查权限：只有指定的现场工作人员可以开始拜访
    if visit.field_worker_id != auth_context.user.id && auth_context.user.role != "system_admin" {
        return Err(AppError::PermissionDenied("只有指定的现场工作人员可以开始拜访".to_string()));
    }

    // 检查状态
    if visit.status != "planned" {
        return Err(AppError::ValidationError("只能开始已计划的拜访".to_string()));
    }

    let now = Utc::now();

    // 更新拜访状态
    sqlx::query(
        r#"
        UPDATE visit_records 
        SET status = 'in_progress', 
            actual_start_time = ?, 
            arrival_lat = ?, 
            arrival_lng = ?, 
            location_accuracy = ?,
            updated_at = ?
        WHERE id = ?
        "#
    )
    .bind(now)
    .bind(request.arrival_lat)
    .bind(request.arrival_lng)
    .bind(request.location_accuracy)
    .bind(now)
    .bind(visit_id)
    .execute(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("开始拜访失败: {}", e)))?;

    // 返回更新后的拜访记录
    let updated_visit: VisitRecord = sqlx::query_as(
        "SELECT * FROM visit_records WHERE id = ?"
    )
    .bind(visit_id)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("查询更新后的拜访记录失败: {}", e)))?;

    Ok(Json(updated_visit))
}

/// 结束拜访
pub async fn end_visit(
    auth_context: AuthContext,
    Path(visit_id): Path<i32>,
    State((database, _config)): State<(Database, crate::Config)>,
    Json(request): Json<EndVisitRequest>,
) -> Result<Json<VisitRecord>, AppError> {
    // 验证请求数据
    request.validate().map_err(|e| {
        AppError::ValidationError(format!("请求验证失败: {}", e))
    })?;

    // 检查拜访记录是否存在
    let visit: VisitRecord = sqlx::query_as(
        "SELECT * FROM visit_records WHERE id = ?"
    )
    .bind(visit_id)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("拜访记录不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询拜访记录失败: {}", e)),
    })?;

    // 检查权限
    if visit.field_worker_id != auth_context.user.id && auth_context.user.role != "system_admin" {
        return Err(AppError::PermissionDenied("只有指定的现场工作人员可以结束拜访".to_string()));
    }

    // 检查状态
    if visit.status != "in_progress" {
        return Err(AppError::ValidationError("只能结束进行中的拜访".to_string()));
    }

    let now = Utc::now();

    // 更新拜访状态
    sqlx::query(
        r#"
        UPDATE visit_records 
        SET status = 'completed',
            actual_end_time = ?,
            departure_lat = ?,
            departure_lng = ?,
            visit_summary = ?,
            customer_feedback = ?,
            business_opportunities = ?,
            competitor_info = ?,
            follow_up_plan = ?,
            visit_rating = ?,
            customer_satisfaction = ?,
            updated_at = ?
        WHERE id = ?
        "#
    )
    .bind(now)
    .bind(request.departure_lat)
    .bind(request.departure_lng)
    .bind(&request.visit_summary)
    .bind(serde_json::to_string(&request.customer_feedback).unwrap_or_default())
    .bind(serde_json::to_string(&request.business_opportunities).unwrap_or_default())
    .bind(serde_json::to_string(&request.competitor_info).unwrap_or_default())
    .bind(&request.follow_up_plan)
    .bind(request.visit_rating)
    .bind(request.customer_satisfaction)
    .bind(now)
    .bind(visit_id)
    .execute(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("结束拜访失败: {}", e)))?;

    // 返回更新后的拜访记录
    let updated_visit: VisitRecord = sqlx::query_as(
        "SELECT * FROM visit_records WHERE id = ?"
    )
    .bind(visit_id)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("查询更新后的拜访记录失败: {}", e)))?;

    Ok(Json(updated_visit))
}

/// 获取拜访记录列表
pub async fn get_visits(
    auth_context: AuthContext,
    Query(query): Query<VisitListQuery>,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<Json<VisitRecordListResponse>, AppError> {
    let page = query.page.unwrap_or(1);
    let page_size = query.page_size.unwrap_or(20).min(100);
    let offset = (page - 1) * page_size;

    // 构建查询条件
    let mut where_clauses = vec!["c.company_id = ?".to_string()];
    let mut params: Vec<String> = vec![auth_context.user.company_id.unwrap_or(1).to_string()];

    if let Some(status) = &query.status {
        where_clauses.push("v.status = ?".to_string());
        params.push(status.clone());
    }

    if let Some(customer_id) = query.customer_id {
        where_clauses.push("v.customer_id = ?".to_string());
        params.push(customer_id.to_string());
    }

    if let Some(field_worker_id) = query.field_worker_id {
        where_clauses.push("v.field_worker_id = ?".to_string());
        params.push(field_worker_id.to_string());
    }

    if let Some(date_from) = &query.date_from {
        where_clauses.push("v.planned_date >= ?".to_string());
        params.push(date_from.clone());
    }

    if let Some(date_to) = &query.date_to {
        where_clauses.push("v.planned_date <= ?".to_string());
        params.push(date_to.clone());
    }

    let where_clause = where_clauses.join(" AND ");

    // 查询总数
    let total_query = format!(
        "SELECT COUNT(*) as count FROM visit_records v JOIN customers c ON v.customer_id = c.id WHERE {}",
        where_clause
    );
    let total: (i32,) = sqlx::query_as(&total_query)
        .bind(auth_context.user.company_id.unwrap_or(1))
        .fetch_one(&database.pool)
        .await
        .map_err(|e| AppError::DatabaseError(format!("查询拜访记录总数失败: {}", e)))?;

    // 查询拜访记录列表（连接客户和用户信息）
    let visits_query = format!(
        r#"
        SELECT 
            v.*,
            c.company_name, c.contact_person, c.phone, c.email, c.address, c.industry,
            c.company_size, c.annual_revenue, c.latitude, c.longitude, c.notes,
            c.created_by as customer_created_by, c.company_id as customer_company_id,
            c.created_at as customer_created_at, c.updated_at as customer_updated_at,
            u.username as field_worker_name
        FROM visit_records v 
        JOIN customers c ON v.customer_id = c.id 
        JOIN users u ON v.field_worker_id = u.id
        WHERE {}
        ORDER BY v.planned_date DESC, v.planned_start_time ASC
        LIMIT ? OFFSET ?
        "#,
        where_clause
    );

    // 这里需要手动构建结果，因为连接查询比较复杂
    let visits: Vec<VisitRecordWithCustomer> = sqlx::query(&visits_query)
        .bind(auth_context.user.company_id.unwrap_or(1))
        .bind(page_size)
        .bind(offset)
        .fetch_all(&database.pool)
        .await
        .map_err(|e| AppError::DatabaseError(format!("查询拜访记录列表失败: {}", e)))?
        .into_iter()
        .map(|row| {
            // 手动映射行数据到结构体
            // 这里简化处理，实际应该用更好的方式
            VisitRecordWithCustomer {
                visit: VisitRecord {
                    id: row.get("id"),
                    customer_id: row.get("customer_id"),
                    field_worker_id: row.get("field_worker_id"),
                    planned_date: row.get("planned_date"),
                    planned_start_time: row.get("planned_start_time"),
                    planned_duration: row.get("planned_duration"),
                    actual_start_time: row.get("actual_start_time"),
                    actual_end_time: row.get("actual_end_time"),
                    arrival_lat: row.get("arrival_lat"),
                    arrival_lng: row.get("arrival_lng"),
                    departure_lat: row.get("departure_lat"),
                    departure_lng: row.get("departure_lng"),
                    location_accuracy: row.get("location_accuracy"),
                    visit_summary: row.get("visit_summary"),
                    customer_feedback: row.get("customer_feedback"),
                    business_opportunities: row.get("business_opportunities"),
                    competitor_info: row.get("competitor_info"),
                    follow_up_plan: row.get("follow_up_plan"),
                    visit_rating: row.get("visit_rating"),
                    customer_satisfaction: row.get("customer_satisfaction"),
                    status: row.get("status"),
                    created_at: row.get("created_at"),
                    updated_at: row.get("updated_at"),
                },
                customer: Customer {
                    id: row.get("customer_id"),
                    company_name: row.get("company_name"),
                    contact_person: row.get("contact_person"),
                    phone: row.get("phone"),
                    email: row.get("email"),
                    address: row.get("address"),
                    industry: row.get("industry"),
                    company_size: row.get("company_size"),
                    annual_revenue: row.get("annual_revenue"),
                    latitude: row.get("latitude"),
                    longitude: row.get("longitude"),
                    notes: row.get("notes"),
                    created_by: row.get("customer_created_by"),
                    company_id: row.get("customer_company_id"),
                    created_at: row.get("customer_created_at"),
                    updated_at: row.get("customer_updated_at"),
                },
                field_worker_name: row.get("field_worker_name"),
                attachments: Vec::new(), // 后续可以单独查询附件
            }
        })
        .collect();

    Ok(Json(VisitRecordListResponse {
        visits,
        total: total.0,
        page,
        page_size,
    }))
}

/// 获取拜访记录详情
pub async fn get_visit(
    auth_context: AuthContext,
    Path(visit_id): Path<i32>,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<Json<VisitRecordWithCustomer>, AppError> {
    // 查询拜访记录和客户信息
    let visit_query = r#"
        SELECT 
            v.*,
            c.company_name, c.contact_person, c.phone, c.email, c.address, c.industry,
            c.company_size, c.annual_revenue, c.latitude, c.longitude, c.notes,
            c.created_by as customer_created_by, c.company_id as customer_company_id,
            c.created_at as customer_created_at, c.updated_at as customer_updated_at,
            u.username as field_worker_name
        FROM visit_records v 
        JOIN customers c ON v.customer_id = c.id 
        JOIN users u ON v.field_worker_id = u.id
        WHERE v.id = ? AND c.company_id = ?
    "#;

    let row = sqlx::query(visit_query)
        .bind(visit_id)
        .bind(auth_context.user.company_id.unwrap_or(1))
        .fetch_one(&database.pool)
        .await
        .map_err(|e| match e {
            sqlx::Error::RowNotFound => AppError::NotFound("拜访记录不存在".to_string()),
            _ => AppError::DatabaseError(format!("查询拜访记录失败: {}", e)),
        })?;

    // 查询附件
    let attachments: Vec<VisitAttachment> = sqlx::query_as(
        "SELECT * FROM visit_attachments WHERE visit_id = ? ORDER BY upload_time DESC"
    )
    .bind(visit_id)
    .fetch_all(&database.pool)
    .await
    .unwrap_or_default();

    let visit_with_customer = VisitRecordWithCustomer {
        visit: VisitRecord {
            id: row.get("id"),
            customer_id: row.get("customer_id"),
            field_worker_id: row.get("field_worker_id"),
            planned_date: row.get("planned_date"),
            planned_start_time: row.get("planned_start_time"),
            planned_duration: row.get("planned_duration"),
            actual_start_time: row.get("actual_start_time"),
            actual_end_time: row.get("actual_end_time"),
            arrival_lat: row.get("arrival_lat"),
            arrival_lng: row.get("arrival_lng"),
            departure_lat: row.get("departure_lat"),
            departure_lng: row.get("departure_lng"),
            location_accuracy: row.get("location_accuracy"),
            visit_summary: row.get("visit_summary"),
            customer_feedback: row.get("customer_feedback"),
            business_opportunities: row.get("business_opportunities"),
            competitor_info: row.get("competitor_info"),
            follow_up_plan: row.get("follow_up_plan"),
            visit_rating: row.get("visit_rating"),
            customer_satisfaction: row.get("customer_satisfaction"),
            status: row.get("status"),
            created_at: row.get("created_at"),
            updated_at: row.get("updated_at"),
        },
        customer: Customer {
            id: row.get("customer_id"),
            company_name: row.get("company_name"),
            contact_person: row.get("contact_person"),
            phone: row.get("phone"),
            email: row.get("email"),
            address: row.get("address"),
            industry: row.get("industry"),
            company_size: row.get("company_size"),
            annual_revenue: row.get("annual_revenue"),
            latitude: row.get("latitude"),
            longitude: row.get("longitude"),
            notes: row.get("notes"),
            created_by: row.get("customer_created_by"),
            company_id: row.get("customer_company_id"),
            created_at: row.get("customer_created_at"),
            updated_at: row.get("customer_updated_at"),
        },
        field_worker_name: row.get("field_worker_name"),
        attachments,
    };

    Ok(Json(visit_with_customer))
}

/// 取消拜访
pub async fn cancel_visit(
    auth_context: AuthContext,
    Path(visit_id): Path<i32>,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<Json<VisitRecord>, AppError> {
    // 检查拜访记录是否存在
    let visit: VisitRecord = sqlx::query_as(
        "SELECT * FROM visit_records WHERE id = ?"
    )
    .bind(visit_id)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound("拜访记录不存在".to_string()),
        _ => AppError::DatabaseError(format!("查询拜访记录失败: {}", e)),
    })?;

    // 检查权限：调研经理或拜访人员可以取消
    if visit.field_worker_id != auth_context.user.id 
        && auth_context.user.role != "research_manager" 
        && auth_context.user.role != "system_admin" {
        return Err(AppError::PermissionDenied("无权取消此拜访".to_string()));
    }

    // 检查状态
    if visit.status == "completed" {
        return Err(AppError::ValidationError("已完成的拜访不能取消".to_string()));
    }

    // 更新状态
    sqlx::query(
        "UPDATE visit_records SET status = 'cancelled', updated_at = ? WHERE id = ?"
    )
    .bind(Utc::now())
    .bind(visit_id)
    .execute(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("取消拜访失败: {}", e)))?;

    // 返回更新后的拜访记录
    let updated_visit: VisitRecord = sqlx::query_as(
        "SELECT * FROM visit_records WHERE id = ?"
    )
    .bind(visit_id)
    .fetch_one(&database.pool)
    .await
    .map_err(|e| AppError::DatabaseError(format!("查询更新后的拜访记录失败: {}", e)))?;

    Ok(Json(updated_visit))
}

/// 获取拜访统计数据
pub async fn get_visit_statistics(
    auth_context: AuthContext,
    State((database, _config)): State<(Database, crate::Config)>,
) -> Result<Json<VisitStatistics>, AppError> {
    let company_id = auth_context.user.company_id.unwrap_or(1);

    // 总拜访数
    let total_visits: (i32,) = sqlx::query_as(
        "SELECT COUNT(*) as count FROM visit_records v JOIN customers c ON v.customer_id = c.id WHERE c.company_id = ?"
    )
    .bind(company_id)
    .fetch_one(&database.pool)
    .await
    .unwrap_or((0,));

    // 已完成拜访数
    let completed_visits: (i32,) = sqlx::query_as(
        "SELECT COUNT(*) as count FROM visit_records v JOIN customers c ON v.customer_id = c.id WHERE c.company_id = ? AND v.status = 'completed'"
    )
    .bind(company_id)
    .fetch_one(&database.pool)
    .await
    .unwrap_or((0,));

    // 计算完成率
    let completion_rate = if total_visits.0 > 0 {
        (completed_visits.0 as f64 / total_visits.0 as f64) * 100.0
    } else {
        0.0
    };

    // 平均拜访时长（已完成的拜访）
    let avg_duration: (Option<f64>,) = sqlx::query_as(
        r#"
        SELECT AVG(
            CASE 
                WHEN actual_start_time IS NOT NULL AND actual_end_time IS NOT NULL 
                THEN (julianday(actual_end_time) - julianday(actual_start_time)) * 24 * 60 
                ELSE NULL 
            END
        ) as avg_minutes
        FROM visit_records v 
        JOIN customers c ON v.customer_id = c.id 
        WHERE c.company_id = ? AND v.status = 'completed'
        "#
    )
    .bind(company_id)
    .fetch_one(&database.pool)
    .await
    .unwrap_or((None,));

    // 客户总数
    let total_customers: (i32,) = sqlx::query_as(
        "SELECT COUNT(*) as count FROM customers WHERE company_id = ?"
    )
    .bind(company_id)
    .fetch_one(&database.pool)
    .await
    .unwrap_or((0,));

    // 活跃客户数（近30天有拜访的客户）
    let active_customers: (i32,) = sqlx::query_as(
        r#"
        SELECT COUNT(DISTINCT v.customer_id) as count 
        FROM visit_records v 
        JOIN customers c ON v.customer_id = c.id 
        WHERE c.company_id = ? AND v.created_at >= datetime('now', '-30 days')
        "#
    )
    .bind(company_id)
    .fetch_one(&database.pool)
    .await
    .unwrap_or((0,));

    // 构建统计结果
    let statistics = VisitStatistics {
        total_visits: total_visits.0,
        completed_visits: completed_visits.0,
        completion_rate,
        average_duration: avg_duration.0.unwrap_or(0.0) as i32,
        total_customers: total_customers.0,
        active_customers: active_customers.0,
        monthly_visits: HashMap::new(), // 可以后续实现
        top_industries: Vec::new(),     // 可以后续实现
        geographic_distribution: HashMap::new(), // 可以后续实现
    };

    Ok(Json(statistics))
}