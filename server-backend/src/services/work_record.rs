use anyhow::{Result, anyhow};
use crate::{Database, models::{UserInfo, WorkRecord, CreateWorkRecordRequest}};
use chrono::Utc;
use uuid::Uuid;

pub struct WorkRecordService {
    database: Database,
}

impl WorkRecordService {
    pub fn new(database: Database) -> Self {
        Self { database }
    }

    /// 获取工作记录列表（带分页和筛选）
    pub async fn list_work_records(
        &self,
        current_user: &UserInfo,
        page: i32,
        limit: i32,
        platform: Option<&str>,
        success: Option<bool>,
    ) -> Result<Vec<WorkRecord>> {
        tracing::info!(
            "查询工作记录列表 - 用户: {}, 页码: {}, 每页: {}, 平台: {:?}, 成功: {:?}",
            current_user.username,
            page,
            limit,
            platform,
            success
        );

        let offset = (page - 1) * limit;

        // 根据角色构建不同的查询条件
        let records = match current_user.role.as_str() {
            "system_admin" => {
                // 系统管理员可以查看所有工作记录
                if let Some(platform_filter) = platform {
                    if let Some(success_filter) = success {
                        sqlx::query_as::<_, WorkRecord>(
                            r#"
                            SELECT * FROM work_records
                            WHERE platform = ? AND status = ?
                            ORDER BY created_at DESC
                            LIMIT ? OFFSET ?
                            "#,
                        )
                        .bind(platform_filter)
                        .bind(if success_filter { "completed" } else { "failed" })
                        .bind(limit)
                        .bind(offset)
                        .fetch_all(&self.database.pool)
                        .await?
                    } else {
                        sqlx::query_as::<_, WorkRecord>(
                            r#"
                            SELECT * FROM work_records
                            WHERE platform = ?
                            ORDER BY created_at DESC
                            LIMIT ? OFFSET ?
                            "#,
                        )
                        .bind(platform_filter)
                        .bind(limit)
                        .bind(offset)
                        .fetch_all(&self.database.pool)
                        .await?
                    }
                } else {
                    sqlx::query_as::<_, WorkRecord>(
                        r#"
                        SELECT * FROM work_records
                        ORDER BY created_at DESC
                        LIMIT ? OFFSET ?
                        "#,
                    )
                    .bind(limit)
                    .bind(offset)
                    .fetch_all(&self.database.pool)
                    .await?
                }
            }
            "user_admin" => {
                // 用户管理员可以查看自己公司所有员工的工作记录
                // 需要关联查询用户表
                if let Some(platform_filter) = platform {
                    sqlx::query_as::<_, WorkRecord>(
                        r#"
                        SELECT wr.* FROM work_records wr
                        INNER JOIN users u ON wr.user_id = CAST(u.id AS TEXT)
                        WHERE u.parent_id = ? AND wr.platform = ?
                        ORDER BY wr.created_at DESC
                        LIMIT ? OFFSET ?
                        "#,
                    )
                    .bind(current_user.id)
                    .bind(platform_filter)
                    .bind(limit)
                    .bind(offset)
                    .fetch_all(&self.database.pool)
                    .await?
                } else {
                    sqlx::query_as::<_, WorkRecord>(
                        r#"
                        SELECT wr.* FROM work_records wr
                        INNER JOIN users u ON wr.user_id = CAST(u.id AS TEXT)
                        WHERE u.parent_id = ?
                        ORDER BY wr.created_at DESC
                        LIMIT ? OFFSET ?
                        "#,
                    )
                    .bind(current_user.id)
                    .bind(limit)
                    .bind(offset)
                    .fetch_all(&self.database.pool)
                    .await?
                }
            }
            "employee" => {
                // 员工只能查看自己的工作记录
                let user_id_str = current_user.id.to_string();
                if let Some(platform_filter) = platform {
                    sqlx::query_as::<_, WorkRecord>(
                        r#"
                        SELECT * FROM work_records
                        WHERE user_id = ? AND platform = ?
                        ORDER BY created_at DESC
                        LIMIT ? OFFSET ?
                        "#,
                    )
                    .bind(&user_id_str)
                    .bind(platform_filter)
                    .bind(limit)
                    .bind(offset)
                    .fetch_all(&self.database.pool)
                    .await?
                } else {
                    sqlx::query_as::<_, WorkRecord>(
                        r#"
                        SELECT * FROM work_records
                        WHERE user_id = ?
                        ORDER BY created_at DESC
                        LIMIT ? OFFSET ?
                        "#,
                    )
                    .bind(&user_id_str)
                    .bind(limit)
                    .bind(offset)
                    .fetch_all(&self.database.pool)
                    .await?
                }
            }
            _ => {
                return Err(anyhow!("无效的用户角色"));
            }
        };

        tracing::info!("查询到 {} 条工作记录", records.len());
        Ok(records)
    }

