use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
    Extension,
};
use std::collections::HashMap;

use crate::{
    errors::{AppError, AppResult},
    models::{
        expense::*,
        User,
    },
    middleware::auth::AuthContext,
    Database, Config,
};

type AppState = (Database, Config);

/// 创建费用记录
pub async fn create_expense(
    State((database, _config)): State<AppState>,
    Extension(auth_context): Extension<AuthContext>,
    Json(request): Json<CreateExpenseRequest>,
) -> AppResult<Json<ExpenseRecord>> {
    let pool = &database.pool;
    let user_id = auth_context.user.id;
    
    // 验证费用类别是否存在
    let category = sqlx::query_as::<_, ExpenseCategory>(
        "SELECT * FROM expense_categories WHERE id = ? AND is_active = true"
    )
    .bind(request.expense_category_id)
    .fetch_optional(pool)
    .await?
    .ok_or_else(|| AppError::BadRequest("费用类别不存在或已禁用".to_string()))?;

    // 验证金额限制
    if let Some(max_amount) = category.max_amount {
        if request.amount > max_amount {
            return Err(AppError::BadRequest(format!(
                "费用金额 {} 超过类别最大限制 {}", 
                request.amount, max_amount
            )));
        }
    }

    let now = chrono::Utc::now();
    
    let expense = sqlx::query_as::<_, ExpenseRecord>(
        r#"
        INSERT INTO expense_records (
            visit_id, employee_id, expense_category_id, amount, currency,
            description, expense_date, location, vendor_name, status,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft', ?, ?)
        RETURNING *
        "#
    )
    .bind(request.visit_id)
    .bind(user_id)
    .bind(request.expense_category_id)
    .bind(request.amount)
    .bind(&request.currency)
    .bind(&request.description)
    .bind(request.expense_date)
    .bind(request.location.as_deref())
    .bind(request.vendor_name.as_deref())
    .bind(now)
    .bind(now)
    .fetch_one(pool)
    .await?;

    Ok(Json(expense))
}

/// 获取费用记录列表
pub async fn get_expenses(
    State((database, _config)): State<AppState>,
    Extension(auth_context): Extension<AuthContext>,
    Query(params): Query<ExpenseListQuery>,
) -> AppResult<Json<HashMap<String, serde_json::Value>>> {
    let pool = &database.pool;
    
    let page = params.page.unwrap_or(1);
    let limit = params.limit.unwrap_or(20).min(100);
    let offset = (page - 1) * limit;

    let expenses = if auth_context.user.role == "employee" {
        sqlx::query_as::<_, ExpenseRecord>(
            "SELECT * FROM expense_records WHERE employee_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?"
        )
        .bind(auth_context.user.id)
        .bind(limit as i64)
        .bind(offset as i64)
        .fetch_all(pool)
        .await?
    } else {
        sqlx::query_as::<_, ExpenseRecord>(
            "SELECT * FROM expense_records ORDER BY created_at DESC LIMIT ? OFFSET ?"
        )
        .bind(limit as i64)
        .bind(offset as i64)
        .fetch_all(pool)
        .await?
    };

    let total = if auth_context.user.role == "employee" {
        sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM expense_records WHERE employee_id = ?"
        )
        .bind(auth_context.user.id)
        .fetch_one(pool)
        .await?
    } else {
        sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM expense_records"
        )
        .fetch_one(pool)
        .await?
    };

    let mut result = HashMap::new();
    result.insert("data".to_string(), serde_json::to_value(expenses)?);
    result.insert("total".to_string(), serde_json::to_value(total)?);
    result.insert("page".to_string(), serde_json::to_value(page)?);
    result.insert("limit".to_string(), serde_json::to_value(limit)?);

    Ok(Json(result))
}

/// 获取单个费用记录详情
pub async fn get_expense(
    State((database, _config)): State<AppState>,
    Extension(auth_context): Extension<AuthContext>,
    Path(id): Path<i32>,
) -> AppResult<Json<ExpenseDetailResponse>> {
    let pool = &database.pool;
    
    let expense = sqlx::query_as::<_, ExpenseRecord>(
        "SELECT * FROM expense_records WHERE id = ?"
    )
    .bind(id)
    .fetch_optional(pool)
    .await?
    .ok_or_else(|| AppError::NotFound("费用记录不存在".to_string()))?;

    // 权限检查
    if auth_context.user.role == "employee" && expense.employee_id != auth_context.user.id {
        return Err(AppError::Forbidden("无权访问此费用记录".to_string()));
    }

    // 获取费用类别
    let category = sqlx::query_as::<_, ExpenseCategory>(
        "SELECT * FROM expense_categories WHERE id = ?"
    )
    .bind(expense.expense_category_id)
    .fetch_one(pool)
    .await?;

    // 获取员工信息
    let employee = sqlx::query_as::<_, User>(
        "SELECT * FROM users WHERE id = ?"
    )
    .bind(expense.employee_id)
    .fetch_one(pool)
    .await?;

    let response = ExpenseDetailResponse {
        expense,
        category,
        invoice_info: None, // 暂时简化
        employee_name: employee.full_name.unwrap_or(employee.username),
        approver_name: None,
        visit_info: None,
    };

    Ok(Json(response))
}

