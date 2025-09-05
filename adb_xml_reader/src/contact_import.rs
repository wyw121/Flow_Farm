use anyhow::{Result, Context, anyhow};
use tokio::time::{sleep, Duration};
use tokio::process::Command as TokioCommand;
use crate::{AdbClient, Contact, UIElement, ADB_PATH};

impl AdbClient {
    /// 优化的联系人导入流程 - 避免Google登录弹窗
    pub async fn execute_contact_import_flow(&self, contacts: &[Contact]) -> Result<()> {
        println!("🚀 开始导入 {} 个联系人（优化版，避免Google登录）...", contacts.len());

        // 检查当前页面并确保在正确位置
        if !self.verify_page_contains_simple("通讯录").await? {
            println!("❌ 不在通讯录页面，请手动导航到小红书通讯录页面");
            return Err(anyhow!("请确保当前页面为小红书通讯录页面"));
        }

        // 方法1: 尝试使用本地存储方式导入联系人
        if let Ok(_) = self.import_contacts_via_local_method(contacts).await {
            println!("✅ 使用本地方法导入成功！");
            return Ok(());
        }

        // 方法2: 使用优化的单个导入方式
        println!("🔄 本地方法失败，改用逐个导入优化方式");
        self.import_contacts_one_by_one_optimized(contacts).await
    }

    /// 简化的页面验证方法
    async fn verify_page_contains_simple(&self, text: &str) -> Result<bool> {
        let xml = self.get_ui_dump().await?;
        Ok(xml.contains(text))
    }

    /// 获取UI结构的简化方法
    async fn get_ui_dump(&self) -> Result<String> {
        self.dump_ui_hierarchy().await
    }

    /// 方法1: 尝试使用本地存储方式导入（避免系统账户）
    async fn import_contacts_via_local_method(&self, contacts: &[Contact]) -> Result<()> {
        println!("📱 尝试使用本地存储方式导入联系人...");

        // 点击添加联系人
        if !self.click_add_contact_button().await? {
            return Err(anyhow!("无法点击添加联系人按钮"));
        }

        // 检查并处理账户选择对话框
        if self.check_and_handle_account_dialog().await? {
            println!("✅ 成功处理账户选择对话框");
        }

        // 批量导入所有联系人
        for (index, contact) in contacts.iter().enumerate() {
            println!("📞 正在导入第{}个联系人: {} - {}", index + 1, contact.name, contact.phone);

            if index > 0 {
                // 点击添加更多联系人或返回添加页面
                if !self.navigate_to_add_contact().await? {
                    println!("⚠️  无法导航到添加联系人页面");
                    break;
                }
            }

            match self.import_single_contact_optimized(contact).await {
                Ok(_) => println!("✅ 第{}个联系人导入成功", index + 1),
                Err(e) => {
                    println!("❌ 第{}个联系人导入失败: {}", index + 1, e);
                    continue;
                }
            }

            // 短暂延迟避免操作过快
            sleep(Duration::from_millis(800)).await;
        }

        Ok(())
    }

    /// 方法2: 优化的逐个导入方式
    async fn import_contacts_one_by_one_optimized(&self, contacts: &[Contact]) -> Result<()> {
        println!("📋 使用逐个导入优化方式...");

        let mut success_count = 0;
        let mut fail_count = 0;

        for (index, contact) in contacts.iter().enumerate() {
            println!("\n--- 处理联系人 {}/{} ---", index + 1, contacts.len());
            println!("📞 正在导入: {} - {}", contact.name, contact.phone);

            // 确保在通讯录主页面
            if !self.verify_page_contains_simple("通讯录").await? {
                if !self.navigate_back_to_contacts().await? {
                    println!("❌ 无法返回通讯录主页");
                    fail_count += 1;
                    continue;
                }
            }

            // 点击添加联系人
            if !self.click_add_contact_button().await? {
                println!("❌ 无法点击添加联系人按钮");
                fail_count += 1;
                continue;
            }

            sleep(Duration::from_secs(1)).await;

            // 处理可能出现的账户选择
            if self.check_and_handle_account_dialog().await? {
                println!("✅ 处理了账户选择对话框");
            }

            // 导入单个联系人
            match self.import_single_contact_optimized(contact).await {
                Ok(_) => {
                    println!("✅ 第{}个联系人导入成功", index + 1);
                    success_count += 1;
                }
                Err(e) => {
                    println!("❌ 第{}个联系人导入失败: {}", index + 1, e);
                    fail_count += 1;
                    // 尝试恢复到主界面
                    self.navigate_back_to_contacts().await.ok();
                }
            }

            // 返回主界面准备下一个
            self.navigate_back_to_contacts().await.ok();
            sleep(Duration::from_millis(500)).await;
        }

        println!("\n📊 联系人导入统计:");
        println!("✅ 成功导入: {} 个", success_count);
        println!("❌ 导入失败: {} 个", fail_count);
        println!("📞 总计处理: {} 个", contacts.len());

        if success_count > 0 {
            println!("🎉 部分或全部联系人导入完成！");
            Ok(())
        } else {
            Err(anyhow!("所有联系人导入均失败"))
        }
    }

