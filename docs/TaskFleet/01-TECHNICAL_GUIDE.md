# TaskFleet - 技术实现指南

**文档目的**: 提供详细的技术实现方案,帮助快速启动开发

**创建日期**: 2025年10月28日  
**版本**: v1.0

---

## 🏗️ 项目结构

### 推荐的目录结构

```
TaskFleet/
├── backend/                    # Rust 后端
│   ├── src/
│   │   ├── main.rs            # 应用入口
│   │   ├── config.rs          # 配置管理
│   │   ├── database.rs        # 数据库连接
│   │   ├── errors.rs          # 错误处理
│   │   ├── models/            # 数据模型
│   │   │   ├── mod.rs
│   │   │   ├── user.rs
│   │   │   ├── project.rs
│   │   │   └── task.rs
│   │   ├── handlers/          # API 处理器
│   │   │   ├── mod.rs
│   │   │   ├── auth.rs
│   │   │   ├── projects.rs
│   │   │   └── tasks.rs
│   │   ├── middleware/        # 中间件
│   │   │   ├── mod.rs
│   │   │   └── auth.rs
│   │   └── utils/             # 工具函数
│   │       ├── mod.rs
│   │       ├── jwt.rs
│   │       └── validation.rs
│   ├── migrations/            # 数据库迁移
│   ├── tests/                 # 测试
│   ├── Cargo.toml
│   └── .env.example
│
├── frontend/                  # React Web 前端
│   ├── src/
│   │   ├── main.tsx          # 应用入口
│   │   ├── App.tsx           # 根组件
│   │   ├── pages/            # 页面组件
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Projects.tsx
│   │   │   └── Tasks.tsx
│   │   ├── components/       # 通用组件
│   │   │   ├── Layout/
│   │   │   ├── TaskCard/
│   │   │   └── Charts/
│   │   ├── services/         # API 服务
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   └── tasks.ts
│   │   ├── stores/           # 状态管理
│   │   │   ├── authStore.ts
│   │   │   └── taskStore.ts
│   │   ├── types/            # TypeScript 类型
│   │   └── utils/            # 工具函数
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── desktop-client/           # Tauri 桌面客户端
│   ├── src-tauri/           # Rust 后端
│   │   ├── src/
│   │   │   ├── main.rs
│   │   │   └── commands/    # Tauri 命令
│   │   ├── Cargo.toml
│   │   └── tauri.conf.json
│   └── src/                 # 前端
│       ├── index.html
│       ├── app.js
│       └── styles.css
│
├── docs/                    # 文档
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── CONTRIBUTING.md
│
├── docker/                  # Docker 配置
│   ├── Dockerfile.backend
│   └── docker-compose.yml
│
└── README.md
```

---

## 🔧 后端实现详解

### 1. 项目初始化

```bash
# 创建 Rust 项目
cargo new backend --bin
cd backend

# 添加依赖到 Cargo.toml
```

**Cargo.toml**:
```toml
[package]
name = "taskfleet-backend"
version = "0.1.0"
edition = "2021"

[dependencies]
# Web 框架
axum = "0.7"
tokio = { version = "1", features = ["full"] }
tower = "0.4"
tower-http = { version = "0.5", features = ["cors", "trace"] }

# 数据库
sqlx = { version = "0.7", features = ["runtime-tokio-native-tls", "postgres", "uuid", "chrono"] }

# 序列化
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# 认证
jsonwebtoken = "9.2"
argon2 = "0.5"

# 其他
uuid = { version = "1.6", features = ["serde", "v4"] }
chrono = { version = "0.4", features = ["serde"] }
dotenv = "0.15"
tracing = "0.1"
tracing-subscriber = "0.3"
anyhow = "1.0"
thiserror = "1.0"
```

---

### 2. 核心代码示例

#### main.rs - 应用入口

