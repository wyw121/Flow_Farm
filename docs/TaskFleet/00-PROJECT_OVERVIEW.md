# TaskFleet - 任务执行专家

**项目愿景**: 专注于任务分发、进度监控和数据统计的开源项目管理系统

**创建日期**: 2025年10月28日  
**版本**: v0.1.0 (MVP阶段)  
**定位**: 任务执行专家 - 为管理多个执行人员的项目提供智能化解决方案

---

## 📋 项目概述

### 核心价值主张

> **"不是又一个项目管理工具,而是专注于任务分发、执行监控、数据统计的专业系统"**

TaskFleet 专注于解决以下核心问题:
- ✅ **任务如何高效分发** - 批量导入、智能分配
- ✅ **进度如何实时监控** - 一目了然的执行状态
- ✅ **数据如何深度统计** - 员工效率、任务完成趋势

### 差异化定位

与通用项目管理工具(Jira/禅道/DooTask)的区别:

| 对比项 | 通用工具 | TaskFleet |
|--------|---------|-----------|
| **定位** | 项目全生命周期管理 | 专注任务执行阶段 |
| **核心功能** | 功能大而全 | 任务分发+监控+统计 |
| **权限架构** | 多层级复杂 | 项目经理-员工扁平结构 |
| **用户体验** | 配置繁琐 | 开箱即用 |
| **技术栈** | PHP/Ruby/Python | Rust + Tauri (高性能) |

### 目标用户

**主要用户**: 需要管理多个执行人员的项目经理

**典型场景**:
- 📊 市场调研团队 (问卷调查、街访)
- 🏢 客户拜访管理 (销售团队、客户成功)
- 📝 数据录入任务 (批量处理、质量控制)
- 🎯 运营任务管理 (内容发布、社群维护)
- 🔧 现场服务管理 (维修、巡检)

---

## 🎯 产品定位

### 核心特性

#### 1. 智能任务分发 🚀
- 批量导入任务 (CSV/Excel)
- 自动均衡分配到员工
- 考虑员工负载和能力
- 手动调整和重新分配

#### 2. 实时进度监控 📊
- 项目整体进度一目了然
- 员工任务列表实时更新
- 任务状态可视化 (待办/进行中/已完成)
- 异常情况自动提醒

#### 3. 深度数据统计 📈
- 员工效率分析
- 任务完成率趋势
- 工作量分布统计
- 可视化图表展示

#### 4. 多端协同 💻
- **Web端**: 全功能版 (项目经理主力,员工辅助)
  - React + TypeScript + Ant Design
  - 完整的项目/任务管理功能
  - 详细的数据统计和报表
  - 批量操作 (CSV导入/导出)
  
- **桌面客户端**: 精简高效版 (员工主力,经理辅助)
  - Tauri + Rust (跨平台)
  - 任务快速查看和更新
  - 系统托盘常驻
  - 离线工作支持
  - 系统级通知提醒
  
- **移动端**: 轻量级查看 (未来计划)

---

## 🏗️ 架构设计

### 权限架构 (扁平化)

```
项目经理 (Project Manager)
  ├─ Web端 (主力) + 桌面端 (辅助)
  ├─ 创建和管理项目
  ├─ 批量创建和分配任务
  ├─ 监控所有任务进度
  ├─ 查看统计和报表
  └─ 管理项目成员

员工 (Employee)
  ├─ 桌面端 (主力) + Web端 (辅助)
  ├─ 查看分配给自己的任务
  ├─ 更新任务进度和状态
  ├─ 提交工作成果
  └─ 查看个人统计数据
```

**设计理念**:
- ✅ 两个角色都可以使用双端
- ✅ 根据场景选择合适的端
- ✅ Web端功能更全面,桌面端更高效

**不需要**:
- ❌ 系统管理员
- ❌ 用户管理员
- ❌ 复杂的多层级组织结构

### 技术架构

