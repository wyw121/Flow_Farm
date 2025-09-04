use crate::adb_manager::{AdbManager, AdbCommandResult};
use crate::contact_manager::{Contact, ContactList};
use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use tracing::{info, warn, error, debug};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct XiaohongshuConfig {
    pub device_id: String,
    pub search_delay_ms: u64,          // 搜索间隔时间
    pub scroll_delay_ms: u64,          // 滚动间隔时间
    pub tap_delay_ms: u64,             // 点击间隔时间
    pub max_search_results: usize,     // 最大搜索结果数
    pub enable_screenshots: bool,      // 是否启用截图
    pub screenshot_dir: String,        // 截图保存目录
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct SearchResult {
    pub contact_id: String,
    pub contact_name: String,
    pub search_keyword: String,
    pub found: bool,
    pub user_info: Option<XiaohongshuUser>,
    pub error: Option<String>,
    pub screenshot_path: Option<String>,
    pub search_time: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct XiaohongshuUser {
    pub username: Option<String>,
    pub display_name: Option<String>,
    pub follower_count: Option<String>,
    pub following_count: Option<String>,
    pub note_count: Option<String>,
    pub is_verified: Option<bool>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AutomationTask {
    pub id: String,
    pub name: String,
    pub device_id: String,
    pub contact_list: ContactList,
    pub config: XiaohongshuConfig,
    pub status: String, // created, running, paused, completed, failed
    pub progress: f64,
    pub current_contact_index: usize,
    pub results: Vec<SearchResult>,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub updated_at: chrono::DateTime<chrono::Utc>,
    pub started_at: Option<chrono::DateTime<chrono::Utc>>,
    pub completed_at: Option<chrono::DateTime<chrono::Utc>>,
}

#[derive(Clone)]
pub struct XiaohongshuAutomator {
    adb: AdbManager,
}

impl XiaohongshuAutomator {
    pub fn new(adb_manager: AdbManager) -> Self {
        Self {
            adb: adb_manager,
        }
    }

    /// 创建自动化任务
    pub fn create_task(
        &self,
        name: String,
        device_id: String,
        contact_list: ContactList,
        config: XiaohongshuConfig,
    ) -> AutomationTask {
        let task_id = uuid::Uuid::new_v4().to_string();

        AutomationTask {
            id: task_id,
            name,
            device_id,
            contact_list,
            config,
            status: "created".to_string(),
            progress: 0.0,
            current_contact_index: 0,
            results: Vec::new(),
            created_at: chrono::Utc::now(),
            updated_at: chrono::Utc::now(),
            started_at: None,
            completed_at: None,
        }
    }

    /// 检查小红书应用是否可用
    pub async fn check_xiaohongshu_app(&self, device_id: &str) -> Result<bool> {
        info!("Checking Xiaohongshu app on device: {}", device_id);

        // 小红书包名
        let package_name = "com.xingin.xhs";

        // 检查应用是否安装
        let is_installed = self.adb.is_app_installed(device_id, package_name).await?;

        if !is_installed {
            warn!("Xiaohongshu app is not installed on device: {}", device_id);
            return Ok(false);
        }

        info!("Xiaohongshu app is available on device: {}", device_id);
        Ok(true)
    }

    /// 启动小红书应用
    pub async fn launch_xiaohongshu(&self, device_id: &str) -> Result<AdbCommandResult> {
        info!("Launching Xiaohongshu app on device: {}", device_id);

        let package_name = "com.xingin.xhs";
        let activity_name = "com.xingin.xhs.index.v2.IndexActivityV2";

        let result = self.adb.start_app(device_id, package_name, Some(activity_name)).await?;

        if result.success {
            info!("Xiaohongshu app launched successfully");
            // 等待应用启动
            self.adb.wait(3000).await;
        } else {
            error!("Failed to launch Xiaohongshu app: {:?}", result.error);
        }

        Ok(result)
    }

    /// 执行搜索任务
    pub async fn run_search_task(&self, mut task: AutomationTask) -> Result<AutomationTask> {
        info!("Starting search task: {} with {} contacts", task.name, task.contact_list.total_count);

        task.status = "running".to_string();
        task.started_at = Some(chrono::Utc::now());
        task.updated_at = chrono::Utc::now();

        // 检查小红书应用
        if !self.check_xiaohongshu_app(&task.device_id).await? {
            task.status = "failed".to_string();
            return Err(anyhow::anyhow!("Xiaohongshu app not available"));
        }

        // 启动小红书应用
        let launch_result = self.launch_xiaohongshu(&task.device_id).await?;
        if !launch_result.success {
            task.status = "failed".to_string();
            return Err(anyhow::anyhow!("Failed to launch Xiaohongshu app"));
        }

        // 创建截图目录
        if task.config.enable_screenshots {
            std::fs::create_dir_all(&task.config.screenshot_dir)
                .context("Failed to create screenshot directory")?;
        }

        // 遍历联系人进行搜索
        let total_contacts = task.contact_list.contacts.len();

        for (index, contact) in task.contact_list.contacts.iter().enumerate() {
            if task.status != "running" {
                break; // 任务被停止
            }

            task.current_contact_index = index;
            task.progress = (index as f64) / (total_contacts as f64) * 100.0;
            task.updated_at = chrono::Utc::now();

            info!("Searching contact {}/{}: {}", index + 1, total_contacts, contact.name);

            // 执行搜索
            let search_result = self.search_contact(&task.config, contact).await;
            task.results.push(search_result);

            // 延迟
            self.adb.wait(task.config.search_delay_ms).await;
        }

        task.status = "completed".to_string();
        task.progress = 100.0;
        task.completed_at = Some(chrono::Utc::now());
        task.updated_at = chrono::Utc::now();

        info!("Search task completed: {} results", task.results.len());
        Ok(task)
    }

    /// 搜索单个联系人
    async fn search_contact(&self, config: &XiaohongshuConfig, contact: &Contact) -> SearchResult {
        let mut result = SearchResult {
            contact_id: contact.id.clone(),
            contact_name: contact.name.clone(),
            search_keyword: String::new(),
            found: false,
            user_info: None,
            error: None,
            screenshot_path: None,
            search_time: chrono::Utc::now(),
        };

        // 确定搜索关键词
        let search_keyword = if let Some(username) = &contact.username {
            username.clone()
        } else {
            contact.name.clone()
        };

        result.search_keyword = search_keyword.clone();

        // 执行搜索流程
        match self.perform_search(&config.device_id, &search_keyword, config).await {
            Ok(user_info) => {
                result.found = true;
                result.user_info = user_info;
            }
            Err(e) => {
                error!("Failed to search contact {}: {}", contact.name, e);
                result.error = Some(e.to_string());
            }
        }

        // 截图
        if config.enable_screenshots {
            let screenshot_name = format!("{}_{}.png",
                contact.id,
                chrono::Utc::now().format("%Y%m%d_%H%M%S"));
            let screenshot_path = format!("{}/{}", config.screenshot_dir, screenshot_name);

            if let Ok(screenshot_result) = self.adb.screenshot(&config.device_id, &screenshot_path).await {
                if screenshot_result.success {
                    result.screenshot_path = Some(screenshot_path);
                }
            }
        }

        result
    }

    /// 执行具体的搜索操作
    async fn perform_search(
        &self,
        device_id: &str,
        keyword: &str,
        config: &XiaohongshuConfig,
    ) -> Result<Option<XiaohongshuUser>> {
        debug!("Performing search for keyword: {}", keyword);

        // 点击搜索框 (坐标可能需要根据实际应用调整)
        self.tap_search_box(device_id).await?;

        // 清空搜索框
        self.clear_search_box(device_id).await?;

        // 输入搜索关键词
        self.adb.input_text(device_id, keyword).await?;
        self.adb.wait(config.tap_delay_ms).await;

        // 点击搜索按钮或按回车
        self.adb.press_key(device_id, 66).await?; // Enter key
        self.adb.wait(config.search_delay_ms).await;

        // 点击用户标签页 (如果存在)
        self.tap_user_tab(device_id).await?;
        self.adb.wait(config.tap_delay_ms).await;

        // 尝试解析搜索结果
        let user_info = self.parse_search_results(device_id, keyword).await?;

        Ok(user_info)
    }

    /// 点击搜索框
    async fn tap_search_box(&self, device_id: &str) -> Result<()> {
        // 这些坐标需要根据实际的小红书应用界面调整
        // 通常搜索框在屏幕顶部中央
        let x = 540; // 假设屏幕宽度1080
        let y = 100; // 假设搜索框在顶部

        self.adb.tap(device_id, x, y).await?;
        Ok(())
    }

    /// 清空搜索框
    async fn clear_search_box(&self, device_id: &str) -> Result<()> {
        // 全选文本
        self.adb.press_key(device_id, 113).await?; // Ctrl+A
        self.adb.wait(200).await;

        // 删除文本
        self.adb.press_key(device_id, 67).await?; // Delete key
        self.adb.wait(200).await;

        Ok(())
    }

    /// 点击用户标签页
    async fn tap_user_tab(&self, device_id: &str) -> Result<()> {
        // 假设用户标签在搜索结果页面的某个位置
        let x = 200; // 需要根据实际界面调整
        let y = 300;

        self.adb.tap(device_id, x, y).await?;
        Ok(())
    }

    /// 解析搜索结果 (简化版本，实际需要结合OCR或UI分析)
    async fn parse_search_results(&self, _device_id: &str, keyword: &str) -> Result<Option<XiaohongshuUser>> {
        // 这里是一个简化的实现
        // 实际应用中需要使用OCR或其他技术来解析界面内容

        debug!("Parsing search results for: {}", keyword);

        // 等待搜索结果加载
        self.adb.wait(2000).await;

        // 检查是否有搜索结果
        // 这里返回一个模拟的用户信息
        Ok(Some(XiaohongshuUser {
            username: Some(keyword.to_string()),
            display_name: Some(format!("用户_{}", keyword)),
            follower_count: Some("1000".to_string()),
            following_count: Some("500".to_string()),
            note_count: Some("50".to_string()),
            is_verified: Some(false),
        }))
    }

    /// 暂停任务
    pub async fn pause_task(&self, task: &AutomationTask) -> Result<AutomationTask> {
        let mut updated_task = task.clone();
        if updated_task.status == "running" {
            updated_task.status = "paused".to_string();
            updated_task.updated_at = chrono::Utc::now();
            info!("Task paused: {}", updated_task.name);
        }
        Ok(updated_task)
    }

    /// 恢复任务
    pub async fn resume_task(&self, task: &AutomationTask) -> Result<AutomationTask> {
        let mut updated_task = task.clone();
        if updated_task.status == "paused" {
            updated_task.status = "running".to_string();
            updated_task.updated_at = chrono::Utc::now();
            info!("Task resumed: {}", updated_task.name);
        }
        Ok(updated_task)
    }

    /// 停止任务
    pub async fn stop_task(&self, task: &AutomationTask) -> Result<AutomationTask> {
        let mut updated_task = task.clone();
        updated_task.status = "stopped".to_string();
        updated_task.updated_at = chrono::Utc::now();
        updated_task.completed_at = Some(chrono::Utc::now());
        info!("Task stopped: {}", updated_task.name);
        Ok(updated_task)
    }

    /// 导出搜索结果
    pub async fn export_results(&self, task: &AutomationTask, file_path: &str) -> Result<()> {
        let mut content = String::new();

        content.push_str(&format!("# 小红书搜索结果报告\n"));
        content.push_str(&format!("任务名称: {}\n", task.name));
        content.push_str(&format!("设备ID: {}\n", task.device_id));
        content.push_str(&format!("开始时间: {}\n",
            task.started_at.map(|t| t.format("%Y-%m-%d %H:%M:%S").to_string())
                .unwrap_or_else(|| "未开始".to_string())));
        content.push_str(&format!("完成时间: {}\n",
            task.completed_at.map(|t| t.format("%Y-%m-%d %H:%M:%S").to_string())
                .unwrap_or_else(|| "未完成".to_string())));
        content.push_str(&format!("总联系人数: {}\n", task.contact_list.total_count));
        content.push_str(&format!("成功找到: {}\n",
            task.results.iter().filter(|r| r.found).count()));
        content.push_str(&format!("搜索失败: {}\n\n",
            task.results.iter().filter(|r| !r.found).count()));

        content.push_str("详细结果:\n");
        content.push_str("联系人姓名,搜索关键词,是否找到,用户名,显示名,粉丝数,关注数,笔记数,认证状态,错误信息\n");

        for result in &task.results {
            let user_info = result.user_info.as_ref();
            content.push_str(&format!(
                "{},{},{},{},{},{},{},{},{},{}\n",
                result.contact_name,
                result.search_keyword,
                if result.found { "是" } else { "否" },
                user_info.and_then(|u| u.username.as_ref()).map_or("", |v| v),
                user_info.and_then(|u| u.display_name.as_ref()).map_or("", |v| v),
                user_info.and_then(|u| u.follower_count.as_ref()).map_or("", |v| v),
                user_info.and_then(|u| u.following_count.as_ref()).map_or("", |v| v),
                user_info.and_then(|u| u.note_count.as_ref()).map_or("", |v| v),
                user_info.and_then(|u| u.is_verified.as_ref())
                    .map(|v| if *v { "是" } else { "否" }).unwrap_or(""),
                result.error.as_ref().map_or("", |v| v)
            ));
        }

        std::fs::write(file_path, content)
            .context("Failed to save results file")?;

        info!("Results exported to: {}", file_path);
        Ok(())
    }
}
