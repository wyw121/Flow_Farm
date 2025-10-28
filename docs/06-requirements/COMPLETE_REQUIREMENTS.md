# Flow Farm - 完整需求文档

**项目名称**: Flow Farm - 社交平台自动化获客管理系统  
**文档版本**: 1.0  
**更新日期**: 2025年10月27日  
**文档状态**: 完整需求规格说明

---

## 📋 项目概述

### 项目定位

Flow Farm 是一个专业的**社交平台自动化获客管理系统**，为企业和个人提供多平台社交媒体用户关注、监控和精准获客的自动化解决方案。

### 核心价值

- **提升获客效率**: 通过自动化技术批量处理用户关注任务
- **精准客户定位**: 基于关键词和同行监控挖掘潜在客户
- **多平台支持**: 覆盖小红书、抖音等主流社交媒体平台
- **企业级管理**: 三角色权限架构支持团队协作
- **透明计费系统**: 基于实际成功关注数量的公平计费

### 目标用户

1. **系统管理员** (SaaS平台运营方)
   - 管理多个企业客户
   - 设置全局收费规则
   - 监控系统运行状态

2. **用户管理员** (企业客户)
   - 管理企业内部员工账户
   - 查看团队工作统计
   - 管理企业余额和结算

3. **员工用户** (执行人员)
   - 使用桌面客户端执行任务
   - 管理多台自动化设备
   - 查看个人工作记录

---

## 🎯 核心功能需求

### 1. 三角色权限管理系统

#### 1.1 系统管理员 (一级管理员)

**权限范围**:
- ✅ 创建和管理用户管理员账户
- ✅ 查看所有企业和员工的工作数据
- ✅ 设置全局收费标准和计费规则
- ✅ 查看系统级统计报表
- ✅ 配置平台参数和系统设置
- ✅ 管理公司定价策略

**核心功能**:
```
1. 用户管理员开通
   - 创建企业账户
   - 分配初始余额
   - 设置员工限额 (默认10个)

2. 全局数据统计
   - 所有企业总关注量
   - 平台收入统计
   - 活跃度分析

3. 收费规则配置
   - 按关注次数计费标准
   - 不同平台费率设置
   - 套餐价格管理
```

#### 1.2 用户管理员 (二级管理员)

**权限范围**:
- ✅ 创建和管理员工账户 (最多10个)
- ✅ 查看本企业员工工作数据
- ✅ 管理企业账户余额
- ✅ 查看结算界面和扣费明细
- ✅ 调整员工关注数量配额
- ❌ 无法查看其他企业数据
- ❌ 无法修改全局收费规则

**核心功能**:
```
1. 员工账户管理
   - 创建员工用户 (最多10个)
   - 分配员工权限
   - 查看员工工作量统计

2. 余额管理
   - 查看账户余额
   - 充值记录查询
   - 扣费明细查看
   - 余额预警设置

3. 数据统计
   - 按日/周/月统计
   - 按员工分组统计
   - 按平台分类统计
   - 导出统计报表

4. 结算管理
   - 查看计费明细
   - 调整员工配额
   - 生成财务报表
```

#### 1.3 员工用户 (脚本执行用户)

**权限范围**:
- ✅ 使用桌面客户端登录
- ✅ 管理和连接设备 (最多10台)
- ✅ 执行小红书、抖音关注任务
- ✅ 查看个人工作记录
- ✅ 上传任务执行结果
- ❌ 无法查看其他员工数据
- ❌ 无法修改任何设置

**核心功能**:
```
1. 设备管理
   - 连接 Android 设备 (ADB)
   - 查看设备状态
   - 设备在线/离线切换
   - 最多管理10台设备

2. 任务执行
   - 通讯录导入任务
   - 同行监控任务
   - 查看任务进度
   - 任务结果上传

3. 工作记录
   - 查看个人关注记录
   - 查看扣费明细
   - 查看任务执行历史
```

---

### 2. 设备管理系统

#### 2.1 设备限制规则

**限制标准**:
- 每个员工用户最多管理 **10台设备**
- 设备必须通过 ADB (Android Debug Bridge) 连接
- 支持的平台: Android 设备 (小红书/抖音 APP)

#### 2.2 设备管理功能

**核心功能**:
```
1. 设备发现和连接
   - 自动扫描 USB 连接的 Android 设备
   - 显示设备列表 (设备名、型号、状态)
   - 一键连接/断开设备

2. 设备状态监控
   - 在线/离线状态显示
   - 设备电池电量
   - ADB 连接状态
   - 设备屏幕分辨率
   - Android 版本信息

3. 设备操作功能
   - 设备编号分配 (1-10)
   - 设备重命名
   - 设备状态刷新
   - 设备断开连接
   - 设备删除

4. 任务分配规则
   - 任务仅分配给已连接设备
   - 自动均匀分配到多台设备
   - 显示每台设备的任务量
```

