// API集成测试 - 测试辅助模块
// 提供测试用的数据库、服务器、认证等工具函数

use flow_farm_backend::{Config, Database};
use sqlx::SqlitePool;
use std::sync::Arc;

/// 创建测试用的内存数据库
pub async fn create_test_database() -> Database {
    // 使用内存数据库进行测试
    let pool = SqlitePool::connect("sqlite::memory:")
        .await
        .expect("Failed to create test database");

    // 初始化表结构
    initialize_test_schema(&pool).await;

    Database { pool }
}

/// 初始化测试数据库的表结构
async fn initialize_test_schema(pool: &SqlitePool) {
    // 创建users表
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            full_name TEXT,
            company TEXT,
            parent_id TEXT,
            is_active INTEGER DEFAULT 1,
            is_verified INTEGER DEFAULT 0,
            max_employees INTEGER DEFAULT 10,
            current_employees INTEGER DEFAULT 0,
            balance REAL DEFAULT 0.0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_login TEXT
        )
        "#,
    )
    .execute(pool)
    .await
    .expect("Failed to create users table");

    // 创建devices表
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY,
            device_name TEXT NOT NULL,
            device_type TEXT NOT NULL,
            adb_id TEXT,
            status TEXT NOT NULL DEFAULT 'disconnected',
            user_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        "#,
    )
    .execute(pool)
    .await
    .expect("Failed to create devices table");

    // 创建work_records表
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS work_records (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            device_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            action_type TEXT NOT NULL,
            target_count INTEGER NOT NULL,
            completed_count INTEGER DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (device_id) REFERENCES devices(id)
        )
        "#,
    )
    .execute(pool)
    .await
    .expect("Failed to create work_records table");

    // 创建billing_records表
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS billing_records (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            amount REAL NOT NULL,
            billing_type TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        "#,
    )
    .execute(pool)
    .await
    .expect("Failed to create billing_records table");
}

/// 创建测试配置
pub fn create_test_config() -> Config {
    Config {
        app_name: "Flow Farm Test".to_string(),
        version: "1.0.0-test".to_string(),
        debug: true,
        host: "127.0.0.1".to_string(),
        port: 8000,
        database_url: ":memory:".to_string(),
        jwt_secret: "test-secret-key".to_string(),
        jwt_expires_in: 3600, // 1小时
        allowed_origins: vec!["*".to_string()],
        bcrypt_rounds: 4, // 测试时使用更低的成本
        static_dir: "./test_static".to_string(),
        enable_tls: false,
        tls_cert_path: None,
        tls_key_path: None,
    }
}

/// 插入测试用户
pub async fn insert_test_user(
    pool: &SqlitePool,
    id: &str,
    username: &str,
    password_hash: &str,
    role: &str,
) -> Result<(), sqlx::Error> {
    let now = chrono::Utc::now().format("%Y-%m-%d %H:%M:%S").to_string();

    sqlx::query(
        r#"
        INSERT INTO users (
            id, username, password, role, email, phone,
            full_name, company, parent_id, is_active, is_verified,
            max_employees, current_employees, balance,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(id)
    .bind(username)
    .bind(password_hash)
    .bind(role)
    .bind(format!("{}@test.com", username))
    .bind("13800138000")
    .bind(format!("Test {}", username))
    .bind("Test Company")
    .bind(Option::<String>::None)
    .bind(1) // is_active
    .bind(1) // is_verified
    .bind(10)
    .bind(0)
    .bind(1000.0)
    .bind(&now)
    .bind(&now)
    .execute(pool)
    .await?;

    Ok(())
}

/// 生成测试JWT token
pub fn generate_test_token(user_id: &str, username: &str, role: &str) -> String {
    use flow_farm_backend::utils::jwt::create_jwt_token;
    
    let config = create_test_config();
    create_jwt_token(user_id, role, &config.jwt_secret, config.jwt_expires_in)
        .expect("Failed to create test token")
}

/// 清理测试数据库
pub async fn cleanup_test_database(pool: &SqlitePool) {
    let _ = sqlx::query("DELETE FROM billing_records").execute(pool).await;
    let _ = sqlx::query("DELETE FROM work_records").execute(pool).await;
    let _ = sqlx::query("DELETE FROM devices").execute(pool).await;
    let _ = sqlx::query("DELETE FROM users").execute(pool).await;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_create_test_database() {
        let db = create_test_database().await;
        assert!(db.pool.is_closed() == false, "数据库连接应该是打开的");
    }

    #[test]
    fn test_create_test_config() {
        let config = create_test_config();
        assert_eq!(config.database_url, ":memory:");
        assert_eq!(config.jwt_secret, "test-secret-key");
        assert_eq!(config.port, 8000);
    }

    #[tokio::test]
    async fn test_insert_test_user() {
        let db = create_test_database().await;
        
        let result = insert_test_user(
            &db.pool,
            "test-user-1",
            "testuser",
            "hashed_password",
            "employee",
        )
        .await;

        assert!(result.is_ok(), "插入测试用户应该成功");

        // 验证用户已插入
        let count: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM users")
            .fetch_one(&db.pool)
            .await
            .expect("查询用户数量失败");

        assert_eq!(count.0, 1, "应该有1个用户");
    }

    #[test]
    fn test_generate_test_token() {
        let token = generate_test_token("user-1", "testuser", "employee");
        assert!(!token.is_empty(), "Token不应为空");
        assert!(token.len() > 50, "Token长度应该足够长");
    }

    #[tokio::test]
    async fn test_cleanup_test_database() {
        let db = create_test_database().await;

        // 插入测试数据
        insert_test_user(&db.pool, "user-1", "user1", "hash1", "employee")
            .await
            .unwrap();
        insert_test_user(&db.pool, "user-2", "user2", "hash2", "employee")
            .await
            .unwrap();

        // 清理数据库
        cleanup_test_database(&db.pool).await;

        // 验证已清理
        let count: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM users")
            .fetch_one(&db.pool)
            .await
            .expect("查询用户数量失败");

        assert_eq!(count.0, 0, "清理后应该没有用户");
    }
}
