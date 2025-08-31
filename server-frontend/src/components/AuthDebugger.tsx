import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'
import { RootState } from '../store'
import { clearAuthState } from '../store/authSlice'

interface AuthDebuggerProps {
  show?: boolean
}

const AuthDebugger: React.FC<AuthDebuggerProps> = ({ show = false }) => {
  const dispatch = useDispatch()
  const { isAuthenticated, user, loading, error } = useSelector((state: RootState) => state.auth)
  const location = useLocation()

  const handleClearState = () => {
    console.log('手动清理认证状态')
    localStorage.removeItem('token')
    dispatch(clearAuthState())
  }

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
        <button
          onClick={handleClearState}
          style={{
            marginTop: '10px',
            padding: '5px 10px',
            backgroundColor: '#ff4d4f',
            color: 'white',
            border: 'none',
            borderRadius: '3px',
            cursor: 'pointer',
            fontSize: '10px'
          }}
        >
          清理认证状态
        </button>
      </div>
    </div>
  )
}

export default AuthDebugger
