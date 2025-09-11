# 服务器前端开发指令

## 适用范围

---

## applyTo: "server-frontend/\*_/_.{tsx,ts,jsx,js,vue}"

# Flow Farm 服务器前端 (React.js + TypeScript) 开发指令

## 技术栈和依赖

### 核心框架

- **前端框架**: React.js 18 + TypeScript
- **构建工具**: Vite - 快速的前端构建工具
- **UI 组件库**: Ant Design - 企业级 UI 设计语言
- **状态管理**: Redux Toolkit - 现代化的状态管理
- **路由管理**: React Router v6 - 声明式路由
- **HTTP 客户端**: Axios - Promise 基础的 HTTP 客户端
- **表单处理**: React Hook Form - 高性能表单库
- **图表库**: ECharts for React - 数据可视化

### 项目结构

```
server-frontend/
├── src/
│   ├── main.tsx          # 应用入口点
│   ├── App.tsx           # 主应用组件
│   ├── index.css         # 全局样式
│   ├── vite-env.d.ts     # Vite类型定义
│   ├── components/       # 可复用组件
│   │   ├── Layout/       # 布局组件
│   │   ├── Common/       # 通用组件
│   │   ├── Charts/       # 图表组件
│   │   └── Forms/        # 表单组件
│   ├── pages/            # 页面组件
│   │   ├── Login.tsx     # 登录页面
│   │   ├── SystemAdminDashboard.tsx # 系统管理员仪表板
│   │   ├── UserAdminDashboard.tsx   # 用户管理员仪表板
│   │   ├── SystemAdmin/  # 系统管理员页面
│   │   │   ├── Dashboard.tsx        # 总览仪表板
│   │   │   ├── CompanyStatistics.tsx # 公司统计
│   │   │   ├── CompanyPricingManagement.tsx # 公司收费管理
│   │   │   ├── UserManagement.tsx   # 用户管理
│   │   │   └── SystemLogs.tsx       # 系统日志
│   │   └── UserAdmin/    # 用户管理员页面
│   │       ├── Dashboard.tsx        # 用户仪表板
│   │       ├── EmployeeManagement.tsx # 员工管理
│   │       ├── WorkRecords.tsx      # 工作记录
│   │       ├── BillingManagement.tsx # 计费管理
│   │       └── Reports.tsx          # 报表
│   ├── services/         # API服务
│   │   ├── api.ts        # API基础配置
│   │   ├── authService.ts      # 认证服务
│   │   ├── userService.ts      # 用户服务
│   │   ├── billingService.ts   # 计费服务
│   │   ├── workRecordService.ts # 工作记录服务
│   │   └── reportService.ts    # 报表服务
│   ├── store/            # Redux状态管理
│   │   ├── index.ts      # Store配置
│   │   ├── authSlice.ts  # 认证状态
│   │   ├── userSlice.ts  # 用户状态
│   │   └── appSlice.ts   # 应用状态
│   ├── types/            # TypeScript类型定义
│   │   ├── index.ts      # 通用类型
│   │   ├── auth.ts       # 认证相关类型
│   │   ├── user.ts       # 用户相关类型
│   │   └── api.ts        # API响应类型
│   ├── utils/            # 工具函数
│   │   ├── constants.ts  # 常量定义
│   │   ├── helpers.ts    # 辅助函数
│   │   ├── validation.ts # 表单验证
│   │   └── formatting.ts # 格式化函数
│   └── assets/           # 静态资源
│       ├── images/       # 图片资源
│       └── styles/       # 样式文件
├── public/               # 公共静态文件
├── package.json          # 依赖配置
├── tsconfig.json         # TypeScript配置
├── vite.config.ts        # Vite配置
└── index.html           # HTML模板
```

## 编程规范

### TypeScript/React 规范

- 使用函数组件和 Hooks
- 组件命名使用 PascalCase
- 文件命名使用 PascalCase
- 函数和变量使用 camelCase
- 常量使用 UPPER_CASE
- 严格的 TypeScript 配置，避免 any 类型

