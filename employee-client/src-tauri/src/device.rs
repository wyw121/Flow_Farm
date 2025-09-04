use crate::models::DeviceInfo;
use chrono::Utc;
use serde_json;
use std::process::Command;

#[derive(Debug)]
pub struct DeviceManager {
    adb_path: String,
}

impl DeviceManager {
    pub fn new() -> Self {
        Self {
            adb_path: "adb".to_string(), // Assume adb is in PATH
        }
    }

    pub fn set_adb_path(&mut self, path: String) {
        self.adb_path = path;
    }

    pub async fn discover_devices(&self) -> Result<Vec<DeviceInfo>, String> {
        let output = Command::new(&self.adb_path)
            .args(["devices", "-l"])
            .output()
            .map_err(|e| format!("Failed to run adb command: {}", e))?;

        if !output.status.success() {
            return Err(format!(
                "ADB command failed: {}",
                String::from_utf8_lossy(&output.stderr)
            ));
        }

        let output_str = String::from_utf8_lossy(&output.stdout);
        let mut devices = Vec::new();

        for line in output_str.lines().skip(1) {
            // Skip header line
            if line.trim().is_empty() || line.contains("offline") {
                continue;
            }

            if let Some(device_id) = line.split_whitespace().next() {
                if let Ok(device_info) = self.get_device_info(device_id).await {
                    devices.push(device_info);
                }
            }
        }

        Ok(devices)
    }

    pub async fn get_device_info(&self, device_id: &str) -> Result<DeviceInfo, String> {
        // Get device model
        let model = self
            .get_device_property(device_id, "ro.product.model")
            .await
            .unwrap_or_else(|_| "Unknown".to_string());

        // Get Android version
        let android_version = self
            .get_device_property(device_id, "ro.build.version.release")
            .await
            .unwrap_or_else(|_| "Unknown".to_string());

        // Get manufacturer
        let manufacturer = self
            .get_device_property(device_id, "ro.product.manufacturer")
            .await
            .unwrap_or_else(|_| "Unknown".to_string());

        // Get battery level
        let battery_level = self.get_battery_level(device_id).await.ok();

        // Get screen resolution
        let screen_resolution = self
            .get_screen_resolution(device_id)
            .await
            .unwrap_or_else(|_| "Unknown".to_string());

        Ok(DeviceInfo {
            id: device_id.to_string(),
            name: format!("{} {}", manufacturer, model),
            model,
            android_version,
            battery_level,
            screen_resolution,
            manufacturer,
            status: "connected".to_string(),
            last_seen: Utc::now(),
        })
    }

    async fn get_device_property(&self, device_id: &str, property: &str) -> Result<String, String> {
        let output = Command::new(&self.adb_path)
            .args(["-s", device_id, "shell", "getprop", property])
            .output()
            .map_err(|e| format!("Failed to get device property: {}", e))?;

        if output.status.success() {
            Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
        } else {
            Err("Failed to get property".to_string())
        }
    }

    async fn get_battery_level(&self, device_id: &str) -> Result<i32, String> {
        let output = Command::new(&self.adb_path)
            .args([
                "-s", device_id, "shell", "dumpsys", "battery", "|", "grep", "level",
            ])
            .output()
            .map_err(|e| format!("Failed to get battery level: {}", e))?;

        if output.status.success() {
            let output_str = String::from_utf8_lossy(&output.stdout);
            if let Some(line) = output_str.lines().find(|l| l.contains("level:")) {
                if let Some(level_str) = line.split(':').nth(1) {
                    return level_str
                        .trim()
                        .parse()
                        .map_err(|e| format!("Failed to parse battery level: {}", e));
                }
            }
        }

        Err("Failed to get battery level".to_string())
    }

    async fn get_screen_resolution(&self, device_id: &str) -> Result<String, String> {
        let output = Command::new(&self.adb_path)
            .args(["-s", device_id, "shell", "wm", "size"])
            .output()
            .map_err(|e| format!("Failed to get screen resolution: {}", e))?;

        if output.status.success() {
            let output_str = String::from_utf8_lossy(&output.stdout);
            if let Some(line) = output_str.lines().find(|l| l.contains("Physical size:")) {
                if let Some(resolution) = line.split(':').nth(1) {
                    return Ok(resolution.trim().to_string());
                }
            }
        }

        Err("Failed to get screen resolution".to_string())
    }

    pub async fn execute_command(&self, device_id: &str, command: &str) -> Result<String, String> {
        let output = Command::new(&self.adb_path)
            .args(["-s", device_id, "shell", command])
            .output()
            .map_err(|e| format!("Failed to execute command: {}", e))?;

        if output.status.success() {
            Ok(String::from_utf8_lossy(&output.stdout).to_string())
        } else {
            Err(format!(
                "Command execution failed: {}",
                String::from_utf8_lossy(&output.stderr)
            ))
        }
    }

    pub async fn install_app(&self, device_id: &str, apk_path: &str) -> Result<String, String> {
        let output = Command::new(&self.adb_path)
            .args(["-s", device_id, "install", apk_path])
            .output()
            .map_err(|e| format!("Failed to install app: {}", e))?;

        if output.status.success() {
            Ok("App installed successfully".to_string())
        } else {
            Err(format!(
                "App installation failed: {}",
                String::from_utf8_lossy(&output.stderr)
            ))
        }
    }
}
