// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use tauri::{Manager, State, Emitter};
use tokio::time::{interval, Duration};

mod models;
mod contact_manager;
mod adb_manager;
mod xiaohongshu_automator;

use models::*;
use contact_manager::{ContactManager, ContactList};
use adb_manager::{AdbManager, AdbDevice};
use xiaohongshu_automator::{XiaohongshuAutomator, XiaohongshuConfig, AutomationTask, SearchResult};

struct AppState {
    devices: Arc<Mutex<HashMap<String, DeviceInfo>>>,
    tasks: Arc<Mutex<HashMap<String, TaskInfo>>>,
    contact_manager: Arc<ContactManager>,
    adb_manager: Arc<AdbManager>,
    xiaohongshu_automator: Arc<XiaohongshuAutomator>,
    automation_tasks: Arc<Mutex<HashMap<String, AutomationTask>>>,
    contact_lists: Arc<Mutex<HashMap<String, ContactList>>>,
}

#[tauri::command]
async fn get_devices(state: State<'_, AppState>) -> Result<Vec<DeviceInfo>, String> {
    let devices = state.devices.lock().unwrap();
    Ok(devices.values().cloned().collect())
}

#[tauri::command]
async fn get_tasks(state: State<'_, AppState>) -> Result<Vec<TaskInfo>, String> {
    let tasks = state.tasks.lock().unwrap();
    Ok(tasks.values().cloned().collect())
}

#[tauri::command]
async fn connect_device(device_id: String, state: State<'_, AppState>) -> Result<DeviceInfo, String> {
    let mut devices = state.devices.lock().unwrap();

    if let Some(device) = devices.get_mut(&device_id) {
        device.status = "connected".to_string();
        Ok(device.clone())
    } else {
        Err("Device not found".to_string())
    }
}

#[tauri::command]
async fn disconnect_device(device_id: String, state: State<'_, AppState>) -> Result<(), String> {
    let mut devices = state.devices.lock().unwrap();

    if let Some(device) = devices.get_mut(&device_id) {
        device.status = "offline".to_string();
        Ok(())
    } else {
        Err("Device not found".to_string())
    }
}

#[tauri::command]
async fn create_follow_task(
    device_id: String,
    contact_file: String,
    _options: serde_json::Value,
    state: State<'_, AppState>,
) -> Result<TaskInfo, String> {
    let task_id = uuid::Uuid::new_v4().to_string();

    let task = TaskInfo {
        id: task_id.clone(),
        device_id: device_id.clone(),
        task_type: "contact_follow".to_string(),
        status: "created".to_string(),
        progress: 0.0,
        created_at: chrono::Utc::now(),
        updated_at: chrono::Utc::now(),
        config: serde_json::json!({
            "contact_file": contact_file,
            "device_id": device_id
        }),
    };

    let mut tasks = state.tasks.lock().unwrap();
    tasks.insert(task_id, task.clone());

    Ok(task)
}

#[tauri::command]
async fn start_task(task_id: String, state: State<'_, AppState>) -> Result<(), String> {
    let mut tasks = state.tasks.lock().unwrap();
    if let Some(task) = tasks.get_mut(&task_id) {
        task.status = "running".to_string();
        task.updated_at = chrono::Utc::now();
        Ok(())
    } else {
        Err("Task not found".to_string())
    }
}

#[tauri::command]
async fn stop_task(task_id: String, state: State<'_, AppState>) -> Result<(), String> {
    let mut tasks = state.tasks.lock().unwrap();
    if let Some(task) = tasks.get_mut(&task_id) {
        task.status = "stopped".to_string();
        task.updated_at = chrono::Utc::now();
        Ok(())
    } else {
        Err("Task not found".to_string())
    }
}

#[tauri::command]
async fn get_statistics(state: State<'_, AppState>) -> Result<serde_json::Value, String> {
    let devices = state.devices.lock().unwrap();
    let tasks = state.tasks.lock().unwrap();

    let total_devices = devices.len();
    let online_devices = devices.values().filter(|d| d.status == "connected").count();
    let total_tasks = tasks.len();
    let running_tasks = tasks.values().filter(|t| t.status == "running").count();

    Ok(serde_json::json!({
        "total_devices": total_devices,
        "online_devices": online_devices,
        "total_tasks": total_tasks,
        "running_tasks": running_tasks,
        "today_follows": 0,
        "today_contacts": 0
    }))
}