```rust
use axum::{
    routing::{get, post},
    Router,
};
use sqlx::postgres::PgPoolOptions;
use std::net::SocketAddr;
use tower_http::cors::{Any, CorsLayer};
use tracing_subscriber;

mod config;
mod database;
mod errors;
mod handlers;
mod middleware;
mod models;
mod utils;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // 初始化日志
    tracing_subscriber::fmt::init();

    // 加载配置
    dotenv::dotenv().ok();
    let config = config::Config::from_env()?;

    // 连接数据库
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&config.database_url)
        .await?;

    // 运行迁移
    sqlx::migrate!("./migrations").run(&pool).await?;

    // 配置 CORS
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    // 构建路由
    let app = Router::new()
        // 认证路由
        .route("/api/auth/register", post(handlers::auth::register))
        .route("/api/auth/login", post(handlers::auth::login))
        
        // 项目路由
        .route("/api/projects", get(handlers::projects::list))
        .route("/api/projects", post(handlers::projects::create))
        .route("/api/projects/:id", get(handlers::projects::get))
        .route("/api/projects/:id", put(handlers::projects::update))
        .route("/api/projects/:id", delete(handlers::projects::delete))
        
        // 任务路由
        .route("/api/tasks", get(handlers::tasks::list))
        .route("/api/tasks", post(handlers::tasks::create))
        .route("/api/tasks/:id", get(handlers::tasks::get))
        .route("/api/tasks/:id", put(handlers::tasks::update))
        .route("/api/tasks/:id/status", put(handlers::tasks::update_status))
        
        // 统计路由
        .route("/api/stats/overview", get(handlers::stats::overview))
        
        .layer(cors)
        .with_state(pool);

    // 启动服务器
    let addr = SocketAddr::from(([0, 0, 0, 0], config.port));
    tracing::info!("Server listening on {}", addr);
    
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await?;

    Ok(())
}
```

---

#### models/task.rs - 任务数据模型

```rust
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Task {
    pub id: Uuid,
    pub project_id: Uuid,
    pub title: String,
    pub description: Option<String>,
    pub assigned_to: Option<Uuid>,
    pub created_by: Uuid,
    pub status: TaskStatus,
    pub priority: TaskPriority,
    pub due_date: Option<DateTime<Utc>>,
    pub completed_at: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "task_status", rename_all = "lowercase")]
pub enum TaskStatus {
    Todo,
    InProgress,
    Completed,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "task_priority", rename_all = "lowercase")]
pub enum TaskPriority {
    Low,
    Medium,
    High,
}

#[derive(Debug, Deserialize)]
pub struct CreateTaskRequest {
    pub project_id: Uuid,
    pub title: String,
    pub description: Option<String>,
    pub assigned_to: Option<Uuid>,
    pub priority: Option<TaskPriority>,
    pub due_date: Option<DateTime<Utc>>,
}

#[derive(Debug, Deserialize)]
pub struct UpdateTaskRequest {
    pub title: Option<String>,
    pub description: Option<String>,
    pub assigned_to: Option<Uuid>,
    pub status: Option<TaskStatus>,
    pub priority: Option<TaskPriority>,
    pub due_date: Option<DateTime<Utc>>,
}

#[derive(Debug, Deserialize)]
pub struct UpdateTaskStatusRequest {
    pub status: TaskStatus,
}
```

---

#### handlers/tasks.rs - 任务 API 处理器

