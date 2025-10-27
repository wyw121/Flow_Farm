use crate::{
    models::{KpiStats, UserInfo, UserStats},
    Database,
};
use anyhow::{anyhow, Result};

pub struct KpiService {
    database: Database,
}

impl KpiService {
    pub fn new(database: Database) -> Self {
        Self { database }
    }

    /// 获取KPI统计数据（基于真实work_records表）
    pub async fn get_kpi_stats(
        &self,
        current_user: &UserInfo,
        start_date: Option<&str>,
        end_date: Option<&str>,
        platform: Option<&str>,
    ) -> Result<KpiStats> {
        tracing::info!(
            "获取KPI统计 - 用户: {}, 开始日期: {:?}, 结束日期: {:?}, 平台: {:?}",
            current_user.username,
            start_date,
            end_date,
            platform
        );

        // 根据用户角色构建不同的查询条件
        let stats = match current_user.role.as_str() {
            "system_admin" => {
                // 系统管理员查看所有数据
                self.query_global_kpi_stats(start_date, end_date, platform).await?
            }
            "user_admin" => {
                // 用户管理员查看自己公司的数据
                self.query_company_kpi_stats(current_user.id, start_date, end_date, platform).await?
            }
            "employee" => {
                // 员工查看自己的数据
                self.query_employee_kpi_stats(current_user.id, start_date, end_date, platform).await?
            }
            _ => {
                return Err(anyhow!("无效的用户角色"));
            }
        };

        tracing::info!(
            "KPI统计完成 - 总操作: {}, 成功: {}, 失败: {}, 成功率: {:.2}%",
            stats.total_actions,
            stats.successful_actions,
            stats.failed_actions,
            stats.success_rate
        );

        Ok(stats)
    }

    /// 查询全局KPI统计（系统管理员）
    async fn query_global_kpi_stats(
        &self,
        start_date: Option<&str>,
        end_date: Option<&str>,
        platform: Option<&str>,
    ) -> Result<KpiStats> {
        let mut query = String::from(
            r#"
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
            FROM work_records
            WHERE 1=1
            "#
        );

        if let Some(sd) = start_date {
            query.push_str(&format!(" AND created_at >= '{}'", sd));
        }
        if let Some(ed) = end_date {
            query.push_str(&format!(" AND created_at <= '{}'", ed));
        }
        if let Some(p) = platform {
            query.push_str(&format!(" AND platform = '{}'", p));
        }

        let row: (i64, i64, i64) = sqlx::query_as(&query)
            .fetch_one(&self.database.pool)
            .await?;

        let total = row.0;
        let successful = row.1;
        let failed = row.2;
        let success_rate = if total > 0 {
            (successful as f64 / total as f64) * 100.0
        } else {
            0.0
        };

        Ok(KpiStats {
            total_actions: total,
            successful_actions: successful,
            failed_actions: failed,
            success_rate,
        })
    }

    /// 查询公司KPI统计（用户管理员）
    async fn query_company_kpi_stats(
        &self,
        user_admin_id: i32,
        start_date: Option<&str>,
        end_date: Option<&str>,
        platform: Option<&str>,
    ) -> Result<KpiStats> {
        let mut query = String::from(
            r#"
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN wr.status = 'completed' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN wr.status = 'failed' THEN 1 ELSE 0 END) as failed
            FROM work_records wr
            INNER JOIN users u ON wr.user_id = CAST(u.id AS TEXT)
            WHERE u.parent_id = ?
            "#
        );

        let mut bind_values = vec![user_admin_id.to_string()];

        if let Some(sd) = start_date {
            query.push_str(" AND wr.created_at >= ?");
            bind_values.push(sd.to_string());
        }
        if let Some(ed) = end_date {
            query.push_str(" AND wr.created_at <= ?");
            bind_values.push(ed.to_string());
        }
        if let Some(p) = platform {
            query.push_str(" AND wr.platform = ?");
            bind_values.push(p.to_string());
        }

        // 构建查询
        let mut query_builder = sqlx::query_as::<_, (i64, i64, i64)>(&query);
        for value in &bind_values {
            query_builder = query_builder.bind(value);
        }

        let row = query_builder
            .fetch_one(&self.database.pool)
            .await?;

