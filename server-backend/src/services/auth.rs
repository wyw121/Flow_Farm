use anyhow::{Result, anyhow};
use uuid::Uuid;
use chrono::Utc;

use crate::{
    Database,
    Config,
    models::{CreateUserRequest, LoginResponse, UserInfo, User, UserRole},
    utils::jwt::create_jwt_token,
};

pub struct AuthService {
    database: Database,
    config: Config,
}

impl AuthService {
    pub fn new(database: Database, config: Config) -> Self {
        Self { database, config }
    }

    pub async fn login(&self, username: &str, password: &str) -> Result<LoginResponse> {
        // 查找用户
        let user = sqlx::query_as::<_, User>(
            "SELECT * FROM users WHERE username = ? AND is_active = true"
        )
        .bind(username)
        .fetch_optional(&self.database.pool)
        .await?
        .ok_or_else(|| anyhow!("用户不存在或已被禁用"))?;

        // 验证密码
        if !bcrypt::verify(password, &user.password_hash)? {
            return Err(anyhow!("密码错误"));
        }

        // 生成JWT token
        let token = create_jwt_token(&user.id, &user.role, &self.config.jwt_secret, self.config.jwt_expires_in)?;

        Ok(LoginResponse {
            token,
            user: user.into(),
        })
    }

    pub async fn register(&self, request: CreateUserRequest) -> Result<UserInfo> {
        // 检查用户名是否已存在
        let existing_user = sqlx::query("SELECT id FROM users WHERE username = ? OR email = ?")
            .bind(&request.username)
            .bind(&request.email)
            .fetch_optional(&self.database.pool)
            .await?;

        if existing_user.is_some() {
            return Err(anyhow!("用户名或邮箱已存在"));
        }

        // 生成密码哈希
        let password_hash = bcrypt::hash(&request.password, self.config.bcrypt_rounds)?;
        let user_id = Uuid::new_v4().to_string();
        let now = Utc::now();

        // 插入新用户
        sqlx::query(
            r#"
            INSERT INTO users (id, username, email, password_hash, role, company_id, is_active, max_employees, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            "#
        )
        .bind(&user_id)
        .bind(&request.username)
        .bind(&request.email)
        .bind(&password_hash)
        .bind(request.role.to_string())
        .bind(request.company_id.as_deref())
        .bind(true)
        .bind(request.max_employees)
        .bind(now)
        .bind(now)
        .execute(&self.database.pool)
        .await?;

        // 返回用户信息
        Ok(UserInfo {
            id: user_id,
            username: request.username,
            email: request.email,
            role: request.role,
            company_id: request.company_id,
            is_active: true,
            max_employees: request.max_employees,
        })
    }

    pub async fn refresh_token(&self, user_id: &str) -> Result<String> {
        // 查找用户
        let user = sqlx::query_as::<_, User>(
            "SELECT * FROM users WHERE id = ? AND is_active = true"
        )
        .bind(user_id)
        .fetch_optional(&self.database.pool)
        .await?
        .ok_or_else(|| anyhow!("用户不存在或已被禁用"))?;

        // 生成新的JWT token
        create_jwt_token(&user.id, &user.role, &self.config.jwt_secret, self.config.jwt_expires_in)
    }
}