### 组件设计规范

- 单一职责原则，组件功能清晰
- 使用 React.memo 优化性能
- Props 接口定义要完整
- 使用自定义 Hooks 抽离逻辑
- 组件要有适当的错误边界

### 样式规范

- 使用 CSS Modules 或 styled-components
- 遵循 BEM 命名规范
- 响应式设计，支持移动端
- 使用 Ant Design 的主题定制

## 核心功能模块

### 1. 认证系统

```typescript
// src/services/authService.ts
export interface LoginRequest {
  username: string;
  password: string;
  role: "system_admin" | "user_admin";
}

export interface AuthResponse {
  token: string;
  user: User;
  permissions: string[];
}

export const authService = {
  login: (data: LoginRequest): Promise<AuthResponse> => {
    return apiClient.post("/auth/login", data);
  },

  logout: (): Promise<void> => {
    return apiClient.post("/auth/logout");
  },

  refreshToken: (): Promise<AuthResponse> => {
    return apiClient.post("/auth/refresh");
  },
};
```

### 2. 状态管理

```typescript
// src/store/authSlice.ts
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  permissions: string[];
  loading: boolean;
}

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    loginStart: (state) => {
      state.loading = true;
    },
    loginSuccess: (state, action: PayloadAction<AuthResponse>) => {
      state.isAuthenticated = true;
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.permissions = action.payload.permissions;
      state.loading = false;
    },
    loginFailure: (state) => {
      state.loading = false;
      state.isAuthenticated = false;
    },
    logout: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.token = null;
      state.permissions = [];
    },
  },
});
```

### 3. API 客户端配置

```typescript
// src/services/api.ts
import axios from "axios";
import { store } from "../store";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 10000,
});

// 请求拦截器 - 添加认证令牌
apiClient.interceptors.request.use(
  (config) => {
    const state = store.getState();
    const token = state.auth.token;

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器 - 处理认证错误
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      store.dispatch(logout());
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 4. 权限控制组件

```typescript
// src/components/Common/PermissionGuard.tsx
interface PermissionGuardProps {
  permissions: string[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  permissions,
  children,
  fallback = null,
}) => {
  const userPermissions = useSelector(
    (state: RootState) => state.auth.permissions
  );

  const hasPermission = permissions.some((permission) =>
    userPermissions.includes(permission)
  );

  return hasPermission ? <>{children}</> : <>{fallback}</>;
};
```

## 开发模式

### 启动开发服务器

```bash
cd server-frontend
npm install
npm run dev
# 开发服务器在 http://localhost:3000
```

### 构建和部署

```bash
# 构建生产版本
npm run build

# 预览构建结果
npm run preview

# 类型检查
npm run type-check

# 代码格式化
npm run format

# ESLint检查
npm run lint
```

### 测试

```bash
# 运行单元测试
npm run test

# 运行测试并生成覆盖率报告
npm run test:coverage

# 运行端到端测试
npm run test:e2e
```

## 用户界面设计

### 系统管理员界面

- **总览仪表板**: 显示系统整体运营数据
- **公司统计**: 各用户管理员公司的数据统计
- **价格设置**: 配置计费规则和价格
- **用户管理**: 管理用户管理员账户
- **系统日志**: 查看系统操作日志

### 用户管理员界面

- **员工仪表板**: 显示公司员工工作概况
- **员工管理**: 管理员工账户（最多 10 个）
- **工作记录**: 查看员工的工作记录和统计
- **计费管理**: 查看使用情况和费用
- **报表中心**: 生成各类数据报表

### 通用组件

- **数据表格**: 支持排序、筛选、分页
- **图表组件**: 各类统计图表
- **表单组件**: 统一的表单设计
- **布局组件**: 响应式布局

## 性能优化

### 代码分割

```typescript
// 路由级别的代码分割
const SystemAdminDashboard = lazy(
  () => import("../pages/SystemAdminDashboard")
);
const UserAdminDashboard = lazy(() => import("../pages/UserAdminDashboard"));