        let total = row.0;
        let successful = row.1;
        let failed = row.2;
        let success_rate = if total > 0 {
            (successful as f64 / total as f64) * 100.0
        } else {
            0.0
        };

        Ok(KpiStats {
            total_actions: total,
            successful_actions: successful,
            failed_actions: failed,
            success_rate,
        })
    }

    /// 查询员工个人KPI统计
    async fn query_employee_kpi_stats(
        &self,
        employee_id: i32,
        start_date: Option<&str>,
        end_date: Option<&str>,
        platform: Option<&str>,
    ) -> Result<KpiStats> {
        let user_id_str = employee_id.to_string();
        
        let mut query = String::from(
            r#"
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
            FROM work_records
            WHERE user_id = ?
            "#
        );

        let mut bind_values = vec![user_id_str];

        if let Some(sd) = start_date {
            query.push_str(" AND created_at >= ?");
            bind_values.push(sd.to_string());
        }
        if let Some(ed) = end_date {
            query.push_str(" AND created_at <= ?");
            bind_values.push(ed.to_string());
        }
        if let Some(p) = platform {
            query.push_str(" AND platform = ?");
            bind_values.push(p.to_string());
        }

        let mut query_builder = sqlx::query_as::<_, (i64, i64, i64)>(&query);
        for value in &bind_values {
            query_builder = query_builder.bind(value);
        }

        let row = query_builder
            .fetch_one(&self.database.pool)
            .await?;

        let total = row.0;
        let successful = row.1;
        let failed = row.2;
        let success_rate = if total > 0 {
            (successful as f64 / total as f64) * 100.0
        } else {
            0.0
        };

        Ok(KpiStats {
            total_actions: total,
            successful_actions: successful,
            failed_actions: failed,
            success_rate,
        })
    }

    /// 获取用户统计数据（按用户分组）
    pub async fn get_user_stats(
        &self,
        current_user: &UserInfo,
        start_date: Option<&str>,
        end_date: Option<&str>,
    ) -> Result<Vec<UserStats>> {
        tracing::info!(
            "获取用户统计 - 用户: {}, 开始日期: {:?}, 结束日期: {:?}",
            current_user.username,
            start_date,
            end_date
        );

        // 根据用户角色返回不同范围的统计数据
        let stats = match current_user.role.as_str() {
            "system_admin" => {
                // 系统管理员查看所有用户统计
                self.query_all_user_stats(start_date, end_date).await?
            }
            "user_admin" => {
                // 用户管理员查看自己公司员工的统计
                self.query_company_user_stats(current_user.id, start_date, end_date).await?
            }
            "employee" => {
                // 员工只能查看自己的统计
                vec![self.query_single_user_stats(current_user.id, start_date, end_date).await?]
            }
            _ => {
                return Err(anyhow!("无效的用户角色"));
            }
        };

        tracing::info!("用户统计完成，共 {} 个用户", stats.len());
        Ok(stats)
    }

    /// 查询所有用户统计（系统管理员）
    async fn query_all_user_stats(
        &self,
        start_date: Option<&str>,
        end_date: Option<&str>,
    ) -> Result<Vec<UserStats>> {
        let mut query = String::from(
            r#"
            SELECT 
                u.id as user_id,
                u.username,
                COUNT(wr.id) as total_actions,
                SUM(CASE WHEN wr.status = 'completed' THEN 1 ELSE 0 END) as successful_actions,
                MAX(wr.created_at) as last_activity
            FROM users u
            LEFT JOIN work_records wr ON CAST(u.id AS TEXT) = wr.user_id
            WHERE u.role = 'employee'
            "#
        );

        if let Some(sd) = start_date {
            query.push_str(&format!(" AND wr.created_at >= '{}'", sd));
        }
        if let Some(ed) = end_date {
            query.push_str(&format!(" AND wr.created_at <= '{}'", ed));
        }

        query.push_str(" GROUP BY u.id, u.username ORDER BY total_actions DESC");

        let rows: Vec<(String, String, i64, i64, Option<String>)> = sqlx::query_as(&query)
            .fetch_all(&self.database.pool)
            .await?;

        let stats: Vec<UserStats> = rows
            .into_iter()
            .map(|(user_id, username, total, successful, last_activity)| {
                let success_rate = if total > 0 {
                    (successful as f64 / total as f64) * 100.0
                } else {
                    0.0
                };

                let last_activity_dt = last_activity.and_then(|s| {
                    chrono::DateTime::parse_from_rfc3339(&s)
                        .ok()
                        .map(|dt| dt.with_timezone(&chrono::Utc))
                });

                UserStats {
                    user_id,
                    username,
                    total_actions: total,
                    successful_actions: successful,
                    success_rate,
                    last_activity: last_activity_dt,
                }
            })
            .collect();

        Ok(stats)
    }

    /// 查询公司员工统计（用户管理员）
    async fn query_company_user_stats(
        &self,
        user_admin_id: i32,
        start_date: Option<&str>,
        end_date: Option<&str>,
    ) -> Result<Vec<UserStats>> {
        let mut query = String::from(
            r#"
            SELECT 
                u.id as user_id,
                u.username,
                COUNT(wr.id) as total_actions,
                SUM(CASE WHEN wr.status = 'completed' THEN 1 ELSE 0 END) as successful_actions,
                MAX(wr.created_at) as last_activity
            FROM users u
            LEFT JOIN work_records wr ON CAST(u.id AS TEXT) = wr.user_id
            WHERE u.parent_id = ? AND u.role = 'employee'
            "#
        );

        if let Some(sd) = start_date {
            query.push_str(&format!(" AND wr.created_at >= '{}'", sd));
        }
        if let Some(ed) = end_date {
            query.push_str(&format!(" AND wr.created_at <= '{}'", ed));
        }

        query.push_str(" GROUP BY u.id, u.username ORDER BY total_actions DESC");

        let rows: Vec<(String, String, i64, i64, Option<String>)> = sqlx::query_as(&query)
            .bind(user_admin_id)
            .fetch_all(&self.database.pool)
            .await?;

        let stats: Vec<UserStats> = rows
            .into_iter()
            .map(|(user_id, username, total, successful, last_activity)| {
                let success_rate = if total > 0 {
                    (successful as f64 / total as f64) * 100.0
                } else {
                    0.0
                };

                let last_activity_dt = last_activity.and_then(|s| {
                    chrono::DateTime::parse_from_rfc3339(&s)
                        .ok()
                        .map(|dt| dt.with_timezone(&chrono::Utc))
                });

                UserStats {
                    user_id,
                    username,
                    total_actions: total,
                    successful_actions: successful,
                    success_rate,
                    last_activity: last_activity_dt,
                }
            })
            .collect();

        Ok(stats)
    }

    /// 查询单个用户统计（员工）
    async fn query_single_user_stats(
        &self,
        employee_id: i32,
        start_date: Option<&str>,
        end_date: Option<&str>,
    ) -> Result<UserStats> {
        let user_id_str = employee_id.to_string();
        
        // 先获取用户名
        let user = sqlx::query!("SELECT username FROM users WHERE id = ?", employee_id)
            .fetch_one(&self.database.pool)
            .await?;

        let mut query = String::from(
            r#"
            SELECT 
                COUNT(*) as total_actions,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_actions,
                MAX(created_at) as last_activity
            FROM work_records
            WHERE user_id = ?
            "#
        );

        if let Some(sd) = start_date {
            query.push_str(&format!(" AND created_at >= '{}'", sd));
        }
        if let Some(ed) = end_date {
            query.push_str(&format!(" AND created_at <= '{}'", ed));
        }

        let row: (i64, i64, Option<String>) = sqlx::query_as(&query)
            .bind(&user_id_str)
            .fetch_one(&self.database.pool)
            .await?;

        let total = row.0;
        let successful = row.1;
        let success_rate = if total > 0 {
            (successful as f64 / total as f64) * 100.0
        } else {
            0.0
        };

        let last_activity = row.2.and_then(|s| {
            chrono::DateTime::parse_from_rfc3339(&s)
                .ok()
                .map(|dt| dt.with_timezone(&chrono::Utc))
        });

        Ok(UserStats {
            user_id: user_id_str,
            username: user.username,
            total_actions: total,
            successful_actions: successful,
            success_rate,
            last_activity,
        })
    }
}
