use crate::{models::Device, Database};
use anyhow::{anyhow, Result};

/// DeviceRepository: 负责设备相关的数据库操作
pub struct DeviceRepository {
    database: Database,
}

impl DeviceRepository {
    pub fn new(database: Database) -> Self {
        Self { database }
    }

    /// 根据ID查询设备
    pub async fn find_by_id(&self, id: &str) -> Result<Option<Device>> {
        let device = sqlx::query_as::<_, Device>("SELECT * FROM devices WHERE id = ?")
            .bind(id)
            .fetch_optional(&self.database.pool)
            .await?;
        Ok(device)
    }

    /// 查询用户的所有设备
    pub async fn find_by_user_id(&self, user_id: &str) -> Result<Vec<Device>> {
        let devices = sqlx::query_as::<_, Device>("SELECT * FROM devices WHERE user_id = ?")
            .bind(user_id)
            .fetch_all(&self.database.pool)
            .await?;
        Ok(devices)
    }

    /// 创建设备
    pub async fn create(
        &self,
        user_id: &str,
        device_name: &str,
        device_model: Option<&str>,
    ) -> Result<Device> {
        let id = uuid::Uuid::new_v4().to_string();
        let now = chrono::Utc::now();

        sqlx::query(
            r#"
            INSERT INTO devices (id, user_id, device_name, device_model, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            "#,
        )
        .bind(&id)
        .bind(user_id)
        .bind(device_name)
        .bind(device_model)
        .bind("offline")
        .bind(&now)
        .bind(&now)
        .execute(&self.database.pool)
        .await?;

        self.find_by_id(&id)
            .await?
            .ok_or_else(|| anyhow!("设备创建失败"))
    }

    /// 更新设备状态
    pub async fn update_status(&self, id: &str, status: &str) -> Result<()> {
        sqlx::query("UPDATE devices SET status = ?, updated_at = ? WHERE id = ?")
            .bind(status)
            .bind(chrono::Utc::now())
            .bind(id)
            .execute(&self.database.pool)
            .await?;
        Ok(())
    }

    /// 删除设备
    pub async fn delete(&self, id: &str) -> Result<()> {
        sqlx::query("DELETE FROM devices WHERE id = ?")
            .bind(id)
            .execute(&self.database.pool)
            .await?;
        Ok(())
    }

    /// 统计用户的设备数量
    pub async fn count_by_user_id(&self, user_id: &str) -> Result<i64> {
        let (count,): (i64,) = sqlx::query_as("SELECT COUNT(*) FROM devices WHERE user_id = ?")
            .bind(user_id)
            .fetch_one(&self.database.pool)
            .await?;
        Ok(count)
    }
}
