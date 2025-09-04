use anyhow::{Context, Result};
use encoding_rs::*;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;
use tracing::{info, warn};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Contact {
    pub id: String,
    pub name: String,
    pub phone: Option<String>,
    pub username: Option<String>,
    pub notes: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ContactList {
    pub id: String,
    pub name: String,
    pub file_path: String,
    pub contacts: Vec<Contact>,
    pub total_count: usize,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub updated_at: chrono::DateTime<chrono::Utc>,
}

pub struct ContactManager;

impl ContactManager {
    pub fn new() -> Self {
        Self
    }

    /// 读取TXT通讯录文件
    pub async fn load_contacts_from_txt(&self, file_path: &str) -> Result<ContactList> {
        info!("Loading contacts from: {}", file_path);

        if !Path::new(file_path).exists() {
            return Err(anyhow::anyhow!("文件不存在: {}", file_path));
        }

        // 读取文件内容
        let raw_data = fs::read(file_path)
            .with_context(|| format!("无法读取文件: {}", file_path))?;

        // 尝试检测编码并转换为UTF-8
        let content = self.decode_text(&raw_data)?;

        // 解析通讯录内容
        let contacts = self.parse_contacts(&content)?;

        let contact_list = ContactList {
            id: uuid::Uuid::new_v4().to_string(),
            name: Path::new(file_path)
                .file_stem()
                .and_then(|s| s.to_str())
                .unwrap_or("未命名通讯录")
                .to_string(),
            file_path: file_path.to_string(),
            total_count: contacts.len(),
            contacts,
            created_at: chrono::Utc::now(),
            updated_at: chrono::Utc::now(),
        };

        info!("Successfully loaded {} contacts", contact_list.total_count);
        Ok(contact_list)
    }

    /// 检测文本编码并转换为UTF-8
    fn decode_text(&self, raw_data: &[u8]) -> Result<String> {
        // 尝试UTF-8
        if let Ok(utf8_text) = std::str::from_utf8(raw_data) {
            return Ok(utf8_text.to_string());
        }

        // 尝试GBK编码
        let (decoded, encoding, had_errors) = GBK.decode(raw_data);
        if !had_errors {
            info!("Detected encoding: {}", encoding.name());
            return Ok(decoded.into_owned());
        }

        // 尝试GB18030编码
        let (decoded, encoding, had_errors) = GB18030.decode(raw_data);
        if !had_errors {
            info!("Detected encoding: {}", encoding.name());
            return Ok(decoded.into_owned());
        }

        // 最后尝试ISO-8859-1
        let (decoded, encoding, _) = WINDOWS_1252.decode(raw_data);
        warn!("Using fallback encoding: {}", encoding.name());
        Ok(decoded.into_owned())
    }

    /// 解析通讯录内容
    fn parse_contacts(&self, content: &str) -> Result<Vec<Contact>> {
        let mut contacts = Vec::new();
        let lines: Vec<&str> = content.lines().collect();

        for (line_no, line) in lines.iter().enumerate() {
            let line = line.trim();
            if line.is_empty() || line.starts_with('#') || line.starts_with("//") {
                continue; // 跳过空行和注释行
            }

            match self.parse_contact_line(line, line_no + 1) {
                Ok(Some(contact)) => contacts.push(contact),
                Ok(None) => continue, // 跳过无效行
                Err(e) => {
                    warn!("解析第{}行时出错: {} - 内容: {}", line_no + 1, e, line);
                    continue;
                }
            }
        }

        Ok(contacts)
    }

    /// 解析单行通讯录信息
    fn parse_contact_line(&self, line: &str, line_no: usize) -> Result<Option<Contact>> {
        // 支持多种格式：
        // 1. 姓名,手机号
        // 2. 姓名|手机号
        // 3. 姓名 手机号
        // 4. 姓名,手机号,用户名
        // 5. 姓名|手机号|用户名
        // 6. 用户名 (仅用户名)

        let separators = [',', '|', '\t'];
        let mut parts: Vec<&str> = Vec::new();

        // 尝试不同的分隔符
        for &sep in &separators {
            if line.contains(sep) {
                parts = line.split(sep).map(|s| s.trim()).collect();
                break;
            }
        }

        // 如果没有找到分隔符，尝试空格分隔
        if parts.is_empty() {
            let space_parts: Vec<&str> = line.split_whitespace().collect();
            if space_parts.len() >= 2 {
                parts = space_parts;
            } else if space_parts.len() == 1 && !space_parts[0].is_empty() {
                // 仅有一个部分，可能是用户名
                parts = space_parts;
            } else {
                return Ok(None);
            }
        }

        if parts.is_empty() {
            return Ok(None);
        }

        let contact_id = uuid::Uuid::new_v4().to_string();

        match parts.len() {
            1 => {
                // 仅一个字段，判断是姓名还是手机号还是用户名
                let value = parts[0];
                if self.is_phone_number(value) {
                    Ok(Some(Contact {
                        id: contact_id,
                        name: format!("联系人{}", line_no),
                        phone: Some(value.to_string()),
                        username: None,
                        notes: None,
                    }))
                } else {
                    Ok(Some(Contact {
                        id: contact_id,
                        name: value.to_string(),
                        phone: None,
                        username: Some(value.to_string()),
                        notes: None,
                    }))
                }
            }
            2 => {
                // 两个字段：姓名和手机号/用户名
                let name = parts[0];
                let second_field = parts[1];

                if self.is_phone_number(second_field) {
                    Ok(Some(Contact {
                        id: contact_id,
                        name: name.to_string(),
                        phone: Some(second_field.to_string()),
                        username: None,
                        notes: None,
                    }))
                } else {
                    Ok(Some(Contact {
                        id: contact_id,
                        name: name.to_string(),
                        phone: None,
                        username: Some(second_field.to_string()),
                        notes: None,
                    }))
                }
            }
            3 => {
                // 三个字段：姓名、手机号、用户名
                Ok(Some(Contact {
                    id: contact_id,
                    name: parts[0].to_string(),
                    phone: if self.is_phone_number(parts[1]) {
                        Some(parts[1].to_string())
                    } else {
                        None
                    },
                    username: Some(parts[2].to_string()),
                    notes: None,
                }))
            }
            _ => {
                // 更多字段，将额外字段作为备注
                let notes = parts[3..].join(" ");
                Ok(Some(Contact {
                    id: contact_id,
                    name: parts[0].to_string(),
                    phone: if self.is_phone_number(parts[1]) {
                        Some(parts[1].to_string())
                    } else {
                        None
                    },
                    username: Some(parts[2].to_string()),
                    notes: Some(notes),
                }))
            }
        }
    }

    /// 判断是否为手机号码
    fn is_phone_number(&self, text: &str) -> bool {
        use regex::Regex;

        // 中国手机号正则表达式
        let phone_regex = Regex::new(r"^1[3-9]\d{9}$").unwrap();

        // 移除所有非数字字符
        let numbers_only: String = text.chars().filter(|c| c.is_ascii_digit()).collect();

        // 检查是否符合中国手机号格式
        if phone_regex.is_match(&numbers_only) {
            return true;
        }

        // 检查是否为其他常见格式的电话号码
        let general_phone_regex = Regex::new(r"^\d{7,15}$").unwrap();
        general_phone_regex.is_match(&numbers_only)
    }

    /// 搜索联系人
    pub fn search_contacts(&self, contacts: &[Contact], keyword: &str) -> Vec<Contact> {
        let keyword = keyword.to_lowercase();

        contacts.iter()
            .filter(|contact| {
                contact.name.to_lowercase().contains(&keyword) ||
                contact.phone.as_ref().map_or(false, |p| p.contains(&keyword)) ||
                contact.username.as_ref().map_or(false, |u| u.to_lowercase().contains(&keyword))
            })
            .cloned()
            .collect()
    }

    /// 保存通讯录到文件
    pub async fn save_contacts_to_txt(&self, contacts: &ContactList, file_path: &str) -> Result<()> {
        let mut content = String::new();
        content.push_str(&format!("# 通讯录: {}\n", contacts.name));
        content.push_str(&format!("# 总数: {}\n", contacts.total_count));
        content.push_str(&format!("# 导出时间: {}\n\n", chrono::Utc::now().format("%Y-%m-%d %H:%M:%S")));

        for contact in &contacts.contacts {
            let mut line = contact.name.clone();

            if let Some(phone) = &contact.phone {
                line.push_str(&format!(",{}", phone));
            } else {
                line.push_str(",");
            }

            if let Some(username) = &contact.username {
                line.push_str(&format!(",{}", username));
            }

            if let Some(notes) = &contact.notes {
                line.push_str(&format!(" # {}", notes));
            }

            content.push_str(&format!("{}\n", line));
        }

        fs::write(file_path, content)
            .with_context(|| format!("无法保存文件: {}", file_path))?;

        info!("Successfully saved {} contacts to {}", contacts.total_count, file_path);
        Ok(())
    }
}

impl Default for ContactManager {
    fn default() -> Self {
        Self::new()
    }
}
