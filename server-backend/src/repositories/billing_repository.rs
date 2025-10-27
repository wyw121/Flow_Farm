use crate::{models::BillingRecord, Database};
use anyhow::{anyhow, Result};

/// BillingRepository: 负责计费记录的数据库操作
pub struct BillingRepository {
    database: Database,
}

impl BillingRepository {
    pub fn new(database: Database) -> Self {
        Self { database }
    }

    /// 根据ID查询计费记录
    pub async fn find_by_id(&self, id: &str) -> Result<Option<BillingRecord>> {
        let record = sqlx::query_as::<_, BillingRecord>("SELECT * FROM billing_records WHERE id = ?")
            .bind(id)
            .fetch_optional(&self.database.pool)
            .await?;
        Ok(record)
    }

    /// 查询用户的计费记录
    pub async fn find_by_user_id(&self, user_id: &str, limit: i32, offset: i32) -> Result<Vec<BillingRecord>> {
        let records = sqlx::query_as::<_, BillingRecord>(
            "SELECT * FROM billing_records WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?"
        )
        .bind(user_id)
        .bind(limit)
        .bind(offset)
        .fetch_all(&self.database.pool)
        .await?;
        Ok(records)
    }

    /// 创建计费记录
    pub async fn create(
        &self,
        user_id: &str,
        amount: f64,
        record_type: &str,
        description: Option<&str>,
    ) -> Result<BillingRecord> {
        let id = uuid::Uuid::new_v4().to_string();
        let now = chrono::Utc::now();

        sqlx::query(
            r#"
            INSERT INTO billing_records (id, user_id, amount, type, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            "#,
        )
        .bind(&id)
        .bind(user_id)
        .bind(amount)
        .bind(record_type)
        .bind(description)
        .bind(&now)
        .execute(&self.database.pool)
        .await?;

        self.find_by_id(&id)
            .await?
            .ok_or_else(|| anyhow!("计费记录创建失败"))
    }

    /// 统计用户的总消费
    pub async fn sum_by_user_id(&self, user_id: &str) -> Result<f64> {
        let result: (Option<f64>,) = sqlx::query_as(
            "SELECT SUM(amount) FROM billing_records WHERE user_id = ? AND type = 'debit'"
        )
        .bind(user_id)
        .fetch_one(&self.database.pool)
        .await?;

        Ok(result.0.unwrap_or(0.0))
    }

    /// 统计用户的总充值
    pub async fn sum_credit_by_user_id(&self, user_id: &str) -> Result<f64> {
        let result: (Option<f64>,) = sqlx::query_as(
            "SELECT SUM(amount) FROM billing_records WHERE user_id = ? AND type = 'credit'"
        )
        .bind(user_id)
        .fetch_one(&self.database.pool)
        .await?;

        Ok(result.0.unwrap_or(0.0))
    }
}