#### 2.3 设备同步机制

**同步要求**:
```
1. 设备状态实时同步
   - 客户端每30秒心跳同步
   - 上报设备在线/离线状态
   - 同步到服务器数据库

2. 设备限制验证
   - 连接前检查设备数量
   - 超过10台时拒绝连接
   - 提示用户断开旧设备

3. 数据持久化
   - 设备信息保存到数据库
   - 设备历史记录追踪
   - 设备使用统计
```

---

### 3. 任务管理系统

#### 3.1 通讯录导入任务 (批量关注)

**任务流程**:
```
1. 文件准备阶段
   ├── 支持格式: CSV, Excel (.xlsx/.xls), TXT
   ├── 必需字段: 用户名/用户ID
   └── 可选字段: 手机号、邮箱、备注

2. 文件导入阶段
   ├── 选择平台 (小红书/抖音)
   ├── 上传通讯录文件
   ├── 系统解析文件内容
   └── 显示检测到的联系人数量

3. 任务配置阶段
   ├── 选择执行设备 (从已连接设备中选择)
   ├── 设置关注数量 (1-1000)
   ├── 查看预计费用
   └── 检查账户余额

4. 任务执行阶段
   ├── 余额充足 → 提交任务
   ├── 自动扣费并锁定余额
   ├── 任务分配到已连接设备
   ├── 均匀分配 (例: 100人 ÷ 5设备 = 每设备20人)
   └── 设备自动执行关注操作

5. 结果上报阶段
   ├── 成功关注 → 计入统计
   ├── 失败关注 → 退回余额
   ├── 重复用户 → 自动跳过
   └── 更新数据库记录
```

**文件格式示例**:

CSV格式:
```csv
用户名,用户ID,手机号,邮箱,备注
张三,zhang_san_001,13800138001,zhangsan@example.com,重点客户
李四,li_si_002,13900139002,lisi@example.com,普通客户
王五,wang_wu_003,13700137003,wangwu@example.com,VIP客户
```

TXT格式:
```txt
张三
李四
王五
赵六
```

**数据去重机制**:
- 导入时自动检测重复用户
- 与历史关注记录对比
- 显示去重数量提示
- 仅对新用户执行关注

#### 3.2 精准获客任务 (同行监控)

**任务流程**:
```
1. 监控配置阶段
   ├── 输入同行账号 (小红书/抖音账号)
   ├── 设置监控关键词
   │   ├── 手动输入关键词
   │   ├── 使用内置示例
   │   └── AI生成长尾词 (可选)
   └── 设置触发阈值

2. 数据爬取阶段
   ├── 爬取同行账号的帖子/视频
   ├── 爬取评论区内容
   ├── 提取评论用户信息
   └── 存储到待处理列表

3. 关键词匹配阶段
   ├── 评论内容 vs 关键词库
   ├── 识别询问类评论
   ├── 识别购买意向评论
   └── 筛选潜在客户

4. 用户筛选阶段
   ├── 检查用户质量
   │   ├── 是否已关注
   │   ├── 粉丝数量
   │   ├── 活跃度
   │   └── 认证状态
   └── 符合条件的用户加入关注列表

5. 自动关注阶段
   ├── 达到触发阈值 (例: 收集100个用户)
   ├── 检查账户余额
   ├── 自动执行关注操作
   ├── 记录关注结果
   └── 更新统计数据
```

**关键词配置示例**:
```json
{
  "询问类关键词": [
    "怎么买",
    "在哪里买",
    "价格多少",
    "有链接吗",
    "怎么联系"
  ],
  "购买意向关键词": [
    "想买",
    "求购",
    "需要",
    "有没有",
    "求推荐"
  ],
  "负面关键词": [
    "垃圾",
    "骗人",
    "差评",
    "不推荐"
  ]
}
```

**帖子热度判断标准**:

| 平台 | 热度指标 | 阈值建议 |
|------|---------|---------|
| 小红书 | 点赞数 | > 1000 |
| 小红书 | 评论数 | > 100 |
| 小红书 | 收藏数 | > 500 |
| 抖音 | 点赞数 | > 10000 |
| 抖音 | 评论数 | > 500 |
| 抖音 | 分享数 | > 1000 |

**AI长尾词生成**:
- 基于核心关键词扩展
- 生成同义词和相似表达
- 行业术语自动补充
- 地域性关键词变体

#### 3.3 任务分配算法

**均匀分配算法**:
```python
# 示例: 100个用户，5台设备
total_contacts = 100
connected_devices = 5

# 基础分配: 每设备20个
base_allocation = total_contacts // connected_devices  # 20

# 余数分配: 前面的设备多分配1个
remainder = total_contacts % connected_devices  # 0

# 最终分配结果:
# 设备1: 20个
# 设备2: 20个
# 设备3: 20个
# 设备4: 20个
# 设备5: 20个
```