/// 更新费用记录
pub async fn update_expense(
    State((database, _config)): State<AppState>,
    Extension(auth_context): Extension<AuthContext>,
    Path(id): Path<i32>,
    Json(_request): Json<UpdateExpenseRequest>,
) -> AppResult<Json<ExpenseRecord>> {
    let pool = &database.pool;
    
    let expense = sqlx::query_as::<_, ExpenseRecord>(
        "SELECT * FROM expense_records WHERE id = ?"
    )
    .bind(id)
    .fetch_optional(pool)
    .await?
    .ok_or_else(|| AppError::NotFound("费用记录不存在".to_string()))?;

    // 权限检查
    if auth_context.user.role == "employee" && expense.employee_id != auth_context.user.id {
        return Err(AppError::Forbidden("无权修改此费用记录".to_string()));
    }

    // 只能修改草稿状态的费用
    if expense.status != ExpenseStatus::Draft {
        return Err(AppError::BadRequest("只能修改草稿状态的费用记录".to_string()));
    }

    // 简化更新逻辑
    let updated_expense = sqlx::query_as::<_, ExpenseRecord>(
        "UPDATE expense_records SET updated_at = ? WHERE id = ? RETURNING *"
    )
    .bind(chrono::Utc::now())
    .bind(id)
    .fetch_one(pool)
    .await?;

    Ok(Json(updated_expense))
}

/// 提交费用审批
pub async fn submit_expense(
    State((database, _config)): State<AppState>,
    Extension(auth_context): Extension<AuthContext>,
    Json(request): Json<SubmitExpenseRequest>,
) -> AppResult<Json<HashMap<String, serde_json::Value>>> {
    let pool = &database.pool;
    let mut transaction = pool.begin().await?;
    let mut submitted_count = 0;

    for expense_id in &request.expense_ids {
        let expense = sqlx::query_as::<_, ExpenseRecord>(
            "SELECT * FROM expense_records WHERE id = ? AND employee_id = ?"
        )
        .bind(expense_id)
        .bind(auth_context.user.id)
        .fetch_optional(&mut *transaction)
        .await?;

        if let Some(expense) = expense {
            if expense.status == ExpenseStatus::Draft {
                let now = chrono::Utc::now();
                sqlx::query(
                    "UPDATE expense_records SET status = 'submitted', submitted_at = ?, updated_at = ? WHERE id = ?"
                )
                .bind(now)
                .bind(now)
                .bind(expense_id)
                .execute(&mut *transaction)
                .await?;
                
                submitted_count += 1;
            }
        }
    }

    transaction.commit().await?;

    let mut result = HashMap::new();
    result.insert("submitted_count".to_string(), serde_json::to_value(submitted_count)?);
    result.insert("total_count".to_string(), serde_json::to_value(request.expense_ids.len())?);

    Ok(Json(result))
}

/// 审批费用
pub async fn approve_expense(
    State((database, _config)): State<AppState>,
    Extension(auth_context): Extension<AuthContext>,
    Json(request): Json<ApproveExpenseRequest>,
) -> AppResult<Json<HashMap<String, serde_json::Value>>> {
    // 检查权限 - 只有管理员可以审批
    if auth_context.user.role == "employee" {
        return Err(AppError::Forbidden("无权限审批费用".to_string()));
    }

    let pool = &database.pool;
    let mut transaction = pool.begin().await?;
    let mut processed_count = 0;

    for expense_id in &request.expense_ids {
        let expense = sqlx::query_as::<_, ExpenseRecord>(
            "SELECT * FROM expense_records WHERE id = ?"
        )
        .bind(expense_id)
        .fetch_optional(&mut *transaction)
        .await?;

        if let Some(expense) = expense {
            if expense.status == ExpenseStatus::Submitted {
                let now = chrono::Utc::now();
                let new_status = match request.action {
                    ApprovalAction::Approve => "approved",
                    ApprovalAction::Reject => "rejected",
                };

                sqlx::query(
                    r#"
                    UPDATE expense_records 
                    SET status = ?, approved_by = ?, approved_at = ?, updated_at = ? 
                    WHERE id = ?
                    "#
                )
                .bind(new_status)
                .bind(auth_context.user.id)
                .bind(now)
                .bind(now)
                .bind(expense_id)
                .execute(&mut *transaction)
                .await?;
                
                processed_count += 1;
            }
        }
    }

    transaction.commit().await?;

    let mut result = HashMap::new();
    result.insert("processed_count".to_string(), serde_json::to_value(processed_count)?);
    result.insert("total_count".to_string(), serde_json::to_value(request.expense_ids.len())?);

    Ok(Json(result))
}

