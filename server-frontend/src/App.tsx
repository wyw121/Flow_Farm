import { App as AntApp } from 'antd'
import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Navigate, Route, Routes } from 'react-router-dom'
import './App.css'
import TestPage from './components/TestPage'
import UnauthorizedPage from './components/UnauthorizedPage'
import Login from './pages/Login'
import SystemAdminDashboard from './pages/SystemAdminDashboard'
import UserAdminDashboard from './pages/UserAdminDashboard'
import { RootState } from './store'
import { clearAuthState, getCurrentUser } from './store/authSlice'

const App: React.FC = () => {
  const dispatch = useDispatch()
  const { isAuthenticated, user, loading } = useSelector((state: RootState) => state.auth)

  // 应用启动时验证token有效性
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      dispatch(getCurrentUser() as any).catch(() => {
        dispatch(clearAuthState() as any)
      })
    } else {
      dispatch(clearAuthState() as any)
    }
  }, [dispatch])

  // 全局加载状态
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

  // 未认证时显示登录页面
  if (!isAuthenticated) {
    return (
      <AntApp>
        <Routes>
          {/* 重定向所有路径到登录页 */}
          <Route path="/login" element={<Login />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AntApp>
    )
  }

  // 已认证但用户信息为空的异常情况
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
        <div>用户信息加载异常</div>
        <button
          onClick={() => window.location.reload()}
          style={{ marginTop: '20px', padding: '10px 20px' }}
        >
          刷新页面
        </button>
      </div>
    )
  }

  // 已认证时的主要路由
  return (
    <AntApp>
      <Routes>
        {/* 登录页面重定向 - 已登录用户访问登录页时直接重定向到相应仪表板 */}
        <Route
          path="/login"
          element={
            user?.role === 'system_admin' ? (
              <Navigate to="/system-admin/dashboard" replace />
            ) : user?.role === 'user_admin' ? (
              <Navigate to="/user-admin/dashboard" replace />
            ) : user?.role === 'employee' ? (
              <Navigate to="/employee/dashboard" replace />
            ) : (
              <Navigate to="/unauthorized" replace />
            )
          }
        />

        {/* 系统管理员路由 */}
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

        {/* 用户管理员路由 */}
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

        {/* 测试页面路由 */}
        <Route path="/test" element={<TestPage />} />

        {/* 调试路由 */}
        <Route
          path="/debug"
          element={
            <div style={{ padding: '20px' }}>
              <h2>调试信息</h2>
              <div>用户角色: "{user?.role}"</div>
              <div>角色类型: {typeof user?.role}</div>
              <div>角色长度: {user?.role?.length}</div>
              <div>是系统管理员: {user?.role === 'system_admin' ? 'true' : 'false'}</div>
              <div>是用户管理员: {user?.role === 'user_admin' ? 'true' : 'false'}</div>
              <div>是员工: {user?.role === 'employee' ? 'true' : 'false'}</div>
              <pre>{JSON.stringify(user, null, 2)}</pre>
            </div>
          }
        />

        {/* 根路径智能重定向 */}
        <Route
          path="/"
          element={
            user?.role === 'system_admin' ? (
              <Navigate to="/system-admin/dashboard" replace />
            ) : user?.role === 'user_admin' ? (
              <Navigate to="/user-admin/dashboard" replace />
            ) : user?.role === 'employee' ? (
              <Navigate to="/employee/dashboard" replace />
            ) : (
              <Navigate to="/unauthorized" replace />
            )
          }
        />

        {/* 无权限页面 */}
        <Route path="/unauthorized" element={<UnauthorizedPage />} />

        {/* 404页面 - 重定向到根路径 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AntApp>
  )
}

export default App
