use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DeviceInfo {
    pub id: String,
    pub name: String,
    pub model: String,
    pub android_version: String,
    pub battery_level: Option<i32>,
    pub screen_resolution: String,
    pub manufacturer: String,
    pub status: String,
    pub last_seen: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct TaskInfo {
    pub id: String,
    pub device_id: String,
    pub task_type: String,
    pub status: String,
    pub progress: f64,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub config: serde_json::Value,
}
