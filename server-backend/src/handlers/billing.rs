use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json as ResponseJson,
    Json,
};
use serde::Deserialize;

use crate::{
    middleware::auth::AuthContext,
    models::{
        ApiResponse, BillingRecord, CreateBillingRecordRequest, CreatePricingRuleRequest,
        MyBillingInfo, PricingRule,
    },
    services::billing::BillingService,
    Config, Database,
};

type AppState = (Database, Config);

#[derive(Deserialize)]
pub struct BillingQuery {
    pub page: Option<i32>,
    pub limit: Option<i32>,
    pub size: Option<i32>, // 兼容前端的size参数
    pub user_id: Option<String>,
}

pub async fn list_billing_records(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Query(query): Query<BillingQuery>,
) -> Result<ResponseJson<ApiResponse<Vec<BillingRecord>>>, StatusCode> {
    let service = BillingService::new(database);

    // 兼容前端的size参数，优先使用limit，其次使用size
    let limit = query.limit.or(query.size).unwrap_or(20);

    match service
        .list_billing_records(
            &auth_context.user,
            query.page.unwrap_or(1),
            limit,
            query.user_id.as_deref(),
        )
        .await
    {
        Ok(records) => Ok(ResponseJson(ApiResponse::success(records))),
        Err(e) => {
            tracing::error!("获取计费记录失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(
                "获取计费记录失败".to_string(),
            )))
        }
    }
}

pub async fn create_billing_record(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Json(request): Json<CreateBillingRecordRequest>,
) -> Result<ResponseJson<ApiResponse<BillingRecord>>, StatusCode> {
    let service = BillingService::new(database);

    match service
        .create_billing_record(&auth_context.user, request)
        .await
    {
        Ok(record) => Ok(ResponseJson(ApiResponse::success(record))),
        Err(e) => {
            tracing::error!("创建计费记录失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(format!(
                "创建计费记录失败: {}",
                e
            ))))
        }
    }
}

// 获取价格规则列表
pub async fn list_pricing_rules(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
) -> Result<ResponseJson<ApiResponse<Vec<PricingRule>>>, StatusCode> {
    let service = BillingService::new(database);

    match service.list_pricing_rules(&auth_context.user).await {
        Ok(rules) => Ok(ResponseJson(ApiResponse::success(rules))),
        Err(e) => {
            tracing::error!("获取价格规则失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(
                "获取价格规则失败".to_string(),
            )))
        }
    }
}

// 创建价格规则
pub async fn create_pricing_rule(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Json(request): Json<CreatePricingRuleRequest>,
) -> Result<ResponseJson<ApiResponse<PricingRule>>, StatusCode> {
    let service = BillingService::new(database);

    match service
        .create_pricing_rule(&auth_context.user, request)
        .await
    {
        Ok(rule) => Ok(ResponseJson(ApiResponse::success(rule))),
        Err(e) => {
            tracing::error!("创建价格规则失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(format!(
                "创建价格规则失败: {}",
                e
            ))))
        }
    }
}

// 更新价格规则
pub async fn update_pricing_rule(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
    Path(rule_id): Path<i32>,
    Json(request): Json<CreatePricingRuleRequest>,
) -> Result<ResponseJson<ApiResponse<PricingRule>>, StatusCode> {
    // 基本验证
    if request.rule_name.is_empty() || request.billing_type.is_empty() || request.unit_price < 0.0 {
        return Ok(ResponseJson(ApiResponse::error(
            "输入数据无效：规则名称和计费类型不能为空，单价不能为负数".to_string(),
        )));
    }

    let service = BillingService::new(database);

    match service
        .update_pricing_rule(&auth_context.user, rule_id, request)
        .await
    {
        Ok(rule) => Ok(ResponseJson(ApiResponse::success(rule))),
        Err(e) => {
            tracing::error!("更新价格规则失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(format!(
                "更新价格规则失败: {}",
                e
            ))))
        }
    }
}

// 删除价格规则
pub async fn delete_pricing_rule(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Path(rule_id): Path<i32>,
) -> Result<ResponseJson<ApiResponse<()>>, StatusCode> {
    let service = BillingService::new(database);

    match service
        .delete_pricing_rule(&auth_context.user, rule_id)
        .await
    {
        Ok(_) => Ok(ResponseJson(ApiResponse::success(()))),
        Err(e) => {
            tracing::error!("删除价格规则失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(format!(
                "删除价格规则失败: {}",
                e
            ))))
        }
    }
}

// 获取我的计费信息（用户管理员）
pub async fn get_my_billing_info(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
) -> Result<ResponseJson<ApiResponse<MyBillingInfo>>, StatusCode> {
    let service = BillingService::new(database);

    match service.get_my_billing_info(&auth_context.user).await {
        Ok(billing_info) => Ok(ResponseJson(ApiResponse::success(billing_info))),
        Err(e) => {
            tracing::error!("获取计费信息失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(format!(
                "获取计费信息失败: {}",
                e
            ))))
        }
    }
}

// 获取指定用户的计费信息（系统管理员专用）
pub async fn get_user_billing_info(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
    Path(user_id): Path<i64>,
) -> Result<ResponseJson<ApiResponse<MyBillingInfo>>, StatusCode> {
    let service = BillingService::new(database);

    match service.get_user_billing_info(&auth_context.user, user_id).await {
        Ok(billing_info) => Ok(ResponseJson(ApiResponse::success(billing_info))),
        Err(e) => {
            tracing::error!("获取用户计费信息失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(format!(
                "获取用户计费信息失败: {}",
                e
            ))))
        }
    }
}
