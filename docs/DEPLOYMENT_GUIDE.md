# Flow Farm 认证系统部署指南

## 📋 快速部署

### 1. 自动部署（推荐）

使用提供的脚本进行一键部署：

```bash
# Windows
cd d:\repositories\Flow_Farm
scripts\switch-auth.bat new

# Linux/Mac
cd /path/to/Flow_Farm
chmod +x scripts/switch-auth.sh
./scripts/switch-auth.sh new
```

### 2. 手动部署

如果自动脚本无法运行，可以手动执行以下步骤：

#### 步骤 1: 备份现有文件
```bash
mkdir backup_manual
cp src/main.tsx backup_manual/
cp src/App.tsx backup_manual/
cp src/store/index.ts backup_manual/
```

#### 步骤 2: 更新入口文件

**更新 src/main.tsx:**
```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider } from 'react-redux'
import { store } from './store/indexNew'
import AppNew from './AppNew'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <AppNew />
    </Provider>
  </React.StrictMode>,
)
```

**更新 src/App.tsx:**
复制 `src/AppNew.tsx` 的内容到 `src/App.tsx`

**更新 src/store/index.ts:**
复制 `src/store/indexNew.ts` 的内容到 `src/store/index.ts`

## 🔧 环境配置

### 1. 创建环境变量文件

在项目根目录创建 `.env` 文件：

```env
# API配置
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=10000

# 认证配置
VITE_AUTH_TOKEN_KEY=flow_farm_token
VITE_AUTH_REFRESH_TOKEN_KEY=flow_farm_refresh_token
VITE_AUTH_SESSION_TIMEOUT=30

# 安全配置
VITE_PASSWORD_MIN_LENGTH=8
VITE_LOGIN_MAX_ATTEMPTS=5
VITE_LOCKOUT_DURATION=15

# 开发模式配置
VITE_DEBUG_MODE=true
VITE_LOG_LEVEL=debug
```

### 2. 生产环境配置

创建 `.env.production` 文件：

```env
# 生产API配置
VITE_API_BASE_URL=https://your-production-api.com
VITE_API_TIMEOUT=15000

# 生产认证配置
VITE_AUTH_TOKEN_KEY=ff_token
VITE_AUTH_REFRESH_TOKEN_KEY=ff_refresh
VITE_AUTH_SESSION_TIMEOUT=60

# 生产安全配置
VITE_PASSWORD_MIN_LENGTH=12
VITE_LOGIN_MAX_ATTEMPTS=3
VITE_LOCKOUT_DURATION=30

# 生产模式配置
VITE_DEBUG_MODE=false
VITE_LOG_LEVEL=error
```

## ⚡ 启动服务

### 1. 安装依赖
```bash
npm install
```

### 2. 启动开发服务器
```bash
npm run dev
```

### 3. 构建生产版本
```bash
npm run build
```

## 🧪 验证部署

### 1. 使用脚本验证
```bash
# Windows
scripts\switch-auth.bat test

# Linux/Mac
./scripts/switch-auth.sh test
```

### 2. 手动验证

#### 检查必要文件：
- [ ] `src/services/auth/index.ts`
- [ ] `src/services/auth/AuthServiceSimplified.ts`
- [ ] `src/services/auth/ApiAdapter.ts`
- [ ] `src/store/authSliceNew.ts`
- [ ] `src/pages/LoginNew.tsx`
- [ ] `src/components/ProtectedRouteNew.tsx`

#### 检查TypeScript编译：
```bash
npx tsc --noEmit --skipLibCheck
```

#### 检查应用启动：
1. 访问 `http://localhost:3000`
2. 应该看到新的登录界面
3. 测试登录功能
4. 验证角色权限系统

## 🔐 后端API适配

### 1. Rust后端接口格式

确保Rust后端返回以下格式：

```rust
// 登录响应
#[derive(Serialize)]
pub struct LoginResponse {
    pub access_token: String,
    pub refresh_token: Option<String>,
    pub token_type: String,
    pub expires_in: i64,
    pub user: UserInfo,
}

// 用户信息
#[derive(Serialize)]
pub struct UserInfo {
    pub id: i32,
    pub username: String,
    pub role: String,
    pub permissions: Vec<String>,
    pub is_active: bool,
}

// 错误响应
#[derive(Serialize)]
pub struct ErrorResponse {
    pub error: String,
    pub message: String,
    pub details: Option<serde_json::Value>,
}
```

### 2. API端点配置

确保以下端点可用：

- `POST /auth/login` - 用户登录
- `POST /auth/logout` - 用户登出
- `GET /auth/me` - 获取当前用户信息
- `POST /auth/refresh` - 刷新令牌

## 🚨 故障排除

### 1. 常见问题

#### 问题：页面空白或组件未加载
**解决方案：**
```bash
# 清理缓存
rm -rf node_modules/.cache
rm -rf dist
npm install
npm run dev
```

#### 问题：TypeScript编译错误
**解决方案：**
```bash
# 检查类型定义
npm install --save-dev @types/react @types/react-dom
npx tsc --noEmit --skipLibCheck
```

#### 问题：API请求失败
**解决方案：**
1. 检查 `.env` 文件中的 `VITE_API_BASE_URL`
2. 确认后端服务器正在运行
3. 检查网络连接和CORS设置

#### 问题：认证状态丢失
**解决方案：**
1. 检查localStorage中的token
2. 验证token格式和有效期
3. 检查ApiAdapter中的token处理逻辑

### 2. 调试模式

开启调试模式：

```env
VITE_DEBUG_MODE=true
VITE_LOG_LEVEL=debug
```

查看控制台输出：
- 认证流程日志
- API请求详情
- 状态变化记录

### 3. 回滚步骤

如果新系统出现问题，可以快速回滚：

```bash
# 使用脚本回滚
scripts\switch-auth.bat old

# 或手动回滚
cp backup_*/main.tsx.backup src/main.tsx
cp backup_*/App.tsx.backup src/App.tsx
cp backup_*/store_index.ts.backup src/store/index.ts
```

## 📊 监控和维护

### 1. 性能监控

关键指标：
- 登录响应时间 (<2秒)
- Token刷新成功率 (>99%)
- 认证错误率 (<1%)

### 2. 安全检查

定期检查：
- Token过期时间设置
- 密码强度要求
- 登录尝试限制
- 会话超时配置

### 3. 日志分析

监控日志：
```bash
# 查看认证相关日志
grep "AUTH" logs/application.log
grep "LOGIN" logs/application.log
grep "ERROR" logs/application.log
```

## 🎯 后续优化

### 1. 性能优化
- [ ] 实现登录状态缓存
- [ ] 添加请求去重机制
- [ ] 优化组件懒加载

### 2. 安全增强
- [ ] 添加双因素认证
- [ ] 实现设备指纹识别
- [ ] 增强密码策略

### 3. 用户体验
- [ ] 添加记住登录状态
- [ ] 实现单点登录(SSO)
- [ ] 优化移动端适配

---

**部署完成后，请务必验证所有功能正常运行！**
