import {
    DeleteOutlined,
    EditOutlined,
    PlusOutlined,
    SettingOutlined,
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
    Select,
    Space,
    Switch,
    Table,
    Tag,
    Typography,
} from 'antd'
import React, { useEffect, useState } from 'react'
import { billingService } from '../../services/billingService'
import { PricingRule } from '../../types'

const { Title, Text } = Typography
const { Option } = Select
const { TextArea } = Input

const PricingSettings: React.FC = () => {
  const [rules, setRules] = useState<PricingRule[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingRule, setEditingRule] = useState<PricingRule | null>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    loadPricingRules()
  }, [])

  const loadPricingRules = async () => {
    try {
      setLoading(true)
      const data = await billingService.getPricingRules()
      setRules(data)
    } catch (error: any) {
      message.error('加载收费规则失败：' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setEditingRule(null)
    form.resetFields()
    form.setFieldsValue({
      rule_type: 'follow_count',
      billing_period: 'monthly',
      is_active: true,
    })
    setModalVisible(true)
  }

  const handleEdit = (rule: PricingRule) => {
    setEditingRule(rule)
    form.setFieldsValue({
      name: rule.name,
      description: rule.description,
      rule_type: rule.rule_type,
      unit_price: rule.unit_price,
      billing_period: rule.billing_period,
      is_active: rule.is_active,
    })
    setModalVisible(true)
  }

  const handleDelete = async (ruleId: number) => {
    try {
      await billingService.deletePricingRule(ruleId)
      message.success('删除成功')
      loadPricingRules()
    } catch (error: any) {
      message.error('删除失败：' + error.message)
    }
  }

  const handleSubmit = async (values: any) => {
    try {
      const ruleData = {
        name: values.name,
        description: values.description,
        rule_type: values.rule_type,
        unit_price: values.unit_price,
        billing_period: values.billing_period,
        is_active: values.is_active,
        rule_config: {}, // 可以根据需要扩展
      }

      if (editingRule) {
        await billingService.updatePricingRule(editingRule.id, ruleData)
        message.success('更新成功')
      } else {
        await billingService.createPricingRule(ruleData)
        message.success('创建成功')
      }

      setModalVisible(false)
      loadPricingRules()
    } catch (error: any) {
      message.error(editingRule ? '更新失败：' : '创建失败：' + error.message)
    }
  }

  const handleToggleStatus = async (rule: PricingRule) => {
    try {
      await billingService.updatePricingRule(rule.id, {
        is_active: !rule.is_active,
      })
      message.success('状态更新成功')
      loadPricingRules()
    } catch (error: any) {
      message.error('状态更新失败：' + error.message)
    }
  }

  const columns = [
    {
      title: '规则名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '规则类型',
      dataIndex: 'rule_type',
      key: 'rule_type',
      render: (type: string) => {
        const typeMap: Record<string, { text: string; color: string }> = {
          employee_count: { text: '按员工数计费', color: 'blue' },
          follow_count: { text: '按关注数计费', color: 'green' },
        }
        const config = typeMap[type] || { text: type, color: 'default' }
        return <Tag color={config.color}>{config.text}</Tag>
      },
    },
    {
      title: '单价 (¥)',
      dataIndex: 'unit_price',
      key: 'unit_price',
      render: (price: number) => `¥${price.toFixed(2)}`,
    },
    {
      title: '计费周期',
      dataIndex: 'billing_period',
      key: 'billing_period',
      render: (period: string) => {
        const periodMap: Record<string, string> = {
          monthly: '按月',
          yearly: '按年',
          one_time: '一次性',
        }
        return periodMap[period] || period
      },
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean, record: PricingRule) => (
        <Switch
          checked={isActive}
          onChange={() => handleToggleStatus(record)}
          checkedChildren="启用"
          unCheckedChildren="停用"
        />
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (text: string) => (
        <Text ellipsis={{ tooltip: text }}>
          {text || '暂无描述'}
        </Text>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (record: PricingRule) => (
        <Space size="middle">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除此收费规则吗？"
            description="删除后无法恢复，请谨慎操作。"
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

  const ruleTypeOptions = [
    { value: 'employee_count', label: '按员工数计费' },
    { value: 'follow_count', label: '按关注数计费' },
  ]

  const billingPeriodOptions = [
    { value: 'monthly', label: '按月' },
    { value: 'yearly', label: '按年' },
    { value: 'one_time', label: '一次性' },
  ]

  return (
    <div>
      <div className="page-header">
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={2}>收费设置</Title>
            <p>管理系统的收费规则和价格标准</p>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreate}
            >
              添加收费规则
            </Button>
          </Col>
        </Row>
      </div>

      {/* 当前生效规则概览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '2rem' }}>
        {rules.filter(rule => rule.is_active).map(rule => (
          <Col xs={24} sm={12} lg={6} key={rule.id}>
            <Card size="small">
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '8px' }}>
                  {rule.name}
                </div>
                <div style={{ fontSize: '24px', color: '#1890ff', fontWeight: 'bold' }}>
                  ¥{rule.unit_price}
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>
                  {rule.rule_type === 'employee_count' ? '每员工' : '每关注'}
                  /{(() => {
                    switch (rule.billing_period) {
                      case 'monthly': return '月'
                      case 'yearly': return '年'
                      default: return '次'
                    }
                  })()}
                </div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      <Card title={<Space><SettingOutlined />收费规则列表</Space>}>
        <Table
          columns={columns}
          dataSource={rules}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条规则`,
          }}
        />
      </Card>

      <Modal
        title={editingRule ? '编辑收费规则' : '添加收费规则'}
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
          <Form.Item
            name="name"
            label="规则名称"
            rules={[
              { required: true, message: '请输入规则名称' },
              { max: 100, message: '规则名称不能超过100个字符' },
            ]}
          >
            <Input placeholder="请输入规则名称" />
          </Form.Item>

          <Form.Item
            name="rule_type"
            label="规则类型"
            rules={[{ required: true, message: '请选择规则类型' }]}
          >
            <Select placeholder="请选择规则类型">
              {ruleTypeOptions.map(option => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="unit_price"
                label="单价 (¥)"
                rules={[
                  { required: true, message: '请输入单价' },
                  { type: 'number', min: 0.01, message: '单价必须大于0' },
                ]}
              >
                <InputNumber
                  placeholder="请输入单价"
                  precision={2}
                  min={0.01}
                  style={{ width: '100%' }}
                  addonAfter="元"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="billing_period"
                label="计费周期"
                rules={[{ required: true, message: '请选择计费周期' }]}
              >
                <Select placeholder="请选择计费周期">
                  {billingPeriodOptions.map(option => (
                    <Option key={option.value} value={option.value}>
                      {option.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="description"
            label="规则描述"
            rules={[
              { max: 500, message: '描述不能超过500个字符' },
            ]}
          >
            <TextArea
              placeholder="请输入规则描述（可选）"
              rows={3}
              showCount
              maxLength={500}
            />
          </Form.Item>

          <Form.Item
            name="is_active"
            label="规则状态"
            valuePropName="checked"
          >
            <Switch
              checkedChildren="启用"
              unCheckedChildren="停用"
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default PricingSettings
