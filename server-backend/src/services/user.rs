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
                if request.role != "employee" {
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

        // 检查用户名是否已存在
        let existing_user = sqlx::query_as::<_, User>("SELECT * FROM users WHERE username = ?")
            .bind(&request.username)
            .fetch_optional(&self.database.pool)
            .await?;

        if existing_user.is_some() {
            return Err(anyhow!("用户名已存在"));
        }

        // 检查邮箱是否已存在（如果提供了邮箱）
        if let Some(ref email) = request.email {
            let existing_email = sqlx::query_as::<_, User>("SELECT * FROM users WHERE email = ?")
                .bind(email)
                .fetch_optional(&self.database.pool)
                .await?;

            if existing_email.is_some() {
                return Err(anyhow!("邮箱已存在"));
            }
        }

        // 对密码进行哈希加密
        let hashed_password = bcrypt::hash(&request.password, bcrypt::DEFAULT_COST)
            .map_err(|e| anyhow!("密码加密失败: {}", e))?;

        // 设置父级用户ID（如果是员工）
        let parent_id = if request.role == "employee" && current_user.role == "user_admin" {
            Some(current_user.id)
        } else {
            None
        };

        // 设置公司信息（如果是员工，继承父级用户的公司）
        let company = if request.role == "employee" && current_user.role == "user_admin" {
            current_user.company.clone()
        } else {
            request.company
        };

        // 插入新用户
        let max_employees = request.max_employees.unwrap_or(0);
        let user_id = sqlx::query!(
            r#"
            INSERT INTO users (
                username, email, hashed_password, role, is_active, is_verified,
                parent_id, full_name, phone, company, max_employees, current_employees,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            "#,
            request.username,
            request.email,
            hashed_password,
            request.role,
            true,
            false,
            parent_id,
            request.full_name,
            request.phone,
            company,
            max_employees,
            0
        )
        .execute(&self.database.pool)
        .await?
        .last_insert_rowid();

        // 查询并返回创建的用户信息
        let user = sqlx::query_as::<_, User>("SELECT * FROM users WHERE id = ?")
            .bind(user_id)
            .fetch_one(&self.database.pool)
            .await?;

        Ok(user.into())
    }

    #[allow(unused_variables)]
    pub async fn get_user(&self, current_user: &UserInfo, user_id: &str) -> Result<UserInfo> {
        // TODO: 实现获取用户逻辑
        Err(anyhow!("功能待实现"))
    }

    #[allow(unused_variables)]
    pub async fn update_user(
        &self,
        current_user: &UserInfo,
        user_id: &str,
        request: CreateUserRequest,
    ) -> Result<UserInfo> {
        // TODO: 实现更新用户逻辑
        Err(anyhow!("功能待实现"))
    }

    #[allow(unused_variables)]
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
