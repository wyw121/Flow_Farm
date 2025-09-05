use anyhow::{Context, Result};
use roxmltree::Document;
use serde::{Deserialize, Serialize};
use tokio::process::Command as TokioCommand;
use std::time::Duration;
use tokio::time::sleep;

pub mod vcf_import_optimized;

pub use vcf_import_optimized::VcfImporter;

// ADB 可执行文件路径
const ADB_PATH: &str = r"D:\leidian\LDPlayer9\adb.exe";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Bounds {
    pub left: i32,
    pub top: i32,
    pub right: i32,
    pub bottom: i32,
}

impl Bounds {
    pub fn from_string(bounds_str: &str) -> Result<Self> {
        // bounds格式: "[left,top][right,bottom]"
        let bounds_str = bounds_str.trim_matches(['[', ']']);
        let parts: Vec<&str> = bounds_str.split("][").collect();

        if parts.len() != 2 {
            return Err(anyhow::anyhow!("无效的bounds格式: {}", bounds_str));
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

        Ok(Bounds {
            left: left_top[0],
            top: left_top[1],
            right: right_bottom[0],
            bottom: right_bottom[1],
        })
    }

    pub fn center_x(&self) -> i32 {
        (self.left + self.right) / 2
    }

    pub fn center_y(&self) -> i32 {
        (self.top + self.bottom) / 2
    }

    pub fn center(&self) -> (i32, i32) {
        (self.center_x(), self.center_y())
    }
}

impl std::fmt::Display for Bounds {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "[{},{}][{},{}]", self.left, self.top, self.right, self.bottom)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UIElement {
    pub tag: String,
    pub class: Option<String>,
    pub text: Option<String>,
    pub content_desc: Option<String>,
    pub resource_id: Option<String>,
    pub package: Option<String>,
    pub bounds: Option<Bounds>,
    pub clickable: bool,
    pub enabled: bool,
    pub focused: bool,
    pub selected: bool,
    pub children: Vec<UIElement>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Contact {
    pub name: String,
    pub phone: String,
    pub address: Option<String>,
    pub profession: Option<String>,
    pub email: Option<String>,
}

impl Contact {
    pub fn from_csv_line(line: &str) -> Result<Contact> {
        let parts: Vec<&str> = line.split(',').collect();
        if parts.len() < 2 {
            return Err(anyhow::anyhow!("联系人格式错误，至少需要姓名和电话"));
        }

        Ok(Contact {
            name: parts[0].trim().to_string(),
            phone: parts[1].trim().to_string(),
            address: if parts.len() > 2 && !parts[2].trim().is_empty() {
                Some(parts[2].trim().to_string())
            } else { None },
            profession: if parts.len() > 3 && !parts[3].trim().is_empty() {
                Some(parts[3].trim().to_string())
            } else { None },
            email: if parts.len() > 4 && !parts[4].trim().is_empty() {
                Some(parts[4].trim().to_string())
            } else { None },
        })
    }
}

pub struct AdbClient {
    device_id: Option<String>,
}

impl AdbClient {
    pub fn new(device_id: Option<String>) -> Self {
        Self { device_id }
    }

    /// 智能执行联系人流程：自动检测当前页面状态并从合适位置开始
    pub async fn execute_smart_contact_flow(&self) -> Result<()> {
        println!("\n🧠 开始智能联系人流程检测...");

        // 获取当前页面状态
        let ui_xml = self.dump_ui_hierarchy().await?;
        let ui_root = self.parse_ui_xml(&ui_xml)?;

        // 检查当前页面状态
        let current_state = self.detect_current_page_state(&ui_root).await?;

        match current_state.as_str() {
            "contacts_page" => {
                println!("✅ 检测到当前在通讯录页面，直接开始关注");
                self.auto_follow_contacts().await?;
            },
            "discover_friends_page" => {
                println!("✅ 检测到当前在发现好友页面，点击通讯录后开始关注");
                // 点击通讯录选项
                if !self.click_contacts_tab().await? {
                    return Err(anyhow::anyhow!("无法点击通讯录选项"));
                }
                tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
                self.auto_follow_contacts().await?;
            },
            "main_page" => {
                println!("✅ 检测到当前在主页，执行完整流程");
                self.execute_contact_flow().await?;
            },
            _ => {
                return Err(anyhow::anyhow!("无法识别当前页面状态，请确保在小红书APP中"));
            }
        }

        Ok(())
    }

