use anyhow::{Context, Result};
use roxmltree::Document;
use serde::{Deserialize, Serialize};
use tokio::process::Command as TokioCommand;
use std::time::Duration;
use tokio::time::sleep;

// ADB 可执行文件路径
const ADB_PATH: &str = r"D:\leidian\LDPlayer9\adb.exe";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UIElement {
    pub tag: String,
    pub class: Option<String>,
    pub text: Option<String>,
    pub content_desc: Option<String>,
    pub resource_id: Option<String>,
    pub package: Option<String>,
    pub bounds: Option<String>,
    pub clickable: bool,
    pub enabled: bool,
    pub focused: bool,
    pub selected: bool,
    pub children: Vec<UIElement>,
}

pub struct AdbClient {
    device_id: Option<String>,
}

impl AdbClient {
    pub fn new(device_id: Option<String>) -> Self {
        Self { device_id }
    }

    /// 获取连接的设备列表
    pub async fn get_devices(&self) -> Result<Vec<String>> {
        let output = TokioCommand::new(ADB_PATH)
            .args(&["devices"])
            .output()
            .await
            .context("执行 adb devices 命令失败")?;

        if !output.status.success() {
            let error = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow::anyhow!("ADB 命令执行失败: {}", error));
        }

        let output_str = String::from_utf8_lossy(&output.stdout);
        let mut devices = Vec::new();

        for line in output_str.lines().skip(1) {
            if !line.trim().is_empty() {
                let parts: Vec<&str> = line.split_whitespace().collect();
                if parts.len() >= 2 && parts[1] == "device" {
                    devices.push(parts[0].to_string());
                }
            }
        }