#[tauri::command]
async fn greet(name: &str) -> Result<String, String> {
    Ok(format!("Hello, {}! You've been greeted from Rust!", name))
}

// ========== 通讯录管理命令 ==========

#[tauri::command]
async fn load_contacts_from_file(
    file_path: String,
    state: State<'_, AppState>
) -> Result<ContactList, String> {
    let contact_manager = &state.contact_manager;

    match contact_manager.load_contacts_from_txt(&file_path).await {
        Ok(contact_list) => {
            let list_id = contact_list.id.clone();
            let mut contact_lists = state.contact_lists.lock().unwrap();
            contact_lists.insert(list_id, contact_list.clone());
            Ok(contact_list)
        }
        Err(e) => Err(e.to_string())
    }
}

#[tauri::command]
async fn get_contact_lists(state: State<'_, AppState>) -> Result<Vec<ContactList>, String> {
    let contact_lists = state.contact_lists.lock().unwrap();
    Ok(contact_lists.values().cloned().collect())
}

#[tauri::command]
async fn search_contacts(
    list_id: String,
    keyword: String,
    state: State<'_, AppState>
) -> Result<Vec<crate::contact_manager::Contact>, String> {
    let contact_lists = state.contact_lists.lock().unwrap();

    if let Some(contact_list) = contact_lists.get(&list_id) {
        let contact_manager = &state.contact_manager;
        let results = contact_manager.search_contacts(&contact_list.contacts, &keyword);
        Ok(results)
    } else {
        Err("联系人列表不存在".to_string())
    }
}

// ========== ADB设备管理命令 ==========

#[tauri::command]
async fn get_adb_devices(state: State<'_, AppState>) -> Result<Vec<AdbDevice>, String> {
    let adb_manager = &state.adb_manager;

    match adb_manager.get_devices().await {
        Ok(devices) => Ok(devices),
        Err(e) => Err(e.to_string())
    }
}

#[tauri::command]
async fn connect_adb_device(
    device_id: String,
    state: State<'_, AppState>
) -> Result<AdbDevice, String> {
    let adb_manager = &state.adb_manager;

    match adb_manager.connect_device(&device_id).await {
        Ok(device) => Ok(device),
        Err(e) => Err(e.to_string())
    }
}

#[tauri::command]
async fn check_adb_available(state: State<'_, AppState>) -> Result<bool, String> {
    let adb_manager = &state.adb_manager;

    match adb_manager.check_adb_available().await {
        Ok(available) => Ok(available),
        Err(e) => Err(e.to_string())
    }
}

// ========== 小红书自动化命令 ==========

#[tauri::command]
async fn create_xiaohongshu_task(
    name: String,
    device_id: String,
    contact_list_id: String,
    config: XiaohongshuConfig,
    state: State<'_, AppState>
) -> Result<AutomationTask, String> {
    let contact_lists = state.contact_lists.lock().unwrap();

    if let Some(contact_list) = contact_lists.get(&contact_list_id) {
        let automator = &state.xiaohongshu_automator;
        let task = automator.create_task(name, device_id, contact_list.clone(), config);

        let task_id = task.id.clone();
        let mut automation_tasks = state.automation_tasks.lock().unwrap();
        automation_tasks.insert(task_id, task.clone());

        Ok(task)
    } else {
        Err("联系人列表不存在".to_string())
    }
}

#[tauri::command]
async fn start_xiaohongshu_task(
    task_id: String,
    state: State<'_, AppState>
) -> Result<(), String> {
    let mut automation_tasks = state.automation_tasks.lock().unwrap();

    if let Some(task) = automation_tasks.get(&task_id) {
        let task_clone = task.clone();
        drop(automation_tasks); // 释放锁

        let automator = state.xiaohongshu_automator.clone();
        let automation_tasks_clone = state.automation_tasks.clone();

        // 在后台运行任务
        tokio::spawn(async move {
            match automator.run_search_task(task_clone).await {
                Ok(completed_task) => {
                    let mut tasks = automation_tasks_clone.lock().unwrap();
                    tasks.insert(task_id, completed_task);
                }
                Err(e) => {
                    tracing::error!("Task execution failed: {}", e);
                    let mut tasks = automation_tasks_clone.lock().unwrap();
                    if let Some(task) = tasks.get_mut(&task_id) {
                        task.status = "failed".to_string();
                        task.updated_at = chrono::Utc::now();
                    }
                }
            }
        });

        Ok(())
    } else {
        Err("任务不存在".to_string())
    }
}

