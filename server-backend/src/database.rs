use crate::models::*;
use anyhow::Result;
use sqlx::{Row, SqlitePool};

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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                hashed_password TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('system_admin', 'user_admin', 'employee')),
                company_id TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                parent_id INTEGER,
                full_name TEXT,
                phone TEXT,
                company TEXT,
                max_employees INTEGER DEFAULT 10,
                current_employees INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
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

        // 删除旧的价格规则表（如果存在）并重新创建
        sqlx::query("DROP TABLE IF EXISTS pricing_rules")
            .execute(&self.pool)
            .await?;

        // 创建价格规则表
        sqlx::query(
            r#"
            CREATE TABLE pricing_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT NOT NULL,
                billing_type TEXT NOT NULL,
                unit_price REAL NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
        let admin_exists =
            sqlx::query("SELECT COUNT(*) as count FROM users WHERE role = 'system_admin'")
                .fetch_one(&self.pool)
                .await?
                .get::<i64, _>("count")
                > 0;

        if !admin_exists {
            let password_hash = bcrypt::hash("admin123", 12)?;

            sqlx::query(
                r#"
                INSERT INTO users (username, email, hashed_password, role, is_active)
                VALUES (?, ?, ?, ?, ?)
                "#,
            )
            .bind("admin")
            .bind("admin@flowfarm.com")
            .bind(&password_hash)
            .bind("system_admin")
            .bind(true)
            .execute(&self.pool)
            .await?;

            tracing::info!("✅ 默认管理员账户已创建 - 用户名: admin, 密码: admin123");
        }

        // 创建测试用户（仅在开发环境）
        self.create_test_users().await?;

        // 创建测试价格规则
        self.create_test_pricing_rules().await?;

        tracing::info!("✅ 数据库迁移完成");
        Ok(())
    }

    async fn create_test_pricing_rules(&self) -> Result<()> {
        tracing::info!("🔄 创建测试价格规则数据");

        // 检查是否已存在价格规则
        let rules_count = sqlx::query("SELECT COUNT(*) as count FROM pricing_rules")
            .fetch_one(&self.pool)
            .await?
            .get::<i64, _>("count");

        if rules_count == 0 {
            // 创建默认价格规则
            let rules = vec![
                ("抖音关注", "douyin_follow", 0.05),
                ("抖音点赞", "douyin_like", 0.02),
                ("小红书关注", "xiaohongshu_follow", 0.08),
                ("小红书点赞", "xiaohongshu_like", 0.03),
                ("小红书收藏", "xiaohongshu_favorite", 0.04),
            ];

            for (rule_name, billing_type, unit_price) in rules {
                sqlx::query(
                    r#"
                    INSERT INTO pricing_rules (rule_name, billing_type, unit_price, is_active)
                    VALUES (?, ?, ?, ?)
                    "#,
                )
                .bind(rule_name)
                .bind(billing_type)
                .bind(unit_price)
                .bind(true)
                .execute(&self.pool)
                .await?;
            }

            tracing::info!("✅ 测试价格规则创建完成");
        } else {
            tracing::info!("ℹ️  价格规则已存在，跳过创建");
        }

        Ok(())
    }

    async fn create_test_users(&self) -> Result<()> {
        tracing::info!("🔄 创建测试用户数据");

        let password_hash = bcrypt::hash("admin123", 12)?;

        // 检查是否已存在company_admin_1用户
        let company_admin_exists =
            sqlx::query("SELECT COUNT(*) as count FROM users WHERE username = 'company_admin_1'")
                .fetch_one(&self.pool)
                .await?
                .get::<i64, _>("count")
                > 0;

        if !company_admin_exists {
            // 创建公司管理员1
            sqlx::query(
                r#"
                INSERT INTO users (username, email, hashed_password, role, company, is_active, max_employees)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                "#,
            )
            .bind("company_admin_1")
            .bind("company_admin_1@example.com")
            .bind(&password_hash)
            .bind("user_admin")
            .bind("company_001")
            .bind(true)
            .bind(50)
            .execute(&self.pool)
            .await?;

            // 创建公司管理员2
            sqlx::query(
                r#"
                INSERT INTO users (username, email, hashed_password, role, company, is_active, max_employees)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                "#,
            )
            .bind("company_admin_2")
            .bind("company_admin_2@example.com")
            .bind(&password_hash)
            .bind("user_admin")
            .bind("company_002")
            .bind(true)
            .bind(30)
            .execute(&self.pool)
            .await?;

            // 创建测试员工
            let employees = vec![
                ("employee_1", "employee_1@company_001.com", "company_001"),
                ("employee_2", "employee_2@company_001.com", "company_001"),
                ("employee_3", "employee_3@company_002.com", "company_002"),
            ];

            for (username, email, company) in employees {
                sqlx::query(
                    r#"
                    INSERT INTO users (username, email, hashed_password, role, company, is_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                    "#,
                )
                .bind(username)
                .bind(email)
                .bind(&password_hash)
                .bind("employee")
                .bind(company)
                .bind(true)
                .execute(&self.pool)
                .await?;
            }

            tracing::info!("✅ 测试用户创建完成");
            tracing::info!("   - company_admin_1 (密码: admin123)");
            tracing::info!("   - company_admin_2 (密码: admin123)");
            tracing::info!("   - employee_1, employee_2, employee_3 (密码: admin123)");
        } else {
            tracing::info!("ℹ️  测试用户已存在，跳过创建");
        }

        Ok(())
    }
}
