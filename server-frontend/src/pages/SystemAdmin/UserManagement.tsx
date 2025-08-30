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

const { Title } = Typography
const { Option } = Select

interface UserAdmin {
    id: number
    username: string
    email: string
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
            // 这里应该调用实际的API
            // const response = await userService.getAllUserAdmins()
            // setUsers(response.data)

            // 模拟数据
            const mockUsers: UserAdmin[] = [
                {
                    id: 1,
                    username: 'company_admin_1',
                    email: 'admin1@company1.com',
                    company_name: '科技有限公司',
                    max_employees: 10,
                    current_employees: 8,
                    status: 'active',
                    created_at: '2024-01-15',
                    last_login: '2024-02-20',
                    balance: 1500.00
                },
                {
                    id: 2,
                    username: 'company_admin_2',
                    email: 'admin2@company2.com',
                    company_name: '营销策划公司',
                    max_employees: 10,
                    current_employees: 5,
                    status: 'active',
                    created_at: '2024-01-20',
                    last_login: '2024-02-19',
                    balance: 800.00
                },
                {
                    id: 3,
                    username: 'company_admin_3',
                    email: 'admin3@company3.com',
                    company_name: '电商运营公司',
                    max_employees: 10,
                    current_employees: 10,
                    status: 'suspended',
                    created_at: '2024-02-01',
                    last_login: '2024-02-18',
                    balance: 200.00
                }
            ]
            setUsers(mockUsers)
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
            content: `确定要删除用户管理员 "${user.username}" 吗？此操作不可恢复。`,
            okText: '删除',
            okType: 'danger',
            cancelText: '取消',
            onOk: async () => {
                try {
                    // await userService.deleteUserAdmin(user.id)
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
            await form.validateFields()
            // await userService.updateUserAdmin(currentUser!.id, values)
            message.success('保存成功')
            setEditModalVisible(false)
            fetchUsers()
        } catch (error) {
            console.error('保存失败:', error)
            message.error('保存失败')
        }
    }

    // 过滤用户
    const filteredUsers = users.filter(user =>
        user.username.toLowerCase().includes(searchText.toLowerCase()) ||
        user.email.toLowerCase().includes(searchText.toLowerCase()) ||
        user.company_name.toLowerCase().includes(searchText.toLowerCase())
    )

    const columns = [
        {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
            width: 80,
        },
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
            width: 200,
            render: (_: any, record: UserAdmin) => (
                <Space>
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
        <div style={{ padding: '20px' }}>
            <Title level={2}>用户管理员管理</Title>

            <Card>
                <Row justify="space-between" style={{ marginBottom: 16 }}>
                    <Col>
                        <Input.Search
                            placeholder="搜索用户名、邮箱或公司名称"
                            allowClear
                            value={searchText}
                            onChange={e => setSearchText(e.target.value)}
                            style={{ width: 300 }}
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
                width={600}
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
                title="用户管理员详情"
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
                        <Row gutter={[16, 16]}>
                            <Col span={12}>
                                <strong>ID:</strong> {currentUser.id}
                            </Col>
                            <Col span={12}>
                                <strong>用户名:</strong> {currentUser.username}
                            </Col>
                            <Col span={12}>
                                <strong>邮箱:</strong> {currentUser.email}
                            </Col>
                            <Col span={12}>
                                <strong>公司名称:</strong> {currentUser.company_name}
                            </Col>
                            <Col span={12}>
                                <strong>最大员工数:</strong> {currentUser.max_employees}
                            </Col>
                            <Col span={12}>
                                <strong>当前员工数:</strong> {currentUser.current_employees}
                            </Col>
                            <Col span={12}>
                                <strong>余额:</strong>
                                <span style={{ color: currentUser.balance > 0 ? '#52c41a' : '#ff4d4f' }}>
                                    ¥{currentUser.balance.toFixed(2)}
                                </span>
                            </Col>
                            <Col span={12}>
                                <strong>状态:</strong>
                                <Tag color={getStatusColor(currentUser.status)} style={{ marginLeft: 8 }}>
                                    {getStatusText(currentUser.status)}
                                </Tag>
                            </Col>
                            <Col span={12}>
                                <strong>创建时间:</strong> {currentUser.created_at}
                            </Col>
                            <Col span={12}>
                                <strong>最后登录:</strong> {currentUser.last_login}
                            </Col>
                        </Row>
                    </div>
                )}
            </Modal>
        </div>
    )
}

export default UserManagement