```
┌─────────────────────────────────────────────┐
│           前端层 (Frontend)                  │
├─────────────────────────────────────────────┤
│  Web端 (管理端)          │  桌面端 (员工端)  │
│  React + TypeScript      │  Tauri + Rust     │
│  Ant Design / Chakra UI  │  HTML/CSS/JS      │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│            API 层 (Backend)                  │
├─────────────────────────────────────────────┤
│  Rust + Axum                                │
│  - RESTful API                              │
│  - WebSocket (实时推送)                      │
│  - JWT 认证                                 │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│           数据层 (Database)                  │
├─────────────────────────────────────────────┤
│  PostgreSQL + SQLx                          │
│  Redis (缓存 + 实时数据)                     │
└─────────────────────────────────────────────┘
```

---

## 🎨 核心功能流程

### 1. 任务分发流程

```
项目经理创建任务
    ↓
选择分发方式
    ├─ 手动分配: 选择特定员工
    ├─ 批量导入: CSV/Excel上传
    └─ 智能分配: 系统自动均衡
    ↓
任务推送到员工
    ↓
员工接收任务通知
```

### 2. 进度更新流程

```
员工查看任务列表
    ↓
选择任务并开始执行
    ↓
更新任务状态
    ├─ 待办 → 进行中
    ├─ 进行中 → 已完成
    └─ 添加备注/附件
    ↓
实时推送到项目经理
    ↓
项目经理查看进度
```

### 3. 数据统计流程

```
系统自动收集数据
    ↓
实时计算统计指标
    ├─ 任务完成数量
    ├─ 员工工作量
    ├─ 完成率趋势
    └─ 效率分析
    ↓
可视化图表展示
    ↓
项目经理查看报表
```

---

## 🚀 MVP 功能清单

### Phase 1: 核心功能 (必须有) ✅

#### 1. 用户系统
- [x] 用户注册和登录
- [x] JWT 认证
- [ ] 角色管理 (项目经理/员工)
- [ ] 用户个人资料

#### 2. 项目管理
- [ ] 创建项目
- [ ] 编辑项目信息
- [ ] 邀请成员加入项目
- [ ] 设置项目权限 (谁是项目经理)
- [ ] 查看项目列表
- [ ] 归档项目

#### 3. 任务管理
- [ ] 创建单个任务
- [ ] 批量创建任务 (CSV导入)
- [ ] 分配任务到员工 (手动选择)
- [ ] 批量分配任务 (均衡分配)
- [ ] 编辑任务信息
- [ ] 删除任务
- [ ] 任务状态管理 (待办/进行中/已完成)
- [ ] 任务优先级 (低/中/高)
- [ ] 任务截止日期
- [ ] 任务描述和备注

#### 4. 进度监控
- [ ] 项目进度总览 (饼图/进度条)
- [ ] 任务看板视图 (待办/进行中/已完成)
- [ ] 任务列表视图 (可筛选/排序)
- [ ] 员工任务列表
- [ ] 实时状态更新 (WebSocket)
- [ ] 任务详情查看

#### 5. 基础统计
- [ ] 任务完成数量统计
- [ ] 员工工作量统计
- [ ] 完成率计算
- [ ] 简单图表展示 (柱状图/折线图)
- [ ] 按时间维度统计 (日/周/月)

#### 6. Web 端 (项目经理)
- [ ] 响应式布局
- [ ] 项目仪表盘
- [ ] 任务管理界面
- [ ] 统计报表页面
- [ ] 团队成员管理

#### 7. 桌面客户端 (员工)
- [ ] 用户登录
- [ ] 任务列表显示
- [ ] 任务详情查看
- [ ] 更新任务状态
- [ ] 添加任务备注
- [ ] 系统托盘通知

---

### Phase 2: 暂不做 (未来考虑) ❌

- ❌ 即时通讯 (使用第三方如钉钉/企业微信)
- ❌ 文档协作 (专注任务管理)
- ❌ 甘特图 (MVP不需要)
- ❌ 时间追踪 (简化功能)
- ❌ 移动端原生应用
- ❌ 高级权限管理
- ❌ 自定义字段
- ❌ 工作流自动化
- ❌ 文件存储 (仅支持链接)
- ❌ 评论系统
- ❌ 活动日志 (详细版)

---

## 📊 数据模型设计

### 核心数据表

#### 1. users (用户表)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL, -- 'manager' or 'employee'
    avatar_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. projects (项目表)
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'active', -- 'active' or 'archived'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. project_members (项目成员表)
```sql
CREATE TABLE project_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'manager' or 'employee'
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, user_id)
);
```