    /// 检测当前页面状态
    async fn detect_current_page_state(&self, ui_root: &UIElement) -> Result<String> {
        // 检查是否在通讯录页面（有关注相关按钮且页面较简单）
        let follow_buttons = self.count_follow_buttons(ui_root);
        let followed_buttons = self.count_followed_buttons(ui_root);
        let total_buttons = follow_buttons + followed_buttons;

        let has_contacts_tab = self.find_element_by_text(ui_root, "通讯录").is_some();
        let has_contacts_friends_title = self.find_element_by_text(ui_root, "通讯录好友").is_some();
        let has_discover_title = self.find_element_by_text(ui_root, "发现好友").is_some();

        println!("      🔍 页面检测: 关注按钮={}, 已关注按钮={}, 通讯录标题={}, 发现好友标题={}",
                 follow_buttons, followed_buttons, has_contacts_friends_title, has_discover_title);

        // 如果有"通讯录好友"标题，说明在真正的通讯录页面
        if has_contacts_friends_title && total_buttons > 0 {
            return Ok("contacts_page".to_string());
        }

        // 如果有关注相关按钮且数量不多，且没有通讯录选项卡，可能在通讯录页面
        if total_buttons > 0 && total_buttons < 20 && !has_contacts_tab && !has_discover_title {
            return Ok("contacts_page".to_string());
        }

        // 如果有通讯录选项卡且有发现好友标题，在发现好友页面
        if has_contacts_tab && has_discover_title {
            return Ok("discover_friends_page".to_string());
        }

        // 检查是否有左上角菜单（主页特征）
        if self.find_element_by_content_desc(ui_root, "菜单").is_some() {
            return Ok("main_page".to_string());
        }

        Ok("unknown".to_string())
    }

    /// 统计关注按钮数量（仅"关注"按钮）
    fn count_follow_buttons(&self, ui_root: &UIElement) -> i32 {
        let mut count = 0;
        self.count_follow_buttons_recursive(ui_root, &mut count);
        count
    }

    /// 统计已关注按钮数量
    fn count_followed_buttons(&self, ui_root: &UIElement) -> i32 {
        let mut count = 0;
        self.count_followed_buttons_recursive(ui_root, &mut count);
        count
    }

    /// 递归统计关注按钮
    fn count_follow_buttons_recursive(&self, element: &UIElement, count: &mut i32) {
        if element.clickable && element.enabled {
            let is_follow_button =
                element.text.as_ref().map_or(false, |text| text == "关注") ||
                element.content_desc.as_ref().map_or(false, |desc| desc.contains("关注") && !desc.contains("已关注"));

            if is_follow_button {
                *count += 1;
            }
        }

        for child in &element.children {
            self.count_follow_buttons_recursive(child, count);
        }
    }

    /// 递归统计已关注按钮
    fn count_followed_buttons_recursive(&self, element: &UIElement, count: &mut i32) {
        if element.clickable && element.enabled {
            let is_followed_button =
                element.text.as_ref().map_or(false, |text| text == "已关注") ||
                element.content_desc.as_ref().map_or(false, |desc| desc.contains("已关注"));

            if is_followed_button {
                *count += 1;
            }
        }

        for child in &element.children {
            self.count_followed_buttons_recursive(child, count);
        }
    }

    /// 点击通讯录选项卡
    async fn click_contacts_tab(&self) -> Result<bool> {
        println!("📱 正在点击通讯录选项...");

        let ui_xml = self.dump_ui_hierarchy().await?;
        let ui_root = self.parse_ui_xml(&ui_xml)?;

        // 查找"通讯录"文本对应的可点击父元素
        if let Some(contacts_element) = self.find_contacts_clickable_element(&ui_root) {
            if let Some(bounds) = &contacts_element.bounds {
                let center_x = (bounds.left + bounds.right) / 2;
                let center_y = (bounds.top + bounds.bottom) / 2;

                self.click_coordinates(center_x, center_y).await?;
                println!("✅ 成功点击通讯录选项");
                return Ok(true);
            }
        }

        println!("❌ 未找到可点击的通讯录选项");
        Ok(false)
    }

