---
applyTo: "server-frontend/**/*.{vue,ts,js}"
---

# 服务器前端开发指令

## 适用范围
本指令适用于 `server-frontend/` 目录下的所有 Vue.js、TypeScript 和 JavaScript 文件，专门用于构建管理员 Web 界面。

## 技术要求

### 框架和库
- 使用 Vue.js 3 + Composition API
- 使用 TypeScript 进行类型安全
- 使用 Vite 作为构建工具
- 使用 Pinia 进行状态管理
- 使用 Vue Router 进行路由管理
- 使用 Element Plus 作为 UI 组件库

### 三角色界面系统
1. **系统管理员界面**
   - 用户管理模块（增删改查用户管理员）
   - 全系统数据统计仪表板
   - 计费规则配置界面
   - 系统监控和日志查看

2. **用户管理员界面**
   - 员工管理模块（最多10个员工）
   - 本公司数据统计
   - 计费和结算界面
   - 工作量调整工具

### 界面设计规范
- 使用响应式设计，支持桌面和平板
- 遵循 Material Design 设计原则
- 使用统一的颜色主题和字体
- 提供明暗两种主题模式
- 确保良好的用户体验

### 状态管理
- 使用 Pinia stores 管理全局状态
- 实现用户认证状态管理
- 缓存 API 响应数据
- 处理异步操作状态

### API 集成
- 使用 axios 进行 HTTP 请求
- 实现请求拦截器处理认证
- 统一错误处理和提示
- 实现自动重试机制

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
