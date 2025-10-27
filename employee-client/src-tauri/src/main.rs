// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use tauri::{Manager, Emitter};
use tokio::time::{interval, Duration};

// 模块声明
mod models;
mod contact_manager;
mod adb_manager;
mod xiaohongshu_automator;
mod auth_models;
mod auth_service;
mod commands;

// 导入类型
use models::DeviceInfo;
use contact_manager::{ContactManager, ContactList};
use adb_manager::AdbManager;
use xiaohongshu_automator::{XiaohongshuAutomator, AutomationTask};
use auth_service::{AuthService, AuthConfig};

// 应用状态
pub struct AppState {
    pub devices: Arc<Mutex<HashMap<String, DeviceInfo>>>,
    pub tasks: Arc<Mutex<HashMap<String, models::TaskInfo>>>,
    pub contact_manager: Arc<ContactManager>,
    pub adb_manager: Arc<AdbManager>,
    pub xiaohongshu_automator: Arc<XiaohongshuAutomator>,
    pub automation_tasks: Arc<Mutex<HashMap<String, AutomationTask>>>,
    pub contact_lists: Arc<Mutex<HashMap<String, ContactList>>>,
    pub auth_service: Arc<AuthService>,
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

    // 创建应用状态
    // 手动指定雷电模拟器ADB路径
    let custom_adb_path = Some(r"D:\leidian\LDPlayer9\adb.exe".to_string());
    let adb_manager = Arc::new(AdbManager::new(custom_adb_path));
    let contact_manager = Arc::new(ContactManager::new());
    let xiaohongshu_automator = Arc::new(XiaohongshuAutomator::new((*adb_manager).clone()));

    // 创建认证服务
    let auth_config = AuthConfig {
        server_url: "http://localhost:8000".to_string(),
        timeout_seconds: 30,
    };
    let auth_service = Arc::new(AuthService::new(Some(auth_config)));

    let app_state = AppState {
        devices: Arc::new(Mutex::new(HashMap::new())),
        tasks: Arc::new(Mutex::new(HashMap::new())),
        contact_manager,
        adb_manager,
        xiaohongshu_automator,
        automation_tasks: Arc::new(Mutex::new(HashMap::new())),
        contact_lists: Arc::new(Mutex::new(HashMap::new())),
        auth_service,
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
            commands::get_devices,
            commands::connect_device,
            commands::disconnect_device,
            commands::create_follow_task,
            commands::get_tasks,
            commands::start_task,
            commands::stop_task,
            commands::get_statistics,
            // 通讯录管理命令
            commands::load_contacts_from_file,
            commands::get_contact_lists,
            commands::search_contacts,
            // ADB设备管理命令
            commands::get_adb_devices,
            commands::connect_adb_device,
            commands::disconnect_adb_device,
            commands::check_adb_available,
            commands::get_device_info,
            commands::refresh_devices,
            commands::get_connected_devices,
            commands::set_adb_path,
            commands::find_adb_installations,
            // 小红书自动化命令
            commands::create_xiaohongshu_task,
            commands::start_xiaohongshu_task,
            commands::get_automation_tasks,
            commands::get_task_results,
            commands::pause_xiaohongshu_task,
            commands::stop_xiaohongshu_task,
            commands::export_task_results,
            commands::check_xiaohongshu_app
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
