import {
  DeleteOutlined,
  EditOutlined,
  PlusOutlined,
  SettingOutlined,
  TeamOutlined,
  DollarOutlined,
  SearchOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import {
  Button,
  Card,
  Col,
  Form,
  Input,
  InputNumber,
  message,
  Modal,
  Popconfirm,
  Row,
  Space,
  Switch,
  Table,
  Tag,
  Typography,
  Tabs,
  Select,
  Divider,
} from 'antd'
import React, { useEffect, useState } from 'react'
import { companyPricingService } from '../../services/companyPricingService'
import { userService } from '../../services/userService'
import { CompanyPricingPlan, CompanyOperationPricing } from '../../types'

const { Title, Text } = Typography
const { Option } = Select
const { TabPane } = Tabs

const CompanyPricingManagement: React.FC = () => {
  const [companyPlans, setCompanyPlans] = useState<CompanyPricingPlan[]>([])
  const [operationPricing, setOperationPricing] = useState<CompanyOperationPricing[]>([])
  const [filteredPlans, setFilteredPlans] = useState<CompanyPricingPlan[]>([])
  const [filteredOperations, setFilteredOperations] = useState<CompanyOperationPricing[]>([])
  const [companyNames, setCompanyNames] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [planModalVisible, setPlanModalVisible] = useState(false)
  const [operationModalVisible, setOperationModalVisible] = useState(false)
  const [editingPlan, setEditingPlan] = useState<CompanyPricingPlan | null>(null)
  const [editingOperation, setEditingOperation] = useState<CompanyOperationPricing | null>(null)
  const [planForm] = Form.useForm()
  const [operationForm] = Form.useForm()

  // 筛选器状态
  const [planFilters, setPlanFilters] = useState({
    companyName: '',
    planName: '',
    isActive: 'all', // 'all', 'active', 'inactive'
    priceRange: 'all', // 'all', 'low', 'medium', 'high'
  })
  const [operationFilters, setOperationFilters] = useState({
    companyName: '',
    platform: 'all', // 'all', 'xiaohongshu', 'douyin'
    operationType: 'all', // 'all', 'follow', 'like', 'favorite', 'comment'
    isActive: 'all', // 'all', 'active', 'inactive'
    priceRange: 'all', // 'all', 'low', 'medium', 'high'
  })

  useEffect(() => {
    loadData()
  }, [])

  // 监听数据和筛选条件变化，更新筛选结果
  useEffect(() => {
    filterPlans()
  }, [companyPlans, planFilters])

  useEffect(() => {
    filterOperations()
  }, [operationPricing, operationFilters])

  const loadData = async () => {
    await Promise.all([
      loadCompanyPlans(),
      loadOperationPricing(),
      loadCompanyNames()
    ])
  }

  const loadCompanyNames = async () => {
    try {
      const names = await userService.getCompanyNames()
      setCompanyNames(names)
    } catch (error: any) {
      message.error('加载公司名称失败：' + error.message)
    }
  }

  const loadCompanyPlans = async () => {
    try {
      setLoading(true)
      const data = await companyPricingService.getCompanyPricingPlans()
      setCompanyPlans(data)
    } catch (error: any) {
      message.error('加载公司收费计划失败：' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const loadOperationPricing = async () => {
    try {
      const data = await companyPricingService.getCompanyOperationPricing()
      setOperationPricing(data)
    } catch (error: any) {
      message.error('加载操作收费规则失败：' + error.message)
    }
  }

  // 筛选功能
  const filterPlans = () => {
    let filtered = [...companyPlans]

    // 按公司名称筛选
    if (planFilters.companyName.trim()) {
      filtered = filtered.filter(plan => 
        plan.company_name.toLowerCase().includes(planFilters.companyName.toLowerCase())
      )
    }

    // 按计划名称筛选
    if (planFilters.planName.trim()) {
      filtered = filtered.filter(plan => 
        plan.plan_name.toLowerCase().includes(planFilters.planName.toLowerCase())
      )
    }

    // 按状态筛选
    if (planFilters.isActive !== 'all') {
      const isActive = planFilters.isActive === 'active'
      filtered = filtered.filter(plan => plan.is_active === isActive)
    }

    // 按价格范围筛选
    if (planFilters.priceRange !== 'all') {
      filtered = filtered.filter(plan => {
        const price = plan.employee_monthly_fee
        switch (planFilters.priceRange) {
          case 'low': return price < 100
          case 'medium': return price >= 100 && price < 300
          case 'high': return price >= 300
          default: return true
        }
      })
    }

    setFilteredPlans(filtered)
  }

  const filterOperations = () => {
    let filtered = [...operationPricing]

    // 按公司名称筛选
    if (operationFilters.companyName.trim()) {
      filtered = filtered.filter(op => 
        op.company_name.toLowerCase().includes(operationFilters.companyName.toLowerCase())
      )
    }

    // 按平台筛选
    if (operationFilters.platform !== 'all') {
      filtered = filtered.filter(op => op.platform === operationFilters.platform)
    }

    // 按操作类型筛选
    if (operationFilters.operationType !== 'all') {
      filtered = filtered.filter(op => op.operation_type === operationFilters.operationType)
    }

    // 按状态筛选
    if (operationFilters.isActive !== 'all') {
      const isActive = operationFilters.isActive === 'active'
      filtered = filtered.filter(op => op.is_active === isActive)
    }

    // 按价格范围筛选
    if (operationFilters.priceRange !== 'all') {
      filtered = filtered.filter(op => {
        const price = op.unit_price
        switch (operationFilters.priceRange) {
          case 'low': return price < 1
          case 'medium': return price >= 1 && price < 5
          case 'high': return price >= 5
          default: return true
        }
      })
    }

    setFilteredOperations(filtered)
  }

  // 重置筛选器
  const resetPlanFilters = () => {
    setPlanFilters({
      companyName: '',
      planName: '',
      isActive: 'all',
      priceRange: 'all',
    })
  }

  const resetOperationFilters = () => {
    setOperationFilters({
      companyName: '',
      platform: 'all',
      operationType: 'all',
      isActive: 'all',
      priceRange: 'all',
    })
  }

  // 公司收费计划管理

  const handleCreatePlan = () => {
    setEditingPlan(null)
    planForm.resetFields()
    planForm.setFieldsValue({
      employee_monthly_fee: 50.0,
    })
    setPlanModalVisible(true)
  }

  const handleEditPlan = (plan: CompanyPricingPlan) => {
    setEditingPlan(plan)
    planForm.setFieldsValue({
      company_name: plan.company_name,
      plan_name: plan.plan_name,
      employee_monthly_fee: plan.employee_monthly_fee,
      is_active: plan.is_active,
    })
    setPlanModalVisible(true)
  }

  const handleDeletePlan = async (planId: number) => {
    try {
      await companyPricingService.deleteCompanyPricingPlan(planId)
      message.success('删除成功')
      loadCompanyPlans()
    } catch (error: any) {
      message.error('删除失败：' + error.message)
    }
  }

  const handleSubmitPlan = async (values: any) => {
    try {
      const planData = {
        company_name: values.company_name,
        plan_name: values.plan_name,
        employee_monthly_fee: values.employee_monthly_fee,
        is_active: values.is_active,
      }

      if (editingPlan) {
        await companyPricingService.updateCompanyPricingPlan(editingPlan.id, {
          plan_name: planData.plan_name,
          employee_monthly_fee: planData.employee_monthly_fee,
          is_active: planData.is_active,
        })
        message.success('更新成功')
      } else {
        await companyPricingService.createCompanyPricingPlan(planData)
        message.success('创建成功')
      }

      setPlanModalVisible(false)
      loadCompanyPlans()
    } catch (error: any) {
      message.error((editingPlan ? '更新' : '创建') + '失败：' + error.message)
    }
  }

  // 操作收费规则管理

  const handleCreateOperation = () => {
    setEditingOperation(null)
    operationForm.resetFields()
    operationForm.setFieldsValue({
      platform: 'xiaohongshu',
      operation_type: 'follow',
      unit_price: 0.05,
    })
    setOperationModalVisible(true)
  }

  const handleEditOperation = (operation: CompanyOperationPricing) => {
    setEditingOperation(operation)
    operationForm.setFieldsValue({
      company_name: operation.company_name,
      platform: operation.platform,
      operation_type: operation.operation_type,
      unit_price: operation.unit_price,
      is_active: operation.is_active,
    })
    setOperationModalVisible(true)
  }

  const handleDeleteOperation = async (operationId: number) => {
    try {
      await companyPricingService.deleteCompanyOperationPricing(operationId)
      message.success('删除成功')
      loadOperationPricing()
    } catch (error: any) {
      message.error('删除失败：' + error.message)
    }
  }

  const handleSubmitOperation = async (values: any) => {
    try {
      const operationData = {
        company_name: values.company_name,
        platform: values.platform,
        operation_type: values.operation_type,
        unit_price: values.unit_price,
        is_active: values.is_active,
      }

      if (editingOperation) {
        await companyPricingService.updateCompanyOperationPricing(editingOperation.id, {
          unit_price: operationData.unit_price,
          is_active: operationData.is_active,
        })
        message.success('更新成功')
      } else {
        await companyPricingService.createCompanyOperationPricing(operationData)
        message.success('创建成功')
      }

      setOperationModalVisible(false)
      loadOperationPricing()
    } catch (error: any) {
      message.error((editingOperation ? '更新' : '创建') + '失败：' + error.message)
    }
  }

  // 表格配置

  const planColumns = [
    {
      title: '公司名称',
      dataIndex: 'company_name',
      key: 'company_name',
      render: (text: string) => (
        <Space>
          <TeamOutlined style={{ color: '#1890ff' }} />
          <Text strong>{text}</Text>
        </Space>
      ),
    },
    {
      title: '计划名称',
      dataIndex: 'plan_name',
      key: 'plan_name',
    },
    {
      title: '员工月费 (¥)',
      dataIndex: 'employee_monthly_fee',
      key: 'employee_monthly_fee',
      render: (fee: number) => (
        <Space>
          <DollarOutlined style={{ color: '#52c41a' }} />
          <Text>¥{fee.toFixed(2)}/月</Text>
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'actions',
      render: (record: CompanyPricingPlan) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEditPlan(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个收费计划吗？"
            onConfirm={() => handleDeletePlan(record.id)}
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const operationColumns = [
    {
      title: '公司名称',
      dataIndex: 'company_name',
      key: 'company_name',
      render: (text: string) => (
        <Space>
          <TeamOutlined style={{ color: '#1890ff' }} />
          <Text>{text}</Text>
        </Space>
      ),
    },
    {
      title: '平台',
      dataIndex: 'platform',
      key: 'platform',
      render: (platform: string) => {
        const platformMap: Record<string, { text: string; color: string }> = {
          xiaohongshu: { text: '小红书', color: 'red' },
          douyin: { text: '抖音', color: 'blue' },
        }
        const config = platformMap[platform] || { text: platform, color: 'default' }
        return <Tag color={config.color}>{config.text}</Tag>
      },
    },
    {
      title: '操作类型',
      dataIndex: 'operation_type',
      key: 'operation_type',
      render: (type: string) => {
        const typeMap: Record<string, { text: string; color: string }> = {
          follow: { text: '关注', color: 'green' },
          like: { text: '点赞', color: 'orange' },
          favorite: { text: '收藏', color: 'purple' },
          comment: { text: '评论', color: 'cyan' },
        }
        const config = typeMap[type] || { text: type, color: 'default' }
        return <Tag color={config.color}>{config.text}</Tag>
      },
    },
    {
      title: '单价 (¥)',
      dataIndex: 'unit_price',
      key: 'unit_price',
      render: (price: number) => (
        <Space>
          <DollarOutlined style={{ color: '#52c41a' }} />
          <Text>¥{price.toFixed(3)}</Text>
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'actions',
      render: (record: CompanyOperationPricing) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEditOperation(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个收费规则吗？"
            onConfirm={() => handleDeleteOperation(record.id)}
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div className="page-header">
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={2}>
              <SettingOutlined style={{ marginRight: '8px' }} />
              公司收费管理
            </Title>
            <p>管理各公司的收费计划和操作定价</p>
          </Col>
        </Row>
      </div>

      <Tabs defaultActiveKey="plans">
        <TabPane tab="公司收费计划" key="plans">
          <Card>
            <div style={{ marginBottom: '16px' }}>
              <Row gutter={[16, 16]} align="middle">
                <Col span={6}>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={handleCreatePlan}
                  >
                    新建收费计划
                  </Button>
                </Col>
                <Col span={18}>
                  <div style={{ 
                    background: '#fafafa', 
                    padding: '12px', 
                    borderRadius: '6px',
                    border: '1px solid #d9d9d9'
                  }}>
                    <Row gutter={[8, 8]} justify="end" align="middle">
                      <Col>
                        <Text style={{ fontSize: '12px', color: '#666' }}>筛选条件：</Text>
                      </Col>
                      <Col>
                        <Select
                          placeholder="公司名称"
                          value={planFilters.companyName}
                          onChange={(value) => setPlanFilters({...planFilters, companyName: value || ''})}
                          style={{ width: 120 }}
                          allowClear
                          showSearch
                          size="small"
                          filterOption={(input, option) =>
                            (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                          }
                          options={[
                            { value: '', label: '全部公司' },
                            ...companyNames.map(name => ({
                              value: name,
                              label: name
                            }))
                          ]}
                        />
                      </Col>
                      <Col>
                        <Input
                          placeholder="计划名称"
                          value={planFilters.planName}
                          onChange={(e) => setPlanFilters({...planFilters, planName: e.target.value})}
                          style={{ width: 120 }}
                          allowClear
                          size="small"
                        />
                      </Col>
                      <Col>
                        <Select
                          value={planFilters.isActive}
                          onChange={(value) => setPlanFilters({...planFilters, isActive: value})}
                          style={{ width: 100 }}
                          placeholder="状态"
                          size="small"
                        >
                          <Option value="all">全部状态</Option>
                          <Option value="active">启用</Option>
                          <Option value="inactive">禁用</Option>
                        </Select>
                      </Col>
                      <Col>
                        <Select
                          value={planFilters.priceRange}
                          onChange={(value) => setPlanFilters({...planFilters, priceRange: value})}
                          style={{ width: 120 }}
                          placeholder="价格范围"
                          size="small"
                        >
                          <Option value="all">全部价格</Option>
                          <Option value="low">低价 (&lt;¥100)</Option>
                          <Option value="medium">中价 (¥100-300)</Option>
                          <Option value="high">高价 (≥¥300)</Option>
                        </Select>
                      </Col>
                      <Col>
                        <Button onClick={resetPlanFilters} icon={<ReloadOutlined />} size="small">重置</Button>
                      </Col>
                    </Row>
                  </div>
                </Col>
              </Row>
            </div>

            <Table
              columns={planColumns}
              dataSource={filteredPlans}
              rowKey="id"
              loading={loading}
              pagination={{
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条记录`,
              }}
            />
            <div style={{ marginTop: '8px', color: '#666', fontSize: '12px' }}>
              <SearchOutlined style={{ marginRight: '4px' }} />
              筛选结果：显示 <Text strong style={{ color: '#1890ff' }}>{filteredPlans.length}</Text> 条，
              共 <Text strong>{companyPlans.length}</Text> 条记录
              {filteredPlans.length < companyPlans.length && (
                <Text style={{ color: '#fa8c16', marginLeft: '8px' }}>
                  (已应用筛选条件)
                </Text>
              )}
            </div>
          </Card>
        </TabPane>

        <TabPane tab="操作收费规则" key="operations">
          <Card>
            <div style={{ marginBottom: '16px' }}>
              <Row gutter={[16, 16]} align="middle">
                <Col span={6}>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={handleCreateOperation}
                  >
                    新建收费规则
                  </Button>
                </Col>
                <Col span={18}>
                  <div style={{ 
                    background: '#fafafa', 
                    padding: '12px', 
                    borderRadius: '6px',
                    border: '1px solid #d9d9d9'
                  }}>
                    <Row gutter={[8, 8]} justify="end" align="middle">
                      <Col>
                        <Text style={{ fontSize: '12px', color: '#666' }}>筛选条件：</Text>
                      </Col>
                      <Col>
                        <Select
                          placeholder="公司名称"
                          value={operationFilters.companyName}
                          onChange={(value) => setOperationFilters({...operationFilters, companyName: value || ''})}
                          style={{ width: 120 }}
                          allowClear
                          showSearch
                          size="small"
                          filterOption={(input, option) =>
                            (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                          }
                          options={[
                            { value: '', label: '全部公司' },
                            ...companyNames.map(name => ({
                              value: name,
                              label: name
                            }))
                          ]}
                        />
                      </Col>
                      <Col>
                        <Select
                          value={operationFilters.platform}
                          onChange={(value) => setOperationFilters({...operationFilters, platform: value})}
                          style={{ width: 100 }}
                          placeholder="平台"
                          size="small"
                        >
                          <Option value="all">全部平台</Option>
                          <Option value="xiaohongshu">小红书</Option>
                          <Option value="douyin">抖音</Option>
                        </Select>
                      </Col>
                      <Col>
                        <Select
                          value={operationFilters.operationType}
                          onChange={(value) => setOperationFilters({...operationFilters, operationType: value})}
                          style={{ width: 100 }}
                          placeholder="操作类型"
                          size="small"
                        >
                          <Option value="all">全部操作</Option>
                          <Option value="follow">关注</Option>
                          <Option value="like">点赞</Option>
                          <Option value="favorite">收藏</Option>
                          <Option value="comment">评论</Option>
                        </Select>
                      </Col>
                      <Col>
                        <Select
                          value={operationFilters.isActive}
                          onChange={(value) => setOperationFilters({...operationFilters, isActive: value})}
                          style={{ width: 100 }}
                          placeholder="状态"
                          size="small"
                        >
                          <Option value="all">全部状态</Option>
                          <Option value="active">启用</Option>
                          <Option value="inactive">禁用</Option>
                        </Select>
                      </Col>
                      <Col>
                        <Select
                          value={operationFilters.priceRange}
                          onChange={(value) => setOperationFilters({...operationFilters, priceRange: value})}
                          style={{ width: 120 }}
                          placeholder="价格范围"
                          size="small"
                        >
                          <Option value="all">全部价格</Option>
                          <Option value="low">低价 (&lt;¥1)</Option>
                          <Option value="medium">中价 (¥1-5)</Option>
                          <Option value="high">高价 (≥¥5)</Option>
                        </Select>
                      </Col>
                      <Col>
                        <Button onClick={resetOperationFilters} icon={<ReloadOutlined />} size="small">重置</Button>
                      </Col>
                    </Row>
                  </div>
                </Col>
              </Row>
            </div>

            <Table
              columns={operationColumns}
              dataSource={filteredOperations}
              rowKey="id"
              loading={loading}
              pagination={{
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条记录`,
              }}
            />
            <div style={{ marginTop: '8px', color: '#666', fontSize: '12px' }}>
              <SearchOutlined style={{ marginRight: '4px' }} />
              筛选结果：显示 <Text strong style={{ color: '#1890ff' }}>{filteredOperations.length}</Text> 条，
              共 <Text strong>{operationPricing.length}</Text> 条记录
              {filteredOperations.length < operationPricing.length && (
                <Text style={{ color: '#fa8c16', marginLeft: '8px' }}>
                  (已应用筛选条件)
                </Text>
              )}
            </div>
          </Card>
        </TabPane>
      </Tabs>

      {/* 公司收费计划模态框 */}
      <Modal
        title={editingPlan ? '编辑收费计划' : '新建收费计划'}
        open={planModalVisible}
        onCancel={() => setPlanModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={planForm}
          layout="vertical"
          onFinish={handleSubmitPlan}
        >
          <Form.Item
            name="company_name"
            label="公司名称"
            rules={[{ required: true, message: '请选择公司名称' }]}
          >
            {editingPlan ? (
              <Input 
                placeholder="公司名称" 
                disabled={true}
              />
            ) : (
              <Select
                placeholder="请选择公司名称"
                allowClear
                showSearch
                filterOption={(input, option) =>
                  (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                }
                options={companyNames.map(name => ({
                  value: name,
                  label: name
                }))}
              />
            )}
          </Form.Item>

          <Form.Item
            name="plan_name"
            label="计划名称"
            rules={[{ required: true, message: '请输入计划名称' }]}
          >
            <Input placeholder="例如：标准计划、高级计划" />
          </Form.Item>

          <Form.Item
            name="employee_monthly_fee"
            label="员工月费 (¥)"
            rules={[
              { required: true, message: '请输入员工月费' },
              { type: 'number', min: 0, message: '价格不能小于0' },
            ]}
          >
            <InputNumber
              placeholder="请输入员工月费"
              style={{ width: '100%' }}
              precision={2}
              min={0}
            />
          </Form.Item>

          {editingPlan && (
            <Form.Item name="is_active" label="启用状态" valuePropName="checked">
              <Switch />
            </Form.Item>
          )}

          <Divider />

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingPlan ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setPlanModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 操作收费规则模态框 */}
      <Modal
        title={editingOperation ? '编辑收费规则' : '新建收费规则'}
        open={operationModalVisible}
        onCancel={() => setOperationModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={operationForm}
          layout="vertical"
          onFinish={handleSubmitOperation}
        >
          <Form.Item
            name="company_name"
            label="公司名称"
            rules={[{ required: true, message: '请选择公司名称' }]}
          >
            {editingOperation ? (
              <Input 
                placeholder="公司名称" 
                disabled={true}
              />
            ) : (
              <Select
                placeholder="请选择公司名称"
                allowClear
                showSearch
                filterOption={(input, option) =>
                  (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                }
                options={companyNames.map(name => ({
                  value: name,
                  label: name
                }))}
              />
            )}
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="platform"
                label="平台"
                rules={[{ required: true, message: '请选择平台' }]}
              >
                <Select placeholder="请选择平台" disabled={!!editingOperation}>
                  <Option value="xiaohongshu">小红书</Option>
                  <Option value="douyin">抖音</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="operation_type"
                label="操作类型"
                rules={[{ required: true, message: '请选择操作类型' }]}
              >
                <Select placeholder="请选择操作类型" disabled={!!editingOperation}>
                  <Option value="follow">关注</Option>
                  <Option value="like">点赞</Option>
                  <Option value="favorite">收藏</Option>
                  <Option value="comment">评论</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="unit_price"
            label="单价 (¥)"
            rules={[
              { required: true, message: '请输入单价' },
              { type: 'number', min: 0, message: '价格不能小于0' },
            ]}
          >
            <InputNumber
              placeholder="请输入单价"
              style={{ width: '100%' }}
              precision={3}
              min={0}
              step={0.001}
            />
          </Form.Item>

          {editingOperation && (
            <Form.Item name="is_active" label="启用状态" valuePropName="checked">
              <Switch />
            </Form.Item>
          )}

          <Divider />

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingOperation ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setOperationModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default CompanyPricingManagement
