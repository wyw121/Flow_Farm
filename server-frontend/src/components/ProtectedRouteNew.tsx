/**
 * 新的受保护路由组件
 * 支持多角色授权，减少控制台日志
 */

import React from 'react'
import { useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'
import { UserRole } from '../services/auth'
import { selectIsAuthenticated, selectIsLoading, selectUser } from '../store/authSliceNew'

interface ProtectedRouteProps {
  children: React.ReactNode
  allowedRoles: UserRole[]
  redirectTo?: string
}

const ProtectedRouteNew: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles,
  redirectTo = '/unauthorized'
}) => {
  const isAuthenticated = useSelector(selectIsAuthenticated)
  const isLoading = useSelector(selectIsLoading)
  const user = useSelector(selectUser)

  // 正在加载中
  if (isLoading) {
    return (
      <div className="route-loading">
        <div className="loading-spinner"></div>
        <p>验证权限中...</p>
      </div>
    )
  }

  // 未认证
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />
  }

  // 检查用户角色权限
  const hasPermission = allowedRoles.includes(user.role)

  if (!hasPermission) {
    // 记录权限检查失败（仅在开发环境）
    if (import.meta.env.DEV) {
      console.warn('权限检查失败:', {
        userRole: user.role,
        allowedRoles,
        userName: user.username
      })
    }

    return <Navigate to={redirectTo} replace />
  }

  // 有权限，渲染子组件
  return <>{children}</>
}

export default ProtectedRouteNew
