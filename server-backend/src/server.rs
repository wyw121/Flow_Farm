use axum::{
    http::Method,
    middleware,
    routing::{delete, get, post, put},
    Router,
};
use std::path::PathBuf;
use tower_http::{
    compression::CompressionLayer, cors::CorsLayer, services::ServeDir,
    trace::TraceLayer,
};

use crate::{handlers, Config, Database};

pub async fn create_app(database: Database, config: Config) -> Router {
    // 创建CORS中间件
    let cors = CorsLayer::new()
        .allow_origin(tower_http::cors::Any)
        .allow_methods([
            Method::GET,
            Method::POST,
            Method::PUT,
            Method::DELETE,
            Method::PATCH,
            Method::OPTIONS,
        ])
        .allow_headers([
            axum::http::HeaderName::from_static("authorization"),
            axum::http::HeaderName::from_static("content-type"),
            axum::http::HeaderName::from_static("x-requested-with"),
        ])
        .allow_credentials(false);

    // 静态文件服务配置
    let static_files_service = {
        let static_dir = PathBuf::from(&config.static_dir);
        if static_dir.exists() {
            tracing::info!(
                "📁 静态文件目录: {:?}",
                static_dir.canonicalize().unwrap_or(static_dir.clone())
            );
            ServeDir::new(&config.static_dir)
                .precompressed_gzip()
                .precompressed_br()
                .append_index_html_on_directories(true)
        } else {
            tracing::warn!("⚠️  静态文件目录不存在: {:?}", static_dir);
            tracing::info!("💡 请确保运行 'npm run build' 构建前端");
            ServeDir::new(".")
        }
    };

    // 公开路由（不需要认证）
    let public_routes = Router::new()
        .route("/health", get(handlers::health::health_check))
        .route("/api/v1/auth/login", post(handlers::auth::login))
        .route("/api/v1/auth/register", post(handlers::auth::register))
        .route("/api/v1/auth/logout", post(handlers::auth::logout))
        .route("/docs", get(handlers::docs::api_docs))
        // 公开问卷回答提交（无需认证）
        .route("/api/v1/surveys/:id/responses", post(handlers::survey::submit_survey_response))
        .with_state((database.clone(), config.clone()));

    // 受保护路由（需要认证）
    let protected_routes = Router::new()
        .route("/api/v1/auth/me", get(handlers::auth::get_current_user))
        .route("/api/v1/auth/refresh", post(handlers::auth::refresh_token))
        // 用户管理
        .route("/api/v1/users", get(handlers::users::list_users))
        .route("/api/v1/users", post(handlers::users::create_user))
        .route("/api/v1/users/:id", get(handlers::users::get_user))
        .route("/api/v1/users/:id", put(handlers::users::update_user))
        .route("/api/v1/users/:id", delete(handlers::users::delete_user))
        .route(
            "/api/v1/users/companies/statistics",
            get(handlers::users::get_company_statistics),
        )
        .route(
            "/api/v1/users/companies/names",
            get(handlers::users::get_company_names),
        )
        // 工作记录
        .route(
            "/api/v1/work-records",
            get(handlers::work_records::list_work_records),
        )
        .route(
            "/api/v1/work-records",
            post(handlers::work_records::create_work_record),
        )
        .route(
            "/api/v1/work-records/:id",
            get(handlers::work_records::get_work_record),
        )
        // KPI统计
        .route("/api/v1/kpi/stats", get(handlers::kpi::get_kpi_stats))
        .route("/api/v1/kpi/user-stats", get(handlers::kpi::get_user_stats))
        // 计费
        .route(
            "/api/v1/billing/records",
            get(handlers::billing::list_billing_records),
        )
        .route(
            "/api/v1/billing/records",
            post(handlers::billing::create_billing_record),
        )
        .route(
            "/api/v1/billing/my-billing-info",
            get(handlers::billing::get_my_billing_info),
        )
        .route(
            "/api/v1/billing/user-billing-info/:id",
            get(handlers::billing::get_user_billing_info),
        )
        // 前端兼容性路由 (Python API fallback)
        .route(
            "/api/v1/billing/billing-records/",
            get(handlers::billing::list_billing_records),
        )
        .route(
            "/api/v1/billing/billing-records/",
            post(handlers::billing::create_billing_record),
        )
        .route(
            "/api/v1/billing/pricing-rules",
            get(handlers::billing::list_pricing_rules),
        )
        .route(
            "/api/v1/billing/pricing-rules",
            post(handlers::billing::create_pricing_rule),
        )
        // 前端兼容性路由 (Python API fallback)
        .route(
            "/api/v1/billing/pricing-rules/",
            get(handlers::billing::list_pricing_rules),
        )
        .route(
            "/api/v1/billing/pricing-rules/",
            post(handlers::billing::create_pricing_rule),
        )
        .route(
            "/api/v1/billing/pricing-rules/:id",
            put(handlers::billing::update_pricing_rule),
        )
        .route(
            "/api/v1/billing/pricing-rules/:id",
            delete(handlers::billing::delete_pricing_rule),
        )
        // 公司收费计划管理
        .route(
            "/api/v1/company-pricing/plans",
            get(handlers::company_pricing::list_company_pricing_plans),
        )
        .route(
            "/api/v1/company-pricing/plans",
            post(handlers::company_pricing::create_company_pricing_plan),
        )
        .route(
            "/api/v1/company-pricing/plans/by-company/:company_name",
            get(handlers::company_pricing::get_company_pricing_plan),
        )
        .route(
            "/api/v1/company-pricing/plans/by-id/:plan_id",
            put(handlers::company_pricing::update_company_pricing_plan),
        )
        .route(
            "/api/v1/company-pricing/plans/by-id/:plan_id",
            delete(handlers::company_pricing::delete_company_pricing_plan),
        )
        // 公司操作收费规则
        .route(
            "/api/v1/company-pricing/operations",
            get(handlers::company_pricing::list_company_operation_pricing),
        )
        .route(
            "/api/v1/company-pricing/operations",
            post(handlers::company_pricing::create_company_operation_pricing),
        )
        .route(
            "/api/v1/company-pricing/operations/:pricing_id",
            put(handlers::company_pricing::update_company_operation_pricing),
        )
        .route(
            "/api/v1/company-pricing/operations/:pricing_id",
            delete(handlers::company_pricing::delete_company_operation_pricing),
        )
        // 查询价格
        .route(
            "/api/v1/company-pricing/operation-price",
            get(handlers::company_pricing::get_operation_price),
        )
        .route(
            "/api/v1/company-pricing/employee-fee/:company_name",
            get(handlers::company_pricing::get_employee_monthly_fee),
        )
        // 报告
        .route(
            "/api/v1/reports/dashboard",
            get(handlers::reports::get_dashboard_data),
        )
        .route(
            "/api/v1/reports/export",
            get(handlers::reports::export_data),
        )
        // 问卷管理
        .route("/api/v1/surveys", get(handlers::survey::get_surveys))
        .route("/api/v1/surveys", post(handlers::survey::create_survey))
        .route("/api/v1/surveys/:id", get(handlers::survey::get_survey))
        .route("/api/v1/surveys/:id", put(handlers::survey::update_survey))
        .route("/api/v1/surveys/:id", delete(handlers::survey::delete_survey))
        .route("/api/v1/surveys/:id/publish", post(handlers::survey::publish_survey))
        .route("/api/v1/surveys/:id/close", post(handlers::survey::close_survey))
        // 问卷分析
        .route("/api/v1/surveys/:id/analytics", get(handlers::analytics::get_survey_analytics))
        .route("/api/v1/surveys/:id/export", get(handlers::analytics::export_survey_report))
        // 客户管理
        .route("/api/v1/customers", get(handlers::customer::get_customers))
        .route("/api/v1/customers", post(handlers::customer::create_customer))
        .route("/api/v1/customers/:id", get(handlers::customer::get_customer))
        .route("/api/v1/customers/:id", put(handlers::customer::update_customer))
        .route("/api/v1/customers/:id", delete(handlers::customer::delete_customer))
        .route("/api/v1/customers/stats", get(handlers::customer::get_customer_statistics))
        // 拜访管理
        .route("/api/v1/visits", get(handlers::visit::get_visits))
        .route("/api/v1/visits", post(handlers::visit::create_visit))
        .route("/api/v1/visits/:id", get(handlers::visit::get_visit))
        .route("/api/v1/visits/:id/start", post(handlers::visit::start_visit))
        .route("/api/v1/visits/:id/end", post(handlers::visit::end_visit))
        .route("/api/v1/visits/:id/cancel", post(handlers::visit::cancel_visit))
        .route("/api/v1/visits/stats", get(handlers::visit::get_visit_statistics))
        // 拜访附件管理
        .route("/api/v1/visits/:id/attachments", get(handlers::attachment::get_visit_attachments))
        .route("/api/v1/visits/:id/attachments", post(handlers::attachment::upload_visit_attachment))
        .route("/api/v1/visits/:visit_id/attachments/:attachment_id", delete(handlers::attachment::delete_visit_attachment))
        .route("/api/v1/visits/:visit_id/attachments/:attachment_id/download", get(handlers::attachment::download_visit_attachment))
        // 费用管理
        .route("/api/v1/expenses", get(handlers::expense::get_expenses))
        .route("/api/v1/expenses", post(handlers::expense::create_expense))
        .route("/api/v1/expenses/:id", get(handlers::expense::get_expense))
        .route("/api/v1/expenses/:id", put(handlers::expense::update_expense))
        .route("/api/v1/expenses/:id", delete(handlers::expense::delete_expense))
        .route("/api/v1/expenses/submit", post(handlers::expense::submit_expense))
        .route("/api/v1/expenses/approve", post(handlers::expense::approve_expense))
        .route("/api/v1/expenses/statistics", get(handlers::expense::get_expense_statistics))
        // 费用类别管理
        .route("/api/v1/expense-categories", get(handlers::expense::get_expense_categories))
        .route("/api/v1/expense-categories", post(handlers::expense::create_expense_category))
        .layer(middleware::from_fn_with_state(
            (database.clone(), config.clone()),
            crate::middleware::auth::AuthLayer::middleware,
        ))
        .with_state((database, config));

    // 合并路由
    Router::new()
        .merge(public_routes)
        .merge(protected_routes)
        // 静态文件服务 (优先级最低，放在最后)
        .fallback_service(static_files_service)
        // 全局中间件
        .layer(CompressionLayer::new())
        .layer(TraceLayer::new_for_http())
        .layer(cors)
}
