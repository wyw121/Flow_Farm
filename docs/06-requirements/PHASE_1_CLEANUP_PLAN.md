# Phase 1: 代码清理执行计划

## 🗂️ 删除清单和执行步骤

### 第一步: 员工客户端 (Tauri) 清理

#### 1.1 删除 ADB 和设备管理相关文件

```bash
# 在 employee-client/ 目录下执行

# 删除 ADB 管理器
rm src-tauri/src/adb_manager.rs

# 删除小红书自动化模块  
rm src-tauri/src/xiaohongshu_automator.rs

# 删除联系人管理器
rm src-tauri/src/contact_manager.rs

# 删除自动化命令
rm src-tauri/src/commands/automation.rs
rm src-tauri/src/commands/contacts.rs  
rm src-tauri/src/commands/devices.rs

# 删除整个 ADB 工具目录
rm -rf ../adb_xml_reader/
```

#### 1.2 更新 main.rs - 移除已删除模块的引用

需要删除的导入：
```rust
// 删除这些导入
mod contact_manager;
mod adb_manager; 
mod xiaohongshu_automator;

use contact_manager::{ContactManager, ContactList};
use adb_manager::AdbManager;
use xiaohongshu_automator::{XiaohongshuAutomator, AutomationTask};
```

需要删除的 AppState 字段：
```rust
pub struct AppState {
    pub devices: Arc<Mutex<HashMap<String, DeviceInfo>>>,  // 保留，改为GPS设备
    pub tasks: Arc<Mutex<HashMap<String, models::TaskInfo>>>, // 保留，改为拜访任务
    // 删除以下字段:
    // pub contact_manager: Arc<ContactManager>,
    // pub adb_manager: Arc<AdbManager>, 
    // pub xiaohongshu_automator: Arc<XiaohongshuAutomator>,
    // pub automation_tasks: Arc<Mutex<HashMap<String, AutomationTask>>>,
    // pub contact_lists: Arc<Mutex<HashMap<String, ContactList>>>,
    pub auth_service: Arc<AuthService>, // 保留
}
```

需要删除的命令注册：
```rust
// 删除这些命令
// commands::load_contacts_from_file,
// commands::get_contact_lists, 
// commands::search_contacts,
// commands::get_adb_devices,
// commands::connect_adb_device,
// commands::disconnect_adb_device,
// commands::check_adb_available,
// commands::get_device_info,
// commands::create_xiaohongshu_task,
// commands::start_xiaohongshu_task,
// commands::pause_xiaohongshu_task,
// commands::stop_xiaohongshu_task,
// commands::get_automation_tasks,
// commands::get_task_results,
// commands::export_task_results,
// commands::check_xiaohongshu_app,
```

#### 1.3 更新 Cargo.toml - 移除不需要的依赖

```toml
# employee-client/src-tauri/Cargo.toml
# 删除或注释掉这些依赖:
# adb_client = "0.8"       # ADB设备连接
# selenium = "0.1"         # 浏览器自动化  
# webscraper = "0.3"       # 网页抓取

# 新增市场调研相关依赖
reqwest = { version = "0.11", features = ["json", "multipart"] }
image = "0.24"                    # 图像处理
base64 = "0.21"                   # Base64编码
mime_guess = "2.0"                # MIME类型检测
geo = "0.26"                      # 地理位置计算
```

#### 1.4 更新前端界面文件

```bash
# 删除设备管理相关的HTML/CSS/JS
rm src-web/device-*.html
rm src-web/device-*.css  
rm src-web/automation-*.js

# 重命名现有文件以反映新功能
mv src-web/index.html src-web/visit-tracker.html
mv src-web/styles.css src-web/visit-styles.css
```

### 第二步: 服务器后端 (Rust) 清理

#### 2.1 删除处理器 (Handlers)

```bash
# 在 server-backend/src/ 目录下执行
rm handlers/social_platforms.rs
rm handlers/device_management.rs  
rm handlers/automation_tasks.rs
rm handlers/contact_import.rs
```

#### 2.2 更新 models.rs - 移除社交媒体模型