    /// 创建工作记录
    pub async fn create_work_record(
        &self,
        current_user: &UserInfo,
        request: CreateWorkRecordRequest,
    ) -> Result<WorkRecord> {
        tracing::info!(
            "创建工作记录 - 用户: {}, 设备: {}, 平台: {}, 操作: {}",
            current_user.username,
            request.device_id,
            request.platform,
            request.action_type
        );

        // 只有员工角色可以创建工作记录
        if current_user.role != "employee" {
            return Err(anyhow!("只有员工角色可以创建工作记录"));
        }

        // 验证设备是否属于当前用户
        let user_id_str = current_user.id.to_string();
        let device_check = sqlx::query(
            r#"
            SELECT id FROM devices
            WHERE id = ? AND user_id = ?
            "#,
        )
        .bind(&request.device_id)
        .bind(&user_id_str)
        .fetch_optional(&self.database.pool)
        .await?;

        if device_check.is_none() {
            return Err(anyhow!("设备不存在或不属于当前用户"));
        }

        // 创建工作记录
        let record_id = Uuid::new_v4().to_string();
        let now = Utc::now();

        sqlx::query(
            r#"
            INSERT INTO work_records (
                id, user_id, device_id, platform, action_type,
                target_count, completed_count, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 0, 'pending', ?, ?)
            "#,
        )
        .bind(&record_id)
        .bind(&user_id_str)
        .bind(&request.device_id)
        .bind(&request.platform)
        .bind(&request.action_type)
        .bind(request.target_count)
        .bind(now)
        .bind(now)
        .execute(&self.database.pool)
        .await?;

        // 查询并返回创建的记录
        let record = sqlx::query_as::<_, WorkRecord>(
            r#"
            SELECT * FROM work_records WHERE id = ?
            "#,
        )
        .bind(&record_id)
        .fetch_one(&self.database.pool)
        .await?;

        tracing::info!("工作记录创建成功: {}", record_id);
        Ok(record)
    }

    /// 获取单个工作记录
    pub async fn get_work_record(&self, current_user: &UserInfo, record_id: &str) -> Result<WorkRecord> {
        tracing::info!(
            "查询工作记录详情 - 用户: {}, 记录ID: {}",
            current_user.username,
            record_id
        );

        // 查询记录
        let record = sqlx::query_as::<_, WorkRecord>(
            r#"
            SELECT * FROM work_records WHERE id = ?
            "#,
        )
        .bind(record_id)
        .fetch_optional(&self.database.pool)
        .await?;

        let record = record.ok_or_else(|| anyhow!("工作记录不存在"))?;

        // 权限检查
        match current_user.role.as_str() {
            "system_admin" => {
                // 系统管理员可以查看所有记录
            }
            "user_admin" => {
                // 用户管理员可以查看自己公司员工的记录
                let user_id: i32 = record.user_id.parse()
                    .map_err(|_| anyhow!("无效的用户ID格式"))?;
                
                let employee = sqlx::query!(
                    r#"
                    SELECT parent_id FROM users WHERE id = ?
                    "#,
                    user_id
                )
                .fetch_optional(&self.database.pool)
                .await?;

                if let Some(emp) = employee {
                    if emp.parent_id != Some(current_user.id as i64) {
                        return Err(anyhow!("无权限访问该工作记录"));
                    }
                } else {
                    return Err(anyhow!("关联的用户不存在"));
                }
            }
            "employee" => {
                // 员工只能查看自己的记录
                if record.user_id != current_user.id.to_string() {
                    return Err(anyhow!("无权限访问该工作记录"));
                }
            }
            _ => {
                return Err(anyhow!("无效的用户角色"));
            }
        }

        Ok(record)
    }

