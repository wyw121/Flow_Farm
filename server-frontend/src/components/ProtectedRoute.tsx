import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { Navigate, useLocation } from 'react-router-dom'
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
  const location = useLocation()
  const [debugInfo, setDebugInfo] = useState<any>({})

  const checkRole = (userRole: string | undefined, required: UserRole): boolean => {
    if (!userRole || !required) return false
    const cleanUserRole = userRole.trim()
    const cleanRequired = required.trim()
    return cleanUserRole === cleanRequired
  }

  useEffect(() => {
    const debug = {
      timestamp: new Date().toISOString(),
      location: location.pathname,
      isAuthenticated,
      loading,
      user: user ? {
        id: user.id,
        username: user.username,
        role: user.role,
        roleType: typeof user.role,
        roleLength: user.role?.length
      } : null,
      requiredRole,
      roleCheckResult: checkRole(user?.role, requiredRole)
    }
    setDebugInfo(debug)

    console.log(`ProtectedRoute [${location.pathname}]:`, debug)
  }, [isAuthenticated, user, loading, location.pathname, requiredRole])

  // 如果正在加载，显示加载页面
  if (loading) {
    console.log('ProtectedRoute: 显示加载状态')
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
    console.log('ProtectedRoute: 用户未认证，重定向到登录页')
    return <Navigate to="/login" replace />
  }

  // 如果用户为空，但是认证状态为true，这是一个异常情况
  if (!user) {
    console.log('ProtectedRoute: 异常状态 - 已认证但用户为空')
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
    console.log('ProtectedRoute: 权限不足，重定向到无权限页面', {
      userRole: user.role,
      requiredRole,
      roleCheckResult: hasRequiredRole,
      debugInfo
    })
    return <Navigate to={redirectTo} replace />
  }

  console.log('ProtectedRoute: 权限验证通过，渲染内容')
  return <>{children}</>
}

export default ProtectedRoute
