import {
    CheckCircleOutlined,
    DeleteOutlined,
    EditOutlined,
    PlusOutlined,
    StopOutlined,
    UserAddOutlined,
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
} from 'antd'
import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { userService } from '../../services/userService'
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

  useEffect(() => {
    loadEmployees()
  }, [])

  const loadEmployees = async () => {
    try {
      setLoading(true)
      const response = await userService.getUsers(1, 100, 'employee')
      // 只显示当前用户管理员下的员工
      const myEmployees = response.items.filter(emp => emp.parent_id === currentUser?.id)
      setEmployees(myEmployees)
    } catch (error: any) {
      message.error('加载员工列表失败：' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    const maxEmployees = currentUser?.max_employees || 10
    if (employees.length >= maxEmployees) {
      message.warning(`您最多只能添加 ${maxEmployees} 名员工`)
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
      message.success('删除成功')
      loadEmployees()
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
        // 创建员工
        const createData: UserCreate = {
          username: values.username,
          password: values.password,
          email: values.email,
          full_name: values.full_name,
          phone: values.phone,
          role: 'employee',
        }
        await userService.createUser(createData)
        message.success('创建成功')
      }
      setModalVisible(false)
      loadEmployees()
    } catch (error: any) {
      message.error(editingEmployee ? '更新失败：' : '创建失败：' + error.message)
    }
  }

  const columns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '姓名',
      dataIndex: 'full_name',
      key: 'full_name',
      render: (name: string) => name || '-',
    },
    {
      title: '手机号',
      dataIndex: 'phone',
      key: 'phone',
      render: (phone: string) => phone || '-',
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      render: (email: string) => email || '-',
    },
    {
      title: '总工作量',
      dataIndex: 'total_work_records',
      key: 'total_work_records',
      render: (count: number) => (
        <Statistic
          value={count}
          suffix="次"
          valueStyle={{ fontSize: '14px' }}
        />
      ),
    },
    {
      title: '今日工作量',
      dataIndex: 'today_work_records',
      key: 'today_work_records',
      render: (count: number) => (
        <Statistic
          value={count}
          suffix="次"
          valueStyle={{ fontSize: '14px', color: '#52c41a' }}
        />
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? '活跃' : '已停用'}
        </Tag>
      ),
    },
    {
      title: '注册时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
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
          >
            编辑
          </Button>
          <Button
            type="link"
            icon={record.is_active ? <StopOutlined /> : <CheckCircleOutlined />}
            onClick={() => handleToggleStatus(record.id)}
          >
            {record.is_active ? '停用' : '启用'}
          </Button>
          <Popconfirm
            title="确定要删除此员工吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
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
            <p>管理您公司的员工账户</p>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreate}
              disabled={currentEmployees >= maxEmployees}
            >
              添加员工
            </Button>
          </Col>
        </Row>
      </div>

      {/* 员工配额使用情况 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '2rem' }}>
        <Col xs={24} lg={8}>
          <Card>
            <Statistic
              title="员工配额使用"
              value={currentEmployees}
              suffix={`/ ${maxEmployees}`}
              prefix={<UserAddOutlined />}
              valueStyle={{ color: usagePercentage >= 90 ? '#ff4d4f' : '#1890ff' }}
            />
            <Progress
              percent={usagePercentage}
              strokeColor={usagePercentage >= 90 ? '#ff4d4f' : '#1890ff'}
              style={{ marginTop: '1rem' }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card>
            <Statistic
              title="活跃员工"
              value={employees.filter(emp => emp.is_active).length}
              suffix="人"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card>
            <Statistic
              title="今日总工作量"
              value={employees.reduce((sum, emp) => sum + emp.today_work_records, 0)}
              suffix="次"
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <Table
          columns={columns}
          dataSource={employees}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 名员工`,
          }}
        />
      </Card>

      <Modal
        title={editingEmployee ? '编辑员工' : '添加员工'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={600}
      >
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
        </Form>
      </Modal>
    </div>
  )
}

export default EmployeeManagement
