use tauri::State;
use crate::AppState;
use crate::xiaohongshu_automator::{AutomationTask, XiaohongshuConfig, SearchResult};

/// 创建小红书自动化任务
#[tauri::command]
pub async fn create_xiaohongshu_task(
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

/// 启动小红书自动化任务
#[tauri::command]
pub async fn start_xiaohongshu_task(
    task_id: String,
    state: State<'_, AppState>
) -> Result<(), String> {
    let automation_tasks = state.automation_tasks.lock().unwrap();

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

/// 获取所有自动化任务
#[tauri::command]
pub async fn get_automation_tasks(state: State<'_, AppState>) -> Result<Vec<AutomationTask>, String> {
    let automation_tasks = state.automation_tasks.lock().unwrap();
    Ok(automation_tasks.values().cloned().collect())
}

/// 获取任务结果
#[tauri::command]
pub async fn get_task_results(
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

/// 暂停小红书任务
#[tauri::command]
pub async fn pause_xiaohongshu_task(
    task_id: String,
    state: State<'_, AppState>
) -> Result<(), String> {
    let task = {
        let automation_tasks = state.automation_tasks.lock().unwrap();
        automation_tasks.get(&task_id).cloned()
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

/// 停止小红书任务
#[tauri::command]
pub async fn stop_xiaohongshu_task(
    task_id: String,
    state: State<'_, AppState>
) -> Result<(), String> {
    let task = {
        let automation_tasks = state.automation_tasks.lock().unwrap();
        automation_tasks.get(&task_id).cloned()
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

/// 导出任务结果
#[tauri::command]
pub async fn export_task_results(
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

/// 检查小红书APP是否可用
#[tauri::command]
pub async fn check_xiaohongshu_app(
    device_id: String,
    state: State<'_, AppState>
) -> Result<bool, String> {
    let automator = &state.xiaohongshu_automator;

    match automator.check_xiaohongshu_app(&device_id).await {
        Ok(available) => Ok(available),
        Err(e) => Err(e.to_string())
    }
}