需要删除的结构体和枚举：
```rust
// 删除这些数据模型
struct SocialAccount { /* ... */ }
struct FollowTask { /* ... */ }  
struct DeviceConnection { /* ... */ }
struct AutomationResult { /* ... */ }
struct ContactImport { /* ... */ }
struct PlatformConfiguration { /* ... */ }

enum SocialPlatform { /* ... */ }
enum TaskStatus { /* ... */ }
enum DeviceStatus { /* ... */ }
```

保留并重构的模型：
```rust
// 更新用户角色枚举
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::Type)]
#[sqlx(rename_all = "snake_case")]
pub enum UserRole {
    SystemAdmin,      // 保持不变
    ResearchManager,  // 原 UserAdmin 重命名
    FieldWorker,      // 原 Employee 重命名
}
```

#### 2.3 删除服务 (Services)

```bash
# 删除社交媒体相关服务
rm services/social_platform_service.rs
rm services/device_service.rs
rm services/automation_service.rs
rm services/contact_service.rs
```

#### 2.4 更新路由配置

在 `server.rs` 中删除相关路由：
```rust
// 删除这些路由组
// .route("/api/social-platforms/*", /* ... */)
// .route("/api/devices/*", /* ... */)  
// .route("/api/automation/*", /* ... */)
// .route("/api/contacts/*", /* ... */)
```

### 第三步: 服务器前端 (React) 清理

#### 3.1 删除组件目录

```bash
# 在 server-frontend/src/ 目录下执行
rm -rf components/DeviceManagement/
rm -rf components/SocialPlatforms/
rm -rf components/AutomationTasks/ 
rm -rf components/ContactImport/
```

#### 3.2 删除页面组件

```bash
# 删除设备和自动化相关页面
rm pages/UserAdmin/DeviceManagement.tsx
rm pages/UserAdmin/AutomationTasks.tsx
rm pages/UserAdmin/ContactManagement.tsx
rm pages/UserAdmin/SocialPlatforms.tsx
```

#### 3.3 更新服务层

```bash
# 删除API服务
rm services/deviceService.ts
rm services/socialPlatformService.ts
rm services/automationService.ts
rm services/contactService.ts
```

#### 3.4 更新路由配置

在 `App.tsx` 中删除相关路由：
```typescript
// 删除这些路由
// <Route path="/devices" element={<DeviceManagement />} />
// <Route path="/automation" element={<AutomationTasks />} />  
// <Route path="/contacts" element={<ContactManagement />} />
// <Route path="/social-platforms" element={<SocialPlatforms />} />
```

#### 3.5 更新包依赖

```json
// server-frontend/package.json  
// 删除这些依赖:
// "adb-utils": "^2.1.0"
// "social-platform-apis": "^1.0.0"  
// "device-management": "^1.0.0"

// 添加新的依赖:
"react-beautiful-dnd": "^13.1.0",     // 拖拽排序（问卷设计）
"echarts": "^5.4.0",                  // 图表库
"echarts-for-react": "^3.0.0",        
"react-quill": "^2.0.0",              // 富文本编辑器
"qrcode.react": "^3.1.0",             // 二维码生成
"react-map-gl": "^7.1.0",             // 地图组件
"mapbox-gl": "^2.15.0"                // 地图引擎
```

### 第四步: 数据库清理

#### 4.1 创建迁移脚本