    /// 更新工作记录进度
    pub async fn update_work_record_progress(
        &self,
        current_user: &UserInfo,
        record_id: &str,
        completed_count: i32,
        status: &str,
    ) -> Result<WorkRecord> {
        tracing::info!(
            "更新工作记录进度 - 用户: {}, 记录ID: {}, 完成数: {}, 状态: {}",
            current_user.username,
            record_id,
            completed_count,
            status
        );

        // 只有员工可以更新自己的工作记录
        if current_user.role != "employee" {
            return Err(anyhow!("只有员工角色可以更新工作记录"));
        }

        let user_id_str = current_user.id.to_string();

        // 验证记录归属
        let record = sqlx::query_as::<_, WorkRecord>(
            r#"
            SELECT * FROM work_records WHERE id = ? AND user_id = ?
            "#,
        )
        .bind(record_id)
        .bind(&user_id_str)
        .fetch_optional(&self.database.pool)
        .await?;

        if record.is_none() {
            return Err(anyhow!("工作记录不存在或无权限访问"));
        }

        // 更新记录
        let now = Utc::now();
        sqlx::query(
            r#"
            UPDATE work_records
            SET completed_count = ?, status = ?, updated_at = ?
            WHERE id = ?
            "#,
        )
        .bind(completed_count)
        .bind(status)
        .bind(now)
        .bind(record_id)
        .execute(&self.database.pool)
        .await?;

        // 查询并返回更新后的记录
        let updated_record = sqlx::query_as::<_, WorkRecord>(
            r#"
            SELECT * FROM work_records WHERE id = ?
            "#,
        )
        .bind(record_id)
        .fetch_one(&self.database.pool)
        .await?;

        tracing::info!("工作记录更新成功: {}", record_id);
        Ok(updated_record)
    }

    /// 统计工作记录数量
    pub async fn count_work_records(
        &self,
        current_user: &UserInfo,
        platform: Option<&str>,
        status: Option<&str>,
        start_date: Option<&str>,
        end_date: Option<&str>,
    ) -> Result<i64> {
        let count = match current_user.role.as_str() {
            "system_admin" => {
                // 系统管理员统计所有记录
                let mut query = String::from("SELECT COUNT(*) as count FROM work_records WHERE 1=1");
                
                if let Some(p) = platform {
                    query.push_str(&format!(" AND platform = '{}'", p));
                }
                if let Some(s) = status {
                    query.push_str(&format!(" AND status = '{}'", s));
                }
                if let Some(sd) = start_date {
                    query.push_str(&format!(" AND created_at >= '{}'", sd));
                }
                if let Some(ed) = end_date {
                    query.push_str(&format!(" AND created_at <= '{}'", ed));
                }

                let row: (i64,) = sqlx::query_as(&query)
                    .fetch_one(&self.database.pool)
                    .await?;
                row.0
            }
            "user_admin" => {
                // 用户管理员统计自己公司的记录
                let row: (i64,) = sqlx::query_as(
                    r#"
                    SELECT COUNT(*) FROM work_records wr
                    INNER JOIN users u ON wr.user_id = CAST(u.id AS TEXT)
                    WHERE u.parent_id = ?
                    "#
                )
                .bind(current_user.id)
                .fetch_one(&self.database.pool)
                .await?;
                row.0
            }
            "employee" => {
                // 员工统计自己的记录
                let user_id_str = current_user.id.to_string();
                let row: (i64,) = sqlx::query_as(
                    r#"
                    SELECT COUNT(*) FROM work_records
                    WHERE user_id = ?
                    "#
                )
                .bind(&user_id_str)
                .fetch_one(&self.database.pool)
                .await?;
                row.0
            }
            _ => 0,
        };

        Ok(count)
    }
}
