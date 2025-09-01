use axum::{
    body::Body,
    extract::{Query, State},
    http::{header, StatusCode},
    response::{Json as ResponseJson, Response},
};
use serde::{Deserialize, Serialize};

use crate::{
    middleware::auth::AuthContext,
    models::{ApiResponse, CompanyStatistics},
    services::{kpi::KpiService, report::ReportService, user::UserService},
    Config, Database,
};

type AppState = (Database, Config);

#[derive(Deserialize)]
pub struct ExportQuery {
    pub format: Option<String>, // csv, json
    pub start_date: Option<String>,
    pub end_date: Option<String>,
    pub user_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DashboardWorkStats {
    pub total_follows: i64,
    pub today_follows: i64,
    pub total_actions: i64,
    pub successful_actions: i64,
    pub success_rate: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DashboardCompanyStats {
    pub total_billing: f64,
    pub unpaid_amount: f64,
    pub total_employees: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DashboardData {
    pub work_stats: DashboardWorkStats,
    pub company_stats: DashboardCompanyStats,
}

/// 获取用户管理员仪表板数据
pub async fn get_dashboard_data(
    State((database, _config)): State<AppState>,
    auth_context: AuthContext,
) -> Result<ResponseJson<DashboardData>, StatusCode> {
    let user_service = UserService::new(database.clone());
    let kpi_service = KpiService::new(database);

    // 根据用户角色返回不同的数据
    match auth_context.user.role.as_str() {
        "user_admin" => {
            // 用户管理员 - 返回自己公司的统计信息
            match get_user_admin_dashboard(&user_service, &kpi_service, &auth_context.user).await {
                Ok(data) => Ok(ResponseJson(data)),
                Err(e) => {
                    tracing::error!("获取用户管理员仪表板数据失败: {}", e);
                    Err(StatusCode::INTERNAL_SERVER_ERROR)
                }
            }
        }
        "system_admin" => {
            // 系统管理员 - 返回系统整体统计信息
            match get_system_admin_dashboard(&user_service, &kpi_service, &auth_context.user).await
            {
                Ok(data) => Ok(ResponseJson(data)),
                Err(e) => {
                    tracing::error!("获取系统管理员仪表板数据失败: {}", e);
                    Err(StatusCode::INTERNAL_SERVER_ERROR)
                }
            }
        }
        _ => {
            tracing::warn!("无权限访问仪表板数据: role={}", auth_context.user.role);
            Err(StatusCode::FORBIDDEN)
        }
    }
}

async fn get_user_admin_dashboard(
    user_service: &UserService,
    kpi_service: &KpiService,
    current_user: &crate::models::UserInfo,
) -> anyhow::Result<DashboardData> {
    // 获取KPI统计数据
    let kpi_stats = kpi_service
        .get_kpi_stats(current_user, None, None, None)
        .await
        .unwrap_or_default();

    // 获取员工数量
    let employees = user_service
        .list_users(current_user, 1, 100, Some("employee"))
        .await?;
    let total_employees = employees.len() as i32;

    // 模拟一些数据，实际应该从数据库查询
    let work_stats = DashboardWorkStats {
        total_follows: kpi_stats.total_actions,
        today_follows: kpi_stats.successful_actions / 7, // 近似今日数据
        total_actions: kpi_stats.total_actions,
        successful_actions: kpi_stats.successful_actions,
        success_rate: kpi_stats.success_rate,
    };

    let company_stats = DashboardCompanyStats {
        total_billing: 0.0, // 需要从billing服务获取
        unpaid_amount: 0.0, // 需要从billing服务获取
        total_employees,
    };

    Ok(DashboardData {
        work_stats,
        company_stats,
    })
}

async fn get_system_admin_dashboard(
    user_service: &UserService,
    kpi_service: &KpiService,
    current_user: &crate::models::UserInfo,
) -> anyhow::Result<DashboardData> {
    // 获取系统整体KPI统计数据
    let kpi_stats = kpi_service
        .get_kpi_stats(current_user, None, None, None)
        .await
        .unwrap_or_default();

    // 获取公司统计信息
    let company_statistics = user_service.get_company_statistics(current_user).await?;

    let total_employees: i32 = company_statistics.iter().map(|cs| cs.total_employees).sum();
    let total_billing: f64 = company_statistics
        .iter()
        .map(|cs| cs.total_billing_amount)
        .sum();
    let unpaid_amount: f64 = company_statistics.iter().map(|cs| cs.unpaid_amount).sum();
    let total_follows: i64 = company_statistics.iter().map(|cs| cs.total_follows).sum();
    let today_follows: i64 = company_statistics.iter().map(|cs| cs.today_follows).sum();

    let work_stats = DashboardWorkStats {
        total_follows,
        today_follows,
        total_actions: kpi_stats.total_actions,
        successful_actions: kpi_stats.successful_actions,
        success_rate: kpi_stats.success_rate,
    };

    let company_stats = DashboardCompanyStats {
        total_billing,
        unpaid_amount,
        total_employees,
    };

    Ok(DashboardData {
        work_stats,
        company_stats,
    })
}

pub async fn export_data(
    State((database, config)): State<AppState>,
    auth_context: AuthContext,
    Query(query): Query<ExportQuery>,
) -> Result<Response<Body>, StatusCode> {
    let service = ReportService::new(database);

    let format = query.format.as_deref().unwrap_or("json");

    match service
        .export_data(
            &auth_context.user,
            format,
            query.start_date.as_deref(),
            query.end_date.as_deref(),
            query.user_id.as_deref(),
        )
        .await
    {
        Ok((content, content_type, filename)) => {
            let response = Response::builder()
                .status(StatusCode::OK)
                .header(header::CONTENT_TYPE, content_type)
                .header(
                    header::CONTENT_DISPOSITION,
                    format!("attachment; filename=\"{}\"", filename),
                )
                .body(Body::from(content))
                .unwrap();

            Ok(response)
        }
        Err(e) => {
            tracing::error!("导出数据失败: {}", e);
            let error_json = serde_json::json!({
                "success": false,
                "message": "导出数据失败",
                "data": serde_json::Value::Null
            });
            let response = Response::builder()
                .status(StatusCode::INTERNAL_SERVER_ERROR)
                .header(header::CONTENT_TYPE, "application/json")
                .body(Body::from(serde_json::to_string(&error_json).unwrap()))
                .unwrap();

            Ok(response)
        }
    }
}