    /// 查找通讯录可点击元素
    fn find_contacts_clickable_element(&self, ui_root: &UIElement) -> Option<UIElement> {
        self.find_contacts_clickable_recursive(ui_root)
    }

    /// 递归查找通讯录可点击元素
    fn find_contacts_clickable_recursive(&self, element: &UIElement) -> Option<UIElement> {
        // 检查当前元素是否包含"通讯录"文本且可点击
        let has_contacts_text = element.text.as_ref().map_or(false, |text| text.contains("通讯录"));
        let has_contacts_child = element.children.iter().any(|child|
            child.text.as_ref().map_or(false, |text| text.contains("通讯录"))
        );

        if element.clickable && (has_contacts_text || has_contacts_child) {
            return Some(element.clone());
        }

        // 递归检查子元素
        for child in &element.children {
            if let Some(found) = self.find_contacts_clickable_recursive(child) {
                return Some(found);
            }
        }

        None
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
        let bounds = node.attribute("bounds")
            .and_then(|s| Bounds::from_string(s).ok());

        let mut element = UIElement {
            tag: node.tag_name().name().to_string(),
            class: node.attribute("class").map(|s| s.to_string()),
            text: node.attribute("text").map(|s| s.to_string()),
            content_desc: node.attribute("content-desc").map(|s| s.to_string()),
            resource_id: node.attribute("resource-id").map(|s| s.to_string()),
            package: node.attribute("package").map(|s| s.to_string()),
            bounds,
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
            println!("{}  bounds: [{},{}][{},{}]", indent_str, bounds.left, bounds.top, bounds.right, bounds.bottom);
        }

        if element.clickable {
            println!("{}  clickable: true", indent_str);
        }

        for child in &element.children {
            self.print_hierarchy(child, indent + 1);
        }
    }

    /// 通过文本内容查找元素
    fn find_element_by_text(&self, ui_root: &UIElement, text: &str) -> Option<UIElement> {
        self.find_element_by_text_recursive(ui_root, text)
    }

    /// 递归通过文本查找元素
    fn find_element_by_text_recursive(&self, element: &UIElement, text: &str) -> Option<UIElement> {
        if element.text.as_ref().map_or(false, |t| t.contains(text)) {
            return Some(element.clone());
        }

        for child in &element.children {
            if let Some(found) = self.find_element_by_text_recursive(child, text) {
                return Some(found);
            }
        }

        None
    }

    /// 通过内容描述查找元素
    fn find_element_by_content_desc(&self, ui_root: &UIElement, desc: &str) -> Option<UIElement> {
        self.find_element_by_content_desc_recursive(ui_root, desc)
    }

