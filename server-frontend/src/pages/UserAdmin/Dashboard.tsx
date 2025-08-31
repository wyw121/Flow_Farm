import { DollarOutlined, RiseOutlined, TeamOutlined, UserOutlined } from '@ant-design/icons'
import { Alert, Card, Col, Row, Spin, Statistic, Typography } from 'antd'
import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { userService } from '../../services/userService'
import { RootState } from '../../store'

const { Title } = Typography

const Dashboard: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState({
    totalEmployees: 0,
    totalFollows: 0,
    todayFollows: 0,
    totalBilling: 0,
    unpaidAmount: 0,
  })

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // 获取仪表板数据 - 使用统一的API
      const dashboardResponse = await fetch('/api/v1/reports/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      })

      if (!dashboardResponse.ok) {
        throw new Error(`HTTP ${dashboardResponse.status}: ${dashboardResponse.statusText}`)
      }

      const dashboardData = await dashboardResponse.json()

      // 从仪表板数据中提取统计信息
      const workStats = dashboardData.work_stats || {}
      const companyStats = dashboardData.company_stats || {}

      // 获取员工列表
      const employeesResponse = await userService.getUsers(1, 100, 'employee')
      const totalEmployees = employeesResponse.items.length

      setStats({
        totalEmployees,
        totalFollows: workStats.total_follows || 0,
        todayFollows: workStats.today_follows || 0,
        totalBilling: companyStats.total_billing || 0,
        unpaidAmount: companyStats.unpaid_amount || 0,
      })
    } catch (err: any) {
      setError(err.message || '加载数据失败')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <Spin size="large" />
        <p style={{ marginTop: '1rem' }}>加载中...</p>
      </div>
    )
  }

  if (error) {
    return (
      <Alert
        message="加载失败"
        description={error}
        type="error"
        showIcon
        style={{ margin: '2rem' }}
      />
    )
  }

  return (
    <div>
      <div className="page-header">
        <Title level={2}>用户管理员控制台</Title>
        <p>欢迎回来，{user?.full_name || user?.username}！</p>
        {user?.company && (
          <p style={{ color: '#666', fontSize: '14px' }}>
            公司：{user.company}
          </p>
        )}
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="员工数量"
              value={stats.totalEmployees}
              suffix={`/ ${user?.max_employees || 10}`}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总关注数"
              value={stats.totalFollows}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="今日关注"
              value={stats.todayFollows}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="累计费用 (¥)"
              value={stats.totalBilling}
              precision={2}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: '2rem' }}>
        <Col xs={24} lg={12}>
          <Card title="员工管理">
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <UserOutlined style={{ fontSize: '48px', color: '#1890ff', marginBottom: '1rem' }} />
              <div style={{ fontSize: '16px', marginBottom: '1rem' }}>
                当前员工：{stats.totalEmployees} 人
              </div>
              <div style={{ color: '#666' }}>
                可添加员工：{(user?.max_employees || 10) - stats.totalEmployees} 人
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="费用概览">
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <DollarOutlined style={{ fontSize: '48px', color: '#fa8c16', marginBottom: '1rem' }} />
              <div style={{ fontSize: '16px', marginBottom: '0.5rem' }}>
                总费用：¥{stats.totalBilling.toFixed(2)}
              </div>
              <div style={{ color: stats.unpaidAmount > 0 ? '#ff4d4f' : '#52c41a' }}>
                {stats.unpaidAmount > 0
                  ? `待付款：¥${stats.unpaidAmount.toFixed(2)}`
                  : '所有费用已结清'
                }
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {stats.totalEmployees === 0 && (
        <Row style={{ marginTop: '2rem' }}>
          <Col span={24}>
            <Alert
              message="开始使用"
              description="您还没有添加任何员工，请前往员工管理页面添加员工账户。"
              type="info"
              showIcon
              action={
                <a href="/user-admin/employees">立即添加</a>
              }
            />
          </Col>
        </Row>
      )}
    </div>
  )
}

export default Dashboard
