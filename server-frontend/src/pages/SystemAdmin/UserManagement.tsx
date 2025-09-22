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
    Statistic,
    Table,
    Tag,
    Typography,
    message,
    Alert,
} from 'antd'
import React, { useEffect, useState } from 'react'
import { AdminUserUpdateRequest, userService } from '../../services/userService'
import { billingService } from '../../services/billingService'

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
    const [deleteModalVisible, setDeleteModalVisible] = useState(false)
    const [currentUser, setCurrentUser] = useState<UserAdmin | null>(null)
    const [userToDelete, setUserToDelete] = useState<UserAdmin | null>(null)
    const [modalError, setModalError] = useState<string>('') // 添加模态框错误状态
    const [form] = Form.useForm()

    // 获取用户列表
    const fetchUsers = async () => {
        try {
            setLoading(true)
            console.log('🔄 开始获取用户列表...')
            console.log('🔑 当前token:', localStorage.getItem('token'))
            
            // 获取所有用户（只包括用户管理员）
            const response = await userService.getUsers(1, 100) // 移除角色过滤
            console.log('📋 获取到的用户数据:', response)
            const userAdminsList = response.items.filter(user => user.role === 'user_admin')
            
            // 并行获取每个用户的余额信息
            const userAdminsWithBalance: UserAdmin[] = await Promise.all(
                userAdminsList.map(async (user) => {
                    try {
                        const billingInfo = await billingService.getUserBillingInfo(user.id)
                        return {
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
                            balance: billingInfo.balance
                        }
                    } catch (error) {
                        console.warn(`获取用户 ${user.id} 的余额失败:`, error)
                        return {
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
                            balance: 0 // 获取失败时的默认值
                        }
                    }
                })
            )
            
            console.log('👥 处理后的用户列表（含余额）:', userAdminsWithBalance)
            setUsers(userAdminsWithBalance)
        } catch (error: any) {
            console.error('❌ 获取用户列表失败:', error)
            console.error('❌ 错误详情:', {
                message: error?.message,
                response: error?.response?.data,
                status: error?.response?.status,
                config: error?.config
            })
            message.error(`获取用户列表失败: ${error?.message || '未知错误'}`)
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
        setModalError('') // 清除之前的错误状态
        setEditModalVisible(true)
    }

    // 查看用户详情
    const handleView = (user: UserAdmin) => {
        setCurrentUser(user)
        setViewModalVisible(true)
    }

    // 删除用户
    const handleDelete = (user: UserAdmin) => {
        console.log('🗑️ 删除用户被点击，用户:', user)
        setUserToDelete(user)
        setDeleteModalVisible(true)
    }

    // 确认删除
    const confirmDelete = async () => {
        if (!userToDelete) return
        
        console.log('✅ 用户确认删除，开始执行删除操作')
        try {
            console.log('🔄 调用删除API...')
            await userService.deleteUser(userToDelete.id)
            console.log('✅ 删除API调用成功')
            message.success('删除成功')
            setDeleteModalVisible(false)
            setUserToDelete(null)
            fetchUsers()
        } catch (error: any) {
            console.error('❌ 删除失败:', error)
            message.error(`删除失败: ${error?.message || error}`)
        }
    }

    // 取消删除
    const cancelDelete = () => {
        console.log('❌ 用户取消删除操作')
        setDeleteModalVisible(false)
        setUserToDelete(null)
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
            setModalError('') // 清除错误状态
            fetchUsers()
        } catch (error: any) {
            console.error('🚨 保存失败:', error)
            console.error('🔍 错误详情:', {
                message: error?.message,
                response: error?.response?.data,
                status: error?.response?.status
            })
            
            // 提取错误信息
            let errorMessage = '未知错误'
            
            if (error?.response?.data?.message) {
                errorMessage = error.response.data.message
                console.log('📡 使用 response.data.message:', errorMessage)
            } else if (error?.message) {
                errorMessage = error.message
                console.log('📝 使用 error.message:', errorMessage)
            }
            
            console.log('🎯 最终错误信息:', JSON.stringify(errorMessage))
            console.log('� 检查用户名已存在:', errorMessage.includes('用户名已存在'))
            console.log('� 检查邮箱已存在:', errorMessage.includes('邮箱已存在'))
            console.log('� 检查手机号已存在:', errorMessage.includes('手机号已存在'))
            
            // 特定错误的友好提示
            if (errorMessage.includes('用户名已存在')) {
                console.log('✅ 匹配到用户名已存在错误 - 显示友好提示')
                const errorMsg = '❌ 用户名已被使用，请选择其他用户名'
                setModalError(errorMsg) // 在模态框中显示错误
                message.error(errorMsg) // 同时显示全局消息
            } else if (errorMessage.includes('邮箱已存在')) {
                console.log('✅ 匹配到邮箱已存在错误 - 显示友好提示')
                const errorMsg = '❌ 邮箱已被注册，请使用其他邮箱地址'
                setModalError(errorMsg)
                message.error(errorMsg)
            } else if (errorMessage.includes('手机号已存在')) {
                console.log('✅ 匹配到手机号已存在错误 - 显示友好提示')
                const errorMsg = '❌ 手机号已被注册，请使用其他手机号'
                setModalError(errorMsg)
                message.error(errorMsg)
            } else if (errorMessage.includes('权限不足')) {
                console.log('✅ 匹配到权限不足错误 - 显示友好提示')
                const errorMsg = '❌ 权限不足，无法执行此操作'
                setModalError(errorMsg)
                message.error(errorMsg)
            } else if (errorMessage.includes('密码')) {
                console.log('✅ 匹配到密码错误 - 显示友好提示')
                const errorMsg = '❌ 密码格式不正确或加密失败'
                setModalError(errorMsg)
                message.error(errorMsg)
            } else {
                console.log('❌ 未匹配到特定错误，显示通用错误')
                console.log('❌ 原始错误信息:', errorMessage)
                const errorMsg = `操作失败: ${errorMessage}`
                setModalError(errorMsg)
                message.error(errorMsg)
            }
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
            title: '用户信息',
            dataIndex: 'username',
            key: 'username',
            render: (username: string, record: UserAdmin) => (
                <div>
                    <div style={{ fontWeight: 'bold' }}>{username}</div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                        {record.email}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                        {record.phone}
                    </div>
                </div>
            ),
        },
        {
            title: '公司信息',
            dataIndex: 'company_name',
            key: 'company_name',
            render: (company: string, record: UserAdmin) => (
                <div>
                    <div style={{ fontWeight: 'bold' }}>{company}</div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                        员工数量：{record.current_employees} / {record.max_employees}
                    </div>
                </div>
            ),
        },
        {
            title: '余额',
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
            title: '时间信息',
            dataIndex: 'created_at',
            key: 'created_at',
            render: (created: string, record: UserAdmin) => (
                <div>
                    <div style={{ fontSize: '12px' }}>
                        创建：{created}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                        登录：{record.last_login || '未登录'}
                    </div>
                </div>
            ),
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
                        onClick={() => {
                            console.log('🖱️ 删除按钮被点击，记录:', record)
                            handleDelete(record)
                        }}
                    >
                        删除
                    </Button>
                </Space>
            ),
        },
    ]

    return (
        <div>
            <div className="page-header">
                <Row justify="space-between" align="middle">
                    <Col>
                        <Title level={2}>用户管理员管理</Title>
                        <p>管理系统中的用户管理员账户</p>
                    </Col>
                    <Col>
                        <Space>
                            <Input
                                placeholder="搜索用户名、邮箱、手机号或公司名称"
                                style={{ width: 300 }}
                                value={searchText}
                                onChange={(e) => setSearchText(e.target.value)}
                                prefix={<SearchOutlined />}
                            />
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
                                    setModalError('') // 清除之前的错误状态
                                    setEditModalVisible(true)
                                }}
                            >
                                新增用户管理员
                            </Button>
                        </Space>
                    </Col>
                </Row>
            </div>

            {/* 用户列表 */}
            <Card title="用户管理员列表">
                <Table
                    columns={columns}
                    dataSource={filteredUsers}
                    rowKey="id"
                    loading={loading}
                    pagination={{
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
                {/* 错误提示 */}
                {modalError && (
                    <Alert 
                        message={modalError} 
                        type="error" 
                        showIcon 
                        style={{ marginBottom: 16 }}
                        closable
                        onClose={() => setModalError('')}
                    />
                )}
                
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

            {/* 删除确认Modal */}
            <Modal
                title="确认删除"
                open={deleteModalVisible}
                onOk={confirmDelete}
                onCancel={cancelDelete}
                okText="删除"
                cancelText="取消"
                okType="danger"
                centered
            >
                {userToDelete && (
                    <p>
                        确定要删除用户 <strong>"{userToDelete.username}"</strong> 吗？
                        <br />
                        <span style={{ color: '#ff4d4f' }}>此操作不可恢复。</span>
                    </p>
                )}
            </Modal>
        </div>
    )
}

export default UserManagement