// 组件级别的代码分割
const ChartComponent = lazy(
  () => import("../components/Charts/ChartComponent")
);
```

### 状态优化

- 使用 React.memo 避免不必要的重渲染
- 使用 useMemo 和 useCallback 优化计算和回调
- 合理设计 Redux 状态结构
- 使用 RTK Query 进行数据缓存

### 网络优化

- 实现请求去重和缓存
- 使用虚拟滚动处理大列表
- 图片懒加载和压缩
- API 响应数据分页

## 错误处理

### 全局错误边界

```typescript
// src/components/Common/ErrorBoundary.tsx
class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
    // 可以在这里上报错误
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }

    return this.props.children;
  }
}
```

### API 错误处理

```typescript
// src/utils/errorHandler.ts
export const handleApiError = (error: any) => {
  if (error.response) {
    // 服务器响应错误
    const { status, data } = error.response;

    switch (status) {
      case 400:
        message.error("请求参数错误");
        break;
      case 401:
        message.error("认证失败，请重新登录");
        break;
      case 403:
        message.error("权限不足");
        break;
      case 500:
        message.error("服务器内部错误");
        break;
      default:
        message.error(data?.message || "未知错误");
    }
  } else if (error.request) {
    // 网络错误
    message.error("网络连接失败，请检查网络");
  } else {
    // 其他错误
    message.error("发生未知错误");
  }
};
```

## 安全要求

### 认证和授权

- 所有页面都要进行认证检查
- 基于权限的路由保护
- 敏感操作需要二次确认
- 自动令牌刷新机制

### 数据保护

- 不在前端存储敏感信息
- 使用 HTTPS 传输数据
- 实现 CSP 内容安全策略
- 防止 XSS 和 CSRF 攻击

### 输入验证

```typescript
// src/utils/validation.ts
export const validationRules = {
  username: [
    { required: true, message: "请输入用户名" },
    { min: 3, max: 20, message: "用户名长度为3-20个字符" },
  ],
  password: [
    { required: true, message: "请输入密码" },
    { min: 8, message: "密码至少8个字符" },
    {
      pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      message: "密码必须包含大小写字母和数字",
    },
  ],
};
```

## 监控和分析

### 用户行为分析

- 页面访问统计
- 用户操作路径分析
- 错误发生频率统计
- 性能指标监控

### 错误监控

```typescript
// src/utils/monitoring.ts
export const reportError = (error: Error, context?: any) => {
  // 上报错误到监控服务
  console.error("Error reported:", error, context);

  // 可以集成第三方错误监控服务
  // 如 Sentry, LogRocket 等
};
```

## 重要提醒

1. **类型安全** - 充分利用 TypeScript 的类型系统，避免运行时错误
2. **组件复用** - 设计可复用的组件，提高开发效率
3. **性能优化** - 注意组件渲染性能，避免不必要的重渲染
4. **用户体验** - 提供友好的加载状态和错误提示
5. **响应式设计** - 确保在不同屏幕尺寸下的良好体验
6. **可访问性** - 遵循 WCAG 可访问性标准
7. **测试覆盖** - 为关键功能编写单元测试和集成测试

## 技术栈

### 核心框架和库

- **前端框架**: Vue.js 3 + TypeScript + Vite
- **UI 组件库**: Ant Design Vue
- **状态管理**: Pinia
- **路由管理**: Vue Router
- **HTTP 客户端**: Axios
- **图表库**: ECharts + vue-echarts
- **时间处理**: dayjs
- **表单验证**: Ant Design Vue 内置验证

### 项目结构

```
server-frontend/src/
├── main.ts                 # 应用程序入口
├── App.vue                 # 根组件
├── types/                  # TypeScript类型定义
│   ├── index.ts           # 通用类型
│   ├── api.ts             # API相关类型
│   └── user.ts            # 用户相关类型
├── components/             # 可复用组件
│   ├── Layout/            # 布局组件
│   ├── Charts/            # 图表组件
│   ├── Forms/             # 表单组件
│   └── Common/            # 通用组件
├── pages/                  # 页面组件
│   ├── Login.tsx          # 登录页面
│   ├── SystemAdmin/       # 系统管理员页面
│   │   ├── Dashboard.tsx
│   │   ├── UserManagement.tsx
│   │   └── SystemSettings.tsx
│   └── UserAdmin/         # 用户管理员页面
│       ├── Dashboard.tsx
│       ├── EmployeeManagement.tsx
│       └── BillingManagement.tsx
├── services/               # 服务层
│   ├── api.ts             # API基础配置
│   ├── authService.ts     # 认证服务
│   ├── userService.ts     # 用户服务
│   ├── billingService.ts  # 计费服务
│   └── workRecordService.ts # 工作记录服务
├── store/                  # Pinia状态管理
│   ├── index.ts           # Store配置
│   ├── authSlice.ts       # 认证状态
│   ├── userSlice.ts       # 用户状态
│   └── appSlice.ts        # 应用状态
├── router/                 # 路由配置
│   ├── index.ts           # 路由主配置
│   └── guards.ts          # 路由守卫
├── utils/                  # 工具函数
│   ├── request.ts         # HTTP请求封装
│   ├── auth.ts            # 认证工具
│   ├── date.ts            # 日期工具
│   └── validation.ts      # 验证工具
└── styles/                 # 样式文件
    ├── globals.css        # 全局样式
    ├── variables.css      # CSS变量
    └── components.css     # 组件样式
