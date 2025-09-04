// API 通信模块 - 与服务器后端通信
use crate::{AppState, UserSession, TaskInfo, FollowStatistics};
use tauri::State;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct FollowStatistics {
    pub total_follows: u32,
    pub daily_follows: u32,
    pub balance: f64,
    pub cost_per_follow: f64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LoginRequest {
    pub username: String,
    pub password: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LoginResponse {
    pub success: bool,
    pub user: Option<UserSession>,
    pub message: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TaskRequest {
    pub task_type: String,
    pub parameters: serde_json::Value,
    pub device_ids: Vec<String>,
}

/// 用户登录
pub async fn login(
    username: String,
    password: String,
    state: &State<'_, AppState>
) -> Result<UserSession, String> {
    let config = state.config.read().await;
    let client = reqwest::Client::new();
    
    let login_req = LoginRequest { username, password };
    
    let response = client
        .post(&format!("{}/api/auth/login", config.server_url))
        .json(&login_req)
        .send()
        .await
        .map_err(|e| format!("登录请求失败: {}", e))?;

    if response.status().is_success() {
        let login_resp: LoginResponse = response
            .json()
            .await
            .map_err(|e| format!("解析登录响应失败: {}", e))?;

        if login_resp.success {
            if let Some(user) = login_resp.user {
                // 保存用户会话
                let mut session = state.user_session.write().await;
                *session = Some(user.clone());
                Ok(user)
            } else {
                Err("登录响应中缺少用户信息".to_string())
            }
        } else {
            Err(login_resp.message)
        }
    } else {
        Err(format!("登录失败，状态码: {}", response.status()))
    }
}

/// 用户登出
pub async fn logout(state: &State<'_, AppState>) -> Result<String, String> {
    let mut session = state.user_session.write().await;
    *session = None;
    Ok("已成功登出".to_string())
}

/// 创建关注通讯录任务
pub async fn create_follow_task(
    contact_file: String,
    devices: Vec<String>,
    state: &State<'_, AppState>
) -> Result<String, String> {
    let config = state.config.read().await;
    let session = state.user_session.read().await;
    
    let user_session = session.as_ref()
        .ok_or("请先登录")?;

    let client = reqwest::Client::new();
    
    let task_params = serde_json::json!({
        "contact_file": contact_file,
        "task_type": "follow_contacts"
    });
    
    let task_req = TaskRequest {
        task_type: "follow_contacts".to_string(),
        parameters: task_params,
        device_ids: devices,
    };

    let response = client
        .post(&format!("{}/api/tasks", config.server_url))
        .header("Authorization", &format!("Bearer {}", user_session.token))
        .json(&task_req)
        .send()
        .await
        .map_err(|e| format!("创建任务失败: {}", e))?;

    if response.status().is_success() {
        let task_info: TaskInfo = response
            .json()
            .await
            .map_err(|e| format!("解析任务响应失败: {}", e))?;

        // 保存任务信息到状态
        let mut tasks = state.tasks.write().await;
        tasks.insert(task_info.id.clone(), task_info.clone());

        Ok(format!("已创建关注任务: {}", task_info.id))
    } else {
        Err(format!("创建任务失败，状态码: {}", response.status()))
    }
}

/// 创建同行监控任务
pub async fn create_monitor_task(
    target_account: String,
    keywords: Vec<String>,
    target_count: u32,
    devices: Vec<String>,
    state: &State<'_, AppState>
) -> Result<String, String> {
    let config = state.config.read().await;
    let session = state.user_session.read().await;
    
    let user_session = session.as_ref()
        .ok_or("请先登录")?;

    let client = reqwest::Client::new();
    
    let task_params = serde_json::json!({
        "target_account": target_account,
        "keywords": keywords,
        "target_count": target_count,
        "task_type": "monitor_competitor"
    });
    
    let task_req = TaskRequest {
        task_type: "monitor_competitor".to_string(),
        parameters: task_params,
        device_ids: devices,
    };

    let response = client
        .post(&format!("{}/api/tasks", config.server_url))
        .header("Authorization", &format!("Bearer {}", user_session.token))
        .json(&task_req)
        .send()
        .await
        .map_err(|e| format!("创建监控任务失败: {}", e))?;

    if response.status().is_success() {
        let task_info: TaskInfo = response
            .json()
            .await
            .map_err(|e| format!("解析任务响应失败: {}", e))?;

        // 保存任务信息到状态
        let mut tasks = state.tasks.write().await;
        tasks.insert(task_info.id.clone(), task_info.clone());

        Ok(format!("已创建监控任务: {}", task_info.id))
    } else {
        Err(format!("创建监控任务失败，状态码: {}", response.status()))
    }
}

/// 获取关注统计数据
pub async fn get_statistics(state: &State<'_, AppState>) -> Result<FollowStatistics, String> {
    let config = state.config.read().await;
    let session = state.user_session.read().await;
    
    let user_session = session.as_ref()
        .ok_or("请先登录")?;

    let client = reqwest::Client::new();

    let response = client
        .get(&format!("{}/api/statistics/follows", config.server_url))
        .header("Authorization", &format!("Bearer {}", user_session.token))
        .send()
        .await
        .map_err(|e| format!("获取统计数据失败: {}", e))?;

    if response.status().is_success() {
        let stats: FollowStatistics = response
            .json()
            .await
            .map_err(|e| format!("解析统计数据失败: {}", e))?;

        Ok(stats)
    } else {
        Err(format!("获取统计数据失败，状态码: {}", response.status()))
    }
}
