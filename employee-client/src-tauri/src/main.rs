// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use tauri::{Manager, Emitter};
use tokio::time::{interval, Duration};

// 模块声明
mod models;
mod auth_models;
mod auth_service;
mod commands;

// 导入类型
use models::DeviceInfo;
use auth_service::{AuthService, AuthConfig};
use commands::gps::GpsService;
use commands::media::MediaService;

// 应用状态
pub struct AppState {
    pub devices: Arc<Mutex<HashMap<String, DeviceInfo>>>,    // 重用于GPS设备管理
    pub tasks: Arc<Mutex<HashMap<String, models::TaskInfo>>>, // 重用于拜访任务
    pub auth_service: Arc<AuthService>,
    pub gps_service: Arc<GpsService>,
    pub media_service: Arc<MediaService>,
}

// 设备扫描器（后台任务）
async fn start_device_scanner(app_handle: tauri::AppHandle) {
    let mut interval = interval(Duration::from_secs(5));

    loop {
        interval.tick().await;

        // 模拟设备扫描
        if let Some(state) = app_handle.try_state::<AppState>() {
            let mut devices = state.devices.lock().unwrap();

            // 添加一个模拟设备
            if devices.is_empty() {
                let device = DeviceInfo {
                    id: "emulator-5554".to_string(),
                    name: "Android Emulator".to_string(),
                    model: "SDK built for x86".to_string(),
                    android_version: "11".to_string(),
                    battery_level: Some(85),
                    screen_resolution: "1080x1920".to_string(),
                    manufacturer: "Google".to_string(),
                    status: "detected".to_string(),
                    last_seen: chrono::Utc::now(),
                };
                devices.insert("emulator-5554".to_string(), device);

                // 发送设备更新事件
                let _ = app_handle.emit("devices-updated", devices.values().cloned().collect::<Vec<_>>());
            }
        }
    }
}

// 主函数
fn main() {
    // 初始化日志
    tracing_subscriber::fmt::init();

    // 创建认证服务
    let auth_config = AuthConfig {
        server_url: "http://localhost:8000".to_string(),
        timeout_seconds: 30,
    };
    let auth_service = Arc::new(AuthService::new(Some(auth_config)));

    // 创建GPS服务
    let gps_service = Arc::new(GpsService::new());

    // 创建媒体服务
    let media_dir = std::env::current_dir()
        .unwrap_or_else(|_| std::path::PathBuf::from("."))
        .join("media");
    let media_service = Arc::new(MediaService::new(media_dir));

    let app_state = AppState {
        devices: Arc::new(Mutex::new(HashMap::new())),
        tasks: Arc::new(Mutex::new(HashMap::new())),
        auth_service,
        gps_service,
        media_service,
    };

    tauri::Builder::default()
        .manage(app_state)
        .setup(|app| {
            let app_handle = app.handle().clone();

            // 启动设备扫描器 - 使用 tauri::async_runtime::spawn 而不是 tokio::spawn
            tauri::async_runtime::spawn(async move {
                start_device_scanner(app_handle).await;
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            // 认证相关命令
            commands::login,
            commands::logout,
            commands::get_current_session,
            commands::is_logged_in,
            commands::get_current_user,
            commands::validate_token,
            commands::update_auth_config,
            // 基础命令
            commands::greet,
            commands::create_follow_task,
            commands::get_tasks,
            commands::start_task,
            commands::stop_task,
            commands::get_statistics,
            // GPS服务命令
            commands::get_current_location,
            commands::start_gps_tracking,
            commands::stop_gps_tracking,
            commands::calculate_distance,
            commands::get_gps_status,
            commands::request_gps_permission,
            // 拜访管理命令  
            commands::get_today_visits,
            commands::start_visit,
            commands::end_visit,
            commands::get_active_visit,
            commands::cancel_visit,
            commands::get_visit_attachments,
            // 多媒体录制命令
            commands::take_photo,
            commands::start_audio_recording,
            commands::stop_audio_recording,
            commands::start_video_recording,
            commands::stop_video_recording,
            commands::get_recording_status,
            commands::upload_media_file,
            commands::get_recording_config,
            commands::update_recording_config
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