```sql
-- server-backend/migrations/001_cleanup_social_media.sql

BEGIN TRANSACTION;

-- 备份现有用户数据
CREATE TABLE IF NOT EXISTS backup_users AS SELECT * FROM users;
CREATE TABLE IF NOT EXISTS backup_companies AS SELECT * FROM companies;

-- 删除社交媒体相关表
DROP TABLE IF EXISTS social_accounts;
DROP TABLE IF EXISTS follow_tasks;
DROP TABLE IF EXISTS contact_imports; 
DROP TABLE IF EXISTS device_connections;
DROP TABLE IF EXISTS automation_results;
DROP TABLE IF EXISTS platform_configurations;
DROP TABLE IF EXISTS contact_lists;
DROP TABLE IF EXISTS search_results;

-- 更新用户角色
UPDATE users SET role = 'research_manager' WHERE role = 'user_admin';
UPDATE users SET role = 'field_worker' WHERE role = 'employee';
-- system_admin 保持不变

-- 删除相关配置
DELETE FROM system_configs WHERE config_key LIKE 'social_%';
DELETE FROM system_configs WHERE config_key LIKE 'device_%'; 
DELETE FROM system_configs WHERE config_key LIKE 'automation_%';
DELETE FROM system_configs WHERE config_key LIKE 'xiaohongshu_%';
DELETE FROM system_configs WHERE config_key LIKE 'douyin_%';

-- 添加新的配置
INSERT OR REPLACE INTO system_configs (config_key, config_value, description) VALUES
('business_type', 'market_research', '业务类型：市场调研'),
('max_visit_duration_hours', '8', '最大拜访时长（小时）'),
('gps_accuracy_threshold_meters', '100', 'GPS精度阈值（米）'),
('photo_watermark_enabled', 'true', '照片水印功能'),
('voice_to_text_enabled', 'true', '语音转文字功能'),
('offline_sync_enabled', 'true', '离线同步功能'),
('expense_approval_required', 'true', '费用审批必需');

COMMIT;
```

### 第五步: 配置文件更新

#### 5.1 更新 .env 文件

```bash
# server-backend/.env
# 删除社交媒体相关配置
# XIAOHONGSHU_API_KEY=
# DOUYIN_API_KEY=
# ADB_PATH=

# 添加新的第三方服务配置
SPEECH_TO_TEXT_PROVIDER=xfyun
XFYUN_APP_ID=your_app_id
XFYUN_API_SECRET=your_secret  
XFYUN_API_KEY=your_key

INVOICE_OCR_PROVIDER=baidu
BAIDU_OCR_API_KEY=your_key
BAIDU_OCR_SECRET_KEY=your_secret

MAP_PROVIDER=amap
AMAP_API_KEY=your_amap_key
```

#### 5.2 更新 Tauri 配置

```json
// employee-client/src-tauri/tauri.conf.json
{
  "tauri": {
    "allowlist": {
      // 删除ADB相关权限
      // "shell": { "sidecar": true },
      
      // 添加新权限
      "camera": { "all": true },      // 拍照功能
      "microphone": { "all": true },  // 录音功能  
      "geolocation": { "all": true }  // GPS定位
    }
  }
}
```

### 第六步: 验证和测试

#### 6.1 编译检查

```bash
# 检查后端编译
cd server-backend
cargo check
cargo build

# 检查前端编译  
cd ../server-frontend
npm run build

# 检查Tauri客户端编译
cd ../employee-client  
cargo tauri build
```

#### 6.2 运行基础测试

```bash
# 后端测试
cd server-backend
cargo test

# 前端测试
cd ../server-frontend  
npm test

# 启动开发服务器验证
cargo run  # 后端
npm run dev  # 前端
```

### 第七步: 清理验证清单

- [ ] 删除所有 ADB 相关文件和代码
- [ ] 删除小红书/抖音自动化模块
- [ ] 删除联系人管理和导入功能
- [ ] 删除设备连接和管理功能  
- [ ] 更新用户角色和权限系统
- [ ] 清理数据库表和配置
- [ ] 更新前端组件和路由
- [ ] 更新依赖包配置
- [ ] 验证编译和基础功能
- [ ] 确保测试通过

---

## ⚠️ 重要注意事项

1. **备份数据**: 在执行任何删除操作前，确保已备份重要数据
2. **分步执行**: 建议按顺序执行，每步完成后验证
3. **Git 提交**: 每个大步骤完成后创建Git提交点
4. **回滚计划**: 如遇问题，准备好回滚到上一个稳定状态
5. **团队协调**: 如果是多人开发，提前通知团队成员

完成 Phase 1 后，项目将彻底摆脱社交媒体自动化的历史包袱，为垂直领域功能开发提供干净的代码基础。