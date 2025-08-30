import { DollarOutlined, RiseOutlined, TeamOutlined, UserOutlined } from '@ant-design/icons'
import { Alert, Card, Col, Row, Spin, Statistic, Typography } from 'antd'
import React, { useEffect, useState } from 'react'
import { userService } from '../../services/userService'
import { CompanyStatistics as CompanyStatsType } from '../../types'

const { Title } = Typography

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<{
    totalCompanies: number
    totalEmployees: number
    totalFollows: number
    totalRevenue: number
    companyStats: CompanyStatsType[]
  }>({
    totalCompanies: 0,
    totalEmployees: 0,
    totalFollows: 0,
    totalRevenue: 0,
    companyStats: [],
  })

  useEffect(() => {
    loadStatistics()
  }, [])

  const loadStatistics = async () => {
    try {
      setLoading(true)
      setError(null)

      const companyStats = await userService.getCompanyStatistics()

      const totalStats = companyStats.reduce(
        (acc, company) => ({
          totalCompanies: acc.totalCompanies + 1,
          totalEmployees: acc.totalEmployees + company.total_employees,
          totalFollows: acc.totalFollows + company.total_follows,
          totalRevenue: acc.totalRevenue + company.total_billing_amount,
        }),
        { totalCompanies: 0, totalEmployees: 0, totalFollows: 0, totalRevenue: 0 }
      )

      setStats({
        ...totalStats,
        companyStats,
      })
    } catch (err: any) {
      setError(err.message || '加载统计数据失败')
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
        <Title level={2}>系统管理员控制台</Title>
        <p>欢迎使用 Flow Farm 管理系统</p>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="活跃公司数"
              value={stats.totalCompanies}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总员工数"
              value={stats.totalEmployees}
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
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总收入 (¥)"
              value={stats.totalRevenue}
              precision={2}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: '2rem' }}>
        <Col span={24}>
          <Card
            title="最近活动概览"
            extra={<a href="/system-admin/companies">查看详情</a>}
          >
            <Row gutter={[16, 16]}>
              {stats.companyStats.slice(0, 3).map((company) => (
                <Col xs={24} md={8} key={company.user_admin_id}>
                  <Card size="small">
                    <div style={{ textAlign: 'center' }}>
                      <Title level={4}>{company.company_name}</Title>
                      <p>管理员：{company.user_admin_name}</p>
                      <Row gutter={16}>
                        <Col span={12}>
                          <Statistic
                            title="员工"
                            value={company.total_employees}
                            suffix="人"
                          />
                        </Col>
                        <Col span={12}>
                          <Statistic
                            title="今日关注"
                            value={company.today_follows}
                            suffix="次"
                          />
                        </Col>
                      </Row>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
            {stats.companyStats.length === 0 && (
              <div style={{ textAlign: 'center', padding: '2rem', color: '#999' }}>
                暂无公司数据
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
