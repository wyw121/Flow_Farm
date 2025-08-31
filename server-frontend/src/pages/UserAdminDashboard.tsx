import {
    BankOutlined,
    DashboardOutlined,
    DownOutlined,
    LogoutOutlined,
    TeamOutlined,
    UserOutlined,
} from '@ant-design/icons'
import { Avatar, Button, Dropdown, Layout, Menu, Space } from 'antd'
import React, { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { AppDispatch, RootState } from '../store'
import { logout } from '../store/authSlice'

// 页面组件导入
import BillingManagement from './UserAdmin/BillingManagement'
import Dashboard from './UserAdmin/Dashboard'
import EmployeeManagement from './UserAdmin/EmployeeManagement'

const { Header, Sider, Content } = Layout

const UserAdminLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const dispatch = useDispatch<AppDispatch>()
  const { user } = useSelector((state: RootState) => state.auth)

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: '控制台',
    },
    {
      key: 'employees',
      icon: <TeamOutlined />,
      label: '员工管理',
    },
    {
      key: 'billing',
      icon: <BankOutlined />,
      label: '费用结算',
    },
  ]

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(`/user-admin/${key}`)
  }

  const handleLogout = () => {
    dispatch(logout()).then(() => {
      // 登出成功后重定向到登录页面
      navigate('/login', { replace: true })
    })
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
  // 从完整路径中提取相对路径
  const relativePath = currentPath.replace('/user-admin/', '')
  const selectedKey = relativePath === 'dashboard' || relativePath === '' ? 'dashboard' : relativePath

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
          selectedKeys={[selectedKey]}
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
                  ({user?.company})
                </span>
                <DownOutlined />
              </Space>
            </Button>
          </Dropdown>
        </Header>

        <Content className="dashboard-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/employees" element={<EmployeeManagement />} />
            <Route path="/billing" element={<BillingManagement />} />
            {/* 默认重定向到dashboard */}
            <Route path="*" element={<Dashboard />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}

export default UserAdminLayout
