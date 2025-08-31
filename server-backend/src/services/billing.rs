use crate::{
    models::{
        BillingRecord, CreateBillingRecordRequest, CreatePricingRuleRequest, PricingRule, UserInfo,
    },
    Database,
};
use anyhow::{anyhow, Result};

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
        Err(anyhow!("功能待实现"))
    }

    pub async fn create_billing_record(
        &self,
        current_user: &UserInfo,
        request: CreateBillingRecordRequest,
    ) -> Result<BillingRecord> {
        Err(anyhow!("功能待实现"))
    }

    // 获取价格规则列表
    pub async fn list_pricing_rules(&self, current_user: &UserInfo) -> Result<Vec<PricingRule>> {
        // 检查权限 - 只有系统管理员可以查看价格规则
        if current_user.role != "system_admin" {
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
}
