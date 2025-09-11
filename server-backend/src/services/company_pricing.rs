use anyhow::{anyhow, Result};
use crate::{
    database::Database,
    models::{
        CompanyPricingPlan, CompanyOperationPricing, 
        CreateCompanyPricingPlanRequest, UpdateCompanyPricingPlanRequest,
        CreateCompanyOperationPricingRequest, UpdateCompanyOperationPricingRequest,
        UserInfo
    },
};

#[derive(Clone)]
pub struct CompanyPricingService {
    database: Database,
}

impl CompanyPricingService {
    pub fn new(database: Database) -> Self {
        Self { database }
    }

    // 获取所有公司收费计划
    pub async fn list_company_pricing_plans(
        &self,
        current_user: &UserInfo,
    ) -> Result<Vec<CompanyPricingPlan>> {
        // 检查权限 - 只有系统管理员可以查看所有计划
        if current_user.role != "system_admin" {
            return Err(anyhow!("权限不足"));
        }

        let plans = sqlx::query_as::<_, CompanyPricingPlan>(
            "SELECT id, company_name, plan_name, employee_monthly_fee, is_active, created_at, updated_at
             FROM company_pricing_plans
             ORDER BY created_at DESC",
        )
        .fetch_all(&self.database.pool)
        .await?;

        Ok(plans)
    }

    // 根据公司名获取收费计划
    pub async fn get_company_pricing_plan(
        &self,
        current_user: &UserInfo,
        company_name: &str,
    ) -> Result<Option<CompanyPricingPlan>> {
        // 检查权限 - 系统管理员可以查看所有，用户管理员只能查看自己公司的
        if current_user.role == "user_admin" {
            if let Some(user_company) = &current_user.company {
                if user_company != company_name {
                    return Err(anyhow!("权限不足"));
                }
            } else {
                return Err(anyhow!("权限不足"));
            }
        } else if current_user.role != "system_admin" {
            return Err(anyhow!("权限不足"));
        }

        let plan = sqlx::query_as::<_, CompanyPricingPlan>(
            "SELECT id, company_name, plan_name, employee_monthly_fee, is_active, created_at, updated_at
             FROM company_pricing_plans
             WHERE company_name = ?",
        )
        .bind(company_name)
        .fetch_optional(&self.database.pool)
        .await?;

        Ok(plan)
    }

    // 创建公司收费计划
    pub async fn create_company_pricing_plan(
        &self,
        current_user: &UserInfo,
        request: CreateCompanyPricingPlanRequest,
    ) -> Result<CompanyPricingPlan> {
        // 检查权限 - 只有系统管理员可以创建
        if current_user.role != "system_admin" {
            return Err(anyhow!("权限不足"));
        }

        // 检查公司是否已存在收费计划
        let existing = sqlx::query_scalar::<_, i64>(
            "SELECT COUNT(*) FROM company_pricing_plans WHERE company_name = ?",
        )
        .bind(&request.company_name)
        .fetch_one(&self.database.pool)
        .await?;

        if existing > 0 {
            return Err(anyhow!("该公司已存在收费计划"));
        }

        let plan = sqlx::query_as::<_, CompanyPricingPlan>(
            "INSERT INTO company_pricing_plans (company_name, plan_name, employee_monthly_fee, is_active, created_at, updated_at)
             VALUES (?, ?, ?, true, datetime('now'), datetime('now'))
             RETURNING id, company_name, plan_name, employee_monthly_fee, is_active, created_at, updated_at"
        )
        .bind(&request.company_name)
        .bind(&request.plan_name)
        .bind(request.employee_monthly_fee)
        .fetch_one(&self.database.pool)
        .await?;

        tracing::info!("公司收费计划已创建: {}", request.company_name);
        Ok(plan)
    }

