// 设备管理模块 - ADB 设备连接和控制
use crate::{AppState, DeviceInfo};
use tauri::{AppHandle, State, Manager};
use std::process::Command;
use std::collections::HashMap;
use tokio::time::{sleep, Duration};

/// 连接指定设备
pub async fn connect_device(device_id: &str, state: &State<'_, AppState>) -> Result<String, String> {
    // 使用 ADB 连接设备
    let output = Command::new("adb")
        .args(&["connect", device_id])
        .output()
        .map_err(|e| format!("执行 ADB 命令失败: {}", e))?;

    let result = String::from_utf8_lossy(&output.stdout);
    
    if output.status.success() && result.contains("connected") {
        // 获取设备详细信息
        let device_info = get_device_info(device_id).await?;
        
        // 更新设备状态
        let mut devices = state.devices.write().await;
        devices.insert(device_id.to_string(), device_info);
        
        Ok(format!("设备 {} 连接成功", device_id))
    } else {
        Err(format!("设备连接失败: {}", result))
    }
}

/// 断开指定设备
pub async fn disconnect_device(device_id: &str, state: &State<'_, AppState>) -> Result<String, String> {
    let output = Command::new("adb")
        .args(&["disconnect", device_id])
        .output()
        .map_err(|e| format!("执行 ADB 命令失败: {}", e))?;

    let result = String::from_utf8_lossy(&output.stdout);
    
    if output.status.success() {
        // 移除设备状态
        let mut devices = state.devices.write().await;
        devices.remove(device_id);
        
        Ok(format!("设备 {} 已断开连接", device_id))
    } else {
        Err(format!("设备断开失败: {}", result))
    }
}

/// 获取设备详细信息
async fn get_device_info(device_id: &str) -> Result<DeviceInfo, String> {
    // 获取设备型号
    let model_output = Command::new("adb")
        .args(&["-s", device_id, "shell", "getprop", "ro.product.model"])
        .output()
        .map_err(|e| format!("获取设备型号失败: {}", e))?;

    let model = String::from_utf8_lossy(&model_output.stdout).trim().to_string();

    // 获取设备状态
    let status_output = Command::new("adb")
        .args(&["-s", device_id, "get-state"])
        .output()
        .map_err(|e| format!("获取设备状态失败: {}", e))?;

    let status = String::from_utf8_lossy(&status_output.stdout).trim().to_string();

    // 检查设备能力（是否支持 uiautomator2）
    let capabilities = check_device_capabilities(device_id).await?;

    Ok(DeviceInfo {
        id: device_id.to_string(),
        name: if model.is_empty() { format!("设备 {}", device_id) } else { model },
        status: if status == "device" { "已连接".to_string() } else { "离线".to_string() },
        last_seen: chrono::Utc::now(),
        capabilities,
    })
}

/// 检查设备支持的功能
async fn check_device_capabilities(device_id: &str) -> Result<Vec<String>, String> {
    let mut capabilities = Vec::new();

    // 检查是否支持 UI Automator
    let ui_output = Command::new("adb")
        .args(&["-s", device_id, "shell", "pm", "list", "packages", "com.github.uiautomator"])
        .output();

    if let Ok(output) = ui_output {
        if !output.stdout.is_empty() {
            capabilities.push("UI Automator".to_string());
        }
    }

    // 检查 Android 版本
    let version_output = Command::new("adb")
        .args(&["-s", device_id, "shell", "getprop", "ro.build.version.release"])
        .output();

    if let Ok(output) = version_output {
        let version = String::from_utf8_lossy(&output.stdout).trim();
        if !version.is_empty() {
            capabilities.push(format!("Android {}", version));
        }
    }

    // 检查屏幕分辨率
    let display_output = Command::new("adb")
        .args(&["-s", device_id, "shell", "wm", "size"])
        .output();

    if let Ok(output) = display_output {
        let display_info = String::from_utf8_lossy(&output.stdout);
        if let Some(size_line) = display_info.lines().find(|line| line.contains("Physical size:")) {
            if let Some(size) = size_line.split(':').nth(1) {
                capabilities.push(format!("屏幕: {}", size.trim()));
            }
        }
    }

    Ok(capabilities)
}

/// 扫描可用设备
async fn scan_devices() -> Result<Vec<String>, String> {
    let output = Command::new("adb")
        .args(&["devices"])
        .output()
        .map_err(|e| format!("扫描设备失败: {}", e))?;

    let result = String::from_utf8_lossy(&output.stdout);
    let mut devices = Vec::new();

    for line in result.lines().skip(1) { // 跳过标题行
        if !line.trim().is_empty() && line.contains("device") {
            if let Some(device_id) = line.split_whitespace().next() {
                devices.push(device_id.to_string());
            }
        }
    }

    Ok(devices)
}

/// 启动设备扫描器（后台任务）
pub async fn start_device_scanner(app_handle: AppHandle) {
    tokio::spawn(async move {
        loop {
            // 每 5 秒扫描一次设备
            sleep(Duration::from_secs(5)).await;

            match scan_devices().await {
                Ok(device_ids) => {
                    if let Some(state) = app_handle.try_state::<AppState>() {
                        let mut devices = state.devices.write().await;
                        let mut current_devices = HashMap::new();

                        for device_id in device_ids {
                            if devices.contains_key(&device_id) {
                                // 更新现有设备的最后检测时间
                                if let Some(device) = devices.get_mut(&device_id) {
                                    device.last_seen = chrono::Utc::now();
                                }
                                current_devices.insert(device_id.clone(), devices.get(&device_id).unwrap().clone());
                            } else {
                                // 发现新设备
                                if let Ok(device_info) = get_device_info(&device_id).await {
                                    current_devices.insert(device_id.clone(), device_info);
                                }
                            }
                        }

                        // 更新设备列表（移除不再连接的设备）
                        *devices = current_devices;

                        // 向前端发送设备更新事件
                        let _ = app_handle.emit_all("devices_updated", &*devices);
                    }
                }
                Err(e) => {
                    tracing::warn!("设备扫描失败: {}", e);
                }
            }
        }
    });
}
