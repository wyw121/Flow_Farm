use anyhow::{Result, anyhow};
use crate::{Database, models::{UserInfo, Device, CreateDeviceRequest}};

pub struct DeviceService {
    database: Database,
}

impl DeviceService {
    pub fn new(database: Database) -> Self {
        Self { database }
    }

    pub async fn list_devices(&self, current_user: &UserInfo) -> Result<Vec<Device>> {
        Err(anyhow!("功能待实现"))
    }

    pub async fn create_device(&self, current_user: &UserInfo, request: CreateDeviceRequest) -> Result<Device> {
        Err(anyhow!("功能待实现"))
    }

    pub async fn get_device(&self, current_user: &UserInfo, device_id: &str) -> Result<Device> {
        Err(anyhow!("功能待实现"))
    }

    pub async fn update_device(&self, current_user: &UserInfo, device_id: &str, request: CreateDeviceRequest) -> Result<Device> {
        Err(anyhow!("功能待实现"))
    }

    pub async fn delete_device(&self, current_user: &UserInfo, device_id: &str) -> Result<()> {
        Err(anyhow!("功能待实现"))
    }
}
