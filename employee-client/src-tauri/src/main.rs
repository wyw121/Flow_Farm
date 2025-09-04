// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use tauri::{Manager, State};
use tokio::time::{interval, Duration};

mod models;

use models::*;

#[derive(Default)]
struct AppState {
    devices: Arc<Mutex<HashMap<String, DeviceInfo>>>,
    tasks: Arc<Mutex<HashMap<String, TaskInfo>>>,
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
async fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
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

    tauri::Builder::default()
        .manage(AppState::default())
        .setup(|app| {
            let app_handle = app.handle().clone();

            // 启动设备扫描器
            tokio::spawn(async move {
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
            get_statistics
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
