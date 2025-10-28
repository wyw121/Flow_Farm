# Flow Farm AI代理指令

## 项目总览

Flow Farm是一个社交平台自动化获客系统，包含三个主要组件：

- 服务器后端（Rust + Axum + SQLite）
- 服务器前端（React + TypeScript）
- 员工客户端（Rust + Tauri 2.0 + HTML/CSS/JS）

## 构建和验证指令

### 环境设置（必须按顺序执行）

```bash
# 1. 服务器后端
cd server-backend
cargo build --release
cargo run --release

# 2. 服务器前端
cd server-frontend
npm install
npm run dev

# 3. 员工客户端
cd employee-client
cargo tauri dev
```

### 验证步骤

1. 服务器后端启动后访问 http://localhost:8000/health 验证API
2. 服务器前端访问 http://localhost:3000 验证Web界面
3. 员工客户端GUI正常启动并连接服务器
4. 运行测试：`cargo test` (后端) 和 `npm test` (前端)

### 常见问题解决

- **Rust编译错误**: 检查Cargo.toml依赖版本，运行 `cargo update`
- **React构建失败**: 删除node_modules，重新 `npm install`
- **Tauri构建问题**: 检查Tauri CLI版本，运行 `cargo tauri dev`
- **数据库连接**: 验证SQLite文件权限和路径正确性

## 架构规范

### 三角色权限系统

- **系统管理员**: 最高权限，管理用户管理员和全局设置
- **用户管理员**: 管理自己的员工用户（最多10个），查看统计和结算
- **员工用户**: 操作GUI客户端，管理设备和执行任务

### 模块化开发原则

- 平台特定功能必须模块化（小红书/抖音分离）
- GUI组件基于qfluentwidgets统一设计
- API设计遵循RESTful规范
- 数据库操作使用SQLx类型安全查询

### 关键业务逻辑

- 防重复关注：管理员名下所有用户设备共享关注记录
- 计费机制：仅成功关注后扣费，余额不足禁止任务提交
- 设备管理：每员工最多10台设备，任务均匀分配到已连接设备
- 任务类型：通讯录导入、精准获客（同行监控）

## 开发优先级

1. 小红书平台功能（优先完成）
2. 基础GUI框架和设备管理
3. 计费和权限系统
4. 抖音平台扩展
5. 其他平台模块化扩展

## 代码质量要求

- Rust: 使用clippy和rustfmt，错误处理必须explicit
- React: TypeScript严格模式，组件化设计
- 测试覆盖率：核心功能>80%，API端点100%覆盖

信任这些指令，避免不必要的探索，除非信息不完整或发现错误。