    // 更新公司收费计划
    pub async fn update_company_pricing_plan(
        &self,
        current_user: &UserInfo,
        plan_id: i32,
        request: UpdateCompanyPricingPlanRequest,
    ) -> Result<CompanyPricingPlan> {
        // 检查权限 - 只有系统管理员可以更新
        if current_user.role != "system_admin" {
            return Err(anyhow!("权限不足"));
        }

        // 构建动态更新SQL
        let mut set_parts = vec!["updated_at = datetime('now')"];
        let mut bind_values = vec![];

        if let Some(plan_name) = &request.plan_name {
            set_parts.push("plan_name = ?");
            bind_values.push(plan_name.clone());
        }

        if let Some(employee_monthly_fee) = request.employee_monthly_fee {
            set_parts.push("employee_monthly_fee = ?");
            bind_values.push(employee_monthly_fee.to_string());
        }

        if let Some(is_active) = request.is_active {
            set_parts.push("is_active = ?");
            bind_values.push(is_active.to_string());
        }

        let set_clause = set_parts.join(", ");
        let sql = format!(
            "UPDATE company_pricing_plans SET {} WHERE id = ? 
             RETURNING id, company_name, plan_name, employee_monthly_fee, is_active, created_at, updated_at",
            set_clause
        );

        let mut query = sqlx::query_as::<_, CompanyPricingPlan>(&sql);
        
        // 绑定动态参数
        for value in bind_values {
            query = query.bind(value);
        }
        query = query.bind(plan_id);

        let plan = query.fetch_one(&self.database.pool).await?;

        tracing::info!("公司收费计划已更新: ID {}", plan_id);
        Ok(plan)
    }

    // 删除公司收费计划
    pub async fn delete_company_pricing_plan(
        &self,
        current_user: &UserInfo,
        plan_id: i32,
    ) -> Result<()> {
        // 检查权限 - 只有系统管理员可以删除
        if current_user.role != "system_admin" {
            return Err(anyhow!("权限不足"));
        }

        let affected = sqlx::query("DELETE FROM company_pricing_plans WHERE id = ?")
            .bind(plan_id)
            .execute(&self.database.pool)
            .await?
            .rows_affected();

        if affected == 0 {
            return Err(anyhow!("收费计划不存在"));
        }

        tracing::info!("公司收费计划已删除: ID {}", plan_id);
        Ok(())
    }

    // 获取公司操作收费规则
    pub async fn list_company_operation_pricing(
        &self,
        current_user: &UserInfo,
        company_name: Option<&str>,
    ) -> Result<Vec<CompanyOperationPricing>> {
        // 检查权限
        let company_filter = match current_user.role.as_str() {
            "system_admin" => company_name.map(|s| s.to_string()),
            "user_admin" => {
                // 用户管理员只能查看自己公司的
                if let Some(user_company) = &current_user.company {
                    Some(user_company.clone())
                } else {
                    return Err(anyhow!("权限不足"));
                }
            }
            _ => return Err(anyhow!("权限不足")),
        };

        let pricing = if let Some(company) = company_filter {
            sqlx::query_as::<_, CompanyOperationPricing>(
                "SELECT id, company_name, platform, operation_type, unit_price, is_active, created_at, updated_at
                 FROM company_operation_pricing
                 WHERE company_name = ?
                 ORDER BY platform, operation_type",
            )
            .bind(&company)
            .fetch_all(&self.database.pool)
            .await?
        } else {
            sqlx::query_as::<_, CompanyOperationPricing>(
                "SELECT id, company_name, platform, operation_type, unit_price, is_active, created_at, updated_at
                 FROM company_operation_pricing
                 ORDER BY company_name, platform, operation_type",
            )
            .fetch_all(&self.database.pool)
            .await?
        };

        Ok(pricing)
    }

    // 创建公司操作收费规则
    pub async fn create_company_operation_pricing(
        &self,
        current_user: &UserInfo,
        request: CreateCompanyOperationPricingRequest,
    ) -> Result<CompanyOperationPricing> {
        // 检查权限 - 只有系统管理员可以创建
        if current_user.role != "system_admin" {
            return Err(anyhow!("权限不足"));
        }

        let pricing = sqlx::query_as::<_, CompanyOperationPricing>(
            "INSERT INTO company_operation_pricing (company_name, platform, operation_type, unit_price, is_active, created_at, updated_at)
             VALUES (?, ?, ?, ?, true, datetime('now'), datetime('now'))
             RETURNING id, company_name, platform, operation_type, unit_price, is_active, created_at, updated_at"
        )
        .bind(&request.company_name)
        .bind(&request.platform)
        .bind(&request.operation_type)
        .bind(request.unit_price)
        .fetch_one(&self.database.pool)
        .await?;

        tracing::info!("公司操作收费规则已创建: {} {} {}", 
                      request.company_name, request.platform, request.operation_type);
        Ok(pricing)
    }

