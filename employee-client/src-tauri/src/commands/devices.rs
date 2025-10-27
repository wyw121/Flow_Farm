use tauri::{State, Emitter};
use crate::AppState;
use crate::models::DeviceInfo;
use crate::adb_manager::AdbDevice;

/// 获取设备列表
#[tauri::command]
pub async fn get_devices(state: State<'_, AppState>) -> Result<Vec<DeviceInfo>, String> {
    let devices = state.devices.lock().unwrap();
    Ok(devices.values().cloned().collect())
}

/// 连接设备（简单状态更新）
#[tauri::command]
pub async fn connect_device(device_id: String, state: State<'_, AppState>) -> Result<DeviceInfo, String> {
    let mut devices = state.devices.lock().unwrap();

    if let Some(device) = devices.get_mut(&device_id) {
        device.status = "connected".to_string();
        Ok(device.clone())
    } else {
        Err("Device not found".to_string())
    }
}

/// 断开设备连接（简单状态更新）
#[tauri::command]
pub async fn disconnect_device(device_id: String, state: State<'_, AppState>) -> Result<(), String> {
    let mut devices = state.devices.lock().unwrap();

    if let Some(device) = devices.get_mut(&device_id) {
        device.status = "offline".to_string();
        Ok(())
    } else {
        Err("Device not found".to_string())
    }
}

/// 获取ADB设备列表
#[tauri::command]
pub async fn get_adb_devices(state: State<'_, AppState>) -> Result<Vec<AdbDevice>, String> {
    let adb_manager = &state.adb_manager;

    match adb_manager.get_devices().await {
        Ok(devices) => Ok(devices),
        Err(e) => Err(e.to_string())
    }
}

/// 连接ADB设备
#[tauri::command]
pub async fn connect_adb_device(
    device_id: String,
    state: State<'_, AppState>
) -> Result<AdbDevice, String> {
    let adb_manager = &state.adb_manager;

    match adb_manager.connect_device(&device_id).await {
        Ok(device) => {
            // 更新设备状态到应用状态中
            let mut devices = state.devices.lock().unwrap();
            let device_info = DeviceInfo {
                id: device.id.clone(),
                name: device.name.clone(),
                model: device.model.clone().unwrap_or_default(),
                android_version: device.android_version.clone().unwrap_or_default(),
                battery_level: device.battery_level,
                screen_resolution: device.screen_resolution.clone().unwrap_or_default(),
                manufacturer: device.manufacturer.clone().unwrap_or_default(),
                status: "connected".to_string(),
                last_seen: device.last_seen,
            };
            devices.insert(device.id.clone(), device_info);
            Ok(device)
        }
        Err(e) => Err(e.to_string())
    }
}

/// 断开ADB设备连接
#[tauri::command]
pub async fn disconnect_adb_device(
    device_id: String,
    state: State<'_, AppState>
) -> Result<(), String> {
    let adb_manager = &state.adb_manager;

    match adb_manager.disconnect_device(&device_id).await {
        Ok(_) => {
            // 从应用状态中移除设备
            let mut devices = state.devices.lock().unwrap();
            if let Some(device_info) = devices.get_mut(&device_id) {
                device_info.status = "disconnected".to_string();
            }
            Ok(())
        }
        Err(e) => Err(e.to_string())
    }
}

/// 检查ADB是否可用
#[tauri::command]
pub async fn check_adb_available(state: State<'_, AppState>) -> Result<bool, String> {
    let adb_manager = &state.adb_manager;

    match adb_manager.check_adb_available().await {
        Ok(available) => Ok(available),
        Err(e) => Err(e.to_string())
    }
}

/// 获取设备详细信息
#[tauri::command]
pub async fn get_device_info(
    device_id: String,
    state: State<'_, AppState>
) -> Result<Option<AdbDevice>, String> {
    let adb_manager = &state.adb_manager;

    match adb_manager.get_device_info(&device_id).await {
        Ok(device) => Ok(device),
        Err(e) => Err(e.to_string())
    }
}

