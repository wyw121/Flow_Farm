# TaskFleet - 多端协同设计方案

**文档版本**: 1.0  
**创建日期**: 2025年10月28日  
**目的**: 详细说明 Web端 和 桌面端 的功能分工和协同策略

---

## 🎯 设计理念

### 核心原则

**1. 双端都支持两种角色** ✅
- 项目经理可以使用 Web端 和 桌面端
- 员工也可以使用 Web端 和 桌面端
- 根据使用场景自由选择

**2. 发挥各端优势** ✅
- Web端: 全功能,适合复杂操作
- 桌面端: 高效快捷,适合日常使用

**3. 数据完全同步** ✅
- 两端数据实时同步
- 在任何端的操作都会立即反映到另一端

---

## 📊 功能分工详解

### Web端 (全功能版)

#### 项目经理功能

**1. 项目管理** (完整)
- ✅ 创建新项目
- ✅ 编辑项目信息
- ✅ 归档/删除项目
- ✅ 项目概览仪表盘
- ✅ 项目进度可视化 (甘特图/看板)

**2. 任务管理** (完整)
- ✅ 创建单个任务
- ✅ 批量创建任务
- ✅ CSV/Excel 批量导入
- ✅ 任务模板管理
- ✅ 智能任务分配
- ✅ 任务依赖关系
- ✅ 任务优先级管理
- ✅ 截止日期提醒

**3. 团队管理** (完整)
- ✅ 邀请成员
- ✅ 成员权限管理
- ✅ 成员工作量查看
- ✅ 成员效率分析

**4. 数据统计** (完整)
- ✅ 详细的统计报表
- ✅ 多维度数据分析
- ✅ 自定义图表
- ✅ 数据导出 (PDF/Excel)
- ✅ 趋势预测

**5. 系统设置** (完整)
- ✅ 项目配置
- ✅ 通知设置
- ✅ 个人资料管理

---

#### 员工功能

**1. 任务查看** (完整)
- ✅ 我的任务列表
- ✅ 任务详情查看
- ✅ 任务搜索和筛选
- ✅ 任务排序 (按优先级/日期)

**2. 任务执行** (完整)
- ✅ 更新任务状态
- ✅ 添加任务备注
- ✅ 上传附件 (大文件)
- ✅ 记录工作时间

**3. 个人统计** (完整)
- ✅ 个人完成任务数
- ✅ 个人工作量趋势
- ✅ 个人效率分析

---

### 桌面客户端 (精简高效版)

#### 项目经理功能 (精简版)

**1. 快速查看** ⚡
- ✅ 项目进度概览
- ✅ 待处理任务提醒
- ✅ 关键统计数据
- ⚠️ 简化的图表 (饼图/柱状图)

**2. 快速操作** ⚡
- ✅ 创建单个任务
- ✅ 分配任务给员工
- ✅ 审批任务完成
- ❌ 批量操作 (建议用Web端)

**3. 通知中心** ⚡
- ✅ 任务完成通知
- ✅ 逾期任务提醒
- ✅ 成员@提醒
- ✅ 系统级通知 (Windows/Mac)

**4. 离线工作** ⚡
- ✅ 离线查看项目数据
- ✅ 离线创建任务 (同步后上传)
- ⚠️ 部分功能受限

---

#### 员工功能 (完整版)

**1. 任务管理** ⚡
- ✅ 任务列表 (常驻托盘)
- ✅ 快速查看任务详情
- ✅ 一键更新状态
- ✅ 快捷键操作

**2. 高效执行** ⚡
- ✅ 拖拽上传附件
- ✅ 快速添加备注
- ✅ 任务计时器
- ✅ 专注模式 (隐藏干扰)

**3. 系统集成** ⚡
- ✅ 系统托盘常驻
- ✅ 开机自启动
- ✅ 全局快捷键
- ✅ 文件关联

**4. 离线工作** ⚡
- ✅ 离线查看任务
- ✅ 离线更新状态
- ✅ 自动同步 (联网后)

---

## 💡 使用场景举例

### 场景 1: 项目经理的一天

**早上 9:00 - 办公室 (Web端)**
```
1. 打开浏览器,访问 TaskFleet
2. 查看项目仪表盘,了解整体进度
3. 批量导入今日新任务 (CSV 文件 100条)
4. 使用智能分配功能,自动分配给团队成员
5. 查看详细统计报表,准备周会汇报
```

**中午 12:00 - 午休 (桌面端)**
```
1. 桌面端常驻托盘,收到通知: "员工A完成了10个任务"
2. 快速打开桌面端,审批任务完成
3. 快速创建一个紧急任务分配给员工B
```

**下午 3:00 - 会议中 (桌面端)**
```
1. 会议期间收到系统通知: "5个任务即将逾期"
2. 快速查看是哪些任务
3. 通过桌面端快速调整截止日期
```

