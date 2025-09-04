import type { RouteRecordRaw } from 'vue-router'
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

// 页面组件
const Dashboard = () => import('../views/Dashboard.vue')
const DeviceManagement = () => import('../views/DeviceManagement.vue')
const TaskCenter = () => import('../views/TaskCenter.vue')
const Statistics = () => import('../views/Statistics.vue')
const Settings = () => import('../views/Settings.vue')
const Login = () => import('../views/Login.vue')
const XiaohongshuAutomation = () => import('../views/XiaohongshuAutomation.vue')

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/devices',
    name: 'DeviceManagement',
    component: DeviceManagement,
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks',
    name: 'TaskCenter',
    component: TaskCenter,
    meta: { requiresAuth: true }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: Statistics,
    meta: { requiresAuth: true }
  },
  {
    path: '/xiaohongshu',
    name: 'XiaohongshuAutomation',
    component: XiaohongshuAutomation,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.path === '/login' && userStore.isLoggedIn) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
