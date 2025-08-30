import React from 'react'
import { useSelector } from 'react-redux'
import { Navigate, Route, Routes } from 'react-router-dom'
import './App.css'
import Login from './pages/Login'
import SystemAdminDashboard from './pages/SystemAdminDashboard'
import UserAdminDashboard from './pages/UserAdminDashboard'
import { RootState } from './store'

const App: React.FC = () => {
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth)

  if (!isAuthenticated) {
    return <Login />
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
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
            <Navigate to="/system-admin" replace />
          ) : (
            <Navigate to="/user-admin" replace />
          )
        }
      />
      <Route
        path="/unauthorized"
        element={<div>您没有权限访问此页面</div>}
      />
    </Routes>
  )
}

export default App
