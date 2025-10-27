use tauri::State;
use crate::AppState;
use crate::auth_models::{UserSession, UserInfo};
use crate::auth_service::AuthConfig;

/// 用户登录命令
#[tauri::command]
pub async fn login(
    username: String,
    password: String,
    state: State<'_, AppState>
) -> Result<UserSession, String> {
    tracing::info!("收到登录请求，用户名: {}", username);

    match state.auth_service.login(&username, &password).await {
        Ok(session) => {
            tracing::info!("用户 {} 登录成功", username);
            Ok(session)
        }
        Err(e) => {
            tracing::error!("登录失败: {}", e);
            Err(format!("登录失败: {}", e))
        }
    }
}

/// 用户登出命令
#[tauri::command]
pub async fn logout(state: State<'_, AppState>) -> Result<(), String> {
    state.auth_service.logout();
    Ok(())
}

/// 获取当前会话
#[tauri::command]
pub async fn get_current_session(state: State<'_, AppState>) -> Result<Option<UserSession>, String> {
    Ok(state.auth_service.get_current_session())
}

/// 检查是否已登录
#[tauri::command]
pub async fn is_logged_in(state: State<'_, AppState>) -> Result<bool, String> {
    Ok(state.auth_service.is_logged_in())
}

/// 获取当前用户信息
#[tauri::command]
pub async fn get_current_user(state: State<'_, AppState>) -> Result<Option<UserInfo>, String> {
    Ok(state.auth_service.get_current_user())
}

/// 验证Token
#[tauri::command]
pub async fn validate_token(token: String, state: State<'_, AppState>) -> Result<bool, String> {
    match state.auth_service.validate_token(&token).await {
        Ok(is_valid) => Ok(is_valid),
        Err(e) => {
            tracing::error!("Token验证失败: {}", e);
            Ok(false)
        }
    }
}

/// 更新认证配置
#[tauri::command]
pub async fn update_auth_config(
    server_url: String,
    timeout_seconds: u64,
    _state: State<'_, AppState>
) -> Result<(), String> {
    // 注意：这里需要获取可变引用，但Arc不支持
    // 实际使用中，可能需要重新设计架构或使用其他同步原语
    let config = AuthConfig {
        server_url,
        timeout_seconds,
    };

    // 这里我们记录配置更新，但实际实现可能需要重新创建AuthService
    tracing::info!("收到认证配置更新请求: {:?}", config);
    Ok(())
}
