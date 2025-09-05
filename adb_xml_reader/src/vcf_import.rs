use std::fs;
use std::path::{Path, PathBuf};
use tokio::process::Command;
use anyhow::{Result, Context};
use chrono::Utc;

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
        vcf.push_str(&format!("N:;{};;;\r\n", self.escape_vcf_value(&self.name)));

        // 必需字段：FN (格式化姓名)
        vcf.push_str(&format!("FN:{}\r\n", self.escape_vcf_value(&self.name)));

        // 电话号码 (优化为中国格式，避免自动格式化为美式格式)
        if !self.phone.is_empty() {
            let formatted_phone = self.format_chinese_phone(&self.phone);
            // 使用多种电话标签确保正确识别为中国手机号
            vcf.push_str(&format!("TEL;CELL:{}\r\n", formatted_phone));
            // 添加TYPE属性明确指定为手机号码
            vcf.push_str(&format!("TEL;TYPE=CELL:{}\r\n", formatted_phone));
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

    /// 格式化中国手机号码，避免被系统自动转换为美式格式 (1-234-567-1234)
    fn format_chinese_phone(&self, phone: &str) -> String {
        let clean_phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "");

        // 如果是11位中国手机号（13x, 15x, 18x等开头）
        if clean_phone.len() == 11 && clean_phone.starts_with('1') {
            // 策略1: 添加+86国家代码（推荐）
            let with_country_code = format!("+86 {}", clean_phone);

            // 策略2: 如果仍被格式化，尝试使用空格分隔
            // 这样可以避免Android系统的自动格式化
            if clean_phone.len() >= 11 {
                // 按中国习惯分隔: 138 1234 5678
                let part1 = &clean_phone[0..3];   // 138
                let part2 = &clean_phone[3..7];   // 1234
                let part3 = &clean_phone[7..11];  // 5678
                format!("+86 {} {} {}", part1, part2, part3)
            } else {
                with_country_code
            }
        }
        // 如果已经有+86前缀，保持格式
        else if clean_phone.starts_with("+86") {
            clean_phone
        }
        // 其他格式，尝试添加+86
        else if clean_phone.len() >= 10 {
            format!("+86 {}", clean_phone)
        }
        // 保持原格式
        else {
            clean_phone
        }
    }
}

pub struct VcfImporter<'a> {
    pub adb_path: &'a str,
    pub device_id: &'a str,
}

impl<'a> VcfImporter<'a> {
    pub fn new(adb_path: &'a str, device_id: &'a str) -> Self {
        VcfImporter {
            adb_path,
            device_id,
        }
    }

    /// 从文件读取联系人数据
    pub fn read_contacts_from_file<P: AsRef<Path>>(file_path: P) -> Result<Vec<Contact>> {
        let contents = fs::read_to_string(file_path)
            .context("无法读取联系人文件")?;

        let mut contacts = Vec::new();
        for (line_num, line) in contents.lines().enumerate() {
            if line.trim().is_empty() {
                continue;
            }

            match Contact::from_line(line) {
                Ok(contact) => contacts.push(contact),
                Err(e) => {
                    println!("⚠️ 第{}行解析失败: {}", line_num + 1, e);
                }
            }
        }

        println!("📊 成功读取 {} 个联系人", contacts.len());
        Ok(contacts)
    }

    /// 生成VCF文件
    pub fn generate_vcf_file(contacts: &[Contact], filename: &str) -> Result<()> {
        let mut vcf_content = String::new();

        for contact in contacts {
            vcf_content.push_str(&contact.to_vcf());
            vcf_content.push('\n');
        }

        fs::write(filename, vcf_content.as_bytes())
            .context("写入VCF文件失败")?;

        let file_size = vcf_content.len();
        println!("✅ VCF文件生成成功: {} ({} 字节)", filename, file_size);
        Ok(())
    }

    /// 将VCF文件传输到设备
    async fn transfer_vcf_to_device(&self, local_path: &str, device_path: &str) -> Result<()> {
        println!("📤 传输VCF文件到设备...");

        let output = Command::new(self.adb_path)
            .args(["-s", self.device_id, "push", local_path, device_path])
            .output()
            .await
            .context("ADB push命令执行失败")?;

        if output.status.success() {
            println!("✅ 文件传输成功: {}", device_path);
            Ok(())
        } else {
            let error = String::from_utf8_lossy(&output.stderr);
            Err(anyhow::anyhow!("文件传输失败: {}", error))
        }
    }

