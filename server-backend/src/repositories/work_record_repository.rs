use crate::{models::{WorkRecord, CreateWorkRecordRequest}, Database};
use anyhow::{anyhow, Result};

/// WorkRecordRepository: 负责工作记录的数据库操作
pub struct WorkRecordRepository {
    database: Database,
}

impl WorkRecordRepository {
    pub fn new(database: Database) -> Self {
        Self { database }
    }

    /// 根据ID查询工作记录
    pub async fn find_by_id(&self, id: &str) -> Result<Option<WorkRecord>> {
        let record = sqlx::query_as::<_, WorkRecord>("SELECT * FROM work_records WHERE id = ?")
            .bind(id)
            .fetch_optional(&self.database.pool)
            .await?;
        Ok(record)
    }

    /// 分页查询工作记录
    pub async fn find_all_paginated(
        &self,
        user_id_filter: Option<&str>,
        device_id_filter: Option<&str>,
        platform_filter: Option<&str>,
        status_filter: Option<&str>,
        page: i32,
        limit: i32,
    ) -> Result<Vec<WorkRecord>> {
        let offset = (page - 1) * limit;
        let mut query = "SELECT * FROM work_records WHERE 1=1".to_string();
        let mut bind_values: Vec<String> = vec![];

        if let Some(user_id) = user_id_filter {
            query.push_str(" AND user_id = ?");
            bind_values.push(user_id.to_string());
        }

        if let Some(device_id) = device_id_filter {
            query.push_str(" AND device_id = ?");
            bind_values.push(device_id.to_string());
        }

        if let Some(platform) = platform_filter {
            query.push_str(" AND platform = ?");
            bind_values.push(platform.to_string());
        }

        if let Some(status) = status_filter {
            query.push_str(" AND status = ?");
            bind_values.push(status.to_string());
        }

        query.push_str(" ORDER BY created_at DESC LIMIT ? OFFSET ?");

        let mut sql_query = sqlx::query_as::<_, WorkRecord>(&query);
        for value in &bind_values {
            sql_query = sql_query.bind(value);
        }

        let records = sql_query
            .bind(limit)
            .bind(offset)
            .fetch_all(&self.database.pool)
            .await?;

        Ok(records)
    }

    /// 创建工作记录
    pub async fn create(
        &self,
        user_id: &str,
        device_id: &str,
        request: &CreateWorkRecordRequest,
    ) -> Result<WorkRecord> {
        let id = uuid::Uuid::new_v4().to_string();
        let now = chrono::Utc::now();

        sqlx::query(
            r#"
            INSERT INTO work_records (
                id, user_id, device_id, platform, action_type, 
                target_count, completed_count, status, 
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            "#,
        )
        .bind(&id)
        .bind(user_id)
        .bind(device_id)
        .bind(&request.platform)
        .bind(&request.action_type)
        .bind(request.target_count)
        .bind(0) // completed_count 初始为 0
        .bind("pending") // status 初始为 pending
        .bind(&now)
        .bind(&now)
        .execute(&self.database.pool)
        .await?;

        self.find_by_id(&id)
            .await?
            .ok_or_else(|| anyhow!("工作记录创建失败"))
    }

    /// 更新工作记录进度
    pub async fn update_progress(
        &self,
        id: &str,
        completed_count: i32,
        status: &str,
    ) -> Result<WorkRecord> {
        sqlx::query(
            "UPDATE work_records SET completed_count = ?, status = ?, updated_at = ? WHERE id = ?"
        )
        .bind(completed_count)
        .bind(status)
        .bind(chrono::Utc::now())
        .bind(id)
        .execute(&self.database.pool)
        .await?;

        self.find_by_id(id)
            .await?
            .ok_or_else(|| anyhow!("工作记录不存在"))
    }

    /// 统计工作记录数量
    pub async fn count(
        &self,
        user_id_filter: Option<&str>,
        status_filter: Option<&str>,
    ) -> Result<i64> {
        let mut query = "SELECT COUNT(*) FROM work_records WHERE 1=1".to_string();
        let mut bind_values: Vec<String> = vec![];

        if let Some(user_id) = user_id_filter {
            query.push_str(" AND user_id = ?");
            bind_values.push(user_id.to_string());
        }

        if let Some(status) = status_filter {
            query.push_str(" AND status = ?");
            bind_values.push(status.to_string());
        }

        let mut sql_query = sqlx::query_as::<_, (i64,)>(&query);
        for value in &bind_values {
            sql_query = sql_query.bind(value);
        }

        let (count,) = sql_query.fetch_one(&self.database.pool).await?;
        Ok(count)
    }

    /// 统计用户的总完成数量
    pub async fn sum_completed_by_user(&self, user_id: &str) -> Result<i64> {
        let result: (Option<i64>,) = sqlx::query_as(
            "SELECT SUM(completed_count) FROM work_records WHERE user_id = ? AND status = 'completed'"
        )
        .bind(user_id)
        .fetch_one(&self.database.pool)
        .await?;

        Ok(result.0.unwrap_or(0))
    }

    /// 查询用户的所有工作记录
    pub async fn find_by_user_id(&self, user_id: &str) -> Result<Vec<WorkRecord>> {
        let records = sqlx::query_as::<_, WorkRecord>(
            "SELECT * FROM work_records WHERE user_id = ? ORDER BY created_at DESC"
        )
        .bind(user_id)
        .fetch_all(&self.database.pool)
        .await?;

        Ok(records)
    }

    /// 删除工作记录
    pub async fn delete(&self, id: &str) -> Result<()> {
        sqlx::query("DELETE FROM work_records WHERE id = ?")
            .bind(id)
            .execute(&self.database.pool)
            .await?;
        Ok(())
    }
}
