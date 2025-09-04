use std::sync::{Arc, Mutex};
use reqwest::Client;
use serde_json;

use crate::auth_models::*;

/// 认证服务配置
#[derive(Debug, Clone)]
pub struct AuthConfig {
    pub server_url: String,
    pub timeout_seconds: u64,
}

impl Default for AuthConfig {
    fn default() -> Self {
        Self {
            server_url: "http://localhost:8000".to_string(),
            timeout_seconds: 30,
        }
    }
}

/// 认证服务
pub struct AuthService {
    client: Client,
    config: AuthConfig,
    current_session: Arc<Mutex<Option<UserSession>>>,
}

impl AuthService {
    /// 创建新的认证服务实例
    pub fn new(config: Option<AuthConfig>) -> Self {
        let config = config.unwrap_or_default();
        let client = Client::builder()
            .timeout(std::time::Duration::from_secs(config.timeout_seconds))
            .build()
            .unwrap_or_default();

        Self {
            client,
            config,
            current_session: Arc::new(Mutex::new(None)),
        }
    }

    /// 用户登录
    pub async fn login(&self, username: &str, password: &str) -> Result<UserSession, AuthError> {
        let login_request = LoginRequest {
            username: username.to_string(),
            password: password.to_string(),
        };

        let url = format!("{}/api/v1/auth/login", self.config.server_url);

        tracing::info!("尝试登录用户: {}", username);
        tracing::debug!("登录请求URL: {}", url);

        let response = self
            .client
            .post(&url)
            .header("Content-Type", "application/json")
            .json(&login_request)
            .send()
            .await?;

        let status = response.status();
        let response_text = response.text().await?;

        tracing::debug!("服务器响应状态: {}", status);
        tracing::debug!("服务器响应内容: {}", response_text);

        if !status.is_success() {
            return Err(AuthError::ServerError(format!(
                "服务器返回错误状态: {} - {}",
                status, response_text
            )));
        }

        let api_response: ApiResponse<LoginResponse> = serde_json::from_str(&response_text)
            .map_err(|e| {
                tracing::error!("解析登录响应失败: {} - 原始响应: {}", e, response_text);
                AuthError::SerializationError(e)
            })?;

        if !api_response.success {
            return Err(AuthError::AuthenticationFailed(api_response.message));
        }

        let login_response = api_response
            .data
            .ok_or_else(|| AuthError::ServerError("服务器响应缺少数据".to_string()))?;

        let session = UserSession::new(login_response.token, login_response.user);

        // 保存当前会话
        {
            let mut current_session = self.current_session.lock().unwrap();
            *current_session = Some(session.clone());
        }

        tracing::info!("用户 {} 登录成功", username);
        Ok(session)
    }

    /// 获取当前会话
    pub fn get_current_session(&self) -> Option<UserSession> {
        let session = self.current_session.lock().unwrap();
        session.as_ref().and_then(|s| {
            if s.is_valid() {
                Some(s.clone())
            } else {
                None
            }
        })
    }

    /// 检查用户是否已登录且会话有效
    pub fn is_logged_in(&self) -> bool {
        self.get_current_session().is_some()
    }

    /// 用户登出
    pub fn logout(&self) {
        let mut current_session = self.current_session.lock().unwrap();
        *current_session = None;
        tracing::info!("用户已登出");
    }

    /// 验证token是否有效（可选：向服务器验证）
    pub async fn validate_token(&self, token: &str) -> Result<bool, AuthError> {
        let url = format!("{}/api/v1/auth/validate", self.config.server_url);

        let response = self
            .client
            .get(&url)
            .header("Authorization", format!("Bearer {}", token))
            .send()
            .await?;

        Ok(response.status().is_success())
    }

    /// 刷新当前会话（如果支持token刷新）
    pub async fn refresh_session(&self) -> Result<UserSession, AuthError> {
        let current_session = self.get_current_session()
            .ok_or_else(|| AuthError::AuthenticationFailed("没有活动会话".to_string()))?;

        // 这里可以实现token刷新逻辑
        // 目前简单地检查token是否仍然有效
        if self.validate_token(&current_session.token).await? {
            Ok(current_session)
        } else {
            self.logout();
            Err(AuthError::AuthenticationFailed("会话已过期".to_string()))
        }
    }

    /// 更新服务器配置
    pub fn update_config(&mut self, config: AuthConfig) {
        self.config = config;
        // 重新创建HTTP客户端
        self.client = Client::builder()
            .timeout(std::time::Duration::from_secs(self.config.timeout_seconds))
            .build()
            .unwrap_or_default();
    }

    /// 获取当前用户信息
    pub fn get_current_user(&self) -> Option<UserInfo> {
        self.get_current_session().map(|session| session.user)
    }

    /// 检查当前用户是否有指定角色
    pub fn has_role(&self, role: &str) -> bool {
        self.get_current_user()
            .map(|user| user.role == role)
            .unwrap_or(false)
    }

    /// 检查当前用户是否是员工角色
    pub fn is_employee(&self) -> bool {
        self.has_role("employee")
    }

    /// 检查当前用户是否是管理员角色
    pub fn is_admin(&self) -> bool {
        self.has_role("user_admin") || self.has_role("system_admin")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_auth_service_creation() {
        let auth_service = AuthService::new(None);
        assert!(!auth_service.is_logged_in());
    }

    #[test]
    fn test_user_session_expiration() {
        let user = UserInfo {
            id: 1,
            username: "test_user".to_string(),
            email: Some("test@example.com".to_string()),
            full_name: Some("Test User".to_string()),
            phone: None,
            company: None,
            role: "employee".to_string(),
            is_active: true,
            is_verified: true,
            current_employees: 0,
            max_employees: 0,
            parent_id: None,
            created_at: Utc::now().to_rfc3339(),
            last_login: None,
        };

        let session = UserSession::new("test_token".to_string(), user);
        assert!(session.is_valid());
        assert!(!session.is_expired());
    }
}