```rust
use axum::{
    extract::{Path, State},
    http::StatusCode,
    Json,
};
use sqlx::PgPool;
use uuid::Uuid;

use crate::errors::AppError;
use crate::middleware::auth::Claims;
use crate::models::task::{CreateTaskRequest, Task, UpdateTaskRequest, UpdateTaskStatusRequest};

pub async fn create(
    State(pool): State<PgPool>,
    claims: Claims,
    Json(payload): Json<CreateTaskRequest>,
) -> Result<Json<Task>, AppError> {
    let task = sqlx::query_as::<_, Task>(
        r#"
        INSERT INTO tasks (project_id, title, description, assigned_to, created_by, priority, due_date)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING *
        "#,
    )
    .bind(payload.project_id)
    .bind(payload.title)
    .bind(payload.description)
    .bind(payload.assigned_to)
    .bind(claims.user_id)
    .bind(payload.priority.unwrap_or(TaskPriority::Medium))
    .bind(payload.due_date)
    .fetch_one(&pool)
    .await?;

    Ok(Json(task))
}

pub async fn list(
    State(pool): State<PgPool>,
    claims: Claims,
) -> Result<Json<Vec<Task>>, AppError> {
    let tasks = sqlx::query_as::<_, Task>(
        r#"
        SELECT t.* FROM tasks t
        INNER JOIN project_members pm ON t.project_id = pm.project_id
        WHERE pm.user_id = $1
        ORDER BY t.created_at DESC
        "#,
    )
    .bind(claims.user_id)
    .fetch_all(&pool)
    .await?;

    Ok(Json(tasks))
}

pub async fn get(
    State(pool): State<PgPool>,
    claims: Claims,
    Path(id): Path<Uuid>,
) -> Result<Json<Task>, AppError> {
    let task = sqlx::query_as::<_, Task>(
        r#"
        SELECT t.* FROM tasks t
        INNER JOIN project_members pm ON t.project_id = pm.project_id
        WHERE t.id = $1 AND pm.user_id = $2
        "#,
    )
    .bind(id)
    .bind(claims.user_id)
    .fetch_optional(&pool)
    .await?
    .ok_or(AppError::NotFound)?;

    Ok(Json(task))
}

pub async fn update_status(
    State(pool): State<PgPool>,
    claims: Claims,
    Path(id): Path<Uuid>,
    Json(payload): Json<UpdateTaskStatusRequest>,
) -> Result<Json<Task>, AppError> {
    let task = sqlx::query_as::<_, Task>(
        r#"
        UPDATE tasks
        SET status = $1,
            completed_at = CASE WHEN $1 = 'completed' THEN NOW() ELSE NULL END,
            updated_at = NOW()
        WHERE id = $2 AND (assigned_to = $3 OR created_by = $3)
        RETURNING *
        "#,
    )
    .bind(payload.status)
    .bind(id)
    .bind(claims.user_id)
    .fetch_optional(&pool)
    .await?
    .ok_or(AppError::NotFound)?;

    Ok(Json(task))
}
```

---

## 🎨 前端实现详解

### 1. 项目初始化

```bash
# 使用 Vite 创建项目
npm create vite@latest frontend -- --template react-ts
cd frontend

# 安装依赖
npm install
npm install antd @ant-design/icons
npm install zustand
npm install axios
npm install react-router-dom
npm install echarts echarts-for-react
npm install dayjs
```

---

### 2. API 服务封装

**services/api.ts**:
```typescript
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器 - 添加 JWT token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // 响应拦截器 - 处理错误
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string): Promise<T> {
    const response = await this.client.get<T>(url);
    return response.data;
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post<T>(url, data);
    return response.data;
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.put<T>(url, data);
    return response.data;
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete<T>(url);
    return response.data;
  }
}

export const api = new ApiClient();
```

---

**services/tasks.ts**:
```typescript
import { api } from './api';
import { Task, CreateTaskRequest, UpdateTaskStatusRequest } from '../types';

export const taskService = {
  // 获取任务列表
  async getTasks(): Promise<Task[]> {
    return api.get<Task[]>('/tasks');
  },

  // 获取单个任务
  async getTask(id: string): Promise<Task> {
    return api.get<Task>(`/tasks/${id}`);
  },

  // 创建任务
  async createTask(data: CreateTaskRequest): Promise<Task> {
    return api.post<Task>('/tasks', data);
  },

  // 更新任务状态
  async updateTaskStatus(id: string, status: string): Promise<Task> {
    return api.put<Task>(`/tasks/${id}/status`, { status });
  },

  // 批量创建任务
  async batchCreateTasks(tasks: CreateTaskRequest[]): Promise<Task[]> {
    return api.post<Task[]>('/tasks/batch', { tasks });
  },
};
```

---

### 3. 状态管理 (Zustand)

