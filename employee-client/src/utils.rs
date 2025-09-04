// 工具函数模块
use std::path::Path;
use std::fs;
use serde_json;

/// 验证文件路径是否存在且可读
pub fn validate_file_path(path: &str) -> Result<(), String> {
    let file_path = Path::new(path);
    
    if !file_path.exists() {
        return Err(format!("文件不存在: {}", path));
    }
    
    if !file_path.is_file() {
        return Err(format!("路径不是文件: {}", path));
    }
    
    // 检查文件权限
    match fs::File::open(file_path) {
        Ok(_) => Ok(()),
        Err(e) => Err(format!("无法读取文件 {}: {}", path, e)),
    }
}

/// 解析通讯录文件
pub fn parse_contact_file(file_path: &str) -> Result<Vec<crate::models::Contact>, String> {
    validate_file_path(file_path)?;
    
    let content = fs::read_to_string(file_path)
        .map_err(|e| format!("读取文件失败: {}", e))?;
    
    // 支持多种格式：JSON, CSV, TXT
    let extension = Path::new(file_path)
        .extension()
        .and_then(|s| s.to_str())
        .unwrap_or("")
        .to_lowercase();
    
    match extension.as_str() {
        "json" => parse_json_contacts(&content),
        "csv" => parse_csv_contacts(&content),
        "txt" => parse_txt_contacts(&content),
        _ => Err(format!("不支持的文件格式: {}", extension)),
    }
}

/// 解析 JSON 格式的通讯录
fn parse_json_contacts(content: &str) -> Result<Vec<crate::models::Contact>, String> {
    serde_json::from_str(content)
        .map_err(|e| format!("JSON 解析失败: {}", e))
}

/// 解析 CSV 格式的通讯录
fn parse_csv_contacts(content: &str) -> Result<Vec<crate::models::Contact>, String> {
    let mut contacts = Vec::new();
    
    for (line_num, line) in content.lines().enumerate() {
        if line_num == 0 {
            continue; // 跳过标题行
        }
        
        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() >= 2 {
            contacts.push(crate::models::Contact {
                name: fields[0].trim().to_string(),
                phone: fields[1].trim().to_string(),
                platform_id: fields.get(2).map(|s| s.trim().to_string()),
            });
        }
    }
    
    Ok(contacts)
}

/// 解析 TXT 格式的通讯录（每行一个联系人，格式：姓名,电话）
fn parse_txt_contacts(content: &str) -> Result<Vec<crate::models::Contact>, String> {
    let mut contacts = Vec::new();
    
    for line in content.lines() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        
        let parts: Vec<&str> = line.split(',').collect();
        if parts.len() >= 2 {
            contacts.push(crate::models::Contact {
                name: parts[0].trim().to_string(),
                phone: parts[1].trim().to_string(),
                platform_id: None,
            });
        } else {
            // 如果只有一个字段，假设是电话号码
            contacts.push(crate::models::Contact {
                name: format!("联系人{}", contacts.len() + 1),
                phone: line.to_string(),
                platform_id: None,
            });
        }
    }
    
    Ok(contacts)
}

/// 格式化文件大小
pub fn format_file_size(size: u64) -> String {
    const UNITS: &[&str] = &["B", "KB", "MB", "GB"];
    let mut size = size as f64;
    let mut unit_index = 0;
    
    while size >= 1024.0 && unit_index < UNITS.len() - 1 {
        size /= 1024.0;
        unit_index += 1;
    }
    
    format!("{:.1} {}", size, UNITS[unit_index])
}

/// 格式化持续时间
pub fn format_duration(duration: chrono::Duration) -> String {
    let total_seconds = duration.num_seconds();
    
    if total_seconds < 60 {
        format!("{}秒", total_seconds)
    } else if total_seconds < 3600 {
        let minutes = total_seconds / 60;
        let seconds = total_seconds % 60;
        format!("{}分{}秒", minutes, seconds)
    } else {
        let hours = total_seconds / 3600;
        let minutes = (total_seconds % 3600) / 60;
        format!("{}小时{}分", hours, minutes)
    }
}

/// 生成唯一任务ID
pub fn generate_task_id() -> String {
    uuid::Uuid::new_v4().to_string()
}

/// 验证设备ID格式
pub fn validate_device_id(device_id: &str) -> Result<(), String> {
    if device_id.is_empty() {
        return Err("设备ID不能为空".to_string());
    }
    
    // 检查设备ID格式（IP:Port 或者 设备序列号）
    if device_id.contains(':') {
        // IP:Port 格式
        let parts: Vec<&str> = device_id.split(':').collect();
        if parts.len() != 2 {
            return Err("IP:Port 格式错误".to_string());
        }
        
        // 验证端口号
        if let Err(_) = parts[1].parse::<u16>() {
            return Err("端口号格式错误".to_string());
        }
    }
    
    Ok(())
}
