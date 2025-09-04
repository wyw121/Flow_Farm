use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::process::Command;
use std::time::Duration;
use tokio::time::sleep;
use tracing::{info, warn, error, debug};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AdbDevice {
    pub id: String,
    pub name: String,
    pub status: String, // online, offline, unauthorized, device
    pub model: Option<String>,
    pub android_version: Option<String>,
    pub screen_resolution: Option<String>,
    pub battery_level: Option<i32>,
    pub manufacturer: Option<String>,
    pub last_seen: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AdbCommand {
    pub device_id: String,
    pub command: String,
    pub args: Vec<String>,
    pub timeout: Option<u64>, // 超时时间(秒)
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AdbCommandResult {
    pub success: bool,
    pub output: String,
    pub error: Option<String>,
    pub exit_code: Option<i32>,
    pub duration_ms: u64,
}

#[derive(Clone)]
pub struct AdbManager {
    adb_path: String,
}

impl AdbManager {
    pub fn new(adb_path: Option<String>) -> Self {
        let adb_path = adb_path.unwrap_or_else(|| {
            info!("开始搜索ADB程序...");
            // 尝试查找系统中的ADB路径
            Self::find_adb_path().unwrap_or_else(|| {
                warn!("未找到ADB程序，使用默认命令'adb'");
                "adb".to_string()
            })
        });

        info!("ADB Manager initialized with path: {}", adb_path);
        Self { adb_path }
    }

    /// 尝试查找系统中的ADB路径
    fn find_adb_path() -> Option<String> {
        // 常见的ADB路径，包括模拟器内置的ADB
        let possible_paths = vec![
            // 系统默认路径
            "adb",
            "adb.exe",

            // Android SDK 标准路径
            r"C:\Users\%USERNAME%\AppData\Local\Android\Sdk\platform-tools\adb.exe",
            r"D:\Android\sdk\platform-tools\adb.exe",
            r"C:\Android\sdk\platform-tools\adb.exe",
            r"%ANDROID_HOME%\platform-tools\adb.exe",
            r"%ANDROID_SDK_ROOT%\platform-tools\adb.exe",

            // 雷电模拟器路径
            r"D:\leidian\LDPlayer9\adb.exe",
            r"C:\leidian\LDPlayer9\adb.exe",
            r"D:\LDPlayer\LDPlayer4.0\adb.exe",
            r"C:\LDPlayer\LDPlayer4.0\adb.exe",

            // 夜神模拟器路径
            r"D:\Nox\bin\adb.exe",
            r"C:\Program Files (x86)\Nox\bin\adb.exe",
            r"D:\Program Files\Nox\bin\adb.exe",

            // 逍遥模拟器路径
            r"D:\Microvirt\MEmu\adb.exe",
            r"C:\Program Files\Microvirt\MEmu\adb.exe",
            r"D:\Program Files (x86)\Microvirt\MEmu\adb.exe",

            // BlueStacks 模拟器路径
            r"C:\Program Files\BlueStacks\HD-Adb.exe",
            r"C:\Program Files (x86)\BlueStacks\HD-Adb.exe",

            // MuMu模拟器路径
            r"D:\Program Files\Netease\MuMu\emulator\nemu\vbox\adb.exe",
            r"C:\Program Files\Netease\MuMu\emulator\nemu\vbox\adb.exe",
        ];

        for path in possible_paths {
            // 扩展环境变量
            let expanded_path = if path.contains('%') {
                // 处理环境变量
                let expanded = shellexpand::env(path).unwrap_or_else(|_| path.into());
                expanded.to_string()
            } else {
                path.to_string()
            };

            debug!("正在测试ADB路径: {}", expanded_path);

            // 测试ADB是否可用
            if let Ok(output) = Command::new(&expanded_path)
                .arg("version")
                .output()
            {
                if output.status.success() {
                    info!("Found ADB at: {}", expanded_path);
                    return Some(expanded_path);
                } else {
                    debug!("ADB测试失败: {} (退出码: {:?})", expanded_path, output.status.code());
                }
            } else {
                debug!("无法执行ADB命令: {}", expanded_path);
            }
        }

        warn!("No ADB installation found in common paths");
        None
    }

    /// 检查ADB是否可用
    pub async fn check_adb_available(&self) -> Result<bool> {
        debug!("Checking ADB availability");

        match Command::new(&self.adb_path)
            .arg("version")
            .output()
        {
            Ok(output) => {
                if output.status.success() {
                    let version_info = String::from_utf8_lossy(&output.stdout);
                    info!("ADB available: {}", version_info.lines().next().unwrap_or(""));
                    Ok(true)
                } else {
                    let error_info = String::from_utf8_lossy(&output.stderr);
                    error!("ADB command failed: {}", error_info);
                    Ok(false)
                }
            }
            Err(e) => {
                error!("Failed to execute ADB command: {}", e);
                Ok(false)
            }
        }
    }

    /// 获取连接的设备列表
    pub async fn get_devices(&self) -> Result<Vec<AdbDevice>> {
        debug!("Getting ADB devices list");

        let output = Command::new(&self.adb_path)
            .arg("devices")
            .arg("-l") // 显示详细信息
            .output()
            .context("Failed to execute adb devices command")?;

        if !output.status.success() {
            let error_msg = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow::anyhow!("ADB devices command failed: {}", error_msg));
        }

        let output_str = String::from_utf8_lossy(&output.stdout);
        let mut devices = Vec::new();

        for line in output_str.lines().skip(1) { // 跳过第一行 "List of devices attached"
            let line = line.trim();
            if line.is_empty() {
                continue;
            }

            if let Some(device) = self.parse_device_line(line) {
                devices.push(device);
            }
        }

        info!("Found {} ADB devices", devices.len());
        Ok(devices)
    }

    /// 解析设备信息行
    fn parse_device_line(&self, line: &str) -> Option<AdbDevice> {
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() < 2 {
            return None;
        }

        let device_id = parts[0].to_string();
        let status = parts[1].to_string();

        // 解析额外信息
        let mut model = None;
        let mut manufacturer = None;

        for part in parts.iter().skip(2) {
            if part.starts_with("model:") {
                model = Some(part.strip_prefix("model:").unwrap_or("").to_string());
            } else if part.starts_with("device:") {
                manufacturer = Some(part.strip_prefix("device:").unwrap_or("").to_string());
            }
        }

        Some(AdbDevice {
            id: device_id.clone(),
            name: format!("Android Device {}", device_id),
            status,
            model,
            android_version: None, // 需要单独查询
            screen_resolution: None, // 需要单独查询
            battery_level: None, // 需要单独查询
            manufacturer,
            last_seen: chrono::Utc::now(),
        })
    }

    /// 连接到指定设备
    pub async fn connect_device(&self, device_id: &str) -> Result<AdbDevice> {
        info!("Connecting to device: {}", device_id);

        // 首先检查设备是否存在
        let devices = self.get_devices().await?;
        let device = devices.iter()
            .find(|d| d.id == device_id)
            .ok_or_else(|| anyhow::anyhow!("Device not found: {}", device_id))?;

        if device.status != "device" {
            return Err(anyhow::anyhow!("Device {} is not ready (status: {})", device_id, device.status));
        }

        // 获取详细信息
        let mut connected_device = device.clone();

        // 获取Android版本
        if let Ok(android_version) = self.get_device_property(device_id, "ro.build.version.release").await {
            connected_device.android_version = Some(android_version);
        }

        // 获取屏幕分辨率
        if let Ok(resolution) = self.get_screen_resolution(device_id).await {
            connected_device.screen_resolution = Some(resolution);
        }

        // 获取电池电量
        if let Ok(battery) = self.get_battery_level(device_id).await {
            connected_device.battery_level = Some(battery);
        }

        // 获取制造商
        if let Ok(manufacturer) = self.get_device_property(device_id, "ro.product.manufacturer").await {
            connected_device.manufacturer = Some(manufacturer);
        }

        // 获取型号
        if let Ok(model) = self.get_device_property(device_id, "ro.product.model").await {
            connected_device.model = Some(model);
        }

        info!("Successfully connected to device: {}", device_id);
        Ok(connected_device)
    }

    /// 获取设备属性
    async fn get_device_property(&self, device_id: &str, property: &str) -> Result<String> {
        let output = Command::new(&self.adb_path)
            .arg("-s")
            .arg(device_id)
            .arg("shell")
            .arg("getprop")
            .arg(property)
            .output()
            .context("Failed to get device property")?;

        if output.status.success() {
            Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
        } else {
            Err(anyhow::anyhow!("Failed to get property: {}", property))
        }
    }

    /// 获取屏幕分辨率
    async fn get_screen_resolution(&self, device_id: &str) -> Result<String> {
        let output = Command::new(&self.adb_path)
            .arg("-s")
            .arg(device_id)
            .arg("shell")
            .arg("wm")
            .arg("size")
            .output()
            .context("Failed to get screen resolution")?;

        if output.status.success() {
            let output_str = String::from_utf8_lossy(&output.stdout);
            // 解析输出如: "Physical size: 1080x1920"
            if let Some(line) = output_str.lines().find(|line| line.contains("Physical size")) {
                if let Some(resolution) = line.split(':').nth(1) {
                    return Ok(resolution.trim().to_string());
                }
            }
        }

        Err(anyhow::anyhow!("Failed to get screen resolution"))
    }

    /// 获取电池电量
    async fn get_battery_level(&self, device_id: &str) -> Result<i32> {
        let output = Command::new(&self.adb_path)
            .arg("-s")
            .arg(device_id)
            .arg("shell")
            .arg("dumpsys")
            .arg("battery")
            .arg("|")
            .arg("grep")
            .arg("level")
            .output()
            .context("Failed to get battery level")?;

        if output.status.success() {
            let output_str = String::from_utf8_lossy(&output.stdout);
            for line in output_str.lines() {
                if line.contains("level:") {
                    if let Some(level_str) = line.split(':').nth(1) {
                        if let Ok(level) = level_str.trim().parse::<i32>() {
                            return Ok(level);
                        }
                    }
                }
            }
        }

        Err(anyhow::anyhow!("Failed to get battery level"))
    }

    /// 执行ADB命令
    pub async fn execute_command(&self, cmd: AdbCommand) -> Result<AdbCommandResult> {
        let start_time = std::time::Instant::now();
        debug!("Executing ADB command: {} {:?}", cmd.command, cmd.args);

        let mut command = Command::new(&self.adb_path);
        command
            .arg("-s")
            .arg(&cmd.device_id)
            .arg(&cmd.command);

        for arg in &cmd.args {
            command.arg(arg);
        }

        let output = if let Some(timeout) = cmd.timeout {
            // 使用超时执行
            tokio::time::timeout(
                Duration::from_secs(timeout),
                tokio::task::spawn_blocking(move || command.output())
            )
            .await
            .context("Command timeout")?
            .context("Failed to execute command")?
        } else {
            // 没有超时限制
            tokio::task::spawn_blocking(move || command.output())
                .await
                .context("Failed to execute command")?
        };

        let duration = start_time.elapsed();

        match output {
            Ok(output) => {
                let success = output.status.success();
                let stdout = String::from_utf8_lossy(&output.stdout).to_string();
                let stderr = if output.stderr.is_empty() {
                    None
                } else {
                    Some(String::from_utf8_lossy(&output.stderr).to_string())
                };

                let result = AdbCommandResult {
                    success,
                    output: stdout,
                    error: stderr,
                    exit_code: output.status.code(),
                    duration_ms: duration.as_millis() as u64,
                };

                if success {
                    debug!("Command executed successfully in {}ms", result.duration_ms);
                } else {
                    warn!("Command failed with exit code {:?}: {:?}",
                          result.exit_code, result.error);
                }

                Ok(result)
            }
            Err(e) => {
                error!("Failed to execute ADB command: {}", e);
                Ok(AdbCommandResult {
                    success: false,
                    output: String::new(),
                    error: Some(e.to_string()),
                    exit_code: None,
                    duration_ms: duration.as_millis() as u64,
                })
            }
        }
    }

    /// 点击屏幕坐标
    pub async fn tap(&self, device_id: &str, x: i32, y: i32) -> Result<AdbCommandResult> {
        let cmd = AdbCommand {
            device_id: device_id.to_string(),
            command: "shell".to_string(),
            args: vec![
                "input".to_string(),
                "tap".to_string(),
                x.to_string(),
                y.to_string(),
            ],
            timeout: Some(10),
        };

        self.execute_command(cmd).await
    }

    /// 输入文本
    pub async fn input_text(&self, device_id: &str, text: &str) -> Result<AdbCommandResult> {
        // 需要对文本进行转义
        let escaped_text = text.replace(" ", "%s").replace("&", "\\&");

        let cmd = AdbCommand {
            device_id: device_id.to_string(),
            command: "shell".to_string(),
            args: vec![
                "input".to_string(),
                "text".to_string(),
                escaped_text,
            ],
            timeout: Some(10),
        };

        self.execute_command(cmd).await
    }

    /// 按键操作
    pub async fn press_key(&self, device_id: &str, key_code: i32) -> Result<AdbCommandResult> {
        let cmd = AdbCommand {
            device_id: device_id.to_string(),
            command: "shell".to_string(),
            args: vec![
                "input".to_string(),
                "keyevent".to_string(),
                key_code.to_string(),
            ],
            timeout: Some(10),
        };

        self.execute_command(cmd).await
    }

    /// 滑动操作
    pub async fn swipe(&self, device_id: &str, x1: i32, y1: i32, x2: i32, y2: i32, duration: i32) -> Result<AdbCommandResult> {
        let cmd = AdbCommand {
            device_id: device_id.to_string(),
            command: "shell".to_string(),
            args: vec![
                "input".to_string(),
                "swipe".to_string(),
                x1.to_string(),
                y1.to_string(),
                x2.to_string(),
                y2.to_string(),
                duration.to_string(),
            ],
            timeout: Some(20),
        };

        self.execute_command(cmd).await
    }

    /// 启动应用
    pub async fn start_app(&self, device_id: &str, package_name: &str, activity_name: Option<&str>) -> Result<AdbCommandResult> {
        let activity = if let Some(activity) = activity_name {
            format!("{}/{}", package_name, activity)
        } else {
            package_name.to_string()
        };

        let cmd = AdbCommand {
            device_id: device_id.to_string(),
            command: "shell".to_string(),
            args: vec![
                "am".to_string(),
                "start".to_string(),
                "-n".to_string(),
                activity,
            ],
            timeout: Some(30),
        };

        self.execute_command(cmd).await
    }

    /// 检查应用是否已安装
    pub async fn is_app_installed(&self, device_id: &str, package_name: &str) -> Result<bool> {
        let cmd = AdbCommand {
            device_id: device_id.to_string(),
            command: "shell".to_string(),
            args: vec![
                "pm".to_string(),
                "list".to_string(),
                "packages".to_string(),
                package_name.to_string(),
            ],
            timeout: Some(10),
        };

        let result = self.execute_command(cmd).await?;
        Ok(result.success && result.output.contains(package_name))
    }

    /// 截图
    pub async fn screenshot(&self, device_id: &str, save_path: &str) -> Result<AdbCommandResult> {
        let cmd = AdbCommand {
            device_id: device_id.to_string(),
            command: "shell".to_string(),
            args: vec![
                "screencap".to_string(),
                "-p".to_string(),
                "/sdcard/screenshot.png".to_string(),
            ],
            timeout: Some(10),
        };

        let screenshot_result = self.execute_command(cmd).await?;
        if !screenshot_result.success {
            return Ok(screenshot_result);
        }

        // 拉取截图文件
        let pull_cmd = AdbCommand {
            device_id: device_id.to_string(),
            command: "pull".to_string(),
            args: vec![
                "/sdcard/screenshot.png".to_string(),
                save_path.to_string(),
            ],
            timeout: Some(30),
        };

        self.execute_command(pull_cmd).await
    }

    /// 等待
    pub async fn wait(&self, duration_ms: u64) {
        sleep(Duration::from_millis(duration_ms)).await;
    }

    /// 断开设备连接
    pub async fn disconnect_device(&self, device_id: &str) -> Result<()> {
        info!("Disconnecting device: {}", device_id);

        // ADB 本身不需要显式断开连接，但我们可以检查设备状态
        let devices = self.get_devices().await?;
        let device_exists = devices.iter().any(|d| d.id == device_id);

        if !device_exists {
            return Err(anyhow::anyhow!("Device {} not found", device_id));
        }

        info!("Device {} marked as disconnected", device_id);
        Ok(())
    }

    /// 获取指定设备的详细信息
    pub async fn get_device_info(&self, device_id: &str) -> Result<Option<AdbDevice>> {
        let devices = self.get_devices().await?;
        Ok(devices.into_iter().find(|d| d.id == device_id))
    }
}

impl Default for AdbManager {
    fn default() -> Self {
        Self::new(None)
    }
}