**stores/taskStore.ts**:
```typescript
import { create } from 'zustand';
import { Task } from '../types';
import { taskService } from '../services/tasks';

interface TaskState {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchTasks: () => Promise<void>;
  createTask: (data: CreateTaskRequest) => Promise<void>;
  updateTaskStatus: (id: string, status: string) => Promise<void>;
}

export const useTaskStore = create<TaskState>((set, get) => ({
  tasks: [],
  loading: false,
  error: null,

  fetchTasks: async () => {
    set({ loading: true, error: null });
    try {
      const tasks = await taskService.getTasks();
      set({ tasks, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  createTask: async (data) => {
    set({ loading: true, error: null });
    try {
      const newTask = await taskService.createTask(data);
      set((state) => ({
        tasks: [newTask, ...state.tasks],
        loading: false,
      }));
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  updateTaskStatus: async (id, status) => {
    try {
      const updatedTask = await taskService.updateTaskStatus(id, status);
      set((state) => ({
        tasks: state.tasks.map((t) => (t.id === id ? updatedTask : t)),
      }));
    } catch (error) {
      set({ error: error.message });
    }
  },
}));
```

---

### 4. 核心组件示例

**pages/Dashboard.tsx**:
```typescript
import React, { useEffect } from 'react';
import { Card, Row, Col, Statistic } from 'antd';
import { CheckCircleOutlined, ClockCircleOutlined, LoadingOutlined } from '@ant-design/icons';
import { useTaskStore } from '../stores/taskStore';
import ReactECharts from 'echarts-for-react';

export const Dashboard: React.FC = () => {
  const { tasks, fetchTasks } = useTaskStore();

  useEffect(() => {
    fetchTasks();
  }, []);

  const todoCount = tasks.filter((t) => t.status === 'todo').length;
  const inProgressCount = tasks.filter((t) => t.status === 'in_progress').length;
  const completedCount = tasks.filter((t) => t.status === 'completed').length;

  // 图表配置
  const chartOption = {
    title: { text: '任务状态分布' },
    tooltip: {},
    series: [
      {
        type: 'pie',
        data: [
          { value: todoCount, name: '待办' },
          { value: inProgressCount, name: '进行中' },
          { value: completedCount, name: '已完成' },
        ],
      },
    ],
  };

  return (
    <div>
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic
              title="待办任务"
              value={todoCount}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="进行中"
              value={inProgressCount}
              prefix={<LoadingOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="已完成"
              value={completedCount}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 16 }}>
        <ReactECharts option={chartOption} />
      </Card>
    </div>
  );
};
```

---

## 💻 桌面客户端实现

### Tauri 配置

**tauri.conf.json**:
```json
{
  "build": {
    "beforeBuildCommand": "",
    "beforeDevCommand": "",
    "devPath": "../src",
    "distDir": "../src"
  },
  "package": {
    "productName": "TaskFleet",
    "version": "0.1.0"
  },
  "tauri": {
    "allowlist": {
      "all": false,
      "shell": {
        "all": false,
        "open": true
      },
      "http": {
        "all": true,
        "request": true,
        "scope": ["http://localhost:3000/**", "https://api.taskfleet.com/**"]
      }
    },
    "windows": [
      {
        "title": "TaskFleet - 员工客户端",
        "width": 1000,
        "height": 700,
        "resizable": true,
        "fullscreen": false
      }
    ]
  }
}
```

---

## 🚀 部署指南

### Docker 部署

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: taskfleet
      POSTGRES_PASSWORD: password
      POSTGRES_DB: taskfleet
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./backend
      dockerfile: ../docker/Dockerfile.backend
    environment:
      DATABASE_URL: postgres://taskfleet:password@postgres/taskfleet
      REDIS_URL: redis://redis:6379
      JWT_SECRET: your-secret-key
    ports:
      - "3000:3000"
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: ./frontend
    ports:
      - "5173:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

---

## 📝 开发规范

### Git 工作流

```bash
# 功能分支
git checkout -b feature/task-management
# 开发完成后
git commit -m "feat: add task management"
git push origin feature/task-management
# 创建 Pull Request
```

### Commit 规范

```
feat: 新功能
fix: Bug 修复
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/工具
```

---

**文档结束**