#### 4. tasks (任务表)
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    created_by UUID NOT NULL REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'todo', -- 'todo', 'in_progress', 'completed'
    priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high'
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
```

#### 5. task_notes (任务备注表)
```sql
CREATE TABLE task_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 6. task_history (任务历史表) - 用于统计
```sql
CREATE TABLE task_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🎨 UI/UX 设计原则

### 设计理念

1. **简洁至上** - 去除一切不必要的元素
2. **效率优先** - 减少操作步骤,提升效率
3. **清晰可见** - 信息层级清晰,一目了然
4. **及时反馈** - 操作响应快速,状态明确

### 核心页面

#### Web 端 (项目经理)

1. **仪表盘 (Dashboard)**
   - 项目列表卡片
   - 快速统计数据
   - 最近活动

2. **项目详情页**
   - 项目概览
   - 任务看板 (Kanban)
   - 成员列表

3. **任务管理页**
   - 任务列表 (可筛选/排序)
   - 批量操作
   - 快速创建

4. **统计报表页**
   - 数据可视化图表
   - 员工效率分析
   - 导出功能

5. **团队管理页**
   - 成员列表
   - 邀请成员
   - 权限设置

#### 桌面客户端 (员工)

1. **登录页**
   - 简洁的登录表单
   - 记住密码

2. **任务列表页**
   - 我的任务列表
   - 状态筛选
   - 搜索功能

3. **任务详情页**
   - 任务信息展示
   - 状态更新按钮
   - 添加备注

4. **个人统计页**
   - 完成任务数
   - 工作量趋势
   - 个人排名

---

## 🔧 技术选型详细说明

### 后端技术栈

**核心框架**: Rust + Axum
- ✅ 性能极强 (比 Node.js 快 10-20倍)
- ✅ 内存安全 (无 GC,零成本抽象)
- ✅ 并发能力强 (async/await)
- ✅ 类型安全 (编译时检查)

**数据库**: PostgreSQL + SQLx
- ✅ 功能强大,稳定可靠
- ✅ 支持 JSON, UUID, 全文搜索
- ✅ SQLx 提供编译时 SQL 检查

**缓存**: Redis
- ✅ 高性能缓存
- ✅ 实时数据推送 (Pub/Sub)
- ✅ 会话存储

**认证**: JWT (JSON Web Token)
- ✅ 无状态认证
- ✅ 跨域支持
- ✅ 移动端友好

### 前端技术栈 (Web)

**框架**: React 18 + TypeScript
- ✅ 生态最大,招聘容易
- ✅ 类型安全,减少 Bug
- ✅ 组件化开发

**UI 库**: Ant Design (推荐)
- ✅ 企业级 UI 组件
- ✅ 中文友好
- ✅ 开箱即用

**状态管理**: Zustand
- ✅ 轻量简洁 (< 1KB)
- ✅ 易于使用
- ✅ TypeScript 支持好

**数据可视化**: ECharts
- ✅ 功能强大
- ✅ 中文文档完善
- ✅ 可定制性强

**构建工具**: Vite
- ✅ 开发速度快
- ✅ 热更新快速
- ✅ 生产构建优化

### 桌面客户端技术栈

**框架**: Tauri 2.0
- ✅ 体积小 (比 Electron 小 10倍)
- ✅ 性能好 (使用系统 WebView)
- ✅ 安全性高 (Rust 后端)
- ✅ 跨平台 (Windows/Mac/Linux)

**前端**: HTML/CSS/JavaScript
- ✅ 简单直接
- ✅ 可复用 Web 组件
- ✅ 轻量快速

---

## 📅 开发计划

### 第 1-2 周: 项目初始化和基础架构

**后端**:
- [ ] 初始化 Rust 项目
- [ ] 配置 Axum 框架
- [ ] 设置 PostgreSQL 数据库
- [ ] 设计数据表结构
- [ ] 实现用户认证 (JWT)

**前端**:
- [ ] 初始化 React 项目 (Vite)
- [ ] 配置 TypeScript
- [ ] 集成 Ant Design
- [ ] 设置路由 (React Router)
- [ ] 配置 API 客户端

**客户端**:
- [ ] 初始化 Tauri 项目
- [ ] 配置基础 UI
- [ ] 实现登录功能

---

### 第 3-4 周: 核心功能开发 (项目和任务)

**后端 API**:
- [ ] 项目 CRUD API
- [ ] 任务 CRUD API
- [ ] 项目成员管理 API
- [ ] 任务分配 API

**Web 前端**:
- [ ] 项目列表页
- [ ] 项目创建/编辑
- [ ] 任务看板
- [ ] 任务创建/编辑
- [ ] 任务分配

**桌面客户端**:
- [ ] 任务列表显示
- [ ] 任务详情页
- [ ] 状态更新功能

---

### 第 5-6 周: 进度监控和统计

**后端**:
- [ ] 统计数据 API
- [ ] WebSocket 实时推送
- [ ] 任务历史记录

**Web 前端**:
- [ ] 项目仪表盘
- [ ] 实时进度显示
- [ ] 统计图表 (ECharts)
- [ ] 数据筛选和导出

**桌面客户端**:
- [ ] 实时通知
- [ ] 个人统计页

---

### 第 7-8 周: 测试和优化

**测试**:
- [ ] 单元测试 (后端)
- [ ] 集成测试
- [ ] E2E 测试 (前端)
- [ ] 性能测试

**优化**:
- [ ] 代码重构
- [ ] 性能优化
- [ ] UI/UX 优化
- [ ] Bug 修复

**文档**:
- [ ] API 文档
- [ ] 用户手册
- [ ] 部署文档
- [ ] 开发文档

---

### 第 9-10 周: 早期用户测试

**用户招募**:
- [ ] 在技术社区发布 (V2EX/掘金)
- [ ] 招募 10-20 个测试用户
- [ ] 建立反馈渠道

**反馈收集**:
- [ ] 每周用户访谈
- [ ] 记录问题和建议
- [ ] 快速迭代改进

---

## 🎯 成功指标 (KPI)

### MVP 阶段 (前 3 个月)

**产品指标**:
- [ ] 完成 MVP 所有核心功能
- [ ] GitHub Stars > 100
- [ ] 早期用户 10-20 人

**技术指标**:
- [ ] API 响应时间 < 200ms
- [ ] 页面加载时间 < 2s
- [ ] 桌面客户端启动 < 3s
- [ ] 测试覆盖率 > 70%

**用户指标**:
- [ ] 用户留存率 > 50%
- [ ] 日活跃用户 > 5 人
- [ ] NPS 评分 > 30

---

### 开源发布后 (3-6 个月)

**社区指标**:
- [ ] GitHub Stars > 500
- [ ] Contributors > 5
- [ ] Issues 响应时间 < 24h

**产品指标**:
- [ ] 活跃用户 > 100
- [ ] 项目数 > 200
- [ ] 任务数 > 2000

---

## 📚 参考资源

### 学习资源

**Rust 后端**:
- [Axum 官方文档](https://docs.rs/axum/latest/axum/)
- [SQLx 文档](https://github.com/launchbadge/sqlx)
- [Rust 异步编程](https://rust-lang.github.io/async-book/)

**React 前端**:
- [React 官方文档](https://react.dev/)
- [Ant Design](https://ant.design/)
- [ECharts](https://echarts.apache.org/)

**Tauri 客户端**:
- [Tauri 官方文档](https://tauri.app/)
- [Tauri 最佳实践](https://tauri.app/v1/guides/)

---

## 🚀 下一步行动

### 立即开始 (今天)

1. [ ] 创建新的 GitHub 仓库 `TaskFleet`
2. [ ] 从 Flow_Farm 复制基础代码
3. [ ] 删除不需要的功能模块
4. [ ] 更新 README.md

### 本周完成

1. [ ] 初始化后端项目结构
2. [ ] 初始化前端项目结构
3. [ ] 设计详细的数据库表结构
4. [ ] 绘制核心页面原型图

### 下周开始

1. [ ] 开发用户认证功能
2. [ ] 开发项目管理 API
3. [ ] 开发 Web 端登录页
4. [ ] 开发桌面客户端登录

---

**文档版本**: v1.0  
**最后更新**: 2025年10月28日  
**维护者**: Flow Farm Team

