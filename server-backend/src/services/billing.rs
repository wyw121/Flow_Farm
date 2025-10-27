use crate::{
    models::{
        BillingRecord, CreateBillingRecordRequest, CreatePricingRuleRequest, PricingRule, UserInfo,
    },
    Database,
};
use anyhow::{anyhow, Result};
use chrono::Utc;

pub struct BillingService {
    database: Database,
}

impl BillingService {
    pub fn new(database: Database) -> Self {
        Self { database }
    }

    pub async fn list_billing_records(
        &self,
        current_user: &UserInfo,
        page: i32,
        limit: i32,
        user_id: Option<&str>,
    ) -> Result<Vec<BillingRecord>> {
        let offset = (page - 1) * limit;

        // 根据用户角色决定查询范围
        let query = match current_user.role.as_str() {
            "system_admin" => {
                // 系统管理员可以查看所有记录
                if let Some(uid) = user_id {
                    sqlx::query_as::<_, BillingRecord>(
                        "SELECT id, user_id, amount, billing_type, description, created_at
                         FROM billing_records
                         WHERE user_id = ?
                         ORDER BY created_at DESC
                         LIMIT ? OFFSET ?",
                    )
                    .bind(uid)
                    .bind(limit)
                    .bind(offset)
                    .fetch_all(&self.database.pool)
                    .await?
                } else {
                    sqlx::query_as::<_, BillingRecord>(
                        "SELECT id, user_id, amount, billing_type, description, created_at
                         FROM billing_records
                         ORDER BY created_at DESC
                         LIMIT ? OFFSET ?",
                    )
                    .bind(limit)
                    .bind(offset)
                    .fetch_all(&self.database.pool)
                    .await?
                }
            }
            "user_admin" => {
                // 用户管理员只能查看本公司员工的记录
                if let Some(company) = &current_user.company {
                    // 首先获取该公司的所有员工ID
                    let employee_ids: Vec<String> = sqlx::query_scalar(
                        "SELECT CAST(id AS TEXT) FROM users WHERE company = ? AND role = 'employee'"
                    )
                    .bind(company)
                    .fetch_all(&self.database.pool)
                    .await?;

                    if employee_ids.is_empty() {
                        return Ok(vec![]);
                    }

                    // 构建IN子句的占位符
                    let placeholders = employee_ids
                        .iter()
                        .map(|_| "?")
                        .collect::<Vec<_>>()
                        .join(",");
                    let query_sql = format!(
                        "SELECT id, user_id, amount, billing_type, description, created_at
                         FROM billing_records
                         WHERE user_id IN ({})
                         ORDER BY created_at DESC
                         LIMIT ? OFFSET ?",
                        placeholders
                    );

                    let mut query = sqlx::query_as::<_, BillingRecord>(&query_sql);

                    // 绑定员工ID参数
                    for employee_id in employee_ids {
                        query = query.bind(employee_id);
                    }

                    // 绑定分页参数
                    query = query.bind(limit).bind(offset);

                    query.fetch_all(&self.database.pool).await?
                } else {
                    return Err(anyhow!("用户管理员必须属于一个公司"));
                }
            }
            "employee" => {
                // 员工只能查看自己的记录
                sqlx::query_as::<_, BillingRecord>(
                    "SELECT id, user_id, amount, billing_type, description, created_at
                     FROM billing_records
                     WHERE user_id = ?
                     ORDER BY created_at DESC
                     LIMIT ? OFFSET ?",
                )
                .bind(current_user.id.to_string())
                .bind(limit)
                .bind(offset)
                .fetch_all(&self.database.pool)
                .await?
            }
            _ => return Err(anyhow!("未知用户角色")),
        };

        Ok(query)
    }

    pub async fn create_billing_record(
        &self,
        current_user: &UserInfo,
        request: CreateBillingRecordRequest,
    ) -> Result<BillingRecord> {
        // 检查权限 - 只有系统管理员和用户管理员可以创建计费记录
        if current_user.role != "system_admin" && current_user.role != "user_admin" {
            return Err(anyhow!("权限不足"));
        }

        // 如果是用户管理员，只能为本公司员工创建记录
        if current_user.role == "user_admin" {
            if let Some(company) = &current_user.company {
                // 验证目标用户是否属于同一公司
                let target_user_company = sqlx::query_scalar::<_, Option<String>>(
                    "SELECT company FROM users WHERE id = ?",
                )
                .bind(&request.user_id)
                .fetch_one(&self.database.pool)
                .await?;

                if target_user_company.as_ref() != Some(company) {
                    return Err(anyhow!("只能为本公司员工创建计费记录"));
                }
            } else {
                return Err(anyhow!("用户管理员必须属于一个公司"));
            }
        }

        // 生成记录ID
        let record_id = format!("billing_{}", Utc::now().timestamp_millis());

        let record = sqlx::query_as::<_, BillingRecord>(
            "INSERT INTO billing_records (id, user_id, amount, billing_type, description, created_at)
             VALUES (?, ?, ?, ?, ?, datetime('now'))
             RETURNING id, user_id, amount, billing_type, description, created_at"
        )
        .bind(&record_id)
        .bind(&request.user_id)
        .bind(request.amount)
        .bind(&request.billing_type)
        .bind(&request.description)
        .fetch_one(&self.database.pool)
        .await?;

        tracing::info!("创建计费记录成功: {:?}", record);
        Ok(record)
    }

