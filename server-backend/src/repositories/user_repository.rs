use crate::{models::{User, CreateUserRequest, UpdateUserRequest}, Database};
use anyhow::{anyhow, Result};

/// UserRepository: 负责所有用户相关的数据库操作
pub struct UserRepository {
    database: Database,
}

impl UserRepository {
    pub fn new(database: Database) -> Self {
        Self { database }
    }

    /// 根据ID查询用户
    pub async fn find_by_id(&self, id: &str) -> Result<Option<User>> {
        let user = sqlx::query_as::<_, User>("SELECT * FROM users WHERE id = ?")
            .bind(id)
            .fetch_optional(&self.database.pool)
            .await?;
        Ok(user)
    }

    /// 根据用户名查询用户
    pub async fn find_by_username(&self, username: &str) -> Result<Option<User>> {
        let user = sqlx::query_as::<_, User>("SELECT * FROM users WHERE username = ?")
            .bind(username)
            .fetch_optional(&self.database.pool)
            .await?;
        Ok(user)
    }

    /// 根据邮箱查询用户
    pub async fn find_by_email(&self, email: &str) -> Result<Option<User>> {
        let user = sqlx::query_as::<_, User>("SELECT * FROM users WHERE email = ?")
            .bind(email)
            .fetch_optional(&self.database.pool)
            .await?;
        Ok(user)
    }

    /// 根据手机号查询用户
    pub async fn find_by_phone(&self, phone: &str) -> Result<Option<User>> {
        let user = sqlx::query_as::<_, User>("SELECT * FROM users WHERE phone = ?")
            .bind(phone)
            .fetch_optional(&self.database.pool)
            .await?;
        Ok(user)
    }

    /// 分页查询用户列表
    pub async fn find_all_paginated(
        &self,
        company_filter: Option<&str>,
        role_filter: Option<&str>,
        page: i32,
        limit: i32,
    ) -> Result<Vec<User>> {
        let offset = (page - 1) * limit;
        let mut query = "SELECT * FROM users WHERE 1=1".to_string();
        let mut bind_values = Vec::new();

        // 公司过滤
        if let Some(company) = company_filter {
            query.push_str(" AND company = ?");
            bind_values.push(company.to_string());
        }

        // 角色过滤
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

        Ok(users)
    }

    /// 创建新用户
    pub async fn create(&self, request: &CreateUserRequest, hashed_password: &str, parent_id: Option<&str>) -> Result<User> {
        let id = uuid::Uuid::new_v4().to_string();
        let now = chrono::Utc::now();

        sqlx::query(
            r#"
            INSERT INTO users (
                id, username, password, role, email, phone, 
                full_name, company, parent_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            "#,
        )
        .bind(&id)
        .bind(&request.username)
        .bind(hashed_password)
        .bind(&request.role)
        .bind(&request.email)
        .bind(&request.phone)
        .bind(&request.full_name)
        .bind(&request.company)
        .bind(parent_id)
        .bind(&now)
        .bind(&now)
        .execute(&self.database.pool)
        .await?;

        // 返回新创建的用户
        self.find_by_id(&id)
            .await?
            .ok_or_else(|| anyhow!("用户创建失败"))
    }

    /// 更新用户信息
    pub async fn update(&self, id: &str, request: &UpdateUserRequest) -> Result<User> {
        let now = chrono::Utc::now();

        // 构建动态更新查询
        let mut query = "UPDATE users SET updated_at = ?".to_string();
        let mut bind_values: Vec<String> = vec![];

        if let Some(ref email) = request.email {
            query.push_str(", email = ?");
            bind_values.push(email.clone());
        }

        if let Some(ref phone) = request.phone {
            query.push_str(", phone = ?");
            bind_values.push(phone.clone());
        }

        if let Some(ref full_name) = request.full_name {
            query.push_str(", full_name = ?");
            bind_values.push(full_name.clone());
        }

        if let Some(ref company) = request.company {
            query.push_str(", company = ?");
            bind_values.push(company.clone());
        }

        if let Some(ref password) = request.password {
            let hashed_password = bcrypt::hash(password, bcrypt::DEFAULT_COST)
                .map_err(|e| anyhow!("密码加密失败: {}", e))?;
            query.push_str(", password = ?");
            bind_values.push(hashed_password);
        }

        query.push_str(" WHERE id = ?");

        let mut sql_query = sqlx::query(&query).bind(&now);

        for value in &bind_values {
            sql_query = sql_query.bind(value);
        }

        sql_query.bind(id).execute(&self.database.pool).await?;

        // 返回更新后的用户
        self.find_by_id(id)
            .await?
            .ok_or_else(|| anyhow!("用户不存在"))
    }

    /// 删除用户
    pub async fn delete(&self, id: &str) -> Result<()> {
        sqlx::query("DELETE FROM users WHERE id = ?")
            .bind(id)
            .execute(&self.database.pool)
            .await?;
        Ok(())
    }

    /// 统计用户数量
    pub async fn count_by_company(&self, company: &str) -> Result<i64> {
        let count: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM users WHERE company = ?")
            .bind(company)
            .fetch_one(&self.database.pool)
            .await?;
        Ok(count.0)
    }

    /// 统计特定角色的用户数量
    pub async fn count_by_parent_id(&self, parent_id: &str) -> Result<i64> {
        let count: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM users WHERE parent_id = ?")
            .bind(parent_id)
            .fetch_one(&self.database.pool)
            .await?;
        Ok(count.0)
    }

    /// 查询用户的所有子用户（直接下级）
    pub async fn find_children(&self, parent_id: &str) -> Result<Vec<User>> {
        let users = sqlx::query_as::<_, User>("SELECT * FROM users WHERE parent_id = ?")
            .bind(parent_id)
            .fetch_all(&self.database.pool)
            .await?;
        Ok(users)
    }

    /// 更新用户余额
    pub async fn update_balance(&self, id: &str, new_balance: f64) -> Result<()> {
        sqlx::query("UPDATE users SET balance = ?, updated_at = ? WHERE id = ?")
            .bind(new_balance)
            .bind(chrono::Utc::now())
            .bind(id)
            .execute(&self.database.pool)
            .await?;
        Ok(())
    }
}
