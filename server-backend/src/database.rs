use sqlx::{SqlitePool, Row};
use anyhow::Result;
use crate::models::*;

#[derive(Debug, Clone)]
pub struct Database {
    pub pool: SqlitePool,
}

impl Database {
    pub async fn new(database_url: &str) -> Result<Self> {
        let pool = SqlitePool::connect(database_url).await?;
        Ok(Self { pool })
    }

    pub async fn migrate(&self) -> Result<()> {
        tracing::info!("🔄 开始数据库迁移");

        // 创建用户表
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('system_admin', 'user_admin', 'employee')),
                company_id TEXT,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                max_employees INTEGER DEFAULT 10,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        // 创建工作记录表
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS work_records (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                device_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                action_type TEXT NOT NULL,
                target_user TEXT,
                target_content TEXT,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        // 创建设备表
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS devices (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                device_name TEXT NOT NULL,
                device_type TEXT NOT NULL,
                adb_id TEXT,
                status TEXT NOT NULL DEFAULT 'offline',
                last_seen DATETIME,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        // 创建计费记录表
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS billing_records (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL,
                billing_type TEXT NOT NULL,
                description TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        // 创建系统配置表
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            "#,
        )
        .execute(&self.pool)
        .await?;

        // 插入默认系统管理员（如果不存在）
        let admin_exists = sqlx::query("SELECT COUNT(*) as count FROM users WHERE role = 'system_admin'")
            .fetch_one(&self.pool)
            .await?
            .get::<i64, _>("count") > 0;

        if !admin_exists {
            let admin_id = uuid::Uuid::new_v4().to_string();
            let password_hash = bcrypt::hash("admin123", 12)?;

            sqlx::query(
                r#"
                INSERT INTO users (id, username, email, password_hash, role, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
                "#,
            )
            .bind(&admin_id)
            .bind("admin")
            .bind("admin@flowfarm.com")
            .bind(&password_hash)
            .bind("system_admin")
            .bind(true)
            .execute(&self.pool)
            .await?;

            tracing::info!("✅ 默认管理员账户已创建 - 用户名: admin, 密码: admin123");
        }

        tracing::info!("✅ 数据库迁移完成");
        Ok(())
    }
}
