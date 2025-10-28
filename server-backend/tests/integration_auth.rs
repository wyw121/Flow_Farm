// API集成测试 - Authentication Flow
// 测试登录、注册、Token刷新等认证流程

mod test_helpers;

use axum::{
    body::Body,
    http::{Request, StatusCode},
};
use flow_farm_backend::models::{ApiResponse, CreateUserRequest, LoginRequest, LoginResponse};
use serde_json::json;
use tower::ServiceExt; // for `oneshot`

#[cfg(test)]
mod auth_integration_tests {
    use super::*;
    use test_helpers::*;

    #[tokio::test]
    async fn test_login_success() {
        // 创建测试数据库和配置
        let database = create_test_database().await;
        let config = create_test_config();

        // 插入测试用户（使用bcrypt加密密码）
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        // 创建登录请求
        let login_request = LoginRequest {
            username: "testuser".to_string(),
            password: "password123".to_string(),
        };

        // 注意：这里需要实际的HTTP服务器来测试
        // 由于我们使用的是Axum，需要创建完整的应用实例
        // 简化测试：直接测试Service层

        use flow_farm_backend::services::auth::AuthService;

        let auth_service = AuthService::new(database.clone(), config.clone());
        let result = auth_service
            .login(&login_request.username, &login_request.password)
            .await;

        assert!(result.is_ok(), "登录应该成功");
        let response = result.unwrap();
        assert!(!response.token.is_empty(), "Token不应为空");
        assert_eq!(response.user.username, "testuser", "用户名应该匹配");
        assert_eq!(response.user.role, "employee", "角色应该匹配");
    }

    #[tokio::test]
    async fn test_login_invalid_credentials() {
        let database = create_test_database().await;
        let config = create_test_config();

        // 插入测试用户
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        use flow_farm_backend::services::auth::AuthService;

        let auth_service = AuthService::new(database.clone(), config.clone());

        // 测试错误的密码
        let result = auth_service.login("testuser", "wrongpassword").await;
        assert!(result.is_err(), "错误的密码应该登录失败");

        // 测试不存在的用户
        let result = auth_service.login("nonexistent", "password123").await;
        assert!(result.is_err(), "不存在的用户应该登录失败");
    }

    #[tokio::test]
    async fn test_register_success() {
        let database = create_test_database().await;
        let config = create_test_config();

        let register_request = CreateUserRequest {
            username: "newuser".to_string(),
            email: Some("newuser@test.com".to_string()),
            password: "password123".to_string(),
            role: "employee".to_string(),
            phone: Some("13900139000".to_string()),
            full_name: Some("New User".to_string()),
            company: Some("Test Company".to_string()),
            max_employees: Some(10),
        };

        use flow_farm_backend::services::auth::AuthService;

        let auth_service = AuthService::new(database.clone(), config.clone());
        let result = auth_service.register(register_request).await;

        assert!(result.is_ok(), "注册应该成功");
        let user_info = result.unwrap();
        assert_eq!(user_info.username, "newuser", "用户名应该匹配");
        assert_eq!(user_info.role, "employee", "角色应该匹配");
    }

    #[tokio::test]
    async fn test_register_duplicate_username() {
        let database = create_test_database().await;
        let config = create_test_config();

        // 插入已存在的用户
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "existinguser", &password_hash, "employee")
            .await
            .unwrap();

        let register_request = CreateUserRequest {
            username: "existinguser".to_string(), // 重复的用户名
            email: Some("test@test.com".to_string()),
            password: "password123".to_string(),
            role: "employee".to_string(),
            phone: None,
            full_name: None,
            company: None,
            max_employees: None,
        };

        use flow_farm_backend::services::auth::AuthService;

        let auth_service = AuthService::new(database.clone(), config.clone());
        let result = auth_service.register(register_request).await;

        assert!(result.is_err(), "重复的用户名应该注册失败");
    }

    #[tokio::test]
    async fn test_token_refresh() {
        let database = create_test_database().await;
        let config = create_test_config();

        // 插入测试用户
        let password_hash = bcrypt::hash("password123", bcrypt::DEFAULT_COST).unwrap();
        insert_test_user(&database.pool, "user-1", "testuser", &password_hash, "employee")
            .await
            .unwrap();

        use flow_farm_backend::services::auth::AuthService;

        let auth_service = AuthService::new(database.clone(), config.clone());

        // 刷新Token
        let result = auth_service.refresh_token("user-1").await;

        assert!(result.is_ok(), "Token刷新应该成功");
        let new_token = result.unwrap();
        assert!(!new_token.is_empty(), "新Token不应为空");
    }

    #[tokio::test]
    async fn test_token_validation() {
        let config = create_test_config();

        // 生成Token
        let token = generate_test_token("user-1", "testuser", "employee");

        // 验证Token
        use flow_farm_backend::utils::jwt::decode_jwt_token;

        let result = decode_jwt_token(&token, &config.jwt_secret);
        assert!(result.is_ok(), "Token验证应该成功");

        let claims = result.unwrap();
        assert_eq!(claims.sub, "user-1", "用户ID应该匹配");
        assert_eq!(claims.role, "employee", "角色应该匹配");
    }

    #[tokio::test]
    async fn test_token_expiration() {
        // 创建一个过期时间很短的配置
        let config = create_test_config();
        let short_expire = 1; // 1秒后过期

        use flow_farm_backend::utils::jwt::create_jwt_token;

        let token = create_jwt_token("user-1", "employee", &config.jwt_secret, short_expire).unwrap();

        // 等待Token过期
        tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;

        // 验证过期的Token
        use flow_farm_backend::utils::jwt::verify_jwt_token;

        let result = verify_jwt_token(&token, &config.jwt_secret);
        assert!(result.is_err(), "过期的Token应该验证失败");
    }

    #[tokio::test]
    async fn test_invalid_token_format() {
        let config = create_test_config();

        use flow_farm_backend::utils::jwt::decode_jwt_token;

        // 测试无效的Token格式
        let invalid_tokens = vec![
            "invalid.token.format",
            "not-a-jwt-token",
            "",
            "Bearer invalid-token",
        ];

        for invalid_token in invalid_tokens {
            let result = decode_jwt_token(invalid_token, &config.jwt_secret);
            assert!(result.is_err(), "无效的Token格式应该验证失败: {}", invalid_token);
        }
    }
}