    /// 验证文件是否在设备上存在
    async fn verify_file_on_device(&self, device_path: &str) -> Result<bool> {
        let output = Command::new(self.adb_path)
            .args(["-s", self.device_id, "shell", "ls", "-l", device_path])
            .output()
            .await
            .context("检查设备文件失败")?;

        let result = String::from_utf8_lossy(&output.stdout);
        let exists = !result.contains("No such file") && !result.trim().is_empty();

        if exists {
            println!("✅ 设备文件验证成功: {}", device_path);
        } else {
            println!("❌ 设备文件不存在: {}", device_path);
        }

        Ok(exists)
    }

    /// 正确的通讯录导入流程：通讯录→侧边栏→设置→导入
    async fn import_via_contacts_settings(&self, device_path: &str) -> Result<()> {
        println!("📱 执行正确的通讯录导入流程...");

        // 1. 启动联系人应用
        println!("🔷 1. 启动联系人应用");
        self.open_contacts_app().await?;
        tokio::time::sleep(tokio::time::Duration::from_secs(3)).await;

        // 2. 点击左上角菜单（汉堡菜单）打开侧边栏
        println!("🔷 2. 点击左上角菜单打开侧边栏");
        let menu_click = format!(
            "adb -s {} shell input tap 50 100",
            self.device_id
        );

        tokio::process::Command::new("cmd")
            .args(&["/C", &menu_click])
            .output()
            .await
            .context("点击菜单按钮失败")?;

        tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;

        // 3. 在侧边栏中查找并点击"设置"
        println!("🔷 3. 在侧边栏中点击设置");

        // 首先尝试通过UI查找设置按钮
        let ui_dump = self.get_contacts_ui_dump().await?;

        // 查找设置相关的文本（中英文）
        let settings_keywords = ["设置", "Settings", "设定", "配置"];
        let mut settings_found = false;

        for keyword in &settings_keywords {
            if ui_dump.contains(keyword) {
                println!("   找到设置选项: {}", keyword);
                // 尝试点击设置（通用坐标，可能需要调整）
                let settings_click = format!(
                    "adb -s {} shell input tap 200 300",
                    self.device_id
                );

                tokio::process::Command::new("cmd")
                    .args(&["/C", &settings_click])
                    .output()
                    .await
                    .context("点击设置失败")?;

                settings_found = true;
                break;
            }
        }

        if !settings_found {
            println!("⚠️ 未找到设置选项，尝试通用位置点击");
            let fallback_click = format!(
                "adb -s {} shell input tap 200 400",
                self.device_id
            );

            tokio::process::Command::new("cmd")
                .args(&["/C", &fallback_click])
                .output()
                .await
                .context("点击通用设置位置失败")?;
        }

        tokio::time::sleep(tokio::time::Duration::from_secs(3)).await;

        // 4. 在设置中查找导入选项
        println!("🔷 4. 在设置中查找导入选项");
        let settings_ui = self.get_contacts_ui_dump().await?;

        let import_keywords = ["导入", "Import", "匯入", "导入联系人"];
        let mut import_found = false;

        for keyword in &import_keywords {
            if settings_ui.contains(keyword) {
                println!("   找到导入选项: {}", keyword);
                // 点击导入选项
                let import_click = format!(
                    "adb -s {} shell input tap 400 500",
                    self.device_id
                );

                tokio::process::Command::new("cmd")
                    .args(&["/C", &import_click])
                    .output()
                    .await
                    .context("点击导入选项失败")?;

                import_found = true;
                break;
            }
        }

        if !import_found {
            println!("⚠️ 未找到导入选项，请手动操作");
            println!("   请在设置界面中找到'导入'或'Import'选项并点击");
            tokio::time::sleep(tokio::time::Duration::from_secs(10)).await;
        } else {
            tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
        }

        // 5. 选择从存储导入
        println!("🔷 5. 选择从存储导入VCF文件");
        println!("   📂 目标文件: {}", device_path);

        // 这里需要用户手动选择文件，因为文件选择器的自动化比较复杂
        println!("📝 请手动完成以下步骤:");
        println!("   • 在导入选项中选择'从存储导入'或'Import from storage'");
        println!("   • 浏览到 Downloads 文件夹");
        println!("   • 选择 'contacts_import.vcf' 文件");
        println!("   • 确认导入所有联系人");
        println!("   • 等待导入完成...");

        // 给用户足够时间完成手动操作
        println!("\n⏳ 等待用户完成导入操作（60秒）...");
        tokio::time::sleep(tokio::time::Duration::from_secs(60)).await;

        Ok(())
    }