**晚上 8:00 - 在家 (Web端 + 桌面端)**
```
1. 使用手机浏览器访问 Web端,查看今日统计
2. 或者打开笔记本上的桌面端,查看关键数据
```

---

### 场景 2: 员工的一天

**早上 8:30 - 到公司 (桌面端)**
```
1. 开机自动启动 TaskFleet 桌面端
2. 托盘图标显示: "今日有 8 个待办任务"
3. 快速浏览任务列表,规划一天工作
```

**上午 10:00 - 执行任务 (桌面端)**
```
1. 点击任务卡片,查看详情
2. 按 F2 快捷键,将状态改为 "进行中"
3. 拖拽文件到任务卡片,上传附件
4. 任务完成后,按 F3 标记为 "已完成"
```

**下午 2:00 - 客户现场 (离线)**
```
1. 笔记本没有网络,但桌面端仍可使用
2. 查看离线缓存的任务详情
3. 更新任务状态 (暂存本地)
4. 回到公司连上网络,自动同步数据
```

**晚上 9:00 - 在家偶尔查看 (Web端)**
```
1. 用手机浏览器访问 TaskFleet Web端
2. 快速查看明天的任务列表
3. 如有紧急任务,直接在手机上更新状态
```

---

## 🔧 技术实现方案

### 1. 统一的后端 API

**设计原则**: 
- 后端 API 不区分调用来源 (Web 或 桌面)
- 只根据用户角色和权限返回数据

**示例 API**:
```rust
// 获取任务列表
// Web端和桌面端调用同一个API
#[get("/api/tasks")]
async fn get_tasks(
    user: AuthUser,  // 通过 JWT 识别用户
    query: Query<TaskQuery>,
) -> Result<Json<Vec<Task>>> {
    match user.role {
        UserRole::Manager => {
            // 返回项目所有任务
            get_project_tasks(&user, &query).await
        }
        UserRole::Employee => {
            // 只返回分配给该员工的任务
            get_assigned_tasks(&user, &query).await
        }
    }
}
```

---

### 2. Web端实现

**技术栈**: React + TypeScript + Ant Design

**角色自适应布局**:
```typescript
// src/layouts/MainLayout.tsx
import { useAuthStore } from '@/stores/authStore';
import { ManagerMenu, EmployeeMenu } from '@/components/Menu';

export const MainLayout = () => {
  const { user } = useAuthStore();
  
  return (
    <Layout>
      <Sider>
        {user.role === 'manager' ? <ManagerMenu /> : <EmployeeMenu />}
      </Sider>
      <Layout>
        <Header />
        <Content>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};
```

**路由配置**:
```typescript
// src/routes/index.tsx
const routes = [
  {
    path: '/',
    element: <MainLayout />,
    children: [
      // 通用路由
      { path: 'dashboard', element: <Dashboard /> },
      { path: 'my-tasks', element: <MyTasks /> },
      
      // 项目经理专属路由
      {
        path: 'projects',
        element: <ProtectedRoute role="manager"><Projects /></ProtectedRoute>,
      },
      {
        path: 'statistics',
        element: <ProtectedRoute role="manager"><Statistics /></ProtectedRoute>,
      },
    ],
  },
];
```

---

### 3. 桌面端实现

**技术栈**: Tauri + Rust + HTML/CSS/JS

**角色自适应界面**:
```rust
// src-tauri/src/main.rs
use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            // 根据用户角色调整窗口
            let user_role = get_current_user_role();
            
            let main_window = match user_role {
                UserRole::Manager => {
                    // 项目经理窗口 - 稍大,显示更多信息
                    tauri::WindowBuilder::new(
                        app,
                        "main",
                        tauri::WindowUrl::App("index.html".into()),
                    )
                    .title("TaskFleet - 管理端")
                    .inner_size(1200.0, 800.0)
                    .build()?
                }
                UserRole::Employee => {
                    // 员工窗口 - 紧凑,专注任务
                    tauri::WindowBuilder::new(
                        app,
                        "main",
                        tauri::WindowUrl::App("index.html".into()),
                    )
                    .title("TaskFleet - 员工端")
                    .inner_size(900.0, 700.0)
                    .build()?
                }
            };
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**离线数据缓存**:
```rust
// src-tauri/src/storage.rs
use serde::{Deserialize, Serialize};
use std::fs;

#[derive(Serialize, Deserialize)]
pub struct OfflineCache {
    pub tasks: Vec<Task>,
    pub projects: Vec<Project>,
    pub last_sync: i64,
}

impl OfflineCache {
    // 保存到本地
    pub fn save(&self) -> Result<()> {
        let json = serde_json::to_string(self)?;
        fs::write("cache.json", json)?;
        Ok(())
    }
    