**任务执行控制**:
- 并发控制: 同时最多5台设备执行
- 频率控制: 每次关注间隔3-5秒 (防封号)
- 重试机制: 失败后自动重试3次
- 超时处理: 单次操作超时30秒则跳过

---

### 4. 计费系统

#### 4.1 计费规则

**计费模式**: 按成功关注次数计费

**计费标准**:
```
基础费率:
- 小红书关注: 0.10 元/次
- 抖音关注:   0.10 元/次
- 其他平台:   待定

企业套餐 (可选):
- 月度套餐: 充值1000元，送100次
- 季度套餐: 充值3000元，送500次
- 年度套餐: 充值10000元，送2000次
```

**计费时机**:
```
✅ 成功关注后计费:
   - ADB操作成功
   - 目标用户确认关注
   - 数据写入数据库

❌ 以下情况不计费:
   - 关注操作失败
   - 重复关注 (已关注用户)
   - 用户不存在
   - 网络异常导致失败
```

#### 4.2 余额管理

**余额检查机制**:
```
1. 提交任务前检查
   ├── 计算预估费用 = 关注数量 × 单价
   ├── 检查账户余额 >= 预估费用
   ├── 余额不足 → 拒绝提交，提示充值
   └── 余额充足 → 锁定预估费用，允许提交

2. 任务执行中
   ├── 每次成功关注 → 实时扣费
   ├── 关注失败 → 释放锁定余额
   └── 任务完成 → 释放剩余锁定余额

3. 余额预警
   ├── 余额 < 100元 → 黄色预警
   ├── 余额 < 50元  → 红色警告
   └── 余额 = 0元   → 禁止提交新任务
```

**充值方式**:
```
1. 系统管理员手动充值
   - 管理后台操作
   - 支持批量充值

2. 在线支付 (预留接口)
   - 支付宝
   - 微信支付
   - 银行卡支付
```

#### 4.3 计费记录

**数据库字段**:
```sql
CREATE TABLE billing_records (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,              -- 用户ID
    company TEXT NOT NULL,               -- 公司名称
    amount REAL NOT NULL,                -- 金额
    billing_type TEXT NOT NULL,          -- charge(充值) | deduct(扣费)
    platform TEXT,                       -- 平台 (xiaohongshu | douyin)
    target_user TEXT,                    -- 关注的目标用户
    description TEXT,                    -- 描述
    created_at DATETIME NOT NULL,        -- 创建时间
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

**统计报表**:
- 按日/周/月汇总扣费
- 按平台分类统计
- 按员工分组统计
- 导出Excel报表

---

### 5. 防重复关注系统

#### 5.1 核心需求

**业务规则**:
- 管理员名下所有用户和设备共享关注记录
- 确保不重复关注同一个用户
- 跨设备、跨员工的全局去重

**实现逻辑**:
```
场景示例:
- 公司A (管理员: admin_A)
  - 员工1 (设备1, 设备2)
  - 员工2 (设备3, 设备4)

去重规则:
- 员工1在设备1关注了用户X
- 员工2在设备3尝试关注用户X → 自动跳过
- 同一公司的所有设备共享关注记录
```

#### 5.2 数据库设计

**关注记录表**:
```sql
CREATE TABLE followed_users (
    id TEXT PRIMARY KEY,
    company TEXT NOT NULL,               -- 公司名称 (管理员分组)
    platform TEXT NOT NULL,              -- 平台 (xiaohongshu | douyin)
    target_user_id TEXT NOT NULL,        -- 目标用户ID
    target_username TEXT,                -- 目标用户名
    followed_by_employee TEXT NOT NULL,  -- 执行员工
    followed_by_device TEXT NOT NULL,    -- 执行设备
    followed_at DATETIME NOT NULL,       -- 关注时间
    UNIQUE(company, platform, target_user_id)  -- 唯一约束
);

-- 索引优化
CREATE INDEX idx_company_platform ON followed_users(company, platform);
CREATE INDEX idx_target_user ON followed_users(target_user_id);
```

#### 5.3 去重流程

**执行前检查**:
```
1. 员工客户端准备关注用户X
   ↓
2. 调用API检查: POST /api/v1/follow/check
   ├── 请求参数:
   │   ├── company: "CompanyA"
   │   ├── platform: "xiaohongshu"
   │   └── target_user_id: "user_x_123"
   ↓
3. 服务器查询 followed_users 表
   ├── 存在记录 → 返回 { is_followed: true }
   └── 不存在   → 返回 { is_followed: false }
   ↓
4. 客户端处理
   ├── is_followed = true  → 跳过该用户
   └── is_followed = false → 执行关注操作
```

**执行后记录**:
```
1. ADB操作成功关注用户X
   ↓
