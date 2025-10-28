use serde::{Deserialize, Serialize};
use tauri::State;
use std::sync::{Arc, Mutex};
use chrono::{DateTime, Utc};

/// GPS 坐标信息
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpsLocation {
    pub latitude: f64,
    pub longitude: f64,
    pub accuracy: f64,
    pub altitude: Option<f64>,
    pub speed: Option<f64>,
    pub heading: Option<f64>,
    pub timestamp: DateTime<Utc>,
}

/// GPS 状态
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpsStatus {
    pub enabled: bool,
    pub permissions_granted: bool,
    pub last_location: Option<GpsLocation>,
    pub error_message: Option<String>,
}

/// GPS 服务状态
pub struct GpsService {
    pub current_location: Arc<Mutex<Option<GpsLocation>>>,
    pub is_tracking: Arc<Mutex<bool>>,
    pub permissions_granted: Arc<Mutex<bool>>,
}

impl Default for GpsService {
    fn default() -> Self {
        Self {
            current_location: Arc::new(Mutex::new(None)),
            is_tracking: Arc::new(Mutex::new(false)),
            permissions_granted: Arc::new(Mutex::new(false)),
        }
    }
}

impl GpsService {
    pub fn new() -> Self {
        Self::default()
    }
}

/// 获取当前GPS状态
#[tauri::command]
pub async fn get_gps_status(
    gps_service: State<'_, GpsService>,
) -> Result<GpsStatus, String> {
    let current_location = gps_service.current_location.lock()
        .map_err(|e| format!("Failed to lock current_location: {}", e))?
        .clone();

    let is_tracking = *gps_service.is_tracking.lock()
        .map_err(|e| format!("Failed to lock is_tracking: {}", e))?;

    let permissions_granted = *gps_service.permissions_granted.lock()
        .map_err(|e| format!("Failed to lock permissions_granted: {}", e))?;

    Ok(GpsStatus {
        enabled: is_tracking,
        permissions_granted,
        last_location: current_location,
        error_message: None,
    })
}

/// 请求GPS权限
#[tauri::command]
pub async fn request_gps_permission(
    gps_service: State<'_, GpsService>,
) -> Result<bool, String> {
    // 在实际实现中，这里会调用系统的位置权限请求
    // 暂时模拟为已授权
    let mut permissions = gps_service.permissions_granted.lock()
        .map_err(|e| format!("Failed to lock permissions_granted: {}", e))?;
    
    *permissions = true;
    Ok(true)
}

/// 开始GPS定位
#[tauri::command]
pub async fn start_gps_tracking(
    gps_service: State<'_, GpsService>,
) -> Result<(), String> {
    // 检查权限
    let permissions_granted = *gps_service.permissions_granted.lock()
        .map_err(|e| format!("Failed to lock permissions_granted: {}", e))?;

    if !permissions_granted {
        return Err("GPS permissions not granted".to_string());
    }

    // 开始追踪
    {
        let mut is_tracking = gps_service.is_tracking.lock()
            .map_err(|e| format!("Failed to lock is_tracking: {}", e))?;
        
        *is_tracking = true;
    }

    // 在实际实现中，这里会启动一个后台任务来定期获取GPS位置
    // 暂时使用模拟数据
    simulate_gps_update(gps_service).await?;

    Ok(())
}

/// 停止GPS定位
#[tauri::command]
pub async fn stop_gps_tracking(
    gps_service: State<'_, GpsService>,
) -> Result<(), String> {
    let mut is_tracking = gps_service.is_tracking.lock()
        .map_err(|e| format!("Failed to lock is_tracking: {}", e))?;
    
    *is_tracking = false;
    Ok(())
}

/// 获取当前位置（单次获取）
#[tauri::command]
pub async fn get_current_location(
    gps_service: State<'_, GpsService>,
) -> Result<Option<GpsLocation>, String> {
    // 检查权限
    let permissions_granted = *gps_service.permissions_granted.lock()
        .map_err(|e| format!("Failed to lock permissions_granted: {}", e))?;

    if !permissions_granted {
        return Err("GPS permissions not granted".to_string());
    }

    // 模拟获取当前位置
    let location = simulate_get_location().await?;
    
    // 更新缓存的位置
    let mut current_location = gps_service.current_location.lock()
        .map_err(|e| format!("Failed to lock current_location: {}", e))?;
    *current_location = Some(location.clone());

    Ok(Some(location))
}

/// 计算两个GPS点之间的距离（米）
#[tauri::command]
pub async fn calculate_distance(
    lat1: f64, lon1: f64,
    lat2: f64, lon2: f64,
) -> Result<f64, String> {
    Ok(haversine_distance(lat1, lon1, lat2, lon2))
}

// 辅助函数：模拟GPS位置更新
async fn simulate_gps_update(gps_service: State<'_, GpsService>) -> Result<(), String> {
    let location = simulate_get_location().await?;
    
    let mut current_location = gps_service.current_location.lock()
        .map_err(|e| format!("Failed to lock current_location: {}", e))?;
    *current_location = Some(location);

    Ok(())
}

// 辅助函数：模拟获取GPS位置
async fn simulate_get_location() -> Result<GpsLocation, String> {
    // 在实际实现中，这里会调用系统的位置服务
    // 暂时返回北京的模拟坐标
    Ok(GpsLocation {
        latitude: 39.9042 + (rand::random::<f64>() - 0.5) * 0.01, // 北京坐标加随机偏移
        longitude: 116.4074 + (rand::random::<f64>() - 0.5) * 0.01,
        accuracy: 5.0 + rand::random::<f64>() * 10.0, // 5-15米精度
        altitude: Some(50.0 + rand::random::<f64>() * 20.0),
        speed: Some(rand::random::<f64>() * 5.0), // 0-5 m/s
        heading: Some(rand::random::<f64>() * 360.0),
        timestamp: Utc::now(),
    })
}

// Haversine公式计算两点间距离
fn haversine_distance(lat1: f64, lon1: f64, lat2: f64, lon2: f64) -> f64 {
    const R: f64 = 6371000.0; // 地球半径（米）

    let lat1_rad = lat1.to_radians();
    let lat2_rad = lat2.to_radians();
    let delta_lat = (lat2 - lat1).to_radians();
    let delta_lon = (lon2 - lon1).to_radians();

    let a = (delta_lat / 2.0).sin().powi(2)
        + lat1_rad.cos() * lat2_rad.cos() * (delta_lon / 2.0).sin().powi(2);
    let c = 2.0 * a.sqrt().atan2((1.0 - a).sqrt());

    R * c
}