# Flow Farm API 开发和文档生成

你是一个专业的 API 开发工程师，负责 Flow Farm 系统的 REST API 设计、实现和文档化。

## API 开发任务

为 Flow Farm 计费自动化流量农场系统设计和实现完整的 REST API，支持三角色权限管理。

## 技术栈

- **后端框架**: Rust + Axum
- **数据库**: SQLx + SQLite
- **认证**: JWT Token
- **文档**: OpenAPI 3.0

## API 模块设计

### 1. 认证模块 (/api/auth)

```
POST /api/auth/login        # 用户登录
POST /api/auth/logout       # 用户登出
POST /api/auth/refresh      # 刷新令牌
GET  /api/auth/profile      # 获取用户信息
PUT  /api/auth/profile      # 更新用户信息
```

### 2. 用户管理 (/api/users)

```
GET    /api/users           # 获取用户列表 (分页)
POST   /api/users           # 创建用户
GET    /api/users/{id}      # 获取用户详情
PUT    /api/users/{id}      # 更新用户信息
DELETE /api/users/{id}      # 删除用户
PUT    /api/users/{id}/status # 更新用户状态
```

### 3. 设备管理 (/api/devices)

```
GET    /api/devices         # 获取设备列表
POST   /api/devices         # 注册新设备
GET    /api/devices/{id}    # 获取设备详情
PUT    /api/devices/{id}    # 更新设备信息
DELETE /api/devices/{id}    # 删除设备
POST   /api/devices/{id}/heartbeat # 设备心跳
```

### 4. 工作记录 (/api/work-records)

```
GET    /api/work-records    # 获取工作记录
POST   /api/work-records    # 创建工作记录
GET    /api/work-records/{id} # 获取记录详情
PUT    /api/work-records/{id} # 更新工作记录
DELETE /api/work-records/{id} # 删除工作记录
```

### 5. 计费管理 (/api/billing)

```
GET    /api/billing/usage   # 获取使用统计
GET    /api/billing/bills   # 获取账单列表
POST   /api/billing/recharge # 充值
GET    /api/billing/settings # 获取计费设置
PUT    /api/billing/settings # 更新计费设置
```

### 6. 统计报表 (/api/reports)

```
GET    /api/reports/dashboard    # 仪表板数据
GET    /api/reports/work-stats   # 工作统计
GET    /api/reports/billing-stats # 计费统计
GET    /api/reports/export       # 导出报表
```

## 数据模型设计

### User (用户)

```rust
#[derive(Serialize, Deserialize, sqlx::FromRow)]
pub struct User {
    pub id: i64,
    pub username: String,
    pub email: Option<String>,
    pub role: UserRole,
    pub status: UserStatus,
    pub parent_id: Option<i64>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Serialize, Deserialize, sqlx::Type)]
pub enum UserRole {
    SystemAdmin,
    UserAdmin,
    Employee,
}
```

### Device (设备)

```rust
#[derive(Serialize, Deserialize, sqlx::FromRow)]
pub struct Device {
    pub id: i64,
    pub device_id: String,
    pub device_name: String,
    pub user_id: i64,
    pub platform: DevicePlatform,
    pub status: DeviceStatus,
    pub last_heartbeat: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
}
```

### WorkRecord (工作记录)

```rust
#[derive(Serialize, Deserialize, sqlx::FromRow)]
pub struct WorkRecord {
    pub id: i64,
    pub user_id: i64,
    pub device_id: i64,
    pub platform: String,
    pub operation_type: String,
    pub operation_count: i32,
    pub duration_seconds: i32,
    pub success_count: i32,
    pub created_at: DateTime<Utc>,
}
```

## API 响应格式

### 成功响应

```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "输入数据验证失败",
    "details": {}
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 分页响应

```json
{
  "success": true,
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_pages": 5,
      "total_items": 100
    }
  }
}
```

## 权限控制

### 角色权限矩阵

- **系统管理员**: 所有 API 访问权限
- **用户管理员**: 自己公司范围内的数据访问
- **员工**: 只能访问自己的数据和提交工作记录

### 权限验证中间件

```rust
pub async fn require_role(
    roles: Vec<UserRole>
) -> impl Filter<Extract = (), Error = Rejection> + Clone {
    // 实现权限验证逻辑
}
```

## 开发要求

### 代码质量

1. **错误处理**: 统一的错误类型和响应格式
2. **输入验证**: 使用 validator crate 验证输入
3. **SQL 安全**: 使用参数化查询防止注入
4. **日志记录**: 记录关键操作和错误信息
5. **文档注释**: 所有 API 都要有详细文档

### 性能要求

1. **数据库优化**: 合理的索引设计
2. **查询优化**: 避免 N+1 查询问题
3. **缓存策略**: 适当的缓存层
4. **连接池**: 数据库连接池配置
5. **异步处理**: 充分利用 Rust 异步特性

### 安全要求

1. **认证**: JWT 令牌验证
2. **授权**: 基于角色的权限控制
3. **HTTPS**: 强制使用 HTTPS
4. **CORS**: 适当的跨域配置
5. **限流**: API 请求频率限制

## 测试要求

### 单元测试

- 每个 API 处理器都要有单元测试
- 覆盖正常流程和异常情况
- 测试权限验证逻辑

### 集成测试

- 完整的 API 调用流程测试
- 数据库事务测试
- 认证授权集成测试

### API 文档

- 使用 OpenAPI 3.0 规范
- 自动生成 API 文档
- 提供 API 调用示例
- 错误码说明文档

开始开发前，请确保理解整个项目的架构和业务需求，遵循项目的编码规范和最佳实践。
