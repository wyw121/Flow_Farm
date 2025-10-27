import {
    CheckCircleOutlined,
    DeleteOutlined,
    EditOutlined,
    PlusOutlined,
    StopOutlined,
    UserAddOutlined,
    SearchOutlined,
    ExclamationCircleOutlined,
    DollarOutlined,
    CalendarOutlined,
    WarningOutlined,
} from '@ant-design/icons'
import {
    Button,
    Card,
    Col,
    Form,
    Input,
    message,
    Modal,
    Popconfirm,
    Progress,
    Row,
    Space,
    Statistic,
    Table,
    Tag,
    Typography,
    Alert,
    Tooltip,
    Badge,
} from 'antd'
import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { userService } from '../../services/userService'
import { companyPricingService } from '../../services/companyPricingService'
import { billingService } from '../../services/billingService'
import { RootState } from '../../store'
import { UserCreate, UserUpdate, UserWithStats } from '../../types'

const { Title } = Typography

const EmployeeManagement: React.FC = () => {
  const { user: currentUser } = useSelector((state: RootState) => state.auth)
  const [employees, setEmployees] = useState<UserWithStats[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingEmployee, setEditingEmployee] = useState<UserWithStats | null>(null)
  const [form] = Form.useForm()
  const [searchText, setSearchText] = useState('')
  const [monthlyFee, setMonthlyFee] = useState<number>(300) // 默认月服务费
  const [currentBalance, setCurrentBalance] = useState<number>(0) // 管理员余额
  const [expiringSoon, setExpiringSoon] = useState<UserWithStats[]>([]) // 即将到期的员工

  useEffect(() => {
    loadEmployees()
    loadMonthlyFee()
    loadCurrentBalance()
  }, [])

  const loadEmployees = async () => {
    try {
      setLoading(true)
      const response = await userService.getUsers(1, 100, 'employee')
      // 只显示当前用户管理员下的员工
      const myEmployees = response.items.filter(emp => emp.parent_id === currentUser?.id)
      setEmployees(myEmployees)
      
      // 检查即将到期的员工（下次扣费日期 < 7天）
      const expiring = myEmployees.filter(emp => {
        const nextBillingDate = getNextBillingDate(emp.created_at)
        const daysUntilExpiry = Math.ceil((nextBillingDate.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
        return daysUntilExpiry <= 7 && daysUntilExpiry >= 0
      })
      setExpiringSoon(expiring)
    } catch (error: any) {
      message.error('加载员工列表失败：' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const loadMonthlyFee = async () => {
    try {
      if (currentUser?.company) {
        const fee = await companyPricingService.getEmployeeMonthlyFee(currentUser.company)
        setMonthlyFee(fee)
      }
    } catch (error: any) {
      // 如果获取失败，使用默认值
      console.warn('获取月费失败，使用默认值:', error.message)
    }
  }

  const loadCurrentBalance = async () => {
    try {
      console.log('🔄 开始加载余额信息...')
      const billingInfo = await billingService.getMyBillingInfo()
      console.log('✅ 余额信息加载成功:', billingInfo)
      setCurrentBalance(billingInfo.balance)
      if (billingInfo.monthly_fee > 0) {
        setMonthlyFee(billingInfo.monthly_fee)
      }
      console.log(`✅ 状态更新: 余额=${billingInfo.balance}, 月费=${billingInfo.monthly_fee}`)
    } catch (error: any) {
      console.error('❌ 获取余额失败:', error)
      console.error('Error details:', error.response?.data || error.message)
      // 使用默认值
      setCurrentBalance(0)
    }
  }

  // 计算下次扣费日期（创建时间 + 31天）
  const getNextBillingDate = (createdAt: string): Date => {
    const created = new Date(createdAt)
    const nextBilling = new Date(created)
    nextBilling.setDate(created.getDate() + 31)
    return nextBilling
  }

  // 格式化日期显示
  const formatDate = (date: Date): string => {
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  }

  // 检查是否即将到期（7天内）
  const isExpiringSoon = (createdAt: string): boolean => {
    const nextBillingDate = getNextBillingDate(createdAt)
    const daysUntilExpiry = Math.ceil((nextBillingDate.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
    return daysUntilExpiry <= 7 && daysUntilExpiry >= 0
  }

  const handleCreate = () => {
    const maxEmployees = currentUser?.max_employees || 10
    if (employees.length >= maxEmployees) {
      message.warning(`您最多只能添加 ${maxEmployees} 名员工`)
      return
    }

    // 检查余额是否足够
    if (currentBalance < monthlyFee) {
      Modal.confirm({
        title: '余额不足',
        icon: <ExclamationCircleOutlined />,
        content: `创建员工需要扣费 ¥${monthlyFee}，但您的当前余额为 ¥${currentBalance}。请先充值后再创建员工。`,
        okText: '去充值',
        cancelText: '取消',
        onOk() {
          // 这里可以跳转到充值页面
          message.info('请联系管理员充值')
        }
      })
      return
    }

    setEditingEmployee(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (employee: UserWithStats) => {
    setEditingEmployee(employee)
    form.setFieldsValue({
      username: employee.username,
      email: employee.email,
      full_name: employee.full_name,
      phone: employee.phone,
    })
    setModalVisible(true)
  }

  const handleDelete = async (employeeId: number) => {
    try {
      await userService.deleteUser(employeeId)
      message.success('删除成功（注意：删除不退费）')
      loadEmployees()
      loadCurrentBalance() // 重新加载余额
    } catch (error: any) {
      message.error('删除失败：' + error.message)
    }
  }

  const handleToggleStatus = async (employeeId: number) => {
    try {
      await userService.toggleUserStatus(employeeId)
      message.success('状态更新成功')
      loadEmployees()
    } catch (error: any) {
      message.error('状态更新失败：' + error.message)
    }
  }

  const handleSubmit = async (values: any) => {
    try {
      if (editingEmployee) {
        // 更新员工
        const updateData: UserUpdate = {
          email: values.email,
          full_name: values.full_name,
          phone: values.phone,
        }
        await userService.updateUser(editingEmployee.id, updateData)
        message.success('更新成功')
      } else {
        // 创建员工 - 先再次检查余额
        if (currentBalance < monthlyFee) {
          message.error('余额不足，无法创建员工')
          return
        }

        const createData: UserCreate = {
          username: values.username,
          password: values.password,
          email: values.email,
          full_name: values.full_name,
          phone: values.phone,
          role: 'employee',
        }
        await userService.createUser(createData)
        message.success(`员工创建成功！已扣费 ¥${monthlyFee}，下次扣费日期为31天后`)
        
        // 不再手动减少余额，因为loadCurrentBalance()会获取最新余额
      }
      setModalVisible(false)
      loadEmployees()
      loadCurrentBalance() // 重新加载余额
    } catch (error: any) {
      message.error(editingEmployee ? '更新失败：' : '创建失败：' + error.message)
    }
  }

  // 过滤员工列表（根据搜索条件）
  const filteredEmployees = employees.filter(emp => 
    emp.username.toLowerCase().includes(searchText.toLowerCase()) ||
    emp.full_name?.toLowerCase().includes(searchText.toLowerCase())
  )

  const columns = [
    {
      title: '账号',
      dataIndex: 'username',
      key: 'username',
      render: (username: string, record: UserWithStats) => (
        <Space>
          <span>{username}</span>
          {isExpiringSoon(record.created_at) && (
            <Tooltip title="即将到期，需要续费">
              <WarningOutlined style={{ color: '#faad14' }} />
            </Tooltip>
          )}
        </Space>
      ),
    },
    {
      title: '姓名',
      dataIndex: 'full_name',
      key: 'full_name',
      render: (name: string) => name || '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => formatDate(new Date(date)),
    },
    {
      title: '下次扣费日期',
      dataIndex: 'created_at',
      key: 'next_billing_date',
      render: (createdAt: string) => {
        const nextBillingDate = getNextBillingDate(createdAt)
        const daysUntilExpiry = Math.ceil((nextBillingDate.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
        const isExpiring = daysUntilExpiry <= 7 && daysUntilExpiry >= 0
        
        return (
          <Space>
            <CalendarOutlined />
            <span style={{ color: isExpiring ? '#faad14' : undefined }}>
              {formatDate(nextBillingDate)}
            </span>
            {isExpiring && (
              <Tag color="warning">
                {daysUntilExpiry}天后到期
              </Tag>
            )}
          </Space>
        )
      },
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? '活跃' : '停用'}
        </Tag>
      ),
    },
    {
      title: '手机号/邮箱',
      key: 'contact',
      render: (record: UserWithStats) => (
        <div>
          <div>{record.phone || '-'}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            {record.email || '-'}
          </div>
        </div>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (record: UserWithStats) => (
        <Space size="middle">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
          >
            编辑
          </Button>
          <Button
            type="link"
            icon={record.is_active ? <StopOutlined /> : <CheckCircleOutlined />}
            onClick={() => handleToggleStatus(record.id)}
            size="small"
          >
            {record.is_active ? '停用' : '启用'}
          </Button>
          <Popconfirm
            title="确定要删除此员工吗？"
            description="删除后不可恢复，且不退费"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              size="small"
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const maxEmployees = currentUser?.max_employees || 10
  const currentEmployees = employees.length
  const usagePercentage = (currentEmployees / maxEmployees) * 100

  return (
    <div>
      <div className="page-header">
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={2}>员工管理</Title>
            <p>管理您公司的员工账户，创建员工时立即扣费</p>
          </Col>
          <Col>
            <Space>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleCreate}
                disabled={currentEmployees >= maxEmployees || currentBalance < monthlyFee}
              >
                创建员工
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* 即将到期提醒 */}
      {expiringSoon.length > 0 && (
        <Alert
          message="续费提醒"
          description={
            <div>
              <p>以下员工即将到期，请及时续费：</p>
              {expiringSoon.map(emp => (
                <Tag key={emp.id} color="warning" style={{ marginBottom: 4 }}>
                  {emp.username} - {formatDate(getNextBillingDate(emp.created_at))}到期
                </Tag>
              ))}
            </div>
          }
          type="warning"
          showIcon
          style={{ marginBottom: '1rem' }}
        />
      )}

      {/* 顶部操作区和统计信息 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '1rem' }}>
        <Col xs={24} lg={6}>
          <Card>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span>当前余额</span>
              <Button 
                type="link" 
                size="small" 
                onClick={loadCurrentBalance}
                style={{ padding: 0 }}
              >
                刷新
              </Button>
            </div>
            <Statistic
              value={currentBalance}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="元"
              valueStyle={{ 
                color: currentBalance < monthlyFee ? '#ff4d4f' : '#52c41a',
                fontSize: '20px'
              }}
            />
            {currentBalance < monthlyFee && (
              <div style={{ marginTop: 8, color: '#ff4d4f', fontSize: '12px' }}>
                余额不足，无法创建新员工
              </div>
            )}
          </Card>
        </Col>
        <Col xs={24} lg={6}>
          <Card>
            <Statistic
              title="员工配额"
              value={currentEmployees}
              suffix={`/ ${maxEmployees}`}
              prefix={<UserAddOutlined />}
              valueStyle={{ color: usagePercentage >= 90 ? '#ff4d4f' : '#1890ff' }}
            />
            <Progress
              percent={usagePercentage}
              strokeColor={usagePercentage >= 90 ? '#ff4d4f' : '#1890ff'}
              style={{ marginTop: '0.5rem' }}
              size="small"
            />
          </Card>
        </Col>
        <Col xs={24} lg={6}>
          <Card>
            <Statistic
              title="月服务费"
              value={monthlyFee}
              precision={2}
              suffix="元/人"
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ marginTop: 8, color: '#666', fontSize: '12px' }}>
              创建员工时扣费
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={6}>
          <Card>
            <Statistic
              title="即将到期"
              value={expiringSoon.length}
              suffix="人"
              valueStyle={{ color: expiringSoon.length > 0 ? '#faad14' : '#52c41a' }}
            />
            <div style={{ marginTop: 8, color: '#666', fontSize: '12px' }}>
              7天内需续费
            </div>
          </Card>
        </Col>
      </Row>

      {/* 操作区 */}
      <Card style={{ marginBottom: '1rem' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Input
              placeholder="按账号或姓名搜索"
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 250 }}
              allowClear
            />
          </Col>
          <Col>
            <Space>
              <Badge count={expiringSoon.length} offset={[10, 0]}>
                <Button icon={<WarningOutlined />}>
                  即将到期
                </Button>
              </Badge>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 员工列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredEmployees}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 名员工`,
            pageSizeOptions: ['10', '20', '50', '100'],
          }}
          rowClassName={(record) => isExpiringSoon(record.created_at) ? 'table-row-warning' : ''}
        />
      </Card>

      <Modal
        title={editingEmployee ? '编辑员工' : '创建员工'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={600}
      >
        {!editingEmployee && (
          <Alert
            message="扣费说明"
            description={`创建员工将立即扣费 ¥${monthlyFee}，下次扣费日期为创建后31天`}
            type="info"
            showIcon
            style={{ marginBottom: '1rem' }}
          />
        )}
        
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          {!editingEmployee && (
            <>
              <Form.Item
                name="username"
                label="用户名"
                rules={[
                  { required: true, message: '请输入用户名' },
                  { min: 3, message: '用户名至少3个字符' },
                  { pattern: /^\w+$/, message: '用户名只能包含字母、数字和下划线' },
                ]}
              >
                <Input placeholder="请输入用户名" />
              </Form.Item>
              <Form.Item
                name="password"
                label="密码"
                rules={[
                  { required: true, message: '请输入密码' },
                  { min: 6, message: '密码至少6个字符' },
                ]}
              >
                <Input.Password placeholder="请输入密码" />
              </Form.Item>
            </>
          )}
          <Form.Item
            name="full_name"
            label="员工姓名"
            rules={[{ required: true, message: '请输入员工姓名' }]}
          >
            <Input placeholder="请输入员工姓名" />
          </Form.Item>
          <Form.Item
            name="phone"
            label="手机号"
            rules={[
              { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' },
            ]}
          >
            <Input placeholder="请输入手机号（可选）" />
          </Form.Item>
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { type: 'email', message: '请输入正确的邮箱地址' },
            ]}
          >
            <Input placeholder="请输入邮箱（可选）" />
          </Form.Item>

          {!editingEmployee && (
            <div style={{ 
              padding: '12px', 
              backgroundColor: '#f6f6f6', 
              borderRadius: '6px',
              border: '1px solid #d9d9d9'
            }}>
              <Row justify="space-between">
                <Col>
                  <span style={{ color: '#666' }}>月服务费：</span>
                </Col>
                <Col>
                  <span style={{ fontWeight: 'bold', color: '#1890ff' }}>
                    ¥{monthlyFee} 元
                  </span>
                </Col>
              </Row>
              <Row justify="space-between" style={{ marginTop: 8 }}>
                <Col>
                  <span style={{ color: '#666' }}>当前余额：</span>
                </Col>
                <Col>
                  <span style={{ 
                    fontWeight: 'bold', 
                    color: currentBalance >= monthlyFee ? '#52c41a' : '#ff4d4f' 
                  }}>
                    ¥{currentBalance} 元
                  </span>
                </Col>
              </Row>
            </div>
          )}
        </Form>
      </Modal>

      <style>{`
        .table-row-warning {
          background-color: #fffbe6 !important;
        }
        .table-row-warning:hover {
          background-color: #fff7e6 !important;
        }
      `}</style>
    </div>
  )
}

export default EmployeeManagement
