import React from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'
import { RootState } from '../store'

interface AuthDebuggerProps {
  show?: boolean
}

const AuthDebugger: React.FC<AuthDebuggerProps> = ({ show = false }) => {
  const { isAuthenticated, user, loading, error } = useSelector((state: RootState) => state.auth)
  const location = useLocation()

  if (!show) return null

  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      right: '10px',
      background: 'rgba(0,0,0,0.8)',
      color: 'white',
      padding: '10px',
      borderRadius: '5px',
      zIndex: 9999,
      fontSize: '12px',
      maxWidth: '300px',
      wordBreak: 'break-all'
    }}>
      <h4 style={{ margin: '0 0 10px 0', color: '#fff' }}>认证调试信息</h4>
      <div>
        <p><strong>路径:</strong> {location.pathname}</p>
        <p><strong>加载中:</strong> {loading ? '是' : '否'}</p>
        <p><strong>已认证:</strong> {isAuthenticated ? '是' : '否'}</p>
        <p><strong>用户角色:</strong> {user?.role || '无'}</p>
        <p><strong>用户ID:</strong> {user?.id || '无'}</p>
        <p><strong>用户名:</strong> {user?.username || '无'}</p>
        <p><strong>错误:</strong> {error || '无'}</p>
        <p><strong>Token:</strong> {localStorage.getItem('token') ? '存在' : '不存在'}</p>
        <details style={{ marginTop: '10px' }}>
          <summary style={{ cursor: 'pointer' }}>完整用户对象</summary>
          <pre style={{ fontSize: '10px', marginTop: '5px' }}>
            {JSON.stringify(user, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  )
}

export default AuthDebugger
