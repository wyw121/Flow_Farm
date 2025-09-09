use anyhow::Result;
use flow_farm_backend::{config::Config, server::create_app, database::Database};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[tokio::main]
async fn main() -> Result<()> {
    // 初始化日志
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "flow_farm_backend=debug,tower_http=debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    // 加载配置
    dotenvy::dotenv().ok();
    let config = Config::new()?;

    tracing::info!("🚀 启动 Flow Farm 服务器后端");
    tracing::info!("📊 配置: {}", config.app_name);
    tracing::info!("🌐 监听地址: {}:{}", config.host, config.port);
    tracing::info!("📁 静态文件: {}", config.static_dir);

    if config.debug {
        tracing::info!("⚠️  开发模式已启用");
    } else {
        tracing::info!("🔒 生产模式已启用");
    }

    // 初始化数据库
    let database = Database::new(&config.database_url).await?;
    database.migrate().await?;
    tracing::info!("✅ 数据库连接成功");

    // 创建应用
    let app = create_app(database, config.clone()).await;

    // 启动服务器
    let listener = tokio::net::TcpListener::bind(format!("{}:{}", config.host, config.port)).await?;

    tracing::info!("🎯 服务器启动成功！");

    let protocol = if config.enable_tls { "https" } else { "http" };
    let host_display = if config.host == "0.0.0.0" { "localhost" } else { &config.host };

    tracing::info!("🌐 前端界面: {}://{}:{}/", protocol, host_display, config.port);
    tracing::info!("📖 API文档: {}://{}:{}/docs", protocol, host_display, config.port);
    tracing::info!("❤️  健康检查: {}://{}:{}/health", protocol, host_display, config.port);

    // TODO: 支持TLS的实现
    if config.enable_tls {
        tracing::warn!("⚠️  TLS支持尚未实现，将使用HTTP启动");
    }

    axum::serve(listener, app).await?;

    Ok(())
}
