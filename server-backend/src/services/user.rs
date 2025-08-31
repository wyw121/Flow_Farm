use crate::{
    models::{CompanyStatistics, CreateUserRequest, User, UserInfo},
    Database,
};
use anyhow::{anyhow, Result};

pub struct UserService {
    database: Database,
}

impl UserService {
    pub fn new(database: Database) -> Self {
        Self { database }
    }

    pub async fn list_users(
        &self,
        current_user: &UserInfo,
        page: i32,
        limit: i32,
        role_filter: Option<&str>,
    ) -> Result<Vec<UserInfo>> {
        // 权限检查
        match current_user.role.as_str() {
            "system_admin" => {
                // 系统管理员可以查看所有用户
            }
            "user_admin" => {
                // 用户管理员只能查看自己公司的用户
            }
            "employee" => {
                return Err(anyhow!("权限不足"));
            }
            _ => {
                return Err(anyhow!("未知角色"));
            }
        }

        let offset = (page - 1) * limit;
        let mut query = "SELECT * FROM users WHERE 1=1".to_string();
        let mut bind_values = Vec::new();

        // 根据当前用户角色添加过滤条件
        if current_user.role == "user_admin" {
            query.push_str(" AND company = ?");
            bind_values.push(current_user.company.as_deref().unwrap_or("").to_string());
        }

        if let Some(role) = role_filter {
            query.push_str(" AND role = ?");
            bind_values.push(role.to_string());
        }

        query.push_str(" ORDER BY created_at DESC LIMIT ? OFFSET ?");

        let mut sql_query = sqlx::query_as::<_, User>(&query);

        for value in &bind_values {
            sql_query = sql_query.bind(value);
        }

        let users = sql_query
            .bind(limit)
            .bind(offset)
            .fetch_all(&self.database.pool)
            .await?;

        Ok(users.into_iter().map(|u| u.into()).collect())
    }

    pub async fn create_user(
        &self,
        current_user: &UserInfo,
        request: CreateUserRequest,
    ) -> Result<UserInfo> {
        // 权限检查
        match current_user.role.as_str() {
            "system_admin" => {
                // 系统管理员可以创建任何角色的用户
            }
            "user_admin" => {
                // 用户管理员只能创建员工
                if request.role.to_string() != "employee" {
                    return Err(anyhow!("权限不足：只能创建员工账户"));
                }
            }
            "employee" => {
                return Err(anyhow!("权限不足"));
            }
            _ => {
                return Err(anyhow!("未知角色"));
            }
        }

        // TODO: 实现用户创建逻辑
        Err(anyhow!("功能待实现"))
    }

    pub async fn get_user(&self, current_user: &UserInfo, user_id: &str) -> Result<UserInfo> {
        // TODO: 实现获取用户逻辑
        Err(anyhow!("功能待实现"))
    }

    pub async fn update_user(
        &self,
        current_user: &UserInfo,
        user_id: &str,
        request: CreateUserRequest,
    ) -> Result<UserInfo> {
        // TODO: 实现更新用户逻辑
        Err(anyhow!("功能待实现"))
    }

    pub async fn delete_user(&self, current_user: &UserInfo, user_id: &str) -> Result<()> {
        // TODO: 实现删除用户逻辑
        Err(anyhow!("功能待实现"))
    }

    pub async fn get_company_statistics(
        &self,
        current_user: &UserInfo,
    ) -> Result<Vec<CompanyStatistics>> {
        // 权限检查：只有系统管理员可以查看公司统计信息
        if current_user.role != "system_admin" {
            return Err(anyhow!("权限不足：只有系统管理员可以查看公司统计信息"));
        }

        // 查询所有用户管理员的公司统计信息
        let query = r#"
            SELECT
                COALESCE(u.company, '未命名公司') as company_name,
                u.id as user_admin_id,
                u.username as user_admin_name,
                COALESCE(u.current_employees, 0) as total_employees,
                0 as total_follows,
                0 as today_follows,
                0.0 as total_billing_amount,
                0.0 as unpaid_amount
            FROM users u
            WHERE u.role = 'user_admin'
            ORDER BY u.company, u.username
        "#;

        let statistics = sqlx::query_as::<_, CompanyStatistics>(query)
            .fetch_all(&self.database.pool)
            .await?;

        Ok(statistics)
    }
}