```

### 路由和权限

- 基于角色的路由守卫
- 动态菜单生成
- 页面权限验证
- 404 和错误页面处理

## 代码示例

### Vue 组件示例

```vue
<template>
  <div class="admin-dashboard">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统统计</span>
          <el-button type="primary" @click="refreshData">刷新</el-button>
        </div>
      </template>
      <div class="statistics">
        <el-row :gutter="20">
          <el-col :span="6" v-for="stat in statistics" :key="stat.key">
            <el-statistic
              :title="stat.title"
              :value="stat.value"
              :suffix="stat.suffix"
            />
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useSystemStore } from "@/stores/system";

interface StatisticItem {
  key: string;
  title: string;
  value: number;
  suffix?: string;
}

const systemStore = useSystemStore();
const statistics = ref<StatisticItem[]>([]);

const refreshData = async () => {
  await systemStore.fetchStatistics();
  statistics.value = systemStore.statistics;
};

onMounted(() => {
  refreshData();
});
</script>
```

### Pinia Store 示例

```typescript
import { defineStore } from "pinia";
import { ref } from "vue";
import { authApi } from "@/api/auth";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null);
  const token = ref<string>("");

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await authApi.login(credentials);
      token.value = response.token;
      user.value = response.user;
      localStorage.setItem("token", token.value);
    } catch (error) {
      throw new Error("登录失败");
    }
  };

  const logout = () => {
    user.value = null;
    token.value = "";
    localStorage.removeItem("token");
  };

  const hasPermission = (permission: string): boolean => {
    return user.value?.permissions.includes(permission) || false;
  };

  return {
    user,
    token,
    login,
    logout,
    hasPermission,
  };
});
```

### 路由守卫示例

```typescript
import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/admin",
      component: AdminLayout,
      meta: { requiresAuth: true, role: "SYSTEM_ADMIN" },
      children: [
        {
          path: "users",
          component: UserManagement,
          meta: { permission: "manage_users" },
        },
      ],
    },
  ],
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.token) {
    next("/login");
    return;
  }

  if (to.meta.role && authStore.user?.role !== to.meta.role) {
    next("/403");
    return;
  }

  next();
});
```

## 样式规范

- 使用 SCSS 进行样式开发
- 遵循 BEM 命名约定
- 使用 CSS 变量定义主题色彩
- 实现响应式设计
- 优化加载性能

## 重要提醒

- 确保类型安全，避免使用 any
- 实现错误边界和异常处理
- 优化打包体积和加载速度
- 做好 SEO 优化
- 确保无障碍访问支持
