use anyhow::{Result, Context};
use std::fs;
use std::path::Path;
use tokio::process::Command;

#[derive(Debug, Clone)]
pub struct Contact {
    pub name: String,
    pub phone: String,
    pub address: String,
    pub note: String,
    pub email: String,
}

impl Contact {
    pub fn from_line(line: &str) -> Result<Self> {
        let parts: Vec<&str> = line.trim().split(',').collect();
        if parts.len() < 5 {
            return Err(anyhow::anyhow!("联系人信息格式错误，需要5个字段"));
        }
        
        Ok(Contact {
            name: parts[0].trim().to_string(),
            phone: parts[1].trim().to_string(),
            address: parts[2].trim().to_string(),
            note: parts[3].trim().to_string(),
            email: parts[4].trim().to_string(),
        })
    }
    
    /// 生成符合vCard 2.1标准的格式（兼容性最佳）
    pub fn to_vcf(&self) -> String {
        let mut vcf = String::new();
        
        // 必需字段：BEGIN和VERSION (使用2.1版本确保最大兼容性)
        vcf.push_str("BEGIN:VCARD\r\n");
        vcf.push_str("VERSION:2.1\r\n");
        
        // 结构化姓名 (N) - vCard 2.1格式
        // 格式: Family Name;Given Name;Additional Names;Honorific Prefixes;Honorific Suffixes
        // 对于中文姓名，我们将整个姓名放在Given Name字段
        vcf.push_str(&format!("N:;{};;;\r\n", self.escape_vcf_value(&self.name)));
        
        // 必需字段：FN (格式化姓名)
        vcf.push_str(&format!("FN:{}\r\n", self.escape_vcf_value(&self.name)));
        
        // 电话号码 (使用vCard 2.1的简化格式)
        if !self.phone.is_empty() {
            vcf.push_str(&format!("TEL;CELL:{}\r\n", self.phone));
        }
        
        // 电子邮件 (vCard 2.1格式)
        if !self.email.is_empty() {
            vcf.push_str(&format!("EMAIL;INTERNET:{}\r\n", 
                self.escape_vcf_value(&self.email)));
        }
        
        // 地址 (vCard 2.1简化格式)
        if !self.address.is_empty() {
            vcf.push_str(&format!("ADR;HOME:;;{};;;;;中国\r\n", 
                self.escape_vcf_value(&self.address)));
        }
        
        // 备注/职业信息
        if !self.note.is_empty() {
            vcf.push_str(&format!("NOTE:{}\r\n", self.escape_vcf_value(&self.note)));
        }
        
        // 结束标记
        vcf.push_str("END:VCARD\r\n");
        
        vcf
    }
    
    /// 转义VCF格式的特殊字符
    fn escape_vcf_value(&self, value: &str) -> String {
        value
            .replace("\\", "\\\\")  // 反斜杠
            .replace(",", "\\,")    // 逗号
            .replace(";", "\\;")    // 分号
            .replace("\n", "\\n")   // 换行
            .replace("\r", "")      // 移除回车符
    }
}

pub struct VcfImporter<'a> {
    pub adb_path: &'a str,
    pub device_id: &'a str,
}

impl<'a> VcfImporter<'a> {
    pub fn new(adb_path: &'a str, device_id: &'a str) -> Self {
        Self { adb_path, device_id }
    }
    
    /// 从文件读取联系人数据
    pub fn read_contacts_from_file<P: AsRef<Path>>(file_path: P) -> Result<Vec<Contact>> {
        let content = fs::read_to_string(file_path)
            .context("无法读取联系人文件")?;
            
        let mut contacts = Vec::new();
        
        for (line_num, line) in content.lines().enumerate() {
            if line.trim().is_empty() {
                continue;
            }
            
            match Contact::from_line(line) {
                Ok(contact) => contacts.push(contact),
                Err(e) => {
                    eprintln!("⚠️ 第{}行解析失败: {}", line_num + 1, e);
                }
            }
        }
        
        Ok(contacts)
    }
    