    /// 递归通过内容描述查找元素
    fn find_element_by_content_desc_recursive(&self, element: &UIElement, desc: &str) -> Option<UIElement> {
        if element.content_desc.as_ref().map_or(false, |d| d.contains(desc)) {
            return Some(element.clone());
        }

        for child in &element.children {
            if let Some(found) = self.find_element_by_content_desc_recursive(child, desc) {
                return Some(found);
            }
        }

        None
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

    /// 根据元素bounds点击中心点
    pub async fn click_element_bounds(&self, bounds: &Bounds) -> Result<()> {
        let center_x = bounds.center_x();
        let center_y = bounds.center_y();
        self.click_coordinates(center_x, center_y).await
    }

    /// 根据元素bounds字符串解析坐标并点击中心点（兼容性方法）
    pub async fn click_element_bounds_str(&self, bounds: &str) -> Result<()> {
        let bounds = Bounds::from_string(bounds)?;
        self.click_element_bounds(&bounds).await
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

        // 步骤4: 开始自动关注通讯录好友
        println!("\n--- 步骤 4: 开始自动关注通讯录好友 ---");
        match self.auto_follow_contacts().await {
            Ok(follow_count) => {
                println!("✅ 自动关注完成！成功关注 {} 个好友", follow_count);
            },
            Err(e) => {
                println!("⚠️  自动关注过程中出现错误: {}", e);
                println!("   💡 可能部分用户已关注或页面结构发生变化");
            }
        }

        Ok(())
    }

    /// 自动关注通讯录中的所有好友
    pub async fn auto_follow_contacts(&self) -> Result<i32> {
        println!("🤖 开始自动关注通讯录中的好友...");

        let mut total_followed = 0;
        let mut page_scroll_count = 0;
        let max_pages = 10; // 最多滚动10页，避免无限循环

        loop {
            println!("\n📄 正在处理第 {} 页...", page_scroll_count + 1);

            // 获取当前页面UI
            let ui_xml = self.dump_ui_hierarchy().await?;
            let ui_root = self.parse_ui_xml(&ui_xml)?;

            // 查找所有关注按钮
            let follow_buttons = self.find_follow_buttons(&ui_root).await?;

            if follow_buttons.is_empty() {
                println!("   📝 当前页面没有找到关注按钮");

                // 尝试滚动到下一页
                if page_scroll_count < max_pages {
                    println!("   📜 尝试滚动到下一页...");
                    self.scroll_down().await?;
                    tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
                    page_scroll_count += 1;
                    continue;
                } else {
                    println!("   🏁 已达到最大滚动页数，结束关注");
                    break;
                }
            }

            let buttons_on_page = follow_buttons.len();
            println!("   🎯 找到 {} 个关注按钮", buttons_on_page);

            let mut page_followed = 0;

            // 逐个点击关注按钮
            for (i, button) in follow_buttons.iter().enumerate() {
                println!("      👆 点击第 {} 个关注按钮...", i + 1);

                match self.click_follow_button(button).await {
                    Ok(true) => {
                        page_followed += 1;
                        total_followed += 1;
                        println!("      ✅ 关注成功！");
                    },
                    Ok(false) => {
                        println!("      ⚠️  该用户可能已关注或无法关注");
                    },
                    Err(e) => {
                        println!("      ❌ 关注失败: {}", e);
                    }
                }

                // 每次点击后短暂等待，避免操作过快
                tokio::time::sleep(tokio::time::Duration::from_millis(800)).await;
            }

            println!("   📊 本页关注结果: {}/{} 成功", page_followed, buttons_on_page);

            // 如果本页没有新的关注按钮了，可能是已经全部关注完成
            if page_followed == 0 && buttons_on_page > 0 {
                println!("   💡 本页所有用户可能已关注，尝试下一页...");
            }

            // 滚动到下一页
            if page_scroll_count < max_pages {
                println!("   📜 滚动到下一页...");
                self.scroll_down().await?;
                tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
                page_scroll_count += 1;
            } else {
                println!("   🏁 已处理完所有页面");
                break;
            }
        }

        println!("\n📈 关注统计:");
        println!("   总共关注: {} 个好友", total_followed);
        println!("   处理页数: {} 页", page_scroll_count + 1);

        // 关注完成后，返回主页
        println!("\n🏠 关注完成，返回主页...");
        self.return_to_homepage().await?;

        Ok(total_followed)
    }

    /// 查找页面中的所有关注按钮
    async fn find_follow_buttons(&self, ui_root: &UIElement) -> Result<Vec<UIElement>> {
        let mut buttons = Vec::new();

        // 递归查找关注按钮
        self.find_follow_buttons_recursive(ui_root, &mut buttons);

        Ok(buttons)
    }

    /// 递归查找关注按钮
    fn find_follow_buttons_recursive(&self, element: &UIElement, buttons: &mut Vec<UIElement>) {
        // 查找包含"关注"文本的可点击按钮，但排除已关注的
        if element.clickable && element.enabled {
            let empty_string = String::new();
            let text = element.text.as_ref().unwrap_or(&empty_string);
            let desc = element.content_desc.as_ref().unwrap_or(&empty_string);
            let id = element.resource_id.as_ref().unwrap_or(&empty_string);

            // 检查是否是关注相关按钮
            let is_follow_related =
                text.contains("关注") || text.contains("Follow") || text.contains("关注TA") ||
                desc.contains("关注") || desc.contains("Follow") ||
                id.contains("follow") || id.contains("关注");

            // 检查是否已经关注过了
            let is_already_followed =
                text.contains("已关注") || text.contains("取消关注") ||
                desc.contains("已关注") || desc.contains("取消关注");

            // 只添加需要关注的按钮（关注相关但未关注的）
            if is_follow_related && !is_already_followed {
                buttons.push(element.clone());
                // 调试信息
                println!("      🎯 找到关注按钮: '{}' 位置: {:?}", text, element.bounds);
            } else if is_already_followed {
                // 调试信息：跳过已关注的
                println!("      ⏭️  跳过已关注用户: '{}'", text);
            }
        }

        // 递归检查子元素
        for child in &element.children {
            self.find_follow_buttons_recursive(child, buttons);
        }
    }

    /// 点击关注按钮并验证结果
    async fn click_follow_button(&self, button: &UIElement) -> Result<bool> {
        if let Some(bounds) = &button.bounds {
            // 计算按钮中心点
            let center_x = (bounds.left + bounds.right) / 2;
            let center_y = (bounds.top + bounds.bottom) / 2;

            // 记录点击前的按钮状态
            let before_text = button.text.clone().unwrap_or_default();

            // 点击按钮
            self.click_coordinates(center_x, center_y).await?;

            // 等待UI更新
            tokio::time::sleep(tokio::time::Duration::from_millis(1000)).await;

            // 重新获取UI并检查结果
            let ui_xml = self.dump_ui_hierarchy().await?;
            let ui_root = self.parse_ui_xml(&ui_xml)?;

            // 检查是否关注成功（按钮文本变化）
            if let Some(updated_button) = self.find_button_at_position(&ui_root, center_x, center_y) {
                let after_text = updated_button.text.clone().unwrap_or_default();

                println!("      🔍 按钮文字变化: '{}' -> '{}'", before_text, after_text);

                // 如果按钮文字从"关注"变成了"已关注"或消失，说明关注成功
                if before_text.contains("关注") && !before_text.contains("已关注") {
                    if after_text.contains("已关注") || after_text.contains("取消关注") {
                        println!("      ✅ 按钮状态确认: 关注成功");
                        return Ok(true);
                    } else if after_text.is_empty() {
                        println!("      ✅ 按钮消失确认: 关注成功");
                        return Ok(true);
                    } else if after_text == before_text {
                        println!("      ⚠️  按钮文字未变化，可能已经关注过了");
                        return Ok(false);
                    }
                }
            }

            // 作为备选，检查页面上是否有"已关注"文字（更宽泛的搜索）
            if self.verify_page_contains("已关注", "关注结果验证(备选)").await? {
                println!("      ✅ 页面存在'已关注'文字，确认关注成功");
                return Ok(true);
            }

            // 如果按钮原本就是"已关注"，说明用户已经关注过了
            if before_text.contains("已关注") {
                println!("      💡 用户已经关注过了");
                return Ok(false);
            }

            // 其他情况视为可能成功（避免误判）
            println!("      ❓ 无法明确确定关注结果，假设成功");
            return Ok(true);
        }

        Err(anyhow::anyhow!("无法获取按钮位置信息"))
    }

    /// 在指定位置查找按钮元素
    fn find_button_at_position(&self, ui_root: &UIElement, x: i32, y: i32) -> Option<UIElement> {
        self.find_button_at_position_recursive(ui_root, x, y)
    }

    /// 递归在指定位置查找按钮
    fn find_button_at_position_recursive(&self, element: &UIElement, x: i32, y: i32) -> Option<UIElement> {
        if let Some(bounds) = &element.bounds {
            // 检查点击坐标是否在元素边界内
            if x >= bounds.left && x <= bounds.right && y >= bounds.top && y <= bounds.bottom {
                // 如果是可点击的按钮，返回它
                if element.clickable {
                    return Some(element.clone());
                }
            }
        }

        // 递归检查子元素
        for child in &element.children {
            if let Some(found) = self.find_button_at_position_recursive(child, x, y) {
                return Some(found);
            }
        }

        None
    }

    /// 向下滚动页面
    async fn scroll_down(&self) -> Result<()> {
        // 使用ADB滑动命令向下滚动
        // 从屏幕中间向下滑动
        let default_device = "127.0.0.1:5555";
        let device_id = self.device_id.as_ref().map(|s| s.as_str()).unwrap_or(default_device);
        let cmd = format!("{} -s {} shell input swipe 500 800 500 400 300",
                         ADB_PATH, device_id);

        let output = TokioCommand::new("cmd")
            .args(&["/C", &cmd])
            .output()
            .await
            .context("执行滚动命令失败")?;

        if output.status.success() {
            Ok(())
        } else {
            Err(anyhow::anyhow!("滚动命令执行失败"))
        }
    }

    /// 返回小红书主页
    async fn return_to_homepage(&self) -> Result<()> {
        println!("🏠 准备返回主页...");

        // 方法1: 多次点击返回按钮
        for i in 0..3 {
            println!("   👈 点击返回按钮 ({}/3)...", i + 1);

            // 查找并点击返回按钮
            let ui_xml = self.dump_ui_hierarchy().await?;
            let ui_root = self.parse_ui_xml(&ui_xml)?;

            if let Some(back_button) = self.find_back_button(&ui_root) {
                if let Some(bounds) = &back_button.bounds {
                    let center_x = (bounds.left + bounds.right) / 2;
                    let center_y = (bounds.top + bounds.bottom) / 2;
                    self.click_coordinates(center_x, center_y).await?;
                }
            } else {
                // 如果找不到返回按钮，使用系统返回键
                let default_device = "127.0.0.1:5555";
                let device_id = self.device_id.as_ref().map(|s| s.as_str()).unwrap_or(default_device);
                let cmd = format!("{} -s {} shell input keyevent KEYCODE_BACK",
                                 ADB_PATH, device_id);
                TokioCommand::new("cmd")
                    .args(&["/C", &cmd])
                    .output()
                    .await
                    .context("执行返回键失败")?;
            }

            tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;
        }

        // 方法2: 点击底部导航栏的首页按钮
        println!("   🏠 尝试点击底部首页按钮...");
        let ui_xml = self.dump_ui_hierarchy().await?;
        let ui_root = self.parse_ui_xml(&ui_xml)?;

        if let Some(home_button) = self.find_home_button(&ui_root) {
            if let Some(bounds) = &home_button.bounds {
                let center_x = (bounds.left + bounds.right) / 2;
                let center_y = (bounds.top + bounds.bottom) / 2;
                self.click_coordinates(center_x, center_y).await?;
            }
        }

        tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
        println!("✅ 已返回主页");

        Ok(())
    }

    /// 查找返回按钮
    fn find_back_button(&self, ui_root: &UIElement) -> Option<UIElement> {
        self.find_back_button_recursive(ui_root)
    }

    /// 递归查找返回按钮
    fn find_back_button_recursive(&self, element: &UIElement) -> Option<UIElement> {
        if element.clickable {
            // 检查是否为返回按钮
            let is_back_button =
                element.content_desc.as_ref().map_or(false, |desc|
                    desc.contains("返回") || desc.contains("back") || desc.contains("Back")) ||
                element.text.as_ref().map_or(false, |text|
                    text.contains("返回") || text.contains("back")) ||
                element.resource_id.as_ref().map_or(false, |id|
                    id.contains("back") || id.contains("返回"));

            if is_back_button {
                return Some(element.clone());
            }
        }

        for child in &element.children {
            if let Some(found) = self.find_back_button_recursive(child) {
                return Some(found);
            }
        }

        None
    }

    /// 查找首页按钮（底部导航栏）
    fn find_home_button(&self, ui_root: &UIElement) -> Option<UIElement> {
        self.find_home_button_recursive(ui_root)
    }

    /// 递归查找首页按钮
    fn find_home_button_recursive(&self, element: &UIElement) -> Option<UIElement> {
        if element.clickable {
            // 检查是否为首页按钮
            let is_home_button =
                element.content_desc.as_ref().map_or(false, |desc|
                    desc.contains("首页") || desc.contains("主页") || desc.contains("Home") || desc.contains("home")) ||
                element.text.as_ref().map_or(false, |text|
                    text.contains("首页") || text.contains("主页") || text.contains("Home")) ||
                element.resource_id.as_ref().map_or(false, |id|
                    id.contains("home") || id.contains("首页") || id.contains("main"));

            if is_home_button {
                return Some(element.clone());
            }
        }

        for child in &element.children {
            if let Some(found) = self.find_home_button_recursive(child) {
                return Some(found);
            }
        }

        None
    }

    /// 从CSV文件读取联系人信息
    pub fn load_contacts_from_file(&self, file_path: &str) -> Result<Vec<Contact>> {
        let content = std::fs::read_to_string(file_path)
            .context(format!("无法读取联系人文件: {}", file_path))?;

        let mut contacts = Vec::new();
        for (line_num, line) in content.lines().enumerate() {
            let line = line.trim();
            if line.is_empty() {
                continue;
            }

            match Contact::from_csv_line(line) {
                Ok(contact) => {
                    println!("✅ 解析联系人 {}: {} - {}", line_num + 1, contact.name, contact.phone);
                    contacts.push(contact);
                }
                Err(e) => {
                    println!("⚠️  跳过第{}行，格式错误: {}", line_num + 1, e);
                }
            }
        }

        println!("📞 总共解析到 {} 个联系人", contacts.len());
        Ok(contacts)
    }

    /// 向Android设备添加单个联系人
    pub async fn add_contact_to_device(&self, contact: &Contact) -> Result<bool> {
        println!("📱 正在添加联系人: {} - {}", contact.name, contact.phone);

        // 构建联系人插入命令
        let mut cmd = TokioCommand::new(ADB_PATH);
        if let Some(device) = &self.device_id {
            cmd.args(&["-s", device]);
        }

        // 使用Android的content provider插入联系人
        let insert_cmd = format!(
            "content insert --uri content://com.android.contacts/raw_contacts --bind account_type:s:null --bind account_name:s:null"
        );

        cmd.args(&["shell", &insert_cmd]);

        let output = cmd.output().await
            .context("执行联系人插入命令失败")?;

        if !output.status.success() {
            let error = String::from_utf8_lossy(&output.stderr);
            println!("❌ 插入联系人失败: {}", error);
            return Ok(false);
        }

        // 获取插入的raw_contact_id
        let output_str = String::from_utf8_lossy(&output.stdout);
        println!("📄 插入结果: {}", output_str.trim());

        // 简化实现：使用adb shell am命令启动联系人添加意图
        self.add_contact_via_intent(contact).await
    }

    /// 通过Android Intent添加联系人（更可靠的方法）
    async fn add_contact_via_intent(&self, contact: &Contact) -> Result<bool> {
        let mut cmd = TokioCommand::new(ADB_PATH);
        if let Some(device) = &self.device_id {
            cmd.args(&["-s", device]);
        }

        // 构建Intent命令来添加联系人
        let mut intent_cmd = format!(
            "am start -a android.intent.action.INSERT -t vnd.android.cursor.dir/contact -e name '{}' -e phone '{}'",
            contact.name, contact.phone
        );

        // 添加可选字段
        if let Some(email) = &contact.email {
            intent_cmd.push_str(&format!(" -e email '{}'", email));
        }

        cmd.args(&["shell", &intent_cmd]);

        let output = cmd.output().await
            .context("执行联系人Intent命令失败")?;

        if output.status.success() {
            println!("✅ 成功启动联系人添加界面: {}", contact.name);
            // 等待界面加载
            sleep(Duration::from_secs(2)).await;

            // 尝试自动点击保存按钮
            self.try_save_contact().await?;

            Ok(true)
        } else {
            let error = String::from_utf8_lossy(&output.stderr);
            println!("❌ 启动联系人添加失败: {}", error);
            Ok(false)
        }
    }

    /// 尝试点击保存按钮来保存联系人
    async fn try_save_contact(&self) -> Result<()> {
        println!("🔍 尝试查找并点击保存按钮...");

        // 等待页面加载
        sleep(Duration::from_secs(1)).await;

        // 获取当前页面UI
        let xml_content = self.dump_ui_hierarchy().await?;
        let root_element = self.parse_ui_xml(&xml_content)?;

        // 搜索保存相关的按钮
        let save_texts = ["保存", "确定", "完成", "Save", "Done", "OK"];

        for save_text in &save_texts {
            let found_elements = self.find_elements_by_text(&root_element, save_text);

            for element in found_elements {
                if element.clickable {
                    if let Some(bounds) = &element.bounds {
                        println!("📍 找到保存按钮: {} 位置: [{},{}][{},{}]", save_text,
                                bounds.left, bounds.top, bounds.right, bounds.bottom);
                        self.click_element_bounds(bounds).await?;
                        sleep(Duration::from_secs(1)).await;
                        return Ok(());
                    }
                }
            }
        }

        // 如果没找到保存按钮，尝试点击右上角（通常是保存位置）
        println!("🎯 未找到明确的保存按钮，尝试点击右上角区域...");
        self.click_coordinates(1000, 100).await?;

        Ok(())
    }

    /// 批量导入联系人到设备
    pub async fn import_contacts_to_device(&self, file_path: &str) -> Result<()> {
        println!("🚀 开始批量导入联系人...");
        println!("📁 文件路径: {}", file_path);

        // 加载联系人
        let contacts = self.load_contacts_from_file(file_path)?;

        if contacts.is_empty() {
            println!("❌ 没有找到有效的联系人数据");
            return Ok(());
        }

        println!("📞 准备导入 {} 个联系人", contacts.len());

        let mut success_count = 0;
        let mut failed_count = 0;

        // 先尝试打开联系人应用
        self.open_contacts_app().await?;

        for (index, contact) in contacts.iter().enumerate() {
            println!("\n--- 处理联系人 {}/{} ---", index + 1, contacts.len());

            match self.add_contact_to_device(contact).await {
                Ok(true) => {
                    success_count += 1;
                    println!("✅ 成功导入: {}", contact.name);
                }
                Ok(false) => {
                    failed_count += 1;
                    println!("❌ 导入失败: {}", contact.name);
                }
                Err(e) => {
                    failed_count += 1;
                    println!("❌ 导入出错: {} - {}", contact.name, e);
                }
            }

            // 两次导入间隔，避免过快操作
            if index < contacts.len() - 1 {
                println!("⏳ 等待 3 秒后继续...");
                sleep(Duration::from_secs(3)).await;
            }
        }

        println!("\n📊 导入完成统计:");
        println!("✅ 成功: {} 个联系人", success_count);
        println!("❌ 失败: {} 个联系人", failed_count);
        println!("📞 总计: {} 个联系人", contacts.len());

        // 保存导入报告
        let report = format!(
            "Contact Import Report\nTime: {}\nSuccess: {}\nFailed: {}\nTotal: {}",
            chrono::Utc::now().format("%Y-%m-%d %H:%M:%S"),
            success_count, failed_count, contacts.len()
        );

        std::fs::write("contact_import_report.txt", report)?;
        println!("📄 导入报告已保存到: contact_import_report.txt");

        Ok(())
    }

    /// 打开联系人应用
    async fn open_contacts_app(&self) -> Result<()> {
        println!("📱 正在打开联系人应用...");

        let mut cmd = TokioCommand::new(ADB_PATH);
        if let Some(device) = &self.device_id {
            cmd.args(&["-s", device]);
        }

        // 尝试启动联系人应用
        cmd.args(&["shell", "am", "start", "-n", "com.android.contacts/.activities.PeopleActivity"]);

        let output = cmd.output().await.context("启动联系人应用失败")?;

        if output.status.success() {
            println!("✅ 联系人应用启动成功");
            sleep(Duration::from_secs(3)).await;
        } else {
            // 尝试通用方式
            println!("⚠️  尝试通用方式启动联系人...");
            let mut cmd2 = TokioCommand::new(ADB_PATH);
            if let Some(device) = &self.device_id {
                cmd2.args(&["-s", device]);
            }
            cmd2.args(&["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "content://contacts/people"]);
            cmd2.output().await.context("通用方式启动联系人应用失败")?;
            sleep(Duration::from_secs(3)).await;
        }

        Ok(())
    }
}