2. 调用API记录: POST /api/v1/follow/record
   ├── 请求参数:
   │   ├── company: "CompanyA"
   │   ├── platform: "xiaohongshu"
   │   ├── target_user_id: "user_x_123"
   │   ├── target_username: "张三"
   │   ├── followed_by_employee: "employee_1"
   │   └── followed_by_device: "device_001"
   ↓
3. 服务器插入 followed_users 表
   ├── 成功 → 返回 200 OK
   └── 失败 (重复) → 返回 409 Conflict
   ↓
4. 客户端实时扣费
```

---

### 6. GUI界面要求

#### 6.1 服务器前端 (管理员界面)

**技术栈**: React 19 + TypeScript + Ant Design 5

**系统管理员界面**:
```
1. 用户管理页面
   ├── 用户列表 (表格)
   ├── 创建用户 (模态框)
   ├── 编辑用户 (模态框)
   ├── 删除用户 (确认对话框)
   └── 用户详情 (抽屉)

2. 公司统计页面
   ├── 总关注量 (卡片)
   ├── 总收入 (卡片)
   ├── 活跃企业数 (卡片)
   ├── 关注趋势图 (折线图)
   └── 平台分布图 (饼图)

3. 公司定价页面
   ├── 定价列表 (表格)
   ├── 添加定价 (模态框)
   ├── 编辑定价 (模态框)
   └── 删除定价 (确认对话框)
```

**用户管理员界面**:
```
1. 员工管理页面
   ├── 员工列表 (表格)
   ├── 创建员工 (模态框)
   ├── 编辑员工 (模态框)
   ├── 删除员工 (确认对话框)
   └── 员工统计 (卡片)

2. 计费管理页面
   ├── 余额显示 (大数字卡片)
   ├── 充值记录 (表格)
   ├── 扣费记录 (表格)
   ├── 筛选和搜索
   └── 导出Excel

3. 数据统计页面
   ├── 总关注量 (卡片)
   ├── 按日统计 (表格)
   ├── 按员工统计 (表格)
   ├── 按平台统计 (饼图)
   └── 趋势图 (折线图)