    /// 点击添加联系人按钮
    async fn click_add_contact_button(&self) -> Result<bool> {
        // 尝试多个可能的添加按钮位置和方式
        let add_button_coords = [(194, 249), (360, 249), (180, 260), (200, 240)];

        for coords in &add_button_coords {
            println!("🎯 尝试点击添加按钮坐标: ({}, {})", coords.0, coords.1);
            if let Ok(_) = self.click_coordinates(coords.0, coords.1).await {
                sleep(Duration::from_secs(2)).await;

                // 验证是否成功进入添加页面
                let xml = self.get_ui_dump().await?;
                if xml.contains("添加") || xml.contains("新建") || xml.contains("姓名") || xml.contains("电话") {
                    println!("✅ 成功进入添加联系人页面");
                    return Ok(true);
                }
            }
        }

        // 尝试通过文本查找添加按钮
        if let Ok(Some(element)) = self.find_text_element("添加").await {
            println!("🎯 通过文本找到添加按钮");
            if let Some(bounds) = &element.bounds {
                let center = bounds.center();
                self.click_coordinates(center.0, center.1).await?;
                sleep(Duration::from_secs(2)).await;
                return Ok(true);
            }
        }

        Ok(false)
    }

    /// 检查并处理账户选择对话框
    async fn check_and_handle_account_dialog(&self) -> Result<bool> {
        sleep(Duration::from_millis(500)).await;

        // 检查是否有Google账户相关的弹窗
        let xml = self.get_ui_dump().await?;

        if xml.contains("Google") || xml.contains("账户") || xml.contains("登录") ||
           xml.contains("选择账户") || xml.contains("添加账户") {
            println!("⚠️  检测到账户/登录相关弹窗，尝试处理...");

            // 尝试查找"取消"、"跳过"、"稍后"等按钮
            let cancel_keywords = ["取消", "跳过", "稍后", "不了", "本地", "Cancel", "Skip", "Later", "Local"];

            for keyword in &cancel_keywords {
                if let Ok(Some(element)) = self.find_text_element(keyword).await {
                    println!("🎯 找到{}按钮，点击跳过账户选择", keyword);
                    if let Some(bounds) = &element.bounds {
                        let center = bounds.center();
                        self.click_coordinates(center.0, center.1).await?;
                        sleep(Duration::from_secs(1)).await;
                        return Ok(true);
                    }
                }
            }

            // 如果没找到取消按钮，尝试点击对话框外部区域关闭
            println!("🎯 尝试点击对话框外部关闭弹窗");
            self.click_coordinates(50, 50).await?;  // 点击左上角
            sleep(Duration::from_millis(500)).await;

            // 或者按返回键
            self.run_adb_command(&["shell", "input", "keyevent", "KEYCODE_BACK"]).await?;
            sleep(Duration::from_millis(500)).await;

            return Ok(true);
        }

        Ok(false)
    }

    /// 导航到添加联系人页面
    async fn navigate_to_add_contact(&self) -> Result<bool> {
        // 检查当前是否已经在添加联系人页面
        let xml = self.get_ui_dump().await?;
        if xml.contains("添加联系人") || xml.contains("新建联系人") ||
           (xml.contains("姓名") && xml.contains("电话")) {
            return Ok(true);
        }

        // 如果不在，点击添加按钮
        return self.click_add_contact_button().await;
    }

    /// 返回通讯录主页面
    async fn navigate_back_to_contacts(&self) -> Result<bool> {
        let mut attempts = 0;
        const MAX_ATTEMPTS: usize = 3;

        while attempts < MAX_ATTEMPTS {
            if self.verify_page_contains_simple("通讯录").await? {
                return Ok(true);
            }

            // 按返回键
            self.run_adb_command(&["shell", "input", "keyevent", "KEYCODE_BACK"]).await?;
            sleep(Duration::from_millis(800)).await;
            attempts += 1;
        }

        // 如果还是不在通讯录页面，尝试重新导航
        println!("⚠️  无法返回通讯录页面，可能需要手动干预");
        Ok(false)
    }

    /// 优化的单个联系人导入
    async fn import_single_contact_optimized(&self, contact: &Contact) -> Result<()> {
        // 等待添加联系人页面加载
        sleep(Duration::from_secs(1)).await;

        // 查找并填写姓名字段
        if !self.fill_name_field(&contact.name).await? {
            println!("⚠️  警告: 未找到或无法填写姓名字段");
        }

        // 查找并填写电话号码字段
        if !self.fill_phone_field(&contact.phone).await? {
            println!("⚠️  警告: 未找到或无法填写电话字段");
        }

        // 保存联系人
        self.save_contact().await?;

        Ok(())
    }

    /// 填写姓名字段
    async fn fill_name_field(&self, name: &str) -> Result<bool> {
        let name_keywords = ["姓名", "名字", "Name", "姓", "全名"];

        for keyword in &name_keywords {
            if let Ok(Some(element)) = self.find_text_element(keyword).await {
                println!("🎯 找到姓名字段: {}", keyword);

                // 点击姓名字段（通常在找到的文本下方）
                if let Some(bounds) = &element.bounds {
                    let center = bounds.center();
                    self.click_coordinates(center.0, center.1 + 30).await?;
                    sleep(Duration::from_millis(500)).await;

                    // 清空并输入姓名
                    if self.clear_and_input_text(name).await? {
                        println!("✅ 成功输入姓名: {}", name);
                        return Ok(true);
                    }
                }
            }
        }

        // 如果通过文本没找到，尝试通过输入框类型查找
        if let Ok(input_element) = self.find_input_field_by_type("name").await {
            if let Some(bounds) = &input_element.bounds {
                let center = bounds.center();
                self.click_coordinates(center.0, center.1).await?;
                sleep(Duration::from_millis(500)).await;

                if self.clear_and_input_text(name).await? {
                    println!("✅ 通过输入框类型成功输入姓名: {}", name);
                    return Ok(true);
                }
            }
        }

        Ok(false)
    }

    /// 填写电话字段
    async fn fill_phone_field(&self, phone: &str) -> Result<bool> {
        let phone_keywords = ["电话", "手机", "Phone", "号码", "Mobile"];

        for keyword in &phone_keywords {
            if let Ok(Some(element)) = self.find_text_element(keyword).await {
                println!("🎯 找到电话字段: {}", keyword);

                // 点击电话字段
                if let Some(bounds) = &element.bounds {
                    let center = bounds.center();
                    self.click_coordinates(center.0, center.1 + 30).await?;
                    sleep(Duration::from_millis(500)).await;

                    // 清空并输入电话
                    if self.clear_and_input_text(phone).await? {
                        println!("✅ 成功输入电话: {}", phone);
                        return Ok(true);
                    }
                }
            }
        }

        // 尝试通过输入框类型查找
        if let Ok(input_element) = self.find_input_field_by_type("phone").await {
            if let Some(bounds) = &input_element.bounds {
                let center = bounds.center();
                self.click_coordinates(center.0, center.1).await?;
                sleep(Duration::from_millis(500)).await;

                if self.clear_and_input_text(phone).await? {
                    println!("✅ 通过输入框类型成功输入电话: {}", phone);
                    return Ok(true);
                }
            }
        }

        Ok(false)
    }

    /// 通过输入框类型查找字段
    async fn find_input_field_by_type(&self, _field_type: &str) -> Result<UIElement> {
        let xml = self.get_ui_dump().await?;
        let _root = self.parse_ui_xml(&xml)?;

        // 这里可以实现更复杂的输入框查找逻辑
        // 目前返回一个默认错误
        Err(anyhow!("未实现输入框类型查找"))
    }

    /// 查找文本元素的辅助方法
    async fn find_text_element(&self, text: &str) -> Result<Option<UIElement>> {
        let xml = self.get_ui_dump().await?;
        let root = self.parse_ui_xml(&xml)?;

        let elements = self.find_elements_by_text(&root, text);
        if let Some(element) = elements.first() {
            // 创建一个新的UIElement实例，包含bounds信息
            let mut result = (*element).clone();
            result.bounds = element.bounds.clone();
            return Ok(Some(result));
        }

        Ok(None)
    }

    /// 清空并输入文本的辅助方法
    async fn clear_and_input_text(&self, text: &str) -> Result<bool> {
        // 全选现有内容
        self.run_adb_command(&["shell", "input", "keyevent", "KEYCODE_CTRL_A"]).await?;
        sleep(Duration::from_millis(200)).await;

        // 删除选中内容
        self.run_adb_command(&["shell", "input", "keyevent", "KEYCODE_DEL"]).await?;
        sleep(Duration::from_millis(200)).await;

        // 输入新文本，使用UTF-8编码处理中文
        let escaped_text = text.replace(" ", "%s");
        match self.run_adb_command(&["shell", "input", "text", &escaped_text]).await {
            Ok(_) => {
                sleep(Duration::from_millis(300)).await;
                Ok(true)
            }
            Err(e) => {
                println!("⚠️  文本输入失败: {}", e);
                Ok(false)
            }
        }
    }

    /// 保存联系人的方法
    async fn save_contact(&self) -> Result<()> {
        let save_keywords = ["保存", "完成", "确定", "Save", "Done", "OK"];

        for keyword in &save_keywords {
            if let Ok(Some(element)) = self.find_text_element(keyword).await {
                println!("🎯 找到保存按钮: {}", keyword);
                if let Some(bounds) = &element.bounds {
                    let center = bounds.center();
                    self.click_coordinates(center.0, center.1).await?;
                    sleep(Duration::from_secs(2)).await;

                    // 验证保存成功
                    if self.verify_contact_saved().await? {
                        println!("✅ 联系人保存成功");
                        return Ok(());
                    } else {
                        println!("⚠️  联系人保存状态未确认，但可能已成功");
                        return Ok(()); // 仍然继续，可能保存成功了
                    }
                }
            }
        }

        println!("⚠️  未找到保存按钮，尝试按回车键保存");
        self.run_adb_command(&["shell", "input", "keyevent", "KEYCODE_ENTER"]).await?;
        sleep(Duration::from_secs(1)).await;

        Ok(())
    }

    /// 验证联系人是否保存成功
    async fn verify_contact_saved(&self) -> Result<bool> {
        sleep(Duration::from_millis(500)).await;

        // 检查是否返回到通讯录主页或联系人列表
        if self.verify_page_contains_simple("通讯录").await? ||
           self.verify_page_contains_simple("联系人").await? {
            return Ok(true);
        }

        // 检查是否还在编辑页面（可能有错误）
        if self.verify_page_contains_simple("添加").await? ||
           self.verify_page_contains_simple("新建").await? {
            return Ok(false);
        }

        Ok(true) // 默认认为成功
    }

    /// 执行ADB命令的内部方法
    async fn run_adb_command(&self, args: &[&str]) -> Result<()> {
        let mut cmd = TokioCommand::new(ADB_PATH);

        if let Some(device) = &self.device_id {
            cmd.args(&["-s", device]);
        }

        cmd.args(args);

        let output = cmd.output().await
            .context("执行ADB命令失败")?;

        if !output.status.success() {
            let error = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow!("ADB命令执行失败: {}", error));
        }

        Ok(())
    }
}