    // 更新公司操作收费规则
    pub async fn update_company_operation_pricing(
        &self,
        current_user: &UserInfo,
        pricing_id: i32,
        request: UpdateCompanyOperationPricingRequest,
    ) -> Result<CompanyOperationPricing> {
        // 检查权限 - 只有系统管理员可以更新
        if current_user.role != "system_admin" {
            return Err(anyhow!("权限不足"));
        }

        // 构建动态更新SQL
        let mut set_parts = vec!["updated_at = datetime('now')"];
        let mut bind_values = vec![];

        if let Some(unit_price) = request.unit_price {
            set_parts.push("unit_price = ?");
            bind_values.push(unit_price.to_string());
        }

        if let Some(is_active) = request.is_active {
            set_parts.push("is_active = ?");
            bind_values.push(is_active.to_string());
        }

        let set_clause = set_parts.join(", ");
        let sql = format!(
            "UPDATE company_operation_pricing SET {} WHERE id = ?
             RETURNING id, company_name, platform, operation_type, unit_price, is_active, created_at, updated_at",
            set_clause
        );

        let mut query = sqlx::query_as::<_, CompanyOperationPricing>(&sql);
        
        // 绑定动态参数
        for value in bind_values {
            query = query.bind(value);
        }
        query = query.bind(pricing_id);

        let pricing = query.fetch_one(&self.database.pool).await?;

        tracing::info!("公司操作收费规则已更新: ID {}", pricing_id);
        Ok(pricing)
    }

    // 删除公司操作收费规则
    pub async fn delete_company_operation_pricing(
        &self,
        current_user: &UserInfo,
        pricing_id: i32,
    ) -> Result<()> {
        // 检查权限 - 只有系统管理员可以删除
        if current_user.role != "system_admin" {
            return Err(anyhow!("权限不足"));
        }

        let affected = sqlx::query("DELETE FROM company_operation_pricing WHERE id = ?")
            .bind(pricing_id)
            .execute(&self.database.pool)
            .await?
            .rows_affected();

        if affected == 0 {
            return Err(anyhow!("操作收费规则不存在"));
        }

        tracing::info!("公司操作收费规则已删除: ID {}", pricing_id);
        Ok(())
    }

    // 根据公司、平台和操作类型获取收费价格
    pub async fn get_operation_price(
        &self,
        company_name: &str,
        platform: &str,
        operation_type: &str,
    ) -> Result<f64> {
        let price = sqlx::query_scalar::<_, Option<f64>>(
            "SELECT unit_price FROM company_operation_pricing 
             WHERE company_name = ? AND platform = ? AND operation_type = ? AND is_active = true",
        )
        .bind(company_name)
        .bind(platform)
        .bind(operation_type)
        .fetch_one(&self.database.pool)
        .await?;

        match price {
            Some(p) => Ok(p),
            None => {
                // 如果公司没有特定定价，使用默认定价规则
                let default_price = sqlx::query_scalar::<_, Option<f64>>(
                    "SELECT unit_price FROM pricing_rules 
                     WHERE billing_type = ? AND is_active = true",
                )
                .bind(format!("{}_{}", platform, operation_type))
                .fetch_one(&self.database.pool)
                .await?;

                default_price.ok_or_else(|| anyhow!("未找到该操作的收费标准"))
            }
        }
    }

    // 获取公司员工月费
    pub async fn get_employee_monthly_fee(&self, company_name: &str) -> Result<f64> {
        let fee = sqlx::query_scalar::<_, Option<f64>>(
            "SELECT employee_monthly_fee FROM company_pricing_plans 
             WHERE company_name = ? AND is_active = true",
        )
        .bind(company_name)
        .fetch_one(&self.database.pool)
        .await?;

        match fee {
            Some(f) => Ok(f),
            None => Ok(50.0), // 默认员工月费
        }
    }
}
