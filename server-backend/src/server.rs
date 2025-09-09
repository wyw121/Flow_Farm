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
        // 设备管理
        .route("/api/v1/devices", get(handlers::devices::list_devices))
        .route("/api/v1/devices", post(handlers::devices::create_device))
        .route("/api/v1/devices/:id", get(handlers::devices::get_device))
        .route("/api/v1/devices/:id", put(handlers::devices::update_device))
        .route(
            "/api/v1/devices/:id",
            delete(handlers::devices::delete_device),
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
        // 报告
        .route(
            "/api/v1/reports/dashboard",
            get(handlers::reports::get_dashboard_data),
        )
        .route(
            "/api/v1/reports/export",
            get(handlers::reports::export_data),
        )
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
