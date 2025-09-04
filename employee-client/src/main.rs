// Flow Farm Employee Client - Rust Desktop GUI Application
// 基于 Tauri 框架的现代化桌面应用程序

#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use tauri::{Manager, State};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use tokio::sync::RwLock;

mod api;
mod device;
mod models;
mod utils;

use api::*;
use device::*;
use models::*;

// 应用程序状态管理
#[derive(Default)]
pub struct AppState {
    pub devices: Arc<RwLock<HashMap<String, DeviceInfo>>>,
    pub tasks: Arc<RwLock<HashMap<String, TaskInfo>>>,
    pub user_session: Arc<RwLock<Option<UserSession>>>,
    pub config: Arc<RwLock<AppConfig>>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DeviceInfo {
    pub id: String,
    pub name: String,
    pub status: String,
    pub last_seen: chrono::DateTime<chrono::Utc>,
    pub capabilities: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TaskInfo {
    pub id: String,
    pub name: String,
    pub status: String,
    pub progress: f64,
    pub device_id: Option<String>,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct UserSession {
    pub user_id: String,
    pub username: String,
    pub role: String,
    pub token: String,
    pub expires_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Serialize, Deserialize, Default)]
pub struct AppConfig {
    pub server_url: String,
    pub auto_connect_devices: bool,
    pub max_concurrent_tasks: u32,
    pub log_level: String,
}

// Tauri 命令函数
#[tauri::command]
async fn get_devices(state: State<'_, AppState>) -> Result<Vec<DeviceInfo>, String> {
    let devices = state.devices.read().await;
    Ok(devices.values().cloned().collect())
}

#[tauri::command]
async fn connect_device(device_id: String, state: State<'_, AppState>) -> Result<String, String> {
    device::connect_device(&device_id, &state).await
}

#[tauri::command]
async fn disconnect_device(device_id: String, state: State<'_, AppState>) -> Result<String, String> {
    device::disconnect_device(&device_id, &state).await
}

#[tauri::command]
async fn get_tasks(state: State<'_, AppState>) -> Result<Vec<TaskInfo>, String> {
    let tasks = state.tasks.read().await;
    Ok(tasks.values().cloned().collect())
}

#[tauri::command]
async fn create_follow_task(
    contact_file: String,
    devices: Vec<String>,
    state: State<'_, AppState>
) -> Result<String, String> {
    api::create_follow_task(contact_file, devices, &state).await
}

#[tauri::command]
async fn create_monitor_task(
    target_account: String,
    keywords: Vec<String>,
    target_count: u32,
    devices: Vec<String>,
    state: State<'_, AppState>
) -> Result<String, String> {
    api::create_monitor_task(target_account, keywords, target_count, devices, &state).await
}

#[tauri::command]
async fn get_statistics(state: State<'_, AppState>) -> Result<FollowStatistics, String> {
    api::get_statistics(&state).await
}

#[tauri::command]
async fn login(username: String, password: String, state: State<'_, AppState>) -> Result<UserSession, String> {
    api::login(username, password, &state).await
}

#[tauri::command]
async fn logout(state: State<'_, AppState>) -> Result<String, String> {
    api::logout(&state).await
}

fn main() {
    // 初始化日志
    tracing_subscriber::fmt::init();

    // 创建应用状态
    let app_state = AppState::default();

    tauri::Builder::default()
        .manage(app_state)
        .invoke_handler(tauri::generate_handler![
            get_devices,
            connect_device,
            disconnect_device,
            get_tasks,
            create_follow_task,
            create_monitor_task,
            get_statistics,
            login,
            logout
        ])
        .setup(|app| {
            // 应用程序启动时的初始化逻辑
            let app_handle = app.handle();
            
            // 启动设备扫描任务
            tokio::spawn(async move {
                device::start_device_scanner(app_handle).await;
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
