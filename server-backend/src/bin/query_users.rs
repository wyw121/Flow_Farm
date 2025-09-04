use sqlx::sqlite::SqlitePool;
use sqlx::{Row, Column};
use std::env;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 加载环境变量
    dotenvy::dotenv().ok();

    // 连接到数据库
    let database_url = env::var("DATABASE_URL")
        .unwrap_or_else(|_| "sqlite:data/flow_farm.db".to_string());

    println!("连接到数据库: {}", database_url);

    let pool = SqlitePool::connect(&database_url).await?;

    // 查看所有表
    println!("\n数据库中的表:");
    let tables: Vec<(String,)> = sqlx::query_as(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    .fetch_all(&pool)
    .await?;

    if tables.is_empty() {
        println!("未找到任何用户表");
        return Ok(());
    }

    for (table_name,) in &tables {
        println!("- {}", table_name);
    }

    // 查找用户相关的表并统计数量
    for (table_name,) in &tables {
        if table_name.to_lowercase().contains("user") {
            let count_query = format!("SELECT COUNT(*) FROM {}", table_name);
            let count: (i64,) = sqlx::query_as(&count_query)
                .fetch_one(&pool)
                .await?;

            println!("\n表 '{}' 中的记录数量: {}", table_name, count.0);

            // 尝试获取表结构
            let schema_query = format!("PRAGMA table_info({})", table_name);
            let columns: Vec<(i32, String, String, i32, Option<String>, i32)> =
                sqlx::query_as(&schema_query)
                .fetch_all(&pool)
                .await?;

            println!("表结构:");
            for (_, name, col_type, not_null, default_value, pk) in columns {
                println!("  - {} ({}) {}{}",
                    name,
                    col_type,
                    if pk != 0 { "[主键] " } else { "" },
                    if not_null != 0 { "[非空] " } else { "" }
                );
            }

            // 显示所有用户数据
            if table_name == "users" {
                println!("\n所有用户账号详情:");
                let users_query = "SELECT id, username, email, role, is_active, is_verified, parent_id, full_name, phone, company, max_employees, current_employees, created_at, updated_at, last_login FROM users ORDER BY id";
                let rows = sqlx::query(&users_query)
                    .fetch_all(&pool)
                    .await?;

                for (i, row) in rows.iter().enumerate() {
                    println!("\n=== 用户 {} ===", i + 1);
                    for (j, column) in row.columns().iter().enumerate() {
                        let column_name = column.name();
                        let value: Option<String> = row.try_get(j).unwrap_or(None);
                        let display_value = value.unwrap_or("NULL".to_string());

                        match column_name {
                            "id" => println!("🆔 用户ID: {}", display_value),
                            "username" => println!("👤 用户名: {}", display_value),
                            "email" => println!("📧 邮箱: {}", display_value),
                            "role" => println!("👨‍💼 角色: {}", display_value),
                            "is_active" => println!("🟢 账号状态: {}", if display_value == "1" { "激活" } else { "停用" }),
                            "is_verified" => println!("✅ 验证状态: {}", if display_value == "1" { "已验证" } else { "未验证" }),
                            "parent_id" => if display_value != "NULL" { println!("👥 上级用户ID: {}", display_value); },
                            "full_name" => if display_value != "NULL" { println!("📝 全名: {}", display_value); },
                            "phone" => if display_value != "NULL" { println!("📞 电话: {}", display_value); },
                            "company" => if display_value != "NULL" { println!("🏢 公司: {}", display_value); },
                            "max_employees" => if display_value != "NULL" { println!("👥 最大员工数: {}", display_value); },
                            "current_employees" => if display_value != "NULL" { println!("👷 当前员工数: {}", display_value); },
                            "created_at" => if display_value != "NULL" { println!("📅 创建时间: {}", display_value); },
                            "updated_at" => if display_value != "NULL" { println!("🔄 更新时间: {}", display_value); },
                            "last_login" => if display_value != "NULL" { println!("🕐 最后登录: {}", display_value); },
                            _ => println!("  {}: {}", column_name, display_value),
                        }
                    }
                }
            } else if count.0 > 0 && count.0 <= 10 {
                println!("\n前几条记录:");
                let sample_query = format!("SELECT * FROM {} LIMIT 5", table_name);
                let rows = sqlx::query(&sample_query)
                    .fetch_all(&pool)
                    .await?;

                for (i, row) in rows.iter().enumerate() {
                    println!("记录 {}:", i + 1);
                    for (j, column) in row.columns().iter().enumerate() {
                        let column_name = column.name();
                        // 跳过密码字段的显示
                        if column_name.to_lowercase().contains("password") ||
                           column_name.to_lowercase().contains("pwd") {
                            println!("  {}: [隐藏]", column_name);
                        } else {
                            let value: Option<String> = row.try_get(j).unwrap_or(None);
                            println!("  {}: {:?}", column_name, value.unwrap_or("NULL".to_string()));
                        }
                    }
                    println!();
                }
            }
        }
    }

    Ok(())
}
