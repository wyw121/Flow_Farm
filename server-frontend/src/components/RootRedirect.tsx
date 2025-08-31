import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthGuard } from '../hooks/useAuthGuard'

const RootRedirect: React.FC = () => {
  const { getDefaultRoute, loading, isAuthenticated } = useAuthGuard()

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
        <div style={{ marginBottom: '20px' }}>正在验证登录状态...</div>
        <div style={{ fontSize: '12px', color: '#666' }}>
          检查用户权限和角色...
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  const defaultRoute = getDefaultRoute()

  return <Navigate to={defaultRoute} replace />
}

export default RootRedirect
