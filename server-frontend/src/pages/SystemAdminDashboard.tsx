import {
    DashboardOutlined,
    DownOutlined,
    LogoutOutlined,
    SettingOutlined,
    TeamOutlined,
    UserOutlined,
} from '@ant-design/icons'
import { Avatar, Button, Dropdown, Layout, Menu, Space } from 'antd'
import React, { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { AppDispatch, RootState } from '../store'
import { logout } from '../store/authSlice'

// 页面组件导入（稍后创建）
import CompanyStatistics from './SystemAdmin/CompanyStatistics'
import SystemDashboard from './SystemAdmin/Dashboard'
import PricingSettings from './SystemAdmin/PricingSettings'
import UserManagement from './SystemAdmin/UserManagement'

const { Header, Sider, Content } = Layout

const SystemAdminDashboard: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const dispatch = useDispatch<AppDispatch>()
  const { user } = useSelector((state: RootState) => state.auth)

  const menuItems = [
    {
      key: '/system-admin',
      icon: <DashboardOutlined />,
      label: '控制台',
    },
    {
      key: '/system-admin/users',
      icon: <TeamOutlined />,
      label: '用户管理员管理',
    },
    {
      key: '/system-admin/companies',
      icon: <UserOutlined />,
      label: '公司统计',
    },
    {
      key: '/system-admin/pricing',
      icon: <SettingOutlined />,
      label: '收费设置',
    },
  ]

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  const handleLogout = () => {
    dispatch(logout())
  }

  const userDropdownMenu = {
    items: [
      {
        key: 'profile',
        icon: <UserOutlined />,
        label: '个人信息',
      },
      {
        type: 'divider' as const,
      },
      {
        key: 'logout',
        icon: <LogoutOutlined />,
        label: '退出登录',
        onClick: handleLogout,
      },
    ],
  }

  const currentPath = location.pathname

  return (
    <Layout className="dashboard-layout">
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="dark"
      >
        <div className="dashboard-logo">
          {collapsed ? 'FF' : 'Flow Farm'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[currentPath]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>

      <Layout>
        <Header className="dashboard-header">
          <div />
          <Dropdown menu={userDropdownMenu} placement="bottomRight">
            <Button type="text" style={{ color: 'white' }}>
              <Space>
                <Avatar icon={<UserOutlined />} />
                <span>{user?.full_name || user?.username}</span>
                <span style={{ fontSize: '12px', opacity: 0.8 }}>
                  (系统管理员)
                </span>
                <DownOutlined />
              </Space>
            </Button>
          </Dropdown>
        </Header>

        <Content className="dashboard-content">
          <Routes>
            <Route path="/" element={<SystemDashboard />} />
            <Route path="/users" element={<UserManagement />} />
            <Route path="/companies" element={<CompanyStatistics />} />
            <Route path="/pricing" element={<PricingSettings />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}

export default SystemAdminDashboard