```

#### 6.2 员工客户端 (桌面GUI)

**技术栈**: Rust + Tauri 2.0 + HTML/CSS/JS

**主界面布局**:
```
┌─────────────────────────────────────────────┐
│  Flow Farm 员工客户端                         │
├─────────────────────────────────────────────┤
│  用户: 张三  |  公司: XX科技  |  余额: ¥1250.50 │
├─────────────────────────────────────────────┤
│  [📖 小红书]  [🎵 抖音]                      │
├─────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐           │
│  │ 📇 通讯录导入 │  │ 🔍 同行监控  │           │
│  └─────────────┘  └─────────────┘           │
│                                             │
│  设备管理 (3/10 已连接)                       │
│  ┌─────────────────────────────────┐        │
│  │ ✅ 设备1 - 在线  [断开]           │        │
│  │ ✅ 设备2 - 在线  [断开]           │        │
│  │ ✅ 设备3 - 在线  [断开]           │        │
│  │ ⚪ 设备4 - 离线  [连接]           │        │
│  └─────────────────────────────────┘        │
│                                             │
│  任务状态                                    │
│  ┌─────────────────────────────────┐        │
│  │ 当前任务: 通讯录导入 (小红书)       │        │
│  │ 进度: ████████░░ 80% (80/100)   │        │
│  │ 已扣费: ¥8.00                    │        │
│  └─────────────────────────────────┘        │
└─────────────────────────────────────────────┘
```

**通讯录导入界面**:
```
┌─────────────────────────────────────────────┐
│  通讯录导入 - 小红书                           │
├─────────────────────────────────────────────┤
│  1. 选择文件                                  │
│  ┌─────────────────────────────────┐        │
│  │ 📁 [浏览文件]                     │        │
│  │ 已选择: contacts.csv             │        │
│  │ 📊 检测到 150 条联系人数据         │        │
│  └─────────────────────────────────┘        │
│                                             │
│  2. 导入数据                                  │
│  [📤 导入通讯录]                              │
│  ✅ 已导入 145 条有效数据，去重 5 条          │
│                                             │
│  3. 配置任务                                  │
│  选择设备: [设备1 ▼]                          │
│  关注数量: [100 ━━━━●━━━━ 1000]              │
│  预计费用: ¥10.00                            │
│  账户余额: ¥1250.50 ✅                       │
│                                             │
│  4. 提交任务                                  │
│  [🚀 提交关注任务]                            │
└─────────────────────────────────────────────┘
```

**同行监控界面**:
```
┌─────────────────────────────────────────────┐
│  同行监控 - 抖音                               │
├─────────────────────────────────────────────┤
│  1. 监控配置                                  │
│  同行账号: [输入账号ID或链接]                  │
│  关键词配置:                                  │
│  ┌─────────────────────────────────┐        │
│  │ 怎么买                            │        │
│  │ 在哪里买                          │        │
│  │ 价格多少                          │        │
│  │ 有链接吗                          │        │
│  │ [+ 添加关键词] [🤖 AI生成]         │        │
│  └─────────────────────────────────┘        │
│                                             │
│  触发阈值: [50 ━━━━●━━━━ 500]                │
│  (收集到50个符合条件的用户后自动关注)           │
│                                             │
│  2. 监控状态                                  │
│  ┌─────────────────────────────────┐        │
│  │ 状态: 🟢 监控中                   │        │
│  │ 已爬取评论: 1,234 条              │        │
│  │ 符合条件用户: 28 个               │        │
│  │ 距离触发还需: 22 个               │        │
│  └─────────────────────────────────┘        │
│                                             │
│  3. 控制按钮                                  │
│  [▶️ 开始监控] [⏸️ 暂停] [⏹️ 停止]            │
└─────────────────────────────────────────────┘
```

#### 6.3 界面交互要求

**实时反馈**:
- ✅ 操作成功 → 绿色提示
- ❌ 操作失败 → 红色错误提示
- ⚠️ 余额不足 → 黄色警告

**加载状态**:
- 数据加载中显示骨架屏
- 长时间操作显示进度条
- 按钮点击后显示加载动画

**响应式设计**:
- 支持不同分辨率屏幕
- 最小宽度: 1280px
- 推荐分辨率: 1920x1080

**键盘快捷键**:
- `Ctrl + N`: 新建任务
- `Ctrl + R`: 刷新数据
- `Ctrl + S`: 保存设置
- `Esc`: 关闭模态框

---

### 7. 平台支持

#### 7.1 开发优先级

**第一优先级: 小红书** (已实现基础框架)
```
功能列表:
✅ 设备连接和控制
✅ 用户搜索功能
⚠️ 关注操作 (需完善)
⚠️ 评论爬取 (需完善)
❌ 私信功能 (待开发)
```

**第二优先级: 抖音** (规划中)
```
功能列表:
✅ 基础架构设计
❌ UI元素定位
❌ 关注操作
❌ 评论爬取
❌ 私信功能
```

**第三优先级: 未来扩展**
```
- 快手
- B站
- 微博
- 知乎
```

#### 7.2 平台特定配置

**小红书配置**:
```json
{
  "platform": "xiaohongshu",
  "package_name": "com.xingin.xhs",
  "search_delay_ms": 2000,
  "scroll_delay_ms": 1000,
  "tap_delay_ms": 500,
  "max_retries": 3,
  "ui_elements": {
    "search_button": "com.xingin.xhs:id/search",
    "follow_button": "com.xingin.xhs:id/follow",
    "comment_list": "com.xingin.xhs:id/comment_list"
  }
}
```

**抖音配置**:
```json
{
  "platform": "douyin",
  "package_name": "com.ss.android.ugc.aweme",
  "search_delay_ms": 3000,
  "scroll_delay_ms": 1500,
  "tap_delay_ms": 800,
  "max_retries": 3,
  "ui_elements": {
    "search_button": "待定位",
    "follow_button": "待定位",
    "comment_list": "待定位"
  }
}
```

---

### 8. 数据统计和报表

#### 8.1 实时统计指标

**系统管理员视图**:
```
1. 全局统计卡片
   ├── 总关注量 (所有企业累计)
   ├── 今日新增关注
   ├── 总收入金额
   ├── 活跃企业数

2. 趋势图表
   ├── 近30天关注趋势 (折线图)
   ├── 平台占比 (饼图)
   │   ├── 小红书: 60%
   │   └── 抖音: 40%
   └── Top 10 企业排行

3. 实时监控
   ├── 在线设备数
   ├── 执行中任务数
   └── 系统负载状态
```

**用户管理员视图**:
```
1. 企业统计卡片
   ├── 本月关注量
   ├── 本月消费金额
   ├── 账户余额
   └── 活跃员工数

2. 员工工作量排行
   ├── 员工1: 1,234 次
   ├── 员工2: 987 次
   └── 员工3: 756 次

3. 平台分布
   ├── 小红书: 65%
   └── 抖音: 35%

4. 时间趋势
   ├── 按日统计 (表格)
   ├── 按周统计 (柱状图)
   └── 按月统计 (折线图)
```

**员工用户视图**:
```
1. 个人统计
   ├── 今日关注: 50 次
   ├── 本周关注: 300 次
   ├── 本月关注: 1,200 次
   └── 累计关注: 5,600 次

2. 任务历史
   ├── 任务列表 (表格)
   ├── 任务状态
   └── 任务结果
```

#### 8.2 报表导出

**支持格式**:
- Excel (.xlsx)
- CSV (.csv)
- PDF (预留)

**报表类型**:
```
1. 日报表
   ├── 关注明细
   ├── 扣费明细
   └── 设备使用记录

2. 周报表
   ├── 关注汇总
   ├── 费用汇总
   └── 员工工作量