    /// 启动联系人应用
    async fn open_contacts_app(&self) -> Result<()> {
        println!("📱 启动联系人应用...");

        let output = Command::new(self.adb_path)
            .args(["-s", self.device_id, "shell", "am", "start",
                  "-n", "com.android.contacts/.activities.PeopleActivity"])
            .output()
            .await
            .context("启动联系人应用失败")?;

        if output.status.success() {
            println!("✅ 联系人应用已启动");
            Ok(())
        } else {
            Err(anyhow::anyhow!("启动联系人应用失败"))
        }
    }

    /// 通过联系人应用侧边栏菜单导入VCF文件（正确的导入方式）
    async fn import_via_contacts_sidebar_menu(&self, vcf_path: &str) -> Result<()> {
        println!("📱 通过联系人应用侧边栏菜单导入VCF文件...");
        println!("📋 导入步骤：左上角菜单 → 侧边栏 → 设置 → 导入 → 选择文件");

        // 1. 确保联系人应用已启动
        self.open_contacts_app().await?;
        tokio::time::sleep(tokio::time::Duration::from_secs(3)).await;

        // 2. 点击左上角的菜单按钮（汉堡菜单图标）
        println!("🔘 步骤1: 点击左上角菜单按钮打开侧边栏...");

        // 获取当前UI来定位菜单按钮
        let ui_dump = self.get_contacts_ui_dump().await?;

        // 查找常见的菜单按钮描述
        let menu_indicators = [
            "Open drawer", "Open navigation drawer", "更多选项", "菜单",
            "导航抽屉", "Menu", "Drawer", "Navigation", "汉堡菜单"
        ];

        let mut menu_clicked = false;

        // 尝试通过UI元素定位菜单按钮
        for indicator in &menu_indicators {
            if ui_dump.contains(indicator) {
                println!("   ✅ 找到菜单按钮标识: {}", indicator);
                // 通常菜单按钮在左上角，坐标大约是 (50-100, 100-200)
                let menu_click = format!(
                    "adb -s {} shell input tap 75 150",
                    self.device_id
                );

                tokio::process::Command::new("cmd")
                    .args(&["/C", &menu_click])
                    .output()
                    .await
                    .context("点击菜单按钮失败")?;

                menu_clicked = true;
                break;
            }
        }

        // 如果未找到，尝试通用左上角位置
        if !menu_clicked {
            println!("   💡 未找到明确的菜单按钮，尝试点击左上角通用位置...");
            let fallback_menu_click = format!(
                "adb -s {} shell input tap 50 120",
                self.device_id
            );

            tokio::process::Command::new("cmd")
                .args(&["/C", &fallback_menu_click])
                .output()
                .await
                .context("点击左上角菜单位置失败")?;
        }

        // 等待侧边栏打开
        tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;

        // 3. 在侧边栏中寻找"设置"选项
        println!("🔘 步骤2: 在侧边栏中寻找设置选项...");
        let sidebar_ui = self.get_contacts_ui_dump().await?;

        let settings_keywords = ["设置", "Settings", "設定", "设定"];
        let mut settings_found = false;

        for keyword in &settings_keywords {
            if sidebar_ui.contains(keyword) {
                println!("   ✅ 找到设置选项: {}", keyword);

                // 设置选项通常在侧边栏中间或下方
                let settings_click = format!(
                    "adb -s {} shell input tap 200 400",
                    self.device_id
                );

                tokio::process::Command::new("cmd")
                    .args(&["/C", &settings_click])
                    .output()
                    .await
                    .context("点击设置选项失败")?;

                settings_found = true;
                break;
            }
        }

        if !settings_found {
            println!("   ⚠️  未找到设置选项，请手动点击侧边栏中的设置");
            println!("   📝 请在侧边栏中找到并点击'设置'选项，然后按回车继续...");
            // 可以添加用户输入等待
            tokio::time::sleep(tokio::time::Duration::from_secs(10)).await;
        }

        // 等待设置页面加载
        tokio::time::sleep(tokio::time::Duration::from_secs(3)).await;

        // 4. 在设置中查找导入选项
        println!("🔘 步骤3: 在设置中查找导入选项...");
        let settings_ui = self.get_contacts_ui_dump().await?;

        let import_keywords = ["导入", "Import", "匯入", "导入联系人", "Import contacts"];
        let mut import_found = false;

        for keyword in &import_keywords {
            if settings_ui.contains(keyword) {
                println!("   ✅ 找到导入选项: {}", keyword);

                // 导入选项通常在设置页面的中上部
                let import_click = format!(
                    "adb -s {} shell input tap 400 300",
                    self.device_id
                );

                tokio::process::Command::new("cmd")
                    .args(&["/C", &import_click])
                    .output()
                    .await
                    .context("点击导入选项失败")?;

                import_found = true;
                break;
            }
        }

        if !import_found {
            println!("   ⚠️  未找到导入选项，请手动寻找");
            println!("   📝 请在设置界面中找到'导入'选项并点击，然后按回车继续...");
            tokio::time::sleep(tokio::time::Duration::from_secs(10)).await;
        }

        // 等待导入界面加载
        tokio::time::sleep(tokio::time::Duration::from_secs(3)).await;

        // 5. 选择从存储导入
        println!("🔘 步骤4: 选择从存储导入...");
        let import_ui = self.get_contacts_ui_dump().await?;

        let storage_keywords = ["从存储", "From storage", "存储卡", "SD卡", "文件", "Storage"];
        let mut storage_found = false;

        for keyword in &storage_keywords {
            if import_ui.contains(keyword) {
                println!("   ✅ 找到存储导入选项: {}", keyword);

                let storage_click = format!(
                    "adb -s {} shell input tap 400 350",
                    self.device_id
                );

                tokio::process::Command::new("cmd")
                    .args(&["/C", &storage_click])
                    .output()
                    .await
                    .context("点击存储导入失败")?;

                storage_found = true;
                break;
            }
        }

        if !storage_found {
            println!("   💡 未找到明确的存储导入选项，尝试直接打开文件选择器...");
        }

        // 等待文件选择器打开
        tokio::time::sleep(tokio::time::Duration::from_secs(3)).await;

        println!("📂 文件选择器应该已打开");
        println!("📝 接下来需要手动操作：");
        println!("   1. 在文件选择器中导航到 Download 文件夹");
        println!("   2. 找到并选择 'contacts_import.vcf' 文件");
        println!("   3. 确认导入操作");
        println!("   4. 等待导入完成");

        Ok(())
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

    /// 获取联系人应用的UI文本内容用于验证
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

        // 5. 执行正确的通讯录导入流程（使用侧边栏菜单）
        println!("\n📱 执行通讯录导入流程...");
        println!("📋 导入路径: 通讯录 → 左上角菜单 → 侧边栏 → 设置 → 导入");

        match self.import_via_contacts_sidebar_menu(device_path).await {
            Ok(_) => {
                println!("✅ 侧边栏导入流程已完成");
                println!("⏳ 请按照屏幕提示手动完成最后的文件选择步骤");

                // 等待用户手动完成导入
                println!("⏱️  等待30秒供用户完成导入操作...");
                tokio::time::sleep(tokio::time::Duration::from_secs(30)).await;
            },
            Err(e) => {
                println!("⚠️ 侧边栏导入失败: {}", e);
                println!("📝 请手动操作：");
                println!("   1. 打开通讯录应用");
                println!("   2. 点击左上角菜单按钮");
                println!("   3. 在侧边栏中点击'设置'");
                println!("   4. 找到'导入'功能");
                println!("   5. 选择'从存储导入'");
                println!("   6. 找到并选择Downloads/contacts_import.vcf文件");

                // 等待用户手动操作
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
        println!("  • VCF格式: vCard 2.1 + 中国手机号码优化");
        println!("  • 电话格式: +86前缀，避免美式格式化");
        println!("  • 传输路径: /sdcard/Download/contacts_import.vcf");
        println!("  • 导入路径: 通讯录→菜单→设置→导入→选择文件");
        println!("  • 联系人数量: {} 个", contacts.len());
        println!("  • 字符编码: UTF-8支持中文姓名");

        Ok(())
    }

    /// 生成示例VCF文件用于测试
    pub fn generate_sample_vcf() -> Result<()> {
        println!("🧪 生成示例VCF文件...");

        let sample_contacts = vec![
            Contact {
                name: "张小美".to_string(),
                phone: "13800138000".to_string(),
                address: "北京市朝阳区".to_string(),
                note: "时尚博主".to_string(),
                email: "zhangxiaomei@example.com".to_string(),
            },
            Contact {
                name: "Test User".to_string(),
                phone: "13900139000".to_string(),
                address: "上海市浦东新区".to_string(),
                note: "测试用户".to_string(),
                email: "test@example.com".to_string(),
            }
        ];

        Self::generate_vcf_file(&sample_contacts, "sample_contact.vcf")?;
        println!("✅ 示例VCF文件已生成: sample_contact.vcf");

        Ok(())
    }
}
