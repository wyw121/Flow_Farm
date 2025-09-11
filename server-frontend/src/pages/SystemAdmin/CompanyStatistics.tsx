import {
    DownloadOutlined,
    EyeOutlined,
    ReloadOutlined,
} from '@ant-design/icons'
import {
    Alert,
    Button,
    Card,
    Col,
    DatePicker,
    message,
    Row,
    Space,
    Spin,
    Statistic,
    Table,
    Typography,
} from 'antd'
import dayjs from 'dayjs'
import React, { useEffect, useState } from 'react'
import { userService } from '../../services/userService'
import { workRecordService } from '../../services/workRecordService'
import { CompanyStatistics as CompanyStatsType } from '../../types'

const { Title } = Typography
const { RangePicker } = DatePicker

const CompanyStatistics: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [companies, setCompanies] = useState<CompanyStatsType[]>([])
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().subtract(7, 'day'),
    dayjs(),
  ])
  const [exportLoading, setExportLoading] = useState(false)

  useEffect(() => {
    loadCompanies()
  }, [])

  const loadCompanies = async () => {
    try {
      setLoading(true)
      const stats = await userService.getCompanyStatistics()
      setCompanies(stats)
    } catch (error: any) {
      message.error('加载公司统计失败：' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleExportWorkRecords = async (userAdminId: number) => {
    try {
      setExportLoading(true)
      const [startDate, endDate] = dateRange

      // 获取该公司下所有员工的工作记录
      const blob = await workRecordService.exportWorkRecords(
        undefined, // employeeId - 不指定则导出所有员工
        undefined, // platform
        'follow', // actionType - 只导出关注记录
        startDate.format('YYYY-MM-DD'),
        endDate.format('YYYY-MM-DD')
      )

      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url

      const company = companies.find(c => c.user_admin_id === userAdminId)
      const fileName = `${company?.company_name || 'unknown'}_关注记录_${startDate.format('YYYY-MM-DD')}_${endDate.format('YYYY-MM-DD')}.xlsx`

      link.download = fileName
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      message.success('导出成功')
    } catch (error: any) {
      message.error('导出失败：' + error.message)
    } finally {
      setExportLoading(false)
    }
  }

  const columns = [
    {
      title: '公司名称',
      dataIndex: 'company_name',
      key: 'company_name',
      render: (name: string, record: CompanyStatsType) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{name}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            管理员：{record.user_admin_name}
          </div>
        </div>
      ),
    },
    {
      title: '员工数量',
      dataIndex: 'total_employees',
      key: 'total_employees',
      render: (count: number) => (
        <Statistic
          value={count}
          suffix="人"
          valueStyle={{ fontSize: '14px' }}
        />
      ),
    },
    {
      title: '总关注数',
      dataIndex: 'total_follows',
      key: 'total_follows',
      render: (count: number) => (
        <Statistic
          value={count}
          suffix="次"
          valueStyle={{ fontSize: '14px', color: '#1890ff' }}
        />
      ),
    },
    {
      title: '今日关注',
      dataIndex: 'today_follows',
      key: 'today_follows',
      render: (count: number) => (
        <Statistic
          value={count}
          suffix="次"
          valueStyle={{ fontSize: '14px', color: '#52c41a' }}
        />
      ),
    },
    {
      title: '总费用 (¥)',
      dataIndex: 'total_billing_amount',
      key: 'total_billing_amount',
      render: (amount: number) => (
        <Statistic
          value={amount}
          precision={2}
          prefix="¥"
          valueStyle={{ fontSize: '14px' }}
        />
      ),
    },
    {
      title: '待付款 (¥)',
      dataIndex: 'unpaid_amount',
      key: 'unpaid_amount',
      render: (amount: number) => (
        <Statistic
          value={amount}
          precision={2}
          prefix="¥"
          valueStyle={{
            fontSize: '14px',
            color: amount > 0 ? '#ff4d4f' : '#52c41a'
          }}
        />
      ),
    },
    {
      title: '余额 (¥)',
      dataIndex: 'balance',
      key: 'balance',
      render: (balance: number) => (
        <Statistic
          value={balance}
          precision={2}
          prefix="¥"
          valueStyle={{
            fontSize: '14px',
            color: balance > 0 ? '#52c41a' : '#ff4d4f'
          }}
        />
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (record: CompanyStatsType) => (
        <Space size="middle">
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => {/* TODO: 查看详情功能 */}}
          >
            查看详情
          </Button>
          <Button
            type="link"
            icon={<DownloadOutlined />}
            loading={exportLoading}
            onClick={() => handleExportWorkRecords(record.user_admin_id)}
          >
            导出Excel
          </Button>
        </Space>
      ),
    },
  ]

  const totalStats = companies.reduce(
    (acc, company) => ({
      totalCompanies: acc.totalCompanies + 1,
      totalEmployees: acc.totalEmployees + company.total_employees,
      totalFollows: acc.totalFollows + company.total_follows,
      todayFollows: acc.todayFollows + company.today_follows,
      totalRevenue: acc.totalRevenue + company.total_billing_amount,
      unpaidAmount: acc.unpaidAmount + company.unpaid_amount,
      totalBalance: acc.totalBalance + company.balance,
    }),
    {
      totalCompanies: 0,
      totalEmployees: 0,
      totalFollows: 0,
      todayFollows: 0,
      totalRevenue: 0,
      unpaidAmount: 0,
      totalBalance: 0,
    }
  )

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <Spin size="large" />
        <p style={{ marginTop: '1rem' }}>加载中...</p>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={2}>公司统计</Title>
            <p>查看各公司的员工工作信息和关注数据</p>
          </Col>
          <Col>
            <Space>
              <span>导出时间范围：</span>
              <RangePicker
                value={dateRange}
                onChange={(dates) => {
                  if (dates && dates[0] && dates[1]) {
                    setDateRange([dates[0], dates[1]])
                  }
                }}
                format="YYYY-MM-DD"
              />
              <Button
                icon={<ReloadOutlined />}
                onClick={loadCompanies}
                loading={loading}
              >
                刷新
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* 总体统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '2rem' }}>
        <Col xs={24} sm={12} lg={4}>
          <Card>
            <Statistic
              title="活跃公司"
              value={totalStats.totalCompanies}
              suffix="家"
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={4}>
          <Card>
            <Statistic
              title="总员工数"
              value={totalStats.totalEmployees}
              suffix="人"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={4}>
          <Card>
            <Statistic
              title="总关注数"
              value={totalStats.totalFollows}
              suffix="次"
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={4}>
          <Card>
            <Statistic
              title="今日关注"
              value={totalStats.todayFollows}
              suffix="次"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={4}>
          <Card>
            <Statistic
              title="总收入"
              value={totalStats.totalRevenue}
              precision={2}
              prefix="¥"
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={4}>
          <Card>
            <Statistic
              title="待收款"
              value={totalStats.unpaidAmount}
              precision={2}
              prefix="¥"
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={4}>
          <Card>
            <Statistic
              title="总余额"
              value={totalStats.totalBalance}
              precision={2}
              prefix="¥"
              valueStyle={{ color: totalStats.totalBalance > 0 ? '#52c41a' : '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 公司列表 */}
      <Card title="公司详细统计">
        {companies.length === 0 ? (
          <Alert
            message="暂无数据"
            description="当前系统中还没有注册的公司"
            type="info"
            showIcon
            style={{ textAlign: 'center' }}
          />
        ) : (
          <Table
            columns={columns}
            dataSource={companies}
            rowKey="user_admin_id"
            pagination={{
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 家公司`,
            }}
          />
        )}
      </Card>
    </div>
  )
}

export default CompanyStatistics
