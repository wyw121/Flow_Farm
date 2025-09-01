import {
    DeleteOutlined,
    EditOutlined,
    EyeOutlined,
    PlusOutlined,
    ReloadOutlined,
    SearchOutlined,
} from '@ant-design/icons'
import {
    Button,
    Card,
    Col,
    Form,
    Input,
    Modal,
    Row,
    Select,
    Space,
    Table,
    Tag,
    Typography,
    message,
} from 'antd'
import React, { useEffect, useState } from 'react'
import { AdminUserUpdateRequest, userService } from '../../services/userService'

const { Title } = Typography
const { Option } = Select

interface UserAdmin {
    id: number
    username: string
    email: string
    phone: string
    company_name: string
    max_employees: number
    current_employees: number
    status: 'active' | 'inactive' | 'suspended'
    created_at: string
    last_login: string
    balance: number
}

const UserManagement: React.FC = () => {
    const [loading, setLoading] = useState(false)
    const [users, setUsers] = useState<UserAdmin[]>([])
    const [searchText, setSearchText] = useState('')
    const [editModalVisible, setEditModalVisible] = useState(false)
    const [viewModalVisible, setViewModalVisible] = useState(false)
    const [currentUser, setCurrentUser] = useState<UserAdmin | null>(null)
    const [form] = Form.useForm()

    // 获取用户列表
    const fetchUsers = async () => {
        try {
            setLoading(true)
            // 获取用户管理员列表
            const response = await userService.getUsers(1, 100, 'user_admin')
            const userAdmins: UserAdmin[] = response.items.map(user => ({
                id: user.id,
                username: user.username,
                email: user.email || '',
                phone: user.phone || '',
                company_name: user.company || '',
                max_employees: user.max_employees,
                current_employees: user.current_employees,
                status: user.is_active ? 'active' : 'inactive',
                created_at: user.created_at,
                last_login: user.last_login || '',
                balance: 0 // 这个需要从billing API获取
            }))
            setUsers(userAdmins)
        } catch (error) {
            console.error('获取用户列表失败:', error)
            message.error('获取用户列表失败')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchUsers()
    }, [])

    // 状态标签颜色
    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active': return 'green'
            case 'inactive': return 'orange'
            case 'suspended': return 'red'
            default: return 'default'
        }
    }

    // 状态文本
    const getStatusText = (status: string) => {
        switch (status) {
            case 'active': return '活跃'
            case 'inactive': return '非活跃'
            case 'suspended': return '已暂停'
            default: return '未知'
        }
    }

    // 编辑用户
    const handleEdit = (user: UserAdmin) => {
        setCurrentUser(user)
        form.setFieldsValue({
            username: user.username,
            email: user.email,
            phone: user.phone,
            company_name: user.company_name,
            max_employees: user.max_employees,
            status: user.status,
            balance: user.balance
        })
        setEditModalVisible(true)
    }

    // 查看用户详情
    const handleView = (user: UserAdmin) => {
        setCurrentUser(user)
        setViewModalVisible(true)
    }

    // 删除用户
    const handleDelete = (user: UserAdmin) => {
        Modal.confirm({
            title: '确认删除',
            content: `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
            okText: '删除',
            okType: 'danger',
            cancelText: '取消',
            onOk: async () => {
                try {
                    await userService.deleteUser(user.id)
                    message.success('删除成功')
                    fetchUsers()
                } catch (error) {
                    console.error('删除失败:', error)
                    message.error('删除失败')
                }
            }
        })
    }

    // 保存编辑
    const handleSaveEdit = async () => {
        try {
            const values = await form.validateFields()

            if (currentUser) {
                // 编辑现有用户
                const updateData: AdminUserUpdateRequest = {
                    username: values.username,
                    email: values.email,
                    phone: values.phone,
                    company: values.company_name,
                    max_employees: values.max_employees,
                    is_active: values.status === 'active',
                    ...(values.password && { password: values.password }) // 只有提供密码时才包含
                }

                await userService.adminUpdateUser(currentUser.id, updateData)
                message.success('用户信息更新成功')
            } else {
                // 创建新用户
                const createData = {
                    username: values.username,
                    email: values.email,
                    phone: values.phone,
                    password: values.password,
                    company: values.company_name,
                    max_employees: values.max_employees,
                    role: 'user_admin'
                }

                console.log('创建用户数据:', createData)
                await userService.createUser(createData)
                message.success('用户创建成功')
            }

            setEditModalVisible(false)
            fetchUsers()
        } catch (error) {
            console.error('保存失败:', error)
            console.error('错误详情:', {
                message: error?.message,
                response: error?.response?.data,
                status: error?.response?.status
            })
            message.error(`保存失败: ${error?.response?.data?.message || error?.message || '未知错误'}`)
        }
    }

    // 过滤用户
    const filteredUsers = users.filter(user =>
        user.username.toLowerCase().includes(searchText.toLowerCase()) ||
        user.email.toLowerCase().includes(searchText.toLowerCase()) ||
        user.phone.includes(searchText) ||
        user.company_name.toLowerCase().includes(searchText.toLowerCase())
    )

    // 表格列定义
    const columns = [
        {
            title: '用户名',
            dataIndex: 'username',
            key: 'username',
        },
        {
            title: '邮箱',
            dataIndex: 'email',
            key: 'email',
        },
        {
            title: '手机号',
            dataIndex: 'phone',
            key: 'phone',
        },
        {
            title: '公司名称',
            dataIndex: 'company_name',
            key: 'company_name',
        },
        {
            title: '员工数量',
            key: 'employees',
            render: (_: any, record: UserAdmin) => (
                <span>
                    {record.current_employees} / {record.max_employees}
                </span>
            ),
        },
        {
            title: '余额',
            dataIndex: 'balance',
            key: 'balance',
            render: (balance: number) => (
                <span style={{ color: balance > 0 ? '#52c41a' : '#ff4d4f' }}>
                    ¥{balance.toFixed(2)}
                </span>
            ),
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => (
                <Tag color={getStatusColor(status)}>
                    {getStatusText(status)}
                </Tag>
            ),
        },
        {
            title: '创建时间',
            dataIndex: 'created_at',
            key: 'created_at',
        },
        {
            title: '最后登录',
            dataIndex: 'last_login',
            key: 'last_login',
        },
        {
            title: '操作',
            key: 'action',
            render: (_: any, record: UserAdmin) => (
                <Space size="middle">
                    <Button
                        type="link"
                        icon={<EyeOutlined />}
                        onClick={() => handleView(record)}
                    >
                        查看
                    </Button>
                    <Button
                        type="link"
                        icon={<EditOutlined />}
                        onClick={() => handleEdit(record)}
                    >
                        编辑
                    </Button>
                    <Button
                        type="link"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => handleDelete(record)}
                    >
                        删除
                    </Button>
                </Space>
            ),
        },
    ]

    return (
        <div>
            <Title level={2}>用户管理员管理</Title>

            <Card>
                <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
                    <Col>
                        <Input
                            placeholder="搜索用户名、邮箱、手机号或公司名称"
                            style={{ width: 300 }}
                            value={searchText}
                            onChange={(e) => setSearchText(e.target.value)}
                            prefix={<SearchOutlined />}
                        />
                    </Col>
                    <Col>
                        <Space>
                            <Button
                                icon={<ReloadOutlined />}
                                onClick={fetchUsers}
                                loading={loading}
                            >
                                刷新
                            </Button>
                            <Button
                                type="primary"
                                icon={<PlusOutlined />}
                                onClick={() => {
                                    form.resetFields()
                                    setCurrentUser(null)
                                    setEditModalVisible(true)
                                }}
                            >
                                新增用户管理员
                            </Button>
                        </Space>
                    </Col>
                </Row>

                <Table
                    columns={columns}
                    dataSource={filteredUsers}
                    rowKey="id"
                    loading={loading}
                    pagination={{
                        total: filteredUsers.length,
                        pageSize: 10,
                        showSizeChanger: true,
                        showQuickJumper: true,
                        showTotal: (total) => `共 ${total} 条记录`,
                    }}
                />
            </Card>

            {/* 编辑/新增用户对话框 */}
            <Modal
                title={currentUser ? '编辑用户管理员' : '新增用户管理员'}
                open={editModalVisible}
                onOk={handleSaveEdit}
                onCancel={() => setEditModalVisible(false)}
                width={700}
                okText="保存"
                cancelText="取消"
            >
                <Form form={form} layout="vertical">
                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="username"
                                label="用户名"
                                rules={[{ required: true, message: '请输入用户名' }]}
                            >
                                <Input placeholder="请输入用户名" />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                name="email"
                                label="邮箱"
                                rules={[
                                    { required: true, message: '请输入邮箱' },
                                    { type: 'email', message: '请输入正确的邮箱格式' }
                                ]}
                            >
                                <Input placeholder="请输入邮箱" />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="phone"
                                label="手机号"
                                rules={[
                                    { required: true, message: '请输入手机号' },
                                    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式' }
                                ]}
                            >
                                <Input placeholder="请输入手机号" />
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                name="password"
                                label="密码"
                                rules={[
                                    { required: !currentUser, message: '请输入密码' },
                                    { min: 6, message: '密码至少6位字符' }
                                ]}
                            >
                                <Input.Password
                                    placeholder={currentUser ? "留空则不修改密码" : "请输入密码"}
                                />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Form.Item
                        name="company_name"
                        label="公司名称"
                        rules={[{ required: true, message: '请输入公司名称' }]}
                    >
                        <Input placeholder="请输入公司名称" />
                    </Form.Item>

                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="max_employees"
                                label="最大员工数"
                                rules={[{ required: true, message: '请输入最大员工数' }]}
                            >
                                <Select placeholder="选择最大员工数">
                                    <Option value={5}>5人</Option>
                                    <Option value={10}>10人</Option>
                                    <Option value={20}>20人</Option>
                                    <Option value={50}>50人</Option>
                                </Select>
                            </Form.Item>
                        </Col>
                        <Col span={12}>
                            <Form.Item
                                name="status"
                                label="状态"
                                rules={[{ required: true, message: '请选择状态' }]}
                            >
                                <Select placeholder="选择状态">
                                    <Option value="active">活跃</Option>
                                    <Option value="inactive">非活跃</Option>
                                    <Option value="suspended">已暂停</Option>
                                </Select>
                            </Form.Item>
                        </Col>
                    </Row>

                    <Form.Item
                        name="balance"
                        label="余额"
                        rules={[{ required: true, message: '请输入余额' }]}
                    >
                        <Input type="number" placeholder="请输入余额" addonBefore="¥" />
                    </Form.Item>
                </Form>
            </Modal>

            {/* 查看用户详情对话框 */}
            <Modal
                title="用户详情"
                open={viewModalVisible}
                onCancel={() => setViewModalVisible(false)}
                footer={[
                    <Button key="close" onClick={() => setViewModalVisible(false)}>
                        关闭
                    </Button>
                ]}
                width={600}
            >
                {currentUser && (
                    <div>
                        <Row gutter={16} style={{ marginBottom: 16 }}>
                            <Col span={12}>
                                <strong>用户名：</strong>{currentUser.username}
                            </Col>
                            <Col span={12}>
                                <strong>邮箱：</strong>{currentUser.email}
                            </Col>
                        </Row>
                        <Row gutter={16} style={{ marginBottom: 16 }}>
                            <Col span={12}>
                                <strong>手机号：</strong>{currentUser.phone}
                            </Col>
                            <Col span={12}>
                                <strong>公司名称：</strong>{currentUser.company_name}
                            </Col>
                        </Row>
                        <Row gutter={16} style={{ marginBottom: 16 }}>
                            <Col span={12}>
                                <strong>员工数量：</strong>
                                {currentUser.current_employees} / {currentUser.max_employees}
                            </Col>
                            <Col span={12}>
                                <strong>余额：</strong>
                                <span style={{ color: currentUser.balance > 0 ? '#52c41a' : '#ff4d4f' }}>
                                    ¥{currentUser.balance.toFixed(2)}
                                </span>
                            </Col>
                        </Row>
                        <Row gutter={16} style={{ marginBottom: 16 }}>
                            <Col span={12}>
                                <strong>状态：</strong>
                                <Tag color={getStatusColor(currentUser.status)}>
                                    {getStatusText(currentUser.status)}
                                </Tag>
                            </Col>
                            <Col span={12}>
                                <strong>创建时间：</strong>{currentUser.created_at}
                            </Col>
                        </Row>
                        <Row gutter={16}>
                            <Col span={12}>
                                <strong>最后登录：</strong>{currentUser.last_login}
                            </Col>
                        </Row>
                    </div>
                )}
            </Modal>
        </div>
    )
}

export default UserManagement