3. 月报表
   ├── 完整统计数据
   ├── 趋势分析
   └── 财务对账单
```

---

### 9. 安全性和性能要求

#### 9.1 安全性需求

**认证和授权**:
```
1. JWT Token 认证
   ├── Token有效期: 24小时
   ├── 自动刷新机制
   └── 登出后立即失效

2. 密码安全
   ├── BCrypt 哈希加密
   ├── 最小长度: 8位
   ├── 必须包含字母和数字
   └── 90天强制更换 (可选)

3. API 访问控制
   ├── 基于角色的权限验证
   ├── 跨域请求限制
   └── 请求频率限制
```

**数据安全**:
```
1. 敏感数据加密
   ├── 用户密码 (BCrypt)
   ├── API Token (AES-256)
   └── 支付信息 (预留)

2. 数据备份
   ├── 每日自动备份数据库
   ├── 备份保留30天
   └── 支持手动备份

3. 操作审计
   ├── 记录所有关键操作
   ├── 登录/登出日志
   └── 数据修改日志
```

**防封号机制**:
```
1. 操作频率控制
   ├── 每次关注间隔: 3-5秒随机
   ├── 每小时最多: 100次
   ├── 每天最多: 800次
   └── 模拟人工操作行为

2. 设备轮换
   ├── 多设备分散任务
   ├── 避免单设备过载
   └── 设备冷却时间

3. 异常检测
   ├── 检测失败率过高
   ├── 自动暂停任务
   └── 通知管理员
```

#### 9.2 性能要求

**响应时间**:
```
- API 响应: < 200ms
- 页面加载: < 2s
- 数据库查询: < 100ms
- 任务提交: < 500ms
```

**并发支持**:
```
- 同时在线用户: 100+
- 并发任务执行: 50+
- 并发设备连接: 500+
```

**资源限制**:
```
- 服务器内存: < 2GB
- CPU 使用率: < 60%
- 数据库大小: < 10GB
- 日志文件大小: < 1GB/天
```

---

### 10. 技术架构总结

#### 10.1 系统架构

```
┌─────────────────────────────────────────────────┐
│            Flow Farm 系统架构图                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────┐          ┌─────────────┐      │
│  │ 服务器前端   │  HTTP    │ 员工客户端   │      │
│  │ (React)    │ ←────→   │ (Tauri)     │      │
│  │ Port: 3000 │          │ 桌面应用     │      │
│  └──────┬──────┘          └──────┬──────┘      │
│         │                        │             │
│         │ REST API               │ REST API    │
│         ↓                        ↓             │
│  ┌─────────────────────────────────────┐       │
│  │     服务器后端 (Rust + Axum)         │       │
│  │     Port: 8000                      │       │
│  │  ┌────────────────────────────┐     │       │
│  │  │ Handlers (路由层)           │     │       │
│  │  └────────┬───────────────────┘     │       │
│  │           ↓                         │       │
│  │  ┌────────────────────────────┐     │       │
│  │  │ Services (业务逻辑层)        │     │       │
│  │  └────────┬───────────────────┘     │       │
│  │           ↓                         │       │
│  │  ┌────────────────────────────┐     │       │
│  │  │ Database (数据访问层)        │     │       │
│  │  └────────┬───────────────────┘     │       │
│  └───────────┼─────────────────────────┘       │
│              ↓                                 │
│  ┌─────────────────────────────────────┐       │
│  │     SQLite 数据库                    │       │
│  │  ┌──────────────────────────┐       │       │
│  │  │ users (用户表)            │       │       │
│  │  │ work_records (工作记录)   │       │       │
│  │  │ devices (设备表)          │       │       │
│  │  │ billing_records (计费)    │       │       │
│  │  │ followed_users (关注记录) │       │       │
│  │  │ company_pricing (定价)    │       │       │
│  │  └──────────────────────────┘       │       │
│  └─────────────────────────────────────┘       │
│                                                 │
│  员工客户端通过 ADB 控制 Android 设备:            │
│  ┌──────────────────────────────────┐          │
│  │  员工客户端 (Tauri)                │          │
│  │       ↓ ADB 命令                  │          │
│  │  ┌─────────────────────┐          │          │
│  │  │ Android 设备1       │          │          │
│  │  │ - 小红书 APP        │          │          │
│  │  │ - 抖音 APP          │          │          │
│  │  └─────────────────────┘          │          │
│  │  ┌─────────────────────┐          │          │
│  │  │ Android 设备2       │          │          │
│  │  └─────────────────────┘          │          │
│  │       ... (最多10台)               │          │
│  └──────────────────────────────────┘          │
└─────────────────────────────────────────────────┘
```

#### 10.2 技术栈清单

**服务器后端**:
- 语言: Rust (Edition 2021)
- Web框架: Axum 0.7
- 数据库: SQLite + SQLx 0.7
- 认证: JWT + BCrypt
- 异步运行时: Tokio 1.0

**服务器前端**:
- 框架: React 19.1.1
- 语言: TypeScript 5.9.2
- UI库: Ant Design 5.27.3
- 状态管理: Redux Toolkit 2.9.0
- 构建工具: Vite 7.1.5
- 图表库: ECharts 6.0.0

**员工客户端**:
- 桌面框架: Tauri 2.0
- 后端语言: Rust (Edition 2021)
- 前端技术: HTML/CSS/JavaScript
- HTTP客户端: Reqwest 0.12
- 数据库: SQLx + SQLite
- 设备控制: ADB (Android Debug Bridge)

---

### 11. 部署和运维要求

#### 11.1 部署环境

**服务器要求**:
```
操作系统: Ubuntu 20.04+ / CentOS 8+
CPU: 2核+
内存: 4GB+
硬盘: 50GB+ SSD
网络: 公网IP + 域名 (可选)
```

**客户端要求**:
```
操作系统: Windows 10/11 (主要)
CPU: Intel i5 或同等性能
内存: 8GB+
硬盘: 20GB+
USB: 支持USB 2.0+ (ADB连接)
```

#### 11.2 部署流程

**后端部署**:
```bash
# 1. 克隆代码
git clone https://github.com/your-org/flow-farm.git
cd flow-farm/server-backend

