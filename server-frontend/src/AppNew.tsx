/**
 * 重构后的App组件
 * 移除冗余的调试组件和控制台日志，优化路由和状态管理
 */

import { App as AntApp, ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Navigate, Route, Routes } from 'react-router-dom'
import './AppNew.css'

import { AppDispatch } from './store'
import {
    checkAuthStatusAsync,
    selectIsAuthenticated,
    selectIsLoading,
    selectUser
} from './store/authSliceNew'

// 页面组件
import ProtectedRouteNew from './components/ProtectedRouteNew'
import UnauthorizedPage from './components/UnauthorizedPage'
import LoginNew from './pages/LoginNew'
import SystemAdminDashboard from './pages/SystemAdminDashboard'
import UserAdminDashboard from './pages/UserAdminDashboard'
import { UserRole } from './services/auth'

// 路由权限映射
const ROLE_ROUTES = {
  system_admin: '/admin',
  user_admin: '/user-admin',
  employee: '/employee'
} as const

const AppContent: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>()
  const isAuthenticated = useSelector(selectIsAuthenticated)
  const isLoading = useSelector(selectIsLoading)
  const user = useSelector(selectUser)

  // 应用启动时检查认证状态
  useEffect(() => {
    dispatch(checkAuthStatusAsync())
  }, [dispatch])

  // 全局加载状态
  if (isLoading) {
    return (
      <div className="app-loading">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <p>正在验证登录状态...</p>
        </div>
      </div>
    )
  }

  // 未认证状态 - 显示登录页面
  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<LoginNew />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  // 已认证但用户信息异常
  if (!user) {
    return (
      <div className="app-error">
        <div className="error-content">
          <h3>用户信息加载失败</h3>
          <p>请尝试刷新页面或重新登录</p>
          <button
            onClick={() => window.location.reload()}
            className="retry-button"
          >
            刷新页面
          </button>
        </div>
      </div>
    )
  }

  // 获取用户对应的默认路由
  const defaultRoute = ROLE_ROUTES[user.role as keyof typeof ROLE_ROUTES] || '/unauthorized'

  return (
    <Routes>
      {/* 根路径重定向到用户角色对应的页面 */}
      <Route path="/" element={<Navigate to={defaultRoute} replace />} />

      {/* 系统管理员路由 */}
      <Route
        path="/admin/*"
        element={
          <ProtectedRouteNew allowedRoles={['system_admin' as UserRole]}>
            <SystemAdminDashboard />
          </ProtectedRouteNew>
        }
      />

      {/* 用户管理员路由 */}
      <Route
        path="/user-admin/*"
        element={
          <ProtectedRouteNew allowedRoles={['user_admin' as UserRole]}>
            <UserAdminDashboard />
          </ProtectedRouteNew>
        }
      />

      {/* 未授权页面 */}
      <Route path="/unauthorized" element={<UnauthorizedPage />} />

      {/* 登录页面（已认证用户访问会重定向） */}
      <Route path="/login" element={<Navigate to={defaultRoute} replace />} />

      {/* 其他未匹配路由 */}
      <Route path="*" element={<Navigate to={defaultRoute} replace />} />
    </Routes>
  )
}

const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <AntApp>
        <AppContent />
      </AntApp>
    </ConfigProvider>
  )
}

export default App