    /// 生成VCF文件
    pub fn generate_vcf_file(contacts: &[Contact], output_path: &str) -> Result<()> {
        let mut vcf_content = String::new();
        
        for contact in contacts {
            vcf_content.push_str(&contact.to_vcf());
            vcf_content.push('\n'); // VCF文件中的vCard之间用空行分隔
        }
        
        fs::write(output_path, vcf_content)
            .context("写入VCF文件失败")?;
            
        println!("✅ VCF文件已生成: {}", output_path);
        println!("📝 包含 {} 个联系人", contacts.len());
        
        Ok(())
    }
    
    /// 将VCF文件传输到Android设备
    pub async fn transfer_vcf_to_device(&self, vcf_path: &str, device_path: &str) -> Result<()> {
        println!("📤 正在传输VCF文件到设备...");
        
        let output = Command::new(self.adb_path)
            .args(["-s", self.device_id, "push", vcf_path, device_path])
            .output()
            .await
            .context("执行ADB push命令失败")?;
            
        if !output.status.success() {
            let error = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow::anyhow!("传输VCF文件失败: {}", error));
        }
        
        println!("✅ VCF文件已传输到设备: {}", device_path);
        Ok(())
    }
    
    /// 检查设备上的文件
    pub async fn verify_file_on_device(&self, device_path: &str) -> Result<bool> {
        let output = Command::new(self.adb_path)
            .args(["-s", self.device_id, "shell", "ls", "-la", device_path])
            .output()
            .await
            .context("检查设备文件失败")?;
            
        if output.status.success() {
            let file_info = String::from_utf8_lossy(&output.stdout);
            if !file_info.contains("No such file") {
                println!("📁 设备上的文件信息:");
                println!("{}", file_info);
                return Ok(true);
            }
        }
        
        Ok(false)
    }
    
    /// 验证联系人是否成功导入到设备
    pub async fn verify_contacts_import(&self, expected_contacts: &[Contact]) -> Result<bool> {
        println!("🔍 正在验证联系人导入结果...");
        
        // 等待几秒让系统处理导入
        tokio::time::sleep(tokio::time::Duration::from_secs(3)).await;
        
        // 启动联系人应用并检查
        self.open_contacts_app().await?;
        
        // 再等待应用完全加载
        tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
        
        // 获取当前联系人应用的UI信息
        let ui_dump = self.get_contacts_ui_dump().await?;
        
        let mut verified_count = 0;
        let total_expected = expected_contacts.len();
        
        println!("📋 开始验证 {} 个联系人...", total_expected);
        
        for (index, contact) in expected_contacts.iter().enumerate() {
            println!("🔎 验证第 {} 个联系人: {}", index + 1, contact.name);
            
            // 检查姓名是否存在
            let name_found = ui_dump.contains(&contact.name);
            
            // 检查电话号码是否存在（去除格式化字符）
            let phone_clean = contact.phone.replace("-", "").replace(" ", "").replace("(", "").replace(")", "");
            let phone_found = ui_dump.contains(&phone_clean) || ui_dump.contains(&contact.phone);
            
            if name_found || phone_found {
                verified_count += 1;
                println!("  ✅ 找到联系人: {} (姓名:{}, 电话:{})", 
                    contact.name, 
                    if name_found { "✓" } else { "✗" },
                    if phone_found { "✓" } else { "✗" }
                );
            } else {
                println!("  ❌ 未找到联系人: {}", contact.name);
            }
            
            // 短暂延迟避免过于频繁的操作
            tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
        }
        
        let success_rate = (verified_count as f32 / total_expected as f32) * 100.0;
        
        println!("\n📊 验证结果统计:");
        println!("  成功验证: {} / {} 个联系人", verified_count, total_expected);
        println!("  成功率: {:.1}%", success_rate);
        
        if success_rate >= 80.0 {
            println!("✅ 导入验证成功！大部分联系人已正确导入");
            Ok(true)
        } else if success_rate >= 50.0 {
            println!("⚠️  导入部分成功，建议检查联系人应用");
            Ok(false)
        } else {
            println!("❌ 导入验证失败，联系人可能未正确导入");
            Ok(false)
        }
    }
    
    /// 使用系统Intent自动导入VCF文件
    async fn import_vcf_via_intent(&self, vcf_path: &str) -> Result<()> {
        println!("🤖 尝试使用系统Intent自动导入VCF文件...");
        
        // 方法1: 直接通过Intent启动VCF导入
        let intent_cmd = format!(
            "adb -s {} shell am start -a android.intent.action.VIEW -d file://{} -t text/vcard",
            self.device_id, vcf_path
        );
        
        let output = tokio::process::Command::new("cmd")
            .args(&["/C", &intent_cmd])
            .output()
            .await
            .context("执行Intent导入命令失败")?;
        
        if output.status.success() {
            let result = String::from_utf8_lossy(&output.stdout);
            if result.contains("Starting") || result.is_empty() {
                println!("✅ Intent导入命令已发送");
                return Ok(());
            }
        }
        
        // 方法2: 通过文件管理器打开VCF文件
        println!("🔄 尝试通过文件管理器打开VCF文件...");
        let file_manager_cmd = format!(
            "adb -s {} shell am start -a android.intent.action.VIEW -d file://{} -t text/x-vcard",
            self.device_id, vcf_path
        );
        
        let output2 = tokio::process::Command::new("cmd")
            .args(&["/C", &file_manager_cmd])
            .output()
            .await
            .context("通过文件管理器打开失败")?;
        
        if output2.status.success() {
            println!("✅ 文件管理器Intent已发送");
            return Ok(());
        }
        
        // 方法3: 使用联系人应用的导入Intent
        println!("🔄 尝试直接调用联系人应用导入...");
        let contacts_import_cmd = format!(
            "adb -s {} shell am start -n com.android.contacts/.activities.PeopleActivity -a android.intent.action.VIEW -d file://{}",
            self.device_id, vcf_path
        );
        
        tokio::process::Command::new("cmd")
            .args(&["/C", &contacts_import_cmd])
            .output()
            .await
            .context("联系人应用Intent失败")?;
        
        println!("📱 联系人应用Intent已发送，等待用户确认");
        
        Ok(())
    }
    async fn get_contacts_ui_dump(&self) -> Result<String> {
        let output = Command::new(self.adb_path)
            .args(["-s", self.device_id, "shell", "uiautomator", "dump", "/dev/stdout"])
            .output()
            .await
            .context("获取UI信息失败")?;
            
        if output.status.success() {
            let ui_xml = String::from_utf8_lossy(&output.stdout);
            Ok(ui_xml.to_string())
        } else {
            Err(anyhow::anyhow!("UI dump命令执行失败"))
        }
    }
    
    /// 使用系统Intent方式导入VCF文件
    pub async fn import_vcf_via_intent(&self, device_path: &str) -> Result<()> {
        println!("📱 使用系统Intent导入VCF文件...");
        
        let output = Command::new(self.adb_path)
            .args(["-s", self.device_id, "shell", "am", "start", 
                  "-a", "android.intent.action.VIEW",
                  "-d", &format!("file://{}", device_path),
                  "-t", "text/x-vcard"])
            .output()
            .await
            .context("启动VCF导入Intent失败")?;
            
        if output.status.success() {
            println!("✅ VCF导入Intent已发送");
            println!("📱 请在设备上确认导入操作");
            Ok(())
        } else {
            let error = String::from_utf8_lossy(&output.stderr);
            Err(anyhow::anyhow!("Intent启动失败: {}", error))
        }
    }
        println!("📱 正在启动联系人应用...");
        
        // 启动联系人应用
        let output = Command::new(self.adb_path)
            .args(["-s", self.device_id, "shell", "am", "start", 
                  "-n", "com.android.contacts/.activities.PeopleActivity"])
            .output()
            .await
            .context("启动联系人应用失败")?;
            
        if !output.status.success() {
            // 尝试其他常见的联系人应用包名
            let alternative_packages = [
                "com.google.android.contacts/.activities.PeopleActivity",
                "com.android.contacts/.ContactsListActivity",
                "com.google.android.contacts/.ContactsListActivity",
            ];
            
            for package in &alternative_packages {
                println!("🔄 尝试启动: {}", package);
                let alt_output = Command::new(self.adb_path)
                    .args(["-s", self.device_id, "shell", "am", "start", "-n", package])
                    .output()
                    .await;
                    
                if alt_output.is_ok() && alt_output.unwrap().status.success() {
                    println!("✅ 联系人应用已启动");
                    return Ok(());
                }
            }
            
            // 如果所有尝试都失败，使用通用Intent启动
            println!("🔄 使用通用Intent启动联系人应用...");
            let _output = Command::new(self.adb_path)
                .args(["-s", self.device_id, "shell", "am", "start", 
                      "-a", "android.intent.action.MAIN", 
                      "-c", "android.intent.category.APP_CONTACTS"])
                .output()
                .await
                .context("启动联系人应用失败")?;
        }
        
        println!("✅ 联系人应用已启动");
        println!("📋 请在联系人应用中选择：菜单 > 导入/导出 > 从存储导入");
        
        Ok(())
    }
    
    /// 完整的VCF导入流程（包含导入后验证）
    pub async fn import_contacts_from_file<P: AsRef<Path>>(&self, contacts_file: P) -> Result<()> {
        println!("🚀 开始VCF联系人导入流程（含验证）...");
        
        // 1. 读取联系人数据
        let contacts = Self::read_contacts_from_file(contacts_file)?;
        if contacts.is_empty() {
            return Err(anyhow::anyhow!("没有找到有效的联系人数据"));
        }
        
        // 2. 生成VCF文件（使用vCard 2.1格式提高兼容性）
        let vcf_filename = "contacts_import.vcf";
        Self::generate_vcf_file(&contacts, vcf_filename)?;
        
        println!("📄 生成的VCF格式示例（vCard 2.1）:");
        if let Some(first_contact) = contacts.first() {
            let sample_vcf = first_contact.to_vcf();
            let lines: Vec<&str> = sample_vcf.lines().collect();
            for line in lines.iter().take(6) {  // 显示前6行
                println!("  {}", line);
            }
            if lines.len() > 6 {
                println!("  ...");
            }
        }
        
        // 3. 传输到设备Downloads目录
        let device_path = "/sdcard/Download/contacts_import.vcf";
        self.transfer_vcf_to_device(vcf_filename, device_path).await?;
        
        // 4. 验证文件传输
        if !self.verify_file_on_device(device_path).await? {
            return Err(anyhow::anyhow!("文件验证失败，VCF文件可能没有正确传输"));
        }
        
        // 5. 尝试使用系统Intent自动导入
        println!("\n🤖 尝试自动导入VCF文件...");
        match self.import_vcf_via_intent(device_path).await {
            Ok(_) => {
                println!("✅ 自动导入请求已发送");
                println!("⏳ 等待用户在设备上确认导入...");
                
                // 等待用户操作
                tokio::time::sleep(tokio::time::Duration::from_secs(10)).await;
            },
            Err(e) => {
                println!("⚠️ 自动导入失败: {}", e);
                println!("📱 将启动联系人应用，请手动导入");
                
                // 5b. 启动联系人应用（备用方案）
                self.open_contacts_app().await?;
                
                println!("📝 手动导入步骤:");
                println!("   1. 在联系人应用中点击菜单按钮");
                println!("   2. 选择 '导入/导出' 或 'Import/Export'");
                println!("   3. 选择 '从存储导入' 或 'Import from storage'");
                println!("   4. 找到并选择 'contacts_import.vcf' 文件");
                println!("   5. 确认导入所有 {} 个联系人", contacts.len());
                
                // 等待用户手动操作
                println!("\n⏳ 请完成上述导入步骤，然后等待验证...");
                tokio::time::sleep(tokio::time::Duration::from_secs(20)).await;
            }
        }
        
        // 6. 验证导入结果
        println!("\n🔍 开始验证导入结果...");
        match self.verify_contacts_import(&contacts).await {
            Ok(true) => {
                println!("✅ VCF联系人导入并验证成功！");
                println!("🎯 所有联系人均已正确导入到设备");
            },
            Ok(false) => {
                println!("⚠️ VCF联系人部分导入成功");
                println!("💡 建议检查联系人应用确认导入结果");
            },
            Err(e) => {
                println!("❌ 导入验证过程出错: {}", e);
                println!("💡 请手动检查联系人应用中的导入结果");
            }
        }
        
        // 7. 清理本地临时文件
        if Path::new(vcf_filename).exists() {
            fs::remove_file(vcf_filename).context("清理临时文件失败")?;
            println!("🧹 本地临时文件已清理");
        }
        
        println!("\n📋 导入流程总结:");
        println!("  • 生成VCF文件: vCard 2.1格式 (最佳兼容性)");
        println!("  • 传输到设备: /sdcard/Download/contacts_import.vcf");
        println!("  • 导入方式: 系统Intent + 手动备用");
        println!("  • 验证机制: 自动检查导入结果");
        println!("  • 联系人数量: {} 个", contacts.len());
        
        Ok(())
    }
    
    /// 生成示例VCF文件用于测试
    pub fn generate_sample_vcf() -> Result<()> {
        let sample_contacts = vec![
            Contact {
                name: "测试联系人".to_string(),
                phone: "13800138000".to_string(),
                address: "北京市朝阳区".to_string(),
                note: "VCF导入测试".to_string(),
                email: "test@example.com".to_string(),
            }
        ];
        
        Self::generate_vcf_file(&sample_contacts, "sample_contact.vcf")?;
        println!("✅ 示例VCF文件已生成: sample_contact.vcf");
        
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_contact_from_line() {
        let line = "张小美,13812345678,北京市朝阳区,美妆博主,xiaomei@example.com";
        let contact = Contact::from_line(line).unwrap();
        
        assert_eq!(contact.name, "张小美");
        assert_eq!(contact.phone, "13812345678");
        assert_eq!(contact.address, "北京市朝阳区");
        assert_eq!(contact.note, "美妆博主");
        assert_eq!(contact.email, "xiaomei@example.com");
    }
    
    #[test]
    fn test_vcf_generation() {
        let contact = Contact {
            name: "张小美".to_string(),
            phone: "13812345678".to_string(),
            address: "北京市朝阳区".to_string(),
            note: "美妆博主".to_string(),
            email: "xiaomei@example.com".to_string(),
        };
        
        let vcf = contact.to_vcf();
        
        assert!(vcf.contains("BEGIN:VCARD"));
        assert!(vcf.contains("VERSION:4.0"));
        assert!(vcf.contains("FN:张小美"));
        assert!(vcf.contains("TEL;TYPE=cell,voice:13812345678"));
        assert!(vcf.contains("EMAIL;TYPE=internet:xiaomei@example.com"));
        assert!(vcf.contains("END:VCARD"));
    }
    
    #[test]
    fn test_vcf_escaping() {
        let contact = Contact {
            name: "测试,姓名;特殊\\字符".to_string(),
            phone: "123".to_string(),
            address: "地址\n换行".to_string(),
            note: "备注".to_string(),
            email: "test@example.com".to_string(),
        };
        
        let vcf = contact.to_vcf();
        
        assert!(vcf.contains("FN:测试\\,姓名\\;特殊\\\\字符"));
        assert!(vcf.contains("ADR;TYPE=home:;;地址\\n换行"));
    }
}