# 2. 配置环境变量
cp .env.production .env
# 编辑 .env 设置数据库路径和JWT密钥

# 3. 构建生产版本
cargo build --release

# 4. 运行服务器
./target/release/flow-farm-backend

# 5. 使用 systemd 守护进程 (可选)
sudo systemctl enable flow-farm-backend
sudo systemctl start flow-farm-backend
```

**前端部署**:
```bash
# 1. 构建前端
cd server-frontend
npm install
npm run build

# 2. 复制到后端静态目录
cp -r dist/* ../server-backend/static/

# 3. 访问
http://your-server-ip:8000
```

**客户端分发**:
```bash
# 1. 构建 Tauri 应用
cd employee-client
cargo tauri build

# 2. 分发安装包
# Windows: employee-client/src-tauri/target/release/bundle/msi/
# 发送给员工用户安装
```

#### 11.3 监控和日志

**日志配置**:
```
日志级别: INFO (生产), DEBUG (开发)
日志位置:
- 服务器: /var/log/flow-farm/server.log
- 客户端: C:\Users\{user}\AppData\Local\FlowFarm\logs\

日志轮转:
- 每日自动轮转
- 保留30天
- 单文件最大 100MB
```

**监控指标**:
```
- 系统负载
- 内存使用
- 数据库连接数
- API响应时间
- 错误率统计
- 活跃用户数
```

---

## 📝 需求优先级

### P0 - 核心必需 (已实现)

✅ 三角色权限系统
✅ 用户管理 (CRUD)
✅ JWT 认证
✅ 设备管理基础
✅ 数据库设计
✅ 服务器前端界面
✅ 员工客户端框架

### P1 - 重要功能 (部分实现)

⚠️ 设备状态实时同步
⚠️ 通讯录导入功能
⚠️ 计费扣费系统集成
⚠️ 防重复关注机制
⚠️ 小红书自动化完善

### P2 - 次要功能 (待开发)

❌ 同行监控任务
❌ AI 长尾词生成
❌ 抖音平台支持
❌ 数据统计报表
❌ Excel 导出功能

### P3 - 未来扩展 (规划中)

❌ 快手平台支持
❌ B站平台支持
❌ 在线支付集成
❌ 移动端管理
❌ 多语言支持

---

## 🔄 版本规划

### v1.0 (MVP - 最小可行产品)

**目标**: 实现小红书平台的基础功能

**核心功能**:
- ✅ 三角色权限系统
- ✅ 用户管理
- ⚠️ 设备管理 (需完善同步)
- ⚠️ 通讯录导入 (需完善)
- ⚠️ 计费系统 (需完善)
- ❌ 防重复关注 (待实现)

**交付时间**: 2周内

### v1.1 (功能完善)

**目标**: 完善小红书功能，添加抖音支持

**新增功能**:
- 设备状态实时同步
- 防重复关注机制
- 同行监控任务
- 抖音平台基础支持
- 数据统计报表

**交付时间**: v1.0 后 4周

### v2.0 (平台扩展)

**目标**: 多平台支持，高级功能

**新增功能**:
- 快手平台支持
- B站平台支持
- AI 长尾词生成
- 高级数据分析
- 移动端管理

**交付时间**: v1.1 后 8周

---

## 📚 附录

### A. 数据库完整设计

```sql
-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    hashed_password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('system_admin', 'user_admin', 'employee')),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    parent_id INTEGER,
    full_name TEXT,
    phone TEXT,
    company TEXT,
    max_employees INTEGER DEFAULT 10,
    current_employees INTEGER DEFAULT 0,
    balance REAL DEFAULT 1000.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    FOREIGN KEY (parent_id) REFERENCES users (id)
);

-- 工作记录表
CREATE TABLE work_records (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    device_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    action_type TEXT NOT NULL,
    target_user TEXT,
    target_content TEXT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- 设备表
CREATE TABLE devices (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    device_name TEXT NOT NULL,
    device_type TEXT NOT NULL,
    adb_id TEXT,
    status TEXT NOT NULL DEFAULT 'offline',
    last_seen DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- 计费记录表
CREATE TABLE billing_records (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    amount REAL NOT NULL,
    billing_type TEXT NOT NULL,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- 公司定价表
CREATE TABLE company_pricing (
    id TEXT PRIMARY KEY,
    company TEXT NOT NULL UNIQUE,
    price_per_follow REAL NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 关注记录表 (防重复)
CREATE TABLE followed_users (
    id TEXT PRIMARY KEY,
    company TEXT NOT NULL,
    platform TEXT NOT NULL,
    target_user_id TEXT NOT NULL,
    target_username TEXT,
    followed_by_employee TEXT NOT NULL,
    followed_by_device TEXT NOT NULL,
    followed_at DATETIME NOT NULL,
    UNIQUE(company, platform, target_user_id)
);

-- 索引优化
CREATE INDEX idx_company_platform ON followed_users(company, platform);
CREATE INDEX idx_target_user ON followed_users(target_user_id);
CREATE INDEX idx_work_records_user ON work_records(user_id);
CREATE INDEX idx_devices_user ON devices(user_id);
CREATE INDEX idx_billing_user ON billing_records(user_id);
```

### B. API 端点清单

**认证相关**:
```
POST   /api/v1/auth/login          - 用户登录
POST   /api/v1/auth/logout         - 用户登出
POST   /api/v1/auth/register       - 用户注册
GET    /api/v1/auth/me             - 获取当前用户信息
POST   /api/v1/auth/refresh        - 刷新 Token
```

**用户管理**:
```
GET    /api/v1/users               - 获取用户列表
POST   /api/v1/users               - 创建用户
GET    /api/v1/users/:id           - 获取用户详情
PUT    /api/v1/users/:id           - 更新用户
DELETE /api/v1/users/:id           - 删除用户
GET    /api/v1/users/companies/statistics  - 公司统计
GET    /api/v1/users/companies/names       - 公司名称列表
```

**设备管理**:
```
GET    /api/v1/devices             - 获取设备列表
POST   /api/v1/devices             - 创建设备
GET    /api/v1/devices/:id         - 获取设备详情
PUT    /api/v1/devices/:id         - 更新设备状态
DELETE /api/v1/devices/:id         - 删除设备
```

**工作记录**:
```
GET    /api/v1/work-records        - 获取工作记录列表
POST   /api/v1/work-records        - 创建工作记录
GET    /api/v1/work-records/:id    - 获取工作记录详情
```

**计费管理**:
```
GET    /api/v1/billing             - 获取计费记录
POST   /api/v1/billing/charge      - 充值
POST   /api/v1/billing/deduct      - 扣费
GET    /api/v1/billing/balance     - 查询余额
```

**KPI 统计**:
```
GET    /api/v1/kpi/overview        - 总览统计
GET    /api/v1/kpi/daily           - 按日统计
GET    /api/v1/kpi/weekly          - 按周统计
GET    /api/v1/kpi/monthly         - 按月统计
```

**公司定价**:
```
GET    /api/v1/company-pricing     - 获取定价列表
POST   /api/v1/company-pricing     - 创建定价
PUT    /api/v1/company-pricing/:id - 更新定价
DELETE /api/v1/company-pricing/:id - 删除定价
```

**关注管理** (待实现):
```
POST   /api/v1/follow/check        - 检查是否已关注
POST   /api/v1/follow/record       - 记录关注
GET    /api/v1/follow/history      - 获取关注历史
```

**系统健康**:
```
GET    /health                     - 健康检查
GET    /docs                       - API 文档
```

### C. 术语表

| 术语 | 英文 | 说明 |
|------|------|------|
| 系统管理员 | System Admin | 一级管理员，平台运营方 |
| 用户管理员 | User Admin | 二级管理员，企业客户 |
| 员工用户 | Employee | 执行人员，使用客户端 |
| ADB | Android Debug Bridge | Android 调试桥，设备控制工具 |
| JWT | JSON Web Token | 认证令牌 |
| API | Application Programming Interface | 应用程序接口 |
| GUI | Graphical User Interface | 图形用户界面 |
| CRUD | Create Read Update Delete | 增删改查操作 |
| KPI | Key Performance Indicator | 关键绩效指标 |

---

**文档结束**

此需求文档全面描述了 Flow Farm 项目的所有功能需求、技术架构、业务逻辑和实现细节。建议在开发过程中持续参考和更新此文档。
