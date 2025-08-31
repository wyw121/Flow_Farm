import React from 'react'
import { useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'
import { RootState } from '../store'

export type UserRole = 'system_admin' | 'user_admin' | 'employee'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole: UserRole
  redirectTo?: string
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  redirectTo = '/unauthorized'
}) => {
  const { isAuthenticated, user, loading } = useSelector((state: RootState) => state.auth)

  const checkRole = (userRole: string | undefined, required: UserRole): boolean => {
    if (!userRole || !required) return false
    const cleanUserRole = userRole.trim()
    const cleanRequired = required.trim()
    return cleanUserRole === cleanRequired
  }

  // 如果正在加载，显示加载页面
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '16px'
      }}>
        <div style={{ marginBottom: '20px' }}>验证权限中...</div>
        <div style={{ fontSize: '12px', color: '#666' }}>
          路径: {location.pathname} | 需要角色: {requiredRole}
        </div>
      </div>
    )
  }

  // 如果用户未认证，重定向到登录页
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // 如果用户为空，但是认证状态为true，这是一个异常情况
  if (!user) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '16px'
      }}>
        <div style={{ marginBottom: '20px' }}>用户信息加载中...</div>
        <div style={{ fontSize: '12px', color: '#666' }}>
          认证状态异常，请刷新页面
        </div>
      </div>
    )
  }

  // 检查用户角色权限
  const hasRequiredRole = checkRole(user.role, requiredRole)

  if (!hasRequiredRole) {
    return <Navigate to={redirectTo} replace />
  }

  return <>{children}</>
}

export default ProtectedRoute
