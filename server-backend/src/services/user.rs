use crate::{
    models::{CompanyStatistics, CreateUserRequest, UpdateUserRequest, User, UserInfo},
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

    pub async fn update_user(
        &self,
        current_user: &UserInfo,
        user_id: &str,
        request: UpdateUserRequest,
    ) -> Result<UserInfo> {
        // 权限检查
        match current_user.role.as_str() {
            "system_admin" => {
                // 系统管理员可以更新任何用户
            }
            "user_admin" => {
                // 用户管理员只能更新自己公司的员工
                let user_id_int: i64 = user_id.parse().map_err(|_| anyhow!("无效的用户ID"))?;
                let target_user = sqlx::query_as::<_, User>("SELECT * FROM users WHERE id = ?")
                    .bind(user_id_int)
                    .fetch_optional(&self.database.pool)
                    .await?;

                if let Some(user) = target_user {
                    if user.role != "employee" || user.company != current_user.company {
                        return Err(anyhow!("权限不足：只能更新本公司的员工"));
                    }
                } else {
                    return Err(anyhow!("用户不存在"));
                }
            }
            "employee" => {
                return Err(anyhow!("权限不足"));
            }
            _ => {
                return Err(anyhow!("未知角色"));
            }
        }

        // 解析用户ID
        let user_id_int: i64 = user_id.parse().map_err(|_| anyhow!("无效的用户ID"))?;

        // 检查用户是否存在
        let mut user = sqlx::query_as::<_, User>("SELECT * FROM users WHERE id = ?")
            .bind(user_id_int)
            .fetch_optional(&self.database.pool)
            .await?
            .ok_or_else(|| anyhow!("用户不存在"))?;

        // 检查用户名唯一性（如果要更新用户名）
        if let Some(ref username) = request.username {
            if username != &user.username {
                let existing = sqlx::query_as::<_, User>("SELECT * FROM users WHERE username = ? AND id != ?")
                    .bind(username)
                    .bind(user_id_int)
                    .fetch_optional(&self.database.pool)
                    .await?;

                if existing.is_some() {
                    return Err(anyhow!("用户名已存在"));
                }
            }
        }

        // 构建更新SQL
        let mut set_clauses = Vec::new();
        let mut values: Vec<String> = Vec::new();

        if let Some(username) = request.username {
            set_clauses.push("username = ?");
            values.push(username);
        }

        if let Some(email) = request.email {
            set_clauses.push("email = ?");
            values.push(email);
        }

        if let Some(phone) = request.phone {
            set_clauses.push("phone = ?");
            values.push(phone);
        }

        if let Some(full_name) = request.full_name {
            set_clauses.push("full_name = ?");
            values.push(full_name);
        }

        if let Some(company) = request.company {
            set_clauses.push("company = ?");
            values.push(company);
        }

        if let Some(max_employees) = request.max_employees {
            set_clauses.push("max_employees = ?");
            values.push(max_employees.to_string());
        }

        if let Some(is_active) = request.is_active {
            set_clauses.push("is_active = ?");
            values.push(is_active.to_string());
        }

        // 处理密码更新（需要哈希）
        if let Some(password) = request.password {
            use bcrypt::{hash, DEFAULT_COST};
            let hashed_password = hash(password, DEFAULT_COST)?;
            set_clauses.push("hashed_password = ?");
            values.push(hashed_password);
        }

        if set_clauses.is_empty() {
            return Err(anyhow!("没有要更新的字段"));
        }

        // 添加更新时间
        set_clauses.push("updated_at = datetime('now')");

        let sql = format!(
            "UPDATE users SET {} WHERE id = ?",
            set_clauses.join(", ")
        );

        let mut query = sqlx::query(&sql);
        for value in values {
            query = query.bind(value);
        }
        query = query.bind(user_id_int);

        query.execute(&self.database.pool).await?;

        // 获取更新后的用户信息
        let updated_user = sqlx::query_as::<_, User>("SELECT * FROM users WHERE id = ?")
            .bind(user_id_int)
            .fetch_one(&self.database.pool)
            .await?;

        Ok(updated_user.into())
    }

    pub async fn delete_user(&self, current_user: &UserInfo, user_id: &str) -> Result<()> {
        // 权限检查
        match current_user.role.as_str() {
            "system_admin" => {
                // 系统管理员可以删除任何用户
            }
            "user_admin" => {
                // 用户管理员只能删除自己公司的员工
                let target_user = sqlx::query_as::<_, User>("SELECT * FROM users WHERE id = ?")
                    .bind(user_id)
                    .fetch_optional(&self.database.pool)
                    .await?;

                if let Some(user) = target_user {
                    // 检查是否是员工且属于同一公司
                    if user.role != "employee" || user.company != current_user.company {
                        return Err(anyhow!("权限不足：只能删除本公司的员工"));
                    }
                } else {
                    return Err(anyhow!("用户不存在"));
                }
            }
            "employee" => {
                return Err(anyhow!("权限不足"));
            }
            _ => {
                return Err(anyhow!("未知角色"));
            }
        }

        // 解析用户ID
        let user_id_int: i64 = user_id.parse().map_err(|_| anyhow!("无效的用户ID"))?;

        // 检查用户是否存在
        let user = sqlx::query_as::<_, User>("SELECT * FROM users WHERE id = ?")
            .bind(user_id_int)
            .fetch_optional(&self.database.pool)
            .await?;

        let user = user.ok_or_else(|| anyhow!("用户不存在"))?;

        // 如果是用户管理员，还需要更新其当前员工数量
        if user.role == "employee" && user.parent_id.is_some() {
            sqlx::query!(
                "UPDATE users SET current_employees = current_employees - 1 WHERE id = ?",
                user.parent_id
            )
            .execute(&self.database.pool)
            .await?;
        }

        // 删除相关的工作记录（级联删除）
        // 注意：work_records表中的字段是employee_id(INTEGER)
        sqlx::query!(
            "DELETE FROM work_records WHERE employee_id = ?",
            user_id_int
        )
        .execute(&self.database.pool)
        .await?;

        // 删除相关的计费记录（级联删除）
        // 注意：billing_records表中的user_id是TEXT类型
        sqlx::query!("DELETE FROM billing_records WHERE user_id = ?", user_id)
            .execute(&self.database.pool)
            .await?;

        // 删除相关的设备记录（级联删除）
        // 注意：devices表中的user_id是TEXT类型
        sqlx::query!("DELETE FROM devices WHERE user_id = ?", user_id)
            .execute(&self.database.pool)
            .await?;

        // 最后删除用户
        let result = sqlx::query!("DELETE FROM users WHERE id = ?", user_id_int)
            .execute(&self.database.pool)
            .await?;

        if result.rows_affected() == 0 {
            return Err(anyhow!("删除失败：用户不存在"));
        }

        tracing::info!("用户 {} 已被删除", user.username);
        Ok(())
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