#[tauri::command]
async fn get_automation_tasks(state: State<'_, AppState>) -> Result<Vec<AutomationTask>, String> {
    let automation_tasks = state.automation_tasks.lock().unwrap();
    Ok(automation_tasks.values().cloned().collect())
}

#[tauri::command]
async fn get_task_results(
    task_id: String,
    state: State<'_, AppState>
) -> Result<Vec<SearchResult>, String> {
    let automation_tasks = state.automation_tasks.lock().unwrap();

    if let Some(task) = automation_tasks.get(&task_id) {
        Ok(task.results.clone())
    } else {
        Err("任务不存在".to_string())
    }
}

#[tauri::command]
async fn pause_xiaohongshu_task(
    task_id: String,
    state: State<'_, AppState>
) -> Result<(), String> {
    let task = {
        let mut automation_tasks = state.automation_tasks.lock().unwrap();
        automation_tasks.get_mut(&task_id).cloned()
    };

    if let Some(task) = task {
        let automator = &state.xiaohongshu_automator;
        match automator.pause_task(&task).await {
            Ok(updated_task) => {
                let mut automation_tasks = state.automation_tasks.lock().unwrap();
                automation_tasks.insert(task_id, updated_task);
                Ok(())
            }
            Err(e) => Err(e.to_string())
        }
    } else {
        Err("任务不存在".to_string())
    }
}

#[tauri::command]
async fn stop_xiaohongshu_task(
    task_id: String,
    state: State<'_, AppState>
) -> Result<(), String> {
    let task = {
        let mut automation_tasks = state.automation_tasks.lock().unwrap();
        automation_tasks.get_mut(&task_id).cloned()
    };

    if let Some(task) = task {
        let automator = &state.xiaohongshu_automator;
        match automator.stop_task(&task).await {
            Ok(updated_task) => {
                let mut automation_tasks = state.automation_tasks.lock().unwrap();
                automation_tasks.insert(task_id, updated_task);
                Ok(())
            }
            Err(e) => Err(e.to_string())
        }
    } else {
        Err("任务不存在".to_string())
    }
}

#[tauri::command]
async fn export_task_results(
    task_id: String,
    file_path: String,
    state: State<'_, AppState>
) -> Result<(), String> {
    let task = {
        let automation_tasks = state.automation_tasks.lock().unwrap();
        automation_tasks.get(&task_id).cloned()
    };

    if let Some(task) = task {
        let automator = &state.xiaohongshu_automator;
        match automator.export_results(&task, &file_path).await {
            Ok(_) => Ok(()),
            Err(e) => Err(e.to_string())
        }
    } else {
        Err("任务不存在".to_string())
    }
}

#[tauri::command]
async fn check_xiaohongshu_app(
    device_id: String,
    state: State<'_, AppState>
) -> Result<bool, String> {
    let automator = &state.xiaohongshu_automator;

    match automator.check_xiaohongshu_app(&device_id).await {
        Ok(available) => Ok(available),
        Err(e) => Err(e.to_string())
    }
}

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

fn main() {
    // 初始化日志
    tracing_subscriber::fmt::init();

    // 创建应用状态
    let adb_manager = Arc::new(AdbManager::new(None));
    let contact_manager = Arc::new(ContactManager::new());
    let xiaohongshu_automator = Arc::new(XiaohongshuAutomator::new((*adb_manager).clone()));

    let app_state = AppState {
        devices: Arc::new(Mutex::new(HashMap::new())),
        tasks: Arc::new(Mutex::new(HashMap::new())),
        contact_manager,
        adb_manager,
        xiaohongshu_automator,
        automation_tasks: Arc::new(Mutex::new(HashMap::new())),
        contact_lists: Arc::new(Mutex::new(HashMap::new())),
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
            greet,
            get_devices,
            connect_device,
            disconnect_device,
            create_follow_task,
            get_tasks,
            start_task,
            stop_task,
            get_statistics,
            // 通讯录管理命令
            load_contacts_from_file,
            get_contact_lists,
            search_contacts,
            // ADB设备管理命令
            get_adb_devices,
            connect_adb_device,
            check_adb_available,
            // 小红书自动化命令
            create_xiaohongshu_task,
            start_xiaohongshu_task,
            get_automation_tasks,
            get_task_results,
            pause_xiaohongshu_task,
            stop_xiaohongshu_task,
            export_task_results,
            check_xiaohongshu_app
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
