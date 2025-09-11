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
        ApiResponse, CompanyPricingPlan, CompanyOperationPricing,
        CreateCompanyPricingPlanRequest, UpdateCompanyPricingPlanRequest,
        CreateCompanyOperationPricingRequest, UpdateCompanyOperationPricingRequest,
    },
    services::company_pricing::CompanyPricingService,
    Config, Database,
};

type AppState = (Database, Config);

#[derive(Deserialize)]
pub struct CompanyPricingQuery {
    pub company_name: Option<String>,
}

#[derive(Deserialize)]
pub struct OperationPriceQuery {
    pub company_name: String,
    pub platform: String,
    pub operation_type: String,
}

// 获取所有公司收费计划
pub async fn list_company_pricing_plans(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
) -> Result<ResponseJson<ApiResponse<Vec<CompanyPricingPlan>>>, StatusCode> {
    let service = CompanyPricingService::new(database);
    
    match service.list_company_pricing_plans(&auth_context.user).await {
        Ok(plans) => Ok(ResponseJson(ApiResponse::success(plans))),
        Err(e) => {
            tracing::error!("获取公司收费计划失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(e.to_string())))
        }
    }
}

// 根据公司名获取收费计划
pub async fn get_company_pricing_plan(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
    Path(company_name): Path<String>,
) -> Result<ResponseJson<ApiResponse<Option<CompanyPricingPlan>>>, StatusCode> {
    let service = CompanyPricingService::new(database);
    
    match service.get_company_pricing_plan(&auth_context.user, &company_name).await {
        Ok(plan) => Ok(ResponseJson(ApiResponse::success(plan))),
        Err(e) => {
            tracing::error!("获取公司收费计划失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(e.to_string())))
        }
    }
}

// 创建公司收费计划
pub async fn create_company_pricing_plan(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
    Json(request): Json<CreateCompanyPricingPlanRequest>,
) -> Result<ResponseJson<ApiResponse<CompanyPricingPlan>>, StatusCode> {
    let service = CompanyPricingService::new(database);
    
    match service.create_company_pricing_plan(&auth_context.user, request).await {
        Ok(plan) => Ok(ResponseJson(ApiResponse::success(plan))),
        Err(e) => {
            tracing::error!("创建公司收费计划失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(e.to_string())))
        }
    }
}

// 更新公司收费计划
pub async fn update_company_pricing_plan(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
    Path(plan_id): Path<i32>,
    Json(request): Json<UpdateCompanyPricingPlanRequest>,
) -> Result<ResponseJson<ApiResponse<CompanyPricingPlan>>, StatusCode> {
    let service = CompanyPricingService::new(database);
    
    match service.update_company_pricing_plan(&auth_context.user, plan_id, request).await {
        Ok(plan) => Ok(ResponseJson(ApiResponse::success(plan))),
        Err(e) => {
            tracing::error!("更新公司收费计划失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(e.to_string())))
        }
    }
}

// 删除公司收费计划
pub async fn delete_company_pricing_plan(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
    Path(plan_id): Path<i32>,
) -> Result<ResponseJson<ApiResponse<String>>, StatusCode> {
    let service = CompanyPricingService::new(database);
    
    match service.delete_company_pricing_plan(&auth_context.user, plan_id).await {
        Ok(_) => Ok(ResponseJson(ApiResponse::success("删除成功".to_string()))),
        Err(e) => {
            tracing::error!("删除公司收费计划失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(e.to_string())))
        }
    }
}

// 获取公司操作收费规则
pub async fn list_company_operation_pricing(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
    Query(query): Query<CompanyPricingQuery>,
) -> Result<ResponseJson<ApiResponse<Vec<CompanyOperationPricing>>>, StatusCode> {
    let service = CompanyPricingService::new(database);
    
    match service.list_company_operation_pricing(&auth_context.user, query.company_name.as_deref()).await {
        Ok(pricing) => Ok(ResponseJson(ApiResponse::success(pricing))),
        Err(e) => {
            tracing::error!("获取公司操作收费规则失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(e.to_string())))
        }
    }
}

// 创建公司操作收费规则
pub async fn create_company_operation_pricing(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
    Json(request): Json<CreateCompanyOperationPricingRequest>,
) -> Result<ResponseJson<ApiResponse<CompanyOperationPricing>>, StatusCode> {
    let service = CompanyPricingService::new(database);
    
    match service.create_company_operation_pricing(&auth_context.user, request).await {
        Ok(pricing) => Ok(ResponseJson(ApiResponse::success(pricing))),
        Err(e) => {
            tracing::error!("创建公司操作收费规则失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(e.to_string())))
        }
    }
}

// 更新公司操作收费规则
pub async fn update_company_operation_pricing(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
    Path(pricing_id): Path<i32>,
    Json(request): Json<UpdateCompanyOperationPricingRequest>,
) -> Result<ResponseJson<ApiResponse<CompanyOperationPricing>>, StatusCode> {
    let service = CompanyPricingService::new(database);
    
    match service.update_company_operation_pricing(&auth_context.user, pricing_id, request).await {
        Ok(pricing) => Ok(ResponseJson(ApiResponse::success(pricing))),
        Err(e) => {
            tracing::error!("更新公司操作收费规则失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(e.to_string())))
        }
    }
}

// 删除公司操作收费规则
pub async fn delete_company_operation_pricing(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
    Path(pricing_id): Path<i32>,
) -> Result<ResponseJson<ApiResponse<String>>, StatusCode> {
    let service = CompanyPricingService::new(database);
    
    match service.delete_company_operation_pricing(&auth_context.user, pricing_id).await {
        Ok(_) => Ok(ResponseJson(ApiResponse::success("删除成功".to_string()))),
        Err(e) => {
            tracing::error!("删除公司操作收费规则失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(e.to_string())))
        }
    }
}

// 获取操作价格
pub async fn get_operation_price(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
    Query(query): Query<OperationPriceQuery>,
) -> Result<ResponseJson<ApiResponse<f64>>, StatusCode> {
    let service = CompanyPricingService::new(database);
    
    match service.get_operation_price(&query.company_name, &query.platform, &query.operation_type).await {
        Ok(price) => Ok(ResponseJson(ApiResponse::success(price))),
        Err(e) => {
            tracing::error!("获取操作价格失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(e.to_string())))
        }
    }
}

// 获取员工月费
pub async fn get_employee_monthly_fee(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
    Path(company_name): Path<String>,
) -> Result<ResponseJson<ApiResponse<f64>>, StatusCode> {
    let service = CompanyPricingService::new(database);
    
    match service.get_employee_monthly_fee(&company_name).await {
        Ok(fee) => Ok(ResponseJson(ApiResponse::success(fee))),
        Err(e) => {
            tracing::error!("获取员工月费失败: {}", e);
            Ok(ResponseJson(ApiResponse::error(e.to_string())))
        }
    }
}