/// 刷新设备列表
#[tauri::command]
pub async fn refresh_devices(
    state: State<'_, AppState>,
    app_handle: tauri::AppHandle
) -> Result<Vec<AdbDevice>, String> {
    let adb_manager = &state.adb_manager;

    match adb_manager.get_devices().await {
        Ok(devices) => {
            // 更新内部设备状态
            let mut app_devices = state.devices.lock().unwrap();
            app_devices.clear();

            for device in &devices {
                let device_info = DeviceInfo {
                    id: device.id.clone(),
                    name: device.name.clone(),
                    model: device.model.clone().unwrap_or_default(),
                    android_version: device.android_version.clone().unwrap_or_default(),
                    battery_level: device.battery_level,
                    screen_resolution: device.screen_resolution.clone().unwrap_or_default(),
                    manufacturer: device.manufacturer.clone().unwrap_or_default(),
                    status: if device.status == "device" { "available" } else { &device.status }.to_string(),
                    last_seen: device.last_seen,
                };
                app_devices.insert(device.id.clone(), device_info);
            }

            // 发送设备更新事件
            let _ = app_handle.emit("devices-updated", devices.clone());

            Ok(devices)
        }
        Err(e) => Err(e.to_string())
    }
}

/// 获取已连接的设备
#[tauri::command]
pub async fn get_connected_devices(state: State<'_, AppState>) -> Result<Vec<AdbDevice>, String> {
    let devices = state.devices.lock().unwrap();
    let connected_devices: Vec<AdbDevice> = devices
        .values()
        .filter(|device| device.status == "connected")
        .map(|device_info| AdbDevice {
            id: device_info.id.clone(),
            name: device_info.name.clone(),
            status: device_info.status.clone(),
            model: if device_info.model.is_empty() { None } else { Some(device_info.model.clone()) },
            android_version: if device_info.android_version.is_empty() { None } else { Some(device_info.android_version.clone()) },
            screen_resolution: if device_info.screen_resolution.is_empty() { None } else { Some(device_info.screen_resolution.clone()) },
            battery_level: device_info.battery_level,
            manufacturer: if device_info.manufacturer.is_empty() { None } else { Some(device_info.manufacturer.clone()) },
            last_seen: device_info.last_seen,
        })
        .collect();

    Ok(connected_devices)
}

/// 设置ADB路径
#[tauri::command]
pub async fn set_adb_path(
    adb_path: String,
    _state: State<'_, AppState>
) -> Result<bool, String> {
    // 测试指定的ADB路径是否有效
    match std::process::Command::new(&adb_path)
        .arg("version")
        .output()
    {
        Ok(output) => {
            if output.status.success() {
                // 创建新的AdbManager（注意：在实际应用中，您可能需要重新设计架构以支持动态更改）
                tracing::info!("用户设置的ADB路径有效: {}", adb_path);
                Ok(true)
            } else {
                let error_info = String::from_utf8_lossy(&output.stderr);
                Err(format!("ADB路径无效，命令执行失败: {}", error_info))
            }
        }
        Err(e) => {
            Err(format!("无法访问ADB路径 {}: {}", adb_path, e))
        }
    }
}

/// 查找ADB安装路径
#[tauri::command]
pub async fn find_adb_installations() -> Result<Vec<String>, String> {
    let mut found_paths = Vec::new();

    // 搜索常见的ADB安装路径
    let possible_paths = vec![
        // 雷电模拟器可能的路径
        r"D:\leidian\LDPlayer9\adb.exe",
        r"C:\leidian\LDPlayer9\adb.exe",
        r"D:\LDPlayer\LDPlayer4.0\adb.exe",
        r"C:\LDPlayer\LDPlayer4.0\adb.exe",

        // 夜神模拟器
        r"D:\Nox\bin\adb.exe",
        r"C:\Program Files (x86)\Nox\bin\adb.exe",

        // 逍遥模拟器
        r"D:\Microvirt\MEmu\adb.exe",
        r"C:\Program Files\Microvirt\MEmu\adb.exe",

        // Android SDK
        r"C:\Users\%USERNAME%\AppData\Local\Android\Sdk\platform-tools\adb.exe",
        r"D:\Android\sdk\platform-tools\adb.exe",
    ];

    for path in possible_paths {
        let expanded_path = shellexpand::env(path).unwrap_or_else(|_| path.into()).to_string();

        if std::path::Path::new(&expanded_path).exists() {
            // 测试ADB是否工作
            if let Ok(output) = std::process::Command::new(&expanded_path)
                .arg("version")
                .output()
            {
                if output.status.success() {
                    found_paths.push(expanded_path);
                }
            }
        }
    }

    Ok(found_paths)
}
