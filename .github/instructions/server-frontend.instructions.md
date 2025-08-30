# 服务器前端开发指令

## 适用范围
这些指令适用于 `server-frontend/**/*.{vue,ts,js}` 路径下的所有前端代码文件。

## 技术栈

### 核心框架和库
- **前端框架**: Vue.js 3 + TypeScript + Vite
- **UI组件库**: Ant Design Vue
- **状态管理**: Pinia
- **路由管理**: Vue Router
- **HTTP客户端**: Axios
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
import { ref, onMounted } from 'vue'
import { useSystemStore } from '@/stores/system'

interface StatisticItem {
  key: string
  title: string
  value: number
  suffix?: string
}

const systemStore = useSystemStore()
const statistics = ref<StatisticItem[]>([])

const refreshData = async () => {
  await systemStore.fetchStatistics()
  statistics.value = systemStore.statistics
}

onMounted(() => {
  refreshData()
})
</script>
```

### Pinia Store 示例
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string>('')

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await authApi.login(credentials)
      token.value = response.token
      user.value = response.user
      localStorage.setItem('token', token.value)
    } catch (error) {
      throw new Error('登录失败')
    }
  }

  const logout = () => {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
  }

  const hasPermission = (permission: string): boolean => {
    return user.value?.permissions.includes(permission) || false
  }

  return {
    user,
    token,
    login,
    logout,
    hasPermission
  }
})
```

### 路由守卫示例
```typescript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true, role: 'SYSTEM_ADMIN' },
      children: [
        {
          path: 'users',
          component: UserManagement,
          meta: { permission: 'manage_users' }
        }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.token) {
    next('/login')
    return
  }

  if (to.meta.role && authStore.user?.role !== to.meta.role) {
    next('/403')
    return
  }

  next()
})
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