/// 删除费用记录
pub async fn delete_expense(
    State((database, _config)): State<AppState>,
    Extension(auth_context): Extension<AuthContext>,
    Path(id): Path<i32>,
) -> AppResult<StatusCode> {
    let pool = &database.pool;
    
    let expense = sqlx::query_as::<_, ExpenseRecord>(
        "SELECT * FROM expense_records WHERE id = ?"
    )
    .bind(id)
    .fetch_optional(pool)
    .await?
    .ok_or_else(|| AppError::NotFound("费用记录不存在".to_string()))?;

    // 权限检查
    if auth_context.user.role == "employee" && expense.employee_id != auth_context.user.id {
        return Err(AppError::Forbidden("无权删除此费用记录".to_string()));
    }

    // 只能删除草稿状态的费用
    if expense.status != ExpenseStatus::Draft {
        return Err(AppError::BadRequest("只能删除草稿状态的费用记录".to_string()));
    }

    sqlx::query("DELETE FROM expense_records WHERE id = ?")
        .bind(id)
        .execute(pool)
        .await?;

    Ok(StatusCode::NO_CONTENT)
}

/// 获取费用统计信息
pub async fn get_expense_statistics(
    State((database, _config)): State<AppState>,
    Extension(auth_context): Extension<AuthContext>,
    Query(_params): Query<ExpenseListQuery>,
) -> AppResult<Json<ExpenseStatistics>> {
    let pool = &database.pool;
    
    // 简化统计查询
    let (total_amount, total_count) = if auth_context.user.role == "employee" {
        sqlx::query_as::<_, (f64, i64)>(
            "SELECT COALESCE(SUM(amount), 0), COUNT(*) FROM expense_records WHERE employee_id = ?"
        )
        .bind(auth_context.user.id)
        .fetch_one(pool)
        .await?
    } else {
        sqlx::query_as::<_, (f64, i64)>(
            "SELECT COALESCE(SUM(amount), 0), COUNT(*) FROM expense_records"
        )
        .fetch_one(pool)
        .await?
    };

    let statistics = ExpenseStatistics {
        total_amount,
        pending_amount: 0.0,
        approved_amount: 0.0,
        rejected_amount: 0.0,
        total_count: total_count as i32,
        pending_count: 0,
        approved_count: 0,
        rejected_count: 0,
        by_category: vec![], // 简化实现
        by_month: vec![],    // 简化实现
    };

    Ok(Json(statistics))
}

/// 获取费用类别列表
pub async fn get_expense_categories(
    State((database, _config)): State<AppState>,
) -> AppResult<Json<Vec<ExpenseCategory>>> {
    let pool = &database.pool;
    
    let categories = sqlx::query_as::<_, ExpenseCategory>(
        "SELECT * FROM expense_categories WHERE is_active = true ORDER BY name"
    )
    .fetch_all(pool)
    .await?;

    Ok(Json(categories))
}

/// 创建费用类别
pub async fn create_expense_category(
    State((database, _config)): State<AppState>,
    Extension(auth_context): Extension<AuthContext>,
    Json(request): Json<CreateExpenseCategoryRequest>,
) -> AppResult<Json<ExpenseCategory>> {
    // 只有管理员可以创建费用类别
    if auth_context.user.role == "employee" {
        return Err(AppError::Forbidden("无权限创建费用类别".to_string()));
    }

    let pool = &database.pool;
    let now = chrono::Utc::now();
    
    let category = sqlx::query_as::<_, ExpenseCategory>(
        r#"
        INSERT INTO expense_categories (
            name, code, description, max_amount, requires_receipt, is_active, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, true, ?, ?)
        RETURNING *
        "#
    )
    .bind(&request.name)
    .bind(&request.code)
    .bind(request.description.as_deref())
    .bind(request.max_amount)
    .bind(request.requires_receipt)
    .bind(now)
    .bind(now)
    .fetch_one(pool)
    .await?;

    Ok(Json(category))
}