    // 获取价格规则列表
    pub async fn list_pricing_rules(&self, current_user: &UserInfo) -> Result<Vec<PricingRule>> {
        // 检查权限 - 系统管理员和用户管理员可以查看价格规则
        if current_user.role != "system_admin" && current_user.role != "user_admin" {
            return Err(anyhow!("权限不足"));
        }

        let rules = sqlx::query_as::<_, PricingRule>(
            "SELECT id, rule_name, billing_type, unit_price, is_active, created_at, updated_at
             FROM pricing_rules
             ORDER BY created_at DESC",
        )
        .fetch_all(&self.database.pool)
        .await?;

        Ok(rules)
    }

    // 创建价格规则
    pub async fn create_pricing_rule(
        &self,
        current_user: &UserInfo,
        request: CreatePricingRuleRequest,
    ) -> Result<PricingRule> {
        // 检查权限 - 只有系统管理员可以创建价格规则
        if current_user.role != "system_admin" {
            return Err(anyhow!("权限不足"));
        }

        let rule = sqlx::query_as::<_, PricingRule>(
            "INSERT INTO pricing_rules (rule_name, billing_type, unit_price, is_active, created_at, updated_at)
             VALUES (?, ?, ?, true, datetime('now'), datetime('now'))
             RETURNING id, rule_name, billing_type, unit_price, is_active, created_at, updated_at"
        )
        .bind(&request.rule_name)
        .bind(&request.billing_type)
        .bind(request.unit_price)
        .fetch_one(&self.database.pool)
        .await?;

        Ok(rule)
    }

    // 更新价格规则
    pub async fn update_pricing_rule(
        &self,
        current_user: &UserInfo,
        rule_id: i32,
        request: CreatePricingRuleRequest,
    ) -> Result<PricingRule> {
        // 检查权限 - 只有系统管理员可以更新价格规则
        if current_user.role != "system_admin" {
            return Err(anyhow!("权限不足"));
        }

        tracing::info!("更新价格规则 {} 数据: {:?}", rule_id, request);

        let rule = sqlx::query_as::<_, PricingRule>(
            "UPDATE pricing_rules
             SET rule_name = ?, billing_type = ?, unit_price = ?, updated_at = datetime('now')
             WHERE id = ?
             RETURNING id, rule_name, billing_type, unit_price, is_active, created_at, updated_at",
        )
        .bind(&request.rule_name)
        .bind(&request.billing_type)
        .bind(request.unit_price)
        .bind(rule_id)
        .fetch_one(&self.database.pool)
        .await?;

        tracing::info!("价格规则更新成功: {:?}", rule);
        Ok(rule)
    }

    // 删除价格规则
    pub async fn delete_pricing_rule(&self, current_user: &UserInfo, rule_id: i32) -> Result<()> {
        // 检查权限 - 只有系统管理员可以删除价格规则
        if current_user.role != "system_admin" {
            return Err(anyhow!("权限不足"));
        }

        sqlx::query(
            "UPDATE pricing_rules SET is_active = false, updated_at = datetime('now') WHERE id = ?",
        )
        .bind(rule_id)
        .execute(&self.database.pool)
        .await?;

        Ok(())
    }

    // 获取我的计费信息（用户管理员）
    pub async fn get_my_billing_info(&self, current_user: &UserInfo) -> Result<crate::models::MyBillingInfo> {
        // 只有用户管理员可以查看自己的计费信息
        if current_user.role != "user_admin" {
            return Err(anyhow!("权限不足：只有用户管理员可以查看计费信息"));
        }

        // 从数据库获取最新的用户信息（余额和员工数量）
        let current_balance: f64 = sqlx::query_scalar(
            "SELECT balance FROM users WHERE id = ?"
        )
        .bind(current_user.id)
        .fetch_one(&self.database.pool)
        .await
        .unwrap_or(0.0);

        // 计算当前员工数量（通过parent_id关联）
        let employee_count: i64 = sqlx::query_scalar(
            "SELECT COUNT(*) FROM users WHERE parent_id = ? AND role = 'employee'"
        )
        .bind(current_user.id)
        .fetch_one(&self.database.pool)
        .await
        .unwrap_or(0);

        // 计算总支出：查询该用户管理员的所有员工的计费记录总和
        let total_spent: f64 = if let Some(company) = &current_user.company {
            // 获取该公司所有员工的计费记录总和
            let employee_ids: Vec<String> = sqlx::query_scalar(
                "SELECT id FROM users WHERE parent_id = ? AND role = 'employee'"
            )
            .bind(current_user.id)
            .fetch_all(&self.database.pool)
            .await?
            .into_iter()
            .map(|id: i32| id.to_string())
            .collect();

            if employee_ids.is_empty() {
                0.0
            } else {
                let placeholders = employee_ids
                    .iter()
                    .map(|_| "?")
                    .collect::<Vec<_>>()
                    .join(",");
                
                let query_sql = format!(
                    "SELECT COALESCE(SUM(ABS(amount)), 0.0) FROM billing_records WHERE user_id IN ({})",
                    placeholders
                );

                let mut query = sqlx::query_scalar::<_, f64>(&query_sql);
                for employee_id in employee_ids {
                    query = query.bind(employee_id);
                }
                
                query.fetch_one(&self.database.pool).await.unwrap_or(0.0)
            }
        } else {
            0.0
        };

        // 获取默认月费（可以从配置或数据库获取）
        let monthly_fee = 300.0; // 默认值，实际可以从公司定价计划获取

        Ok(crate::models::MyBillingInfo {
            balance: current_balance,
            total_spent,
            employee_count: employee_count as i32,
            monthly_fee,
        })
    }

    // 获取指定用户的计费信息（系统管理员专用）
    pub async fn get_user_billing_info(&self, current_user: &UserInfo, target_user_id: i64) -> Result<crate::models::MyBillingInfo> {
        // 只有系统管理员可以查看其他用户的计费信息
        if current_user.role != "system_admin" {
            return Err(anyhow!("权限不足：只有系统管理员可以查看其他用户的计费信息"));
        }

        // 获取目标用户信息
        let target_user = sqlx::query_as::<_, UserInfo>(
            "SELECT * FROM users WHERE id = ? AND role = 'user_admin'"
        )
        .bind(target_user_id)
        .fetch_one(&self.database.pool)
        .await
        .map_err(|_| anyhow!("用户不存在或不是用户管理员"))?;

        // 计算总支出：查询该用户管理员的所有员工的计费记录总和
        let total_spent: f64 = if let Some(company) = &target_user.company {
            // 获取该公司所有员工的计费记录总和
            let employee_ids: Vec<String> = sqlx::query_scalar(
                "SELECT id FROM users WHERE parent_id = ? AND role = 'employee'"
            )
            .bind(target_user.id)
            .fetch_all(&self.database.pool)
            .await?
            .into_iter()
            .map(|id: i32| id.to_string())
            .collect();

            if employee_ids.is_empty() {
                0.0
            } else {
                let placeholders = employee_ids
                    .iter()
                    .map(|_| "?")
                    .collect::<Vec<_>>()
                    .join(",");
                
                let query_sql = format!(
                    "SELECT COALESCE(SUM(ABS(amount)), 0.0) FROM billing_records WHERE user_id IN ({})",
                    placeholders
                );

                let mut query = sqlx::query_scalar::<_, f64>(&query_sql);
                for employee_id in employee_ids {
                    query = query.bind(employee_id);
                }
                
                query.fetch_one(&self.database.pool).await.unwrap_or(0.0)
            }
        } else {
            0.0
        };

        // 获取默认月费（可以从配置或数据库获取）
        let monthly_fee = 300.0; // 默认值，实际可以从公司定价计划获取

        Ok(crate::models::MyBillingInfo {
            balance: target_user.balance,
            total_spent,
            employee_count: target_user.current_employees,
            monthly_fee,
        })
    }

    /// 创建员工时扣费
    pub async fn charge_for_employee_creation(
        &self,
        user_admin: &UserInfo,
        employee_info: &UserInfo,
    ) -> Result<()> {
        tracing::info!("开始为用户 {} 创建员工 {} 进行扣费", user_admin.username, employee_info.username);

        // 获取员工创建的价格规则
        let pricing_rule = sqlx::query_scalar::<_, f64>(
            "SELECT unit_price FROM pricing_rules WHERE billing_type = 'employee_creation' AND is_active = 1"
        )
        .fetch_optional(&self.database.pool)
        .await?;

        let employee_fee = pricing_rule.unwrap_or(300.0); // 默认300元

        // 检查用户余额是否足够
        if user_admin.balance < employee_fee {
            return Err(anyhow!("余额不足，当前余额: ¥{:.2}，需要: ¥{:.2}", user_admin.balance, employee_fee));
        }

        // 开始事务
        let mut tx = self.database.pool.begin().await?;

        // 扣减用户余额
        sqlx::query!(
            "UPDATE users SET balance = balance - ?, updated_at = datetime('now') WHERE id = ?",
            employee_fee,
            user_admin.id
        )
        .execute(&mut *tx)
        .await?;

        // 创建计费记录
        let negative_fee = -employee_fee; // 负数表示扣费
        let description = format!("创建员工: {}", employee_info.username);
        
        sqlx::query!(
            "INSERT INTO billing_records (user_id, amount, billing_type, description, created_at)
             VALUES (?, ?, 'employee_creation', ?, datetime('now'))",
            user_admin.id,
            negative_fee,
            description
        )
        .execute(&mut *tx)
        .await?;

        // 提交事务
        tx.commit().await?;

        tracing::info!(
            "员工创建扣费成功: 用户 {} 扣费 ¥{:.2}，创建员工 {}",
            user_admin.username,
            employee_fee,
            employee_info.username
        );

        Ok(())
    }
}
