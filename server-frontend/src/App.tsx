import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Navigate, Route, Routes } from 'react-router-dom'
import './App.css'
import Login from './pages/Login'
import SystemAdminDashboard from './pages/SystemAdminDashboard'
import UserAdminDashboard from './pages/UserAdminDashboard'
import { RootState } from './store'
import { getCurrentUser } from './store/authSlice'

const App: React.FC = () => {
  const dispatch = useDispatch()
  const { isAuthenticated, user, loading } = useSelector((state: RootState) => state.auth)

  // 应用启动时验证token有效性
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token && !user) {
      // 如果有token但没有用户信息，验证token有效性
      console.log('验证现有token...')
      dispatch(getCurrentUser() as any)
    }
  }, [dispatch, user])

  // 调试信息
  useEffect(() => {
    console.log('认证状态:', { isAuthenticated, user: user?.role, loading })
  }, [isAuthenticated, user, loading])

  // 显示加载状态
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '16px'
      }}>
        正在验证登录状态...
      </div>
    )
  }

  // 如果未认证，显示登录页面
  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="*" element={<Login />} />
      </Routes>
    )
  }

  return (
    <Routes>
      <Route path="/login" element={<Navigate to="/" replace />} />
      <Route
        path="/system-admin/*"
        element={
          user?.role === 'system_admin' ? (
            <SystemAdminDashboard />
          ) : (
            <Navigate to="/unauthorized" replace />
          )
        }
      />
      <Route
        path="/user-admin/*"
        element={
          user?.role === 'user_admin' ? (
            <UserAdminDashboard />
          ) : (
            <Navigate to="/unauthorized" replace />
          )
        }
      />
      <Route
        path="/"
        element={
          user?.role === 'system_admin' ? (
            <Navigate to="/system-admin/dashboard" replace />
          ) : user?.role === 'user_admin' ? (
            <Navigate to="/user-admin/dashboard" replace />
          ) : (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100vh',
              fontSize: '18px'
            }}>
              <p>调试信息：</p>
              <p>用户角色: {user?.role || '未知'}</p>
              <p>认证状态: {isAuthenticated ? '已认证' : '未认证'}</p>
              <p>用户信息: {user ? JSON.stringify(user, null, 2) : '无'}</p>
            </div>
          )
        }
      />
      <Route
        path="/unauthorized"
        element={
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',
            fontSize: '18px'
          }}>
            您没有权限访问此页面
          </div>
        }
      />
    </Routes>
  )
}

export default App
