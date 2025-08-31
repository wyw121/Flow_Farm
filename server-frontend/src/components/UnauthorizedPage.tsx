import { Button } from 'antd'
import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuthGuard } from '../hooks/useAuthGuard'

const UnauthorizedPage: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, isAuthenticated, getDefaultRoute } = useAuthGuard()

  const handleGoHome = () => {
    const defaultRoute = getDefaultRoute()
    navigate(defaultRoute)
  }

  const handleGoBack = () => {
    navigate(-1)
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      padding: '20px'
    }}>
      <div style={{
        textAlign: 'center',
        maxWidth: '600px'
      }}>
        <h1 style={{ fontSize: '48px', marginBottom: '20px', color: '#ff4d4f' }}>
          403
        </h1>
        <h2 style={{ marginBottom: '20px' }}>
          您没有权限访问此页面
        </h2>
        <p style={{ marginBottom: '30px', color: '#666' }}>
          抱歉，您当前的角色权限不足以访问此资源。请联系管理员或返回到您有权限的页面。
        </p>

        <div style={{ marginBottom: '30px' }}>
          <Button type="primary" onClick={handleGoHome} style={{ marginRight: '10px' }}>
            返回首页
          </Button>
          <Button onClick={handleGoBack}>
            返回上一页
          </Button>
        </div>

        <details style={{
          marginTop: '30px',
          padding: '20px',
          background: '#f5f5f5',
          borderRadius: '8px',
          textAlign: 'left'
        }}>
          <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
            调试信息（开发模式）
          </summary>
          <div style={{ marginTop: '15px', fontSize: '12px', fontFamily: 'monospace' }}>
            <p><strong>当前路径:</strong> {location.pathname}</p>
            <p><strong>用户角色:</strong> {user?.role || '未知'}</p>
            <p><strong>认证状态:</strong> {isAuthenticated ? '已认证' : '未认证'}</p>
            <p><strong>用户ID:</strong> {user?.id || '无'}</p>
            <p><strong>用户名:</strong> {user?.username || '无'}</p>
            <p><strong>时间戳:</strong> {new Date().toISOString()}</p>
            <details style={{ marginTop: '10px' }}>
              <summary>完整用户信息</summary>
              <pre style={{ fontSize: '10px', marginTop: '5px', overflow: 'auto' }}>
                {JSON.stringify(user, null, 2)}
              </pre>
            </details>
          </div>
        </details>
      </div>
    </div>
  )
}

export default UnauthorizedPage
