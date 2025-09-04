use sqlx::sqlite::{SqlitePool, SqliteConnectOptions};
use sqlx::ConnectOptions;
use std::str::FromStr;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 连接到SQLite数据库
    let database_url = "sqlite:data/flow_farm.db";

    let mut connect_options = SqliteConnectOptions::from_str(database_url)?;
    connect_options.log_statements(log::LevelFilter::Debug);

    let pool = SqlitePool::connect_with(connect_options).await?;

    // 首先查看所有表
    println!("数据库中的表:");
    let tables: Vec<(String,)> = sqlx::query_as(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    .fetch_all(&pool)
    .await?;

    for (table_name,) in &tables {
        println!("- {}", table_name);
    }

    // 如果存在users表，查询用户数量
    if tables.iter().any(|(name,)| name == "users") {
        let count: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM users")
            .fetch_one(&pool)
            .await?;

        println!("\n用户表中的账号数量: {}", count.0);

        // 显示用户的基本信息（不包含密码）
        let users: Vec<(String, String, String)> = sqlx::query_as(
            "SELECT username, email, role FROM users LIMIT 10"
        )
        .fetch_all(&pool)
        .await?;

        println!("\n前10个用户信息:");
        for (username, email, role) in users {
            println!("- 用户名: {}, 邮箱: {}, 角色: {}", username, email, role);
        }
    } else {
        println!("\n未找到users表");
    }

    Ok(())
}