    // 从本地加载
    pub fn load() -> Result<Self> {
        let json = fs::read_to_string("cache.json")?;
        let cache = serde_json::from_str(&json)?;
        Ok(cache)
    }
}
```

---

### 4. 实时同步机制

**WebSocket 实时推送**:
```rust
// 后端: 任务状态变化时推送通知
async fn update_task_status(task_id: Uuid, new_status: TaskStatus) {
    // 更新数据库
    update_task_in_db(task_id, new_status).await;
    
    // 推送到所有相关用户 (Web端 + 桌面端)
    let message = TaskUpdateMessage {
        task_id,
        new_status,
        updated_at: Utc::now(),
    };
    
    broadcast_to_users(message).await;
}
```

**桌面端接收推送**:
```javascript
// desktop-client/src/websocket.js
const ws = new WebSocket('ws://localhost:3000/ws');

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    
    if (message.type === 'task_update') {
        // 更新本地缓存
        updateLocalTask(message.task_id, message.new_status);
        
        // 显示系统通知
        showNotification(`任务状态已更新: ${message.task_id}`);
        
        // 刷新界面
        refreshTaskList();
    }
};
```

---

## 📱 功能对比总结表

| 功能模块 | Web端 (经理) | Web端 (员工) | 桌面端 (经理) | 桌面端 (员工) |
|---------|-------------|-------------|-------------|-------------|
| **用户认证** |
| 登录/注册 | ✅ | ✅ | ✅ | ✅ |
| 个人资料 | ✅ | ✅ | ✅ | ✅ |
| **项目管理** |
| 创建项目 | ✅ | ❌ | ⚠️ 简化 | ❌ |
| 查看项目列表 | ✅ 全部 | ✅ 参与的 | ✅ 全部 | ✅ 参与的 |
| 编辑项目 | ✅ | ❌ | ⚠️ 简化 | ❌ |
| 项目统计 | ✅ 详细 | ✅ 简单 | ⚠️ 简化 | ⚠️ 简化 |
| **任务管理** |
| 创建单个任务 | ✅ | ❌ | ✅ | ❌ |
| 批量创建 | ✅ | ❌ | ❌ | ❌ |
| CSV导入 | ✅ | ❌ | ❌ | ❌ |
| 任务分配 | ✅ | ❌ | ✅ 单个 | ❌ |
| 查看所有任务 | ✅ | ❌ | ✅ | ❌ |
| 我的任务 | ✅ | ✅ | ✅ | ✅ |
| 更新状态 | ✅ | ✅ | ✅ | ✅ |
| 任务详情 | ✅ | ✅ | ✅ | ✅ |
| **统计分析** |
| 详细报表 | ✅ | ✅ 个人 | ⚠️ 简化 | ⚠️ 个人 |
| 数据导出 | ✅ | ✅ | ❌ | ❌ |
| 图表可视化 | ✅ 多种 | ✅ 简单 | ⚠️ 简单 | ⚠️ 简单 |
| **高级功能** |
| 系统托盘 | ❌ | ❌ | ✅ | ✅ |
| 系统通知 | ⚠️ 浏览器 | ⚠️ 浏览器 | ✅ 系统级 | ✅ 系统级 |
| 离线工作 | ❌ | ❌ | ✅ | ✅ |
| 快捷键 | ⚠️ 有限 | ⚠️ 有限 | ✅ 全局 | ✅ 全局 |
| 文件拖拽 | ⚠️ 有限 | ⚠️ 有限 | ✅ | ✅ |

**图例**: 
- ✅ 完整支持
- ⚠️ 部分支持/简化版
- ❌ 不支持

---

## 🎯 开发优先级

### Phase 1: MVP (核心功能)

**Web端** (6周):
1. ✅ 用户认证
2. ✅ 项目管理 (完整)
3. ✅ 任务管理 (完整)
4. ✅ 基础统计
5. ⚠️ 角色自适应布局

**桌面端** (4周):
1. ✅ 用户认证
2. ✅ 任务列表 (员工)
3. ✅ 任务状态更新
4. ✅ 系统托盘
5. ⚠️ 基础离线支持

---

### Phase 2: 功能增强 (2-3个月)

**Web端**:
1. ✅ 批量操作
2. ✅ CSV导入导出
3. ✅ 详细报表
4. ✅ 高级筛选

**桌面端**:
1. ✅ 项目经理功能 (简化版)
2. ✅ 完整离线支持
3. ✅ 全局快捷键
4. ✅ 自动更新

---

## 💬 总结

**最终方案**: 
- ✅ **两个角色都能使用双端**
- ✅ **Web端作为完整功能平台**
- ✅ **桌面端作为高效快捷工具**

**优势**:
1. 灵活性高 - 用户根据场景选择
2. 开发成本可控 - 核心代码复用
3. 用户体验好 - 发挥各端优势
4. 差异化明显 - 桌面端的离线和系统集成

**这个方案完美解决了你提出的问题! 🎉**