        Ok(devices)
    }

    /// 获取设备的 UI 层次结构 XML
    pub async fn dump_ui_hierarchy(&self) -> Result<String> {
        let mut cmd = TokioCommand::new(ADB_PATH);

        if let Some(device) = &self.device_id {
            cmd.args(&["-s", device]);
        }

        cmd.args(&["shell", "uiautomator", "dump", "/sdcard/ui_dump.xml"]);

        let output = cmd.output().await
            .context("执行 uiautomator dump 命令失败")?;

        if !output.status.success() {
            let error = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow::anyhow!("UI dump 失败: {}", error));
        }

        // 读取生成的 XML 文件
        self.pull_xml_file().await
    }

    /// 从设备拉取 XML 文件内容
    async fn pull_xml_file(&self) -> Result<String> {
        let mut cmd = TokioCommand::new(ADB_PATH);

        if let Some(device) = &self.device_id {
            cmd.args(&["-s", device]);
        }

        cmd.args(&["shell", "cat", "/sdcard/ui_dump.xml"]);

        let output = cmd.output().await
            .context("读取 UI XML 文件失败")?;

        if !output.status.success() {
            let error = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow::anyhow!("读取 XML 文件失败: {}", error));
        }

        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    }

    /// 解析 XML 并提取 UI 元素信息
    pub fn parse_ui_xml(&self, xml_content: &str) -> Result<UIElement> {
        let doc = Document::parse(xml_content)
            .context("解析 XML 文档失败")?;

        let root = doc.root();
        if let Some(hierarchy_node) = root.children().find(|n| n.has_tag_name("hierarchy")) {
            if let Some(first_child) = hierarchy_node.children().find(|n| n.is_element()) {
                return Ok(self.parse_node(&first_child));
            }
        }

        Err(anyhow::anyhow!("未找到有效的 UI 层次结构"))
    }

    /// 递归解析 XML 节点
    fn parse_node(&self, node: &roxmltree::Node) -> UIElement {
        let mut element = UIElement {
            tag: node.tag_name().name().to_string(),
            class: node.attribute("class").map(|s| s.to_string()),
            text: node.attribute("text").map(|s| s.to_string()),
            content_desc: node.attribute("content-desc").map(|s| s.to_string()),
            resource_id: node.attribute("resource-id").map(|s| s.to_string()),
            package: node.attribute("package").map(|s| s.to_string()),
            bounds: node.attribute("bounds").map(|s| s.to_string()),
            clickable: node.attribute("clickable").unwrap_or("false") == "true",
            enabled: node.attribute("enabled").unwrap_or("false") == "true",
            focused: node.attribute("focused").unwrap_or("false") == "true",
            selected: node.attribute("selected").unwrap_or("false") == "true",
            children: Vec::new(),
        };

        // 递归解析子元素
        for child in node.children().filter(|n| n.is_element()) {
            element.children.push(self.parse_node(&child));
        }

        element
    }

    /// 查找包含特定文本的元素
    pub fn find_elements_by_text<'a>(&self, root: &'a UIElement, text: &str) -> Vec<&'a UIElement> {
        let mut results = Vec::new();
        self.search_by_text(root, text, &mut results);
        results
    }

    fn search_by_text<'a>(&self, element: &'a UIElement, text: &str, results: &mut Vec<&'a UIElement>) {
        if let Some(element_text) = &element.text {
            if element_text.contains(text) {
                results.push(element);
            }
        }

        if let Some(content_desc) = &element.content_desc {
            if content_desc.contains(text) {
                results.push(element);
            }
        }

        for child in &element.children {
            self.search_by_text(child, text, results);
        }
    }

    /// 查找具有特定资源ID的元素
    pub fn find_element_by_resource_id<'a>(&self, root: &'a UIElement, resource_id: &str) -> Option<&'a UIElement> {
        if let Some(id) = &root.resource_id {
            if id == resource_id {
                return Some(root);
            }
        }

        for child in &root.children {
            if let Some(found) = self.find_element_by_resource_id(child, resource_id) {
                return Some(found);
            }
        }

        None
    }

    /// 打印 UI 层次结构（用于调试）
    pub fn print_hierarchy(&self, element: &UIElement, indent: usize) {
        let indent_str = "  ".repeat(indent);

        println!("{}[{}]", indent_str, element.tag);

        if let Some(class) = &element.class {
            println!("{}  class: {}", indent_str, class);
        }

        if let Some(text) = &element.text {
            if !text.trim().is_empty() {
                println!("{}  text: \"{}\"", indent_str, text);
            }
        }

        if let Some(content_desc) = &element.content_desc {
            if !content_desc.trim().is_empty() {
                println!("{}  content-desc: \"{}\"", indent_str, content_desc);
            }
        }

        if let Some(resource_id) = &element.resource_id {
            println!("{}  resource-id: {}", indent_str, resource_id);
        }

        if let Some(bounds) = &element.bounds {
            println!("{}  bounds: {}", indent_str, bounds);
        }

        if element.clickable {
            println!("{}  clickable: true", indent_str);
        }

        for child in &element.children {
            self.print_hierarchy(child, indent + 1);
        }
    }

    /// 获取当前屏幕截图
    pub async fn take_screenshot(&self, output_path: &str) -> Result<()> {
        let mut cmd = TokioCommand::new(ADB_PATH);

        if let Some(device) = &self.device_id {
            cmd.args(&["-s", device]);
        }

        cmd.args(&["shell", "screencap", "/sdcard/screenshot.png"]);

        let output = cmd.output().await
            .context("截屏命令执行失败")?;

        if !output.status.success() {
            let error = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow::anyhow!("截屏失败: {}", error));
        }

        // 拉取截图文件
        let mut pull_cmd = TokioCommand::new(ADB_PATH);

        if let Some(device) = &self.device_id {
            pull_cmd.args(&["-s", device]);
        }

        pull_cmd.args(&["pull", "/sdcard/screenshot.png", output_path]);

        let pull_output = pull_cmd.output().await
            .context("拉取截图文件失败")?;

        if !pull_output.status.success() {
            let error = String::from_utf8_lossy(&pull_output.stderr);
            return Err(anyhow::anyhow!("拉取截图失败: {}", error));
        }

        println!("截图已保存到: {}", output_path);
        Ok(())
    }

    /// 点击指定坐标位置
    pub async fn click_coordinates(&self, x: i32, y: i32) -> Result<()> {
        let mut cmd = TokioCommand::new(ADB_PATH);

        if let Some(device) = &self.device_id {
            cmd.args(&["-s", device]);
        }

        cmd.args(&["shell", "input", "tap", &x.to_string(), &y.to_string()]);

        let output = cmd.output().await
            .context("执行点击命令失败")?;

        if !output.status.success() {
            let error = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow::anyhow!("点击操作失败: {}", error));
        }

        println!("✅ 点击坐标: ({}, {})", x, y);
        Ok(())
    }

    /// 根据元素bounds字符串解析坐标并点击中心点
    pub async fn click_element_bounds(&self, bounds: &str) -> Result<()> {
        let coords = self.parse_bounds_center(bounds)?;
        self.click_coordinates(coords.0, coords.1).await
    }

    /// 解析bounds字符串获取中心点坐标
    fn parse_bounds_center(&self, bounds: &str) -> Result<(i32, i32)> {
        // bounds格式: "[left,top][right,bottom]"
        let bounds = bounds.trim_matches(['[', ']']);
        let parts: Vec<&str> = bounds.split("][").collect();

        if parts.len() != 2 {
            return Err(anyhow::anyhow!("无效的bounds格式: {}", bounds));
        }

        let left_top: Vec<i32> = parts[0].split(',')
            .map(|s| s.parse::<i32>())
            .collect::<Result<Vec<_>, _>>()
            .context("解析左上角坐标失败")?;

        let right_bottom: Vec<i32> = parts[1].split(',')
            .map(|s| s.parse::<i32>())
            .collect::<Result<Vec<_>, _>>()
            .context("解析右下角坐标失败")?;

        if left_top.len() != 2 || right_bottom.len() != 2 {
            return Err(anyhow::anyhow!("坐标格式错误"));
        }

        let center_x = (left_top[0] + right_bottom[0]) / 2;
        let center_y = (left_top[1] + right_bottom[1]) / 2;

        Ok((center_x, center_y))
    }

    /// 搜索并点击包含指定文本的可点击元素
    pub async fn find_and_click_text(&self, search_text: &str, description: &str) -> Result<bool> {
        println!("\n🔍 正在搜索并点击: {}", description);

        // 获取当前UI结构
        let xml_content = self.dump_ui_hierarchy().await?;
        let elements = self.parse_ui_xml(&xml_content)?;

        // 搜索匹配的元素
        let mut found_elements = Vec::new();
        self.search_elements_text_recursive(&elements, search_text, &mut found_elements);

        // 查找可点击的元素
        for element in &found_elements {
            if element.clickable {
                if let Some(bounds) = &element.bounds {
                    println!("📍 找到可点击元素: {}", description);
                    println!("   文本: {:?}", element.text);
                    println!("   描述: {:?}", element.content_desc);
                    println!("   位置: {}", bounds);

                    self.click_element_bounds(bounds).await?;
                    return Ok(true);
                }
            }
        }

        println!("❌ 未找到可点击的元素: {}", description);
        Ok(false)
    }

    /// 查找包含指定content-desc的可点击元素并点击
    pub async fn find_and_click_content_desc(&self, content_desc: &str, description: &str) -> Result<bool> {
        println!("\n🔍 正在搜索并点击(通过描述): {}", description);

        // 获取当前UI结构
        let xml_content = self.dump_ui_hierarchy().await?;
        let elements = self.parse_ui_xml(&xml_content)?;

        // 搜索匹配的元素
        let mut found_elements = Vec::new();
        self.search_by_content_desc_single(&elements, content_desc, &mut found_elements);

        // 查找可点击的元素
        for element in &found_elements {
            if element.clickable {
                if let Some(bounds) = &element.bounds {
                    println!("📍 找到可点击元素: {}", description);
                    println!("   文本: {:?}", element.text);
                    println!("   描述: {:?}", element.content_desc);
                    println!("   位置: {}", bounds);

                    self.click_element_bounds(bounds).await?;
                    return Ok(true);
                }
            }
        }

        println!("❌ 未找到可点击的元素: {}", description);
        Ok(false)
    }

    /// 递归搜索包含指定content-desc的元素
    fn search_by_content_desc_recursive(&self, elements: &[UIElement], target_desc: &str, results: &mut Vec<UIElement>) {
        for element in elements {
            if let Some(content_desc) = &element.content_desc {
                if content_desc.contains(target_desc) {
                    results.push(element.clone());
                }
            }

            self.search_by_content_desc_recursive(&element.children, target_desc, results);
        }
    }

    /// 在单个元素中搜索包含指定content-desc的元素
    fn search_by_content_desc_single(&self, element: &UIElement, target_desc: &str, results: &mut Vec<UIElement>) {
        if let Some(content_desc) = &element.content_desc {
            if content_desc.contains(target_desc) {
                results.push(element.clone());
            }
        }

        for child in &element.children {
            self.search_by_content_desc_single(child, target_desc, results);
        }
    }

    /// 递归搜索包含指定文本的元素
    fn search_elements_text_recursive(&self, element: &UIElement, search_text: &str, results: &mut Vec<UIElement>) {
        // 检查当前元素的文本内容
        if let Some(text) = &element.text {
            if text.to_lowercase().contains(&search_text.to_lowercase()) {
                results.push(element.clone());
            }
        }

        // 检查content-desc
        if let Some(desc) = &element.content_desc {
            if desc.to_lowercase().contains(&search_text.to_lowercase()) {
                results.push(element.clone());
            }
        }

        // 递归搜索子元素
        for child in &element.children {
            self.search_elements_text_recursive(child, search_text, results);
        }
    }

    /// 验证当前页面是否包含指定文本，用于状态检查
    pub async fn verify_page_contains(&self, expected_text: &str, description: &str) -> Result<bool> {
        println!("\n🔍 验证页面状态: {}", description);

        // 等待页面加载
        sleep(Duration::from_secs(2)).await;

        // 获取当前UI结构
        let xml_content = self.dump_ui_hierarchy().await?;
        let elements = self.parse_ui_xml(&xml_content)?;

        // 搜索匹配的元素
        let mut found_elements = Vec::new();
        self.search_elements_text_recursive(&elements, expected_text, &mut found_elements);

        if !found_elements.is_empty() {
            println!("✅ 页面状态验证成功: 找到 '{}' 相关元素", expected_text);
            return Ok(true);
        }

        println!("❌ 页面状态验证失败: 未找到 '{}' 相关元素", expected_text);
        Ok(false)
    }

    /// 执行完整的点击流程：左上角菜单 -> 发现好友 -> 通讯录
    pub async fn execute_contact_flow(&self) -> Result<()> {
        println!("\n🚀 开始执行完整流程: 左上角菜单 -> 发现好友 -> 通讯录");

        // 步骤1: 点击左上角菜单按钮
        println!("\n--- 步骤 1: 点击左上角菜单按钮 ---");
        let step1_success = self.find_and_click_content_desc("菜单", "左上角菜单按钮").await?;

        if !step1_success {
            return Err(anyhow::anyhow!("步骤1失败: 无法找到或点击左上角菜单按钮"));
        }

        // 验证侧边栏是否打开
        let sidebar_opened = self.verify_page_contains("发现好友", "侧边栏是否打开").await?;
        if !sidebar_opened {
            return Err(anyhow::anyhow!("步骤1验证失败: 侧边栏未正确打开"));
        }

        // 步骤2: 点击发现好友
        println!("\n--- 步骤 2: 点击发现好友 ---");
        let step2_success = self.find_and_click_text("发现好友", "发现好友选项").await?;

        if !step2_success {
            return Err(anyhow::anyhow!("步骤2失败: 无法找到或点击发现好友选项"));
        }

        // 验证是否进入发现好友页面
        let friends_page_opened = self.verify_page_contains("通讯录", "发现好友页面").await?;
        if !friends_page_opened {
            return Err(anyhow::anyhow!("步骤2验证失败: 未正确进入发现好友页面"));
        }

        // 步骤3: 点击通讯录
        println!("\n--- 步骤 3: 点击通讯录 ---");
        let step3_success = self.find_and_click_text("通讯录", "通讯录选项").await?;

        if !step3_success {
            return Err(anyhow::anyhow!("步骤3失败: 无法找到或点击通讯录选项"));
        }

        // 验证是否进入通讯录页面
        let contacts_page_opened = self.verify_page_contains("联系人", "通讯录页面").await?;
        if !contacts_page_opened {
            // 尝试其他可能的验证文本
            let alt_verification = self.verify_page_contains("导入", "通讯录页面(备选验证)").await?;
            if !alt_verification {
                println!("⚠️  警告: 通讯录页面验证不确定，但流程已执行完成");
            } else {
                println!("✅ 通讯录页面验证成功(备选方式)");
            }
        } else {
            println!("✅ 通讯录页面验证成功");
        }

        println!("\n🎉 完整流程执行完成！");
        println!("已成功完成: 左上角菜单 -> 发现好友 -> 通讯录");

        // 保存最终状态
        self.take_screenshot("final_contacts_page.png").await?;
        let final_xml = self.dump_ui_hierarchy().await?;
        std::fs::write("final_contacts_ui.json",
            serde_json::to_string_pretty(&self.parse_ui_xml(&final_xml)?)?)?;

        println!("💾 已保存最终页面状态: final_contacts_page.png, final_contacts_ui.json");

        Ok(())
    }
}
