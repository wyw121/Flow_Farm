use anyhow::{Result, anyhow};
use crate::{Database, models::{UserInfo, CreateUserRequest, User, UserRole}};

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
        match current_user.role {
            UserRole::SystemAdmin => {
                // 系统管理员可以查看所有用户
            }
            UserRole::UserAdmin => {
                // 用户管理员只能查看自己公司的用户
            }
            UserRole::Employee => {
                return Err(anyhow!("权限不足"));
            }
        }

        let offset = (page - 1) * limit;
        let mut query = "SELECT * FROM users WHERE 1=1".to_string();
        let mut bind_values = Vec::new();

        // 根据当前用户角色添加过滤条件
        if matches!(current_user.role, UserRole::UserAdmin) {
            query.push_str(" AND company_id = ?");
            bind_values.push(current_user.company_id.as_deref().unwrap_or("").to_string());
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
        match current_user.role {
            UserRole::SystemAdmin => {
                // 系统管理员可以创建任何角色的用户
            }
            UserRole::UserAdmin => {
                // 用户管理员只能创建员工
                if !matches!(request.role, UserRole::Employee) {
                    return Err(anyhow!("权限不足：只能创建员工账户"));
                }
            }
            UserRole::Employee => {
                return Err(anyhow!("权限不足"));
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
}
