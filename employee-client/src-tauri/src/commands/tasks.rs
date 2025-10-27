use tauri::State;
use crate::AppState;
use crate::models::TaskInfo;

/// 获取任务列表
#[tauri::command]
pub async fn get_tasks(state: State<'_, AppState>) -> Result<Vec<TaskInfo>, String> {
    let tasks = state.tasks.lock().unwrap();
    Ok(tasks.values().cloned().collect())
}

/// 创建关注任务
#[tauri::command]
pub async fn create_follow_task(
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

/// 启动任务
#[tauri::command]
pub async fn start_task(task_id: String, state: State<'_, AppState>) -> Result<(), String> {
    let mut tasks = state.tasks.lock().unwrap();
    if let Some(task) = tasks.get_mut(&task_id) {
        task.status = "running".to_string();
        task.updated_at = chrono::Utc::now();
        Ok(())
    } else {
        Err("Task not found".to_string())
    }
}

/// 停止任务
#[tauri::command]
pub async fn stop_task(task_id: String, state: State<'_, AppState>) -> Result<(), String> {
    let mut tasks = state.tasks.lock().unwrap();
    if let Some(task) = tasks.get_mut(&task_id) {
        task.status = "stopped".to_string();
        task.updated_at = chrono::Utc::now();
        Ok(())
    } else {
        Err("Task not found".to_string())
    }
}

/// 获取统计信息
#[tauri::command]
pub async fn get_statistics(state: State<'_, AppState>) -> Result<serde_json::Value, String> {
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

/// 通用的问候命令（示例）
#[tauri::command]
pub async fn greet(name: &str) -> Result<String, String> {
    Ok(format!("Hello, {}! You've been greeted from Rust!", name))
}
