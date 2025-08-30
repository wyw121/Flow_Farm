import {
    DollarOutlined,
    DownloadOutlined,
    EditOutlined
} from '@ant-design/icons'
import {
    Alert,
    Button,
    Card,
    Col,
    DatePicker,
    Divider,
    Form,
    InputNumber,
    message,
    Modal,
    Row,
    Select,
    Space,
    Statistic,
    Table,
    Tag,
    Typography,
} from 'antd'
import dayjs from 'dayjs'
import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { billingService } from '../../services/billingService'
import { RootState } from '../../store'
import { BillingRecord, PricingRule } from '../../types'

const { Title, Text } = Typography
const { Option } = Select
const { RangePicker } = DatePicker

const BillingManagement: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth)
  const [billingRecords, setBillingRecords] = useState<BillingRecord[]>([])
  const [pricingRules, setPricingRules] = useState<PricingRule[]>([])
  const [loading, setLoading] = useState(false)
  const [adjustModalVisible, setAdjustModalVisible] = useState(false)
  const [previewModalVisible, setPreviewModalVisible] = useState(false)
  const [previewData, setPreviewData] = useState<any>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    loadBillingData()
    loadPricingRules()
  }, [])

  const loadBillingData = async () => {
    try {
      setLoading(true)
      const response = await billingService.getBillingRecords(1, 100, user?.id)
      setBillingRecords(response.items)
    } catch (error: any) {
      message.error('加载计费记录失败：' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const loadPricingRules = async () => {
    try {
      const rules = await billingService.getPricingRules()
      setPricingRules(rules.filter(rule => rule.is_active))
    } catch (error: any) {
      message.error('加载价格规则失败：' + error.message)
    }
  }

  const handleAdjustFollowCount = () => {
    form.resetFields()
    setAdjustModalVisible(true)
  }

  const handlePreviewCalculation = async (values: any) => {
    try {
      const preview = await billingService.calculateBilling(
        user?.id || 0,
        values.billing_type,
        values.quantity
      )
      setPreviewData({
        ...values,
        ...preview,
      })
      setPreviewModalVisible(true)
    } catch (error: any) {
      message.error('计算预览失败：' + error.message)
    }
  }

  const handleSubmitAdjustment = async (values: any) => {
    try {
      await billingService.adjustFollowCount(
        user?.id || 0,
        values.adjustment,
        values.reason
      )
      message.success('调整成功')
      setAdjustModalVisible(false)
      loadBillingData()
    } catch (error: any) {
      message.error('调整失败：' + error.message)
    }
  }

  const columns = [
    {
      title: '计费类型',
      dataIndex: 'billing_type',
      key: 'billing_type',
      render: (type: string) => {
        const typeMap: Record<string, { text: string; color: string }> = {
          employee_count: { text: '员工数计费', color: 'blue' },
          follow_count: { text: '关注数计费', color: 'green' },
        }
        const config = typeMap[type] || { text: type, color: 'default' }
        return <Tag color={config.color}>{config.text}</Tag>
      },
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
    },
    {
      title: '单价 (¥)',
      dataIndex: 'unit_price',
      key: 'unit_price',
      render: (price: number) => `¥${price.toFixed(2)}`,
    },
    {
      title: '总金额 (¥)',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (amount: number) => `¥${amount.toFixed(2)}`,
    },
    {
      title: '计费周期',
      key: 'billing_period',
      render: (record: BillingRecord) => {
        if (record.period_start && record.period_end) {
          return (
            <div>
              <div>{dayjs(record.period_start).format('YYYY-MM-DD')}</div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                至 {dayjs(record.period_end).format('YYYY-MM-DD')}
              </div>
            </div>
          )
        }
        return record.billing_period
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap: Record<string, { text: string; color: string }> = {
          pending: { text: '待付款', color: 'orange' },
          paid: { text: '已付款', color: 'green' },
          overdue: { text: '逾期', color: 'red' },
        }
        const config = statusMap[status] || { text: status, color: 'default' }
        return <Tag color={config.color}>{config.text}</Tag>
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
  ]

  const totalAmount = billingRecords.reduce((sum, record) => sum + record.total_amount, 0)
  const unpaidAmount = billingRecords
    .filter(record => record.status === 'pending')
    .reduce((sum, record) => sum + record.total_amount, 0)
  const paidAmount = billingRecords
    .filter(record => record.status === 'paid')
    .reduce((sum, record) => sum + record.total_amount, 0)

  return (
    <div>
      <div className="page-header">
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={2}>费用结算</Title>
            <p>查看和管理您的计费信息</p>
          </Col>
          <Col>
            <Space>
              <Button
                icon={<EditOutlined />}
                onClick={handleAdjustFollowCount}
              >
                调整关注数
              </Button>
              <Button
                icon={<DownloadOutlined />}
                onClick={() => {/* TODO: 导出账单 */}}
              >
                导出账单
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* 费用概览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '2rem' }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="总费用"
              value={totalAmount}
              precision={2}
              prefix="¥"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="已付款"
              value={paidAmount}
              precision={2}
              prefix="¥"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="待付款"
              value={unpaidAmount}
              precision={2}
              prefix="¥"
              valueStyle={{ color: unpaidAmount > 0 ? '#ff4d4f' : '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 当前价格规则 */}
      {pricingRules.length > 0 && (
        <Card title="当前收费标准" style={{ marginBottom: '2rem' }}>
          <Row gutter={[16, 16]}>
            {pricingRules.map(rule => (
              <Col xs={24} sm={12} lg={6} key={rule.id}>
                <Card size="small" style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '8px' }}>
                    {rule.name}
                  </div>
                  <div style={{ fontSize: '24px', color: '#1890ff', fontWeight: 'bold' }}>
                    ¥{rule.unit_price}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {rule.rule_type === 'employee_count' ? '每员工' : '每关注'}
                    /{rule.billing_period === 'monthly' ? '月' : rule.billing_period === 'yearly' ? '年' : '次'}
                  </div>
                  {rule.description && (
                    <div style={{ fontSize: '12px', color: '#999', marginTop: '8px' }}>
                      {rule.description}
                    </div>
                  )}
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* 计费记录 */}
      <Card title="计费记录">
        {unpaidAmount > 0 && (
          <Alert
            message="您有未付款账单"
            description={`当前有 ¥${unpaidAmount.toFixed(2)} 的未付款金额，请及时处理。`}
            type="warning"
            showIcon
            style={{ marginBottom: '1rem' }}
          />
        )}

        <Table
          columns={columns}
          dataSource={billingRecords}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>

      {/* 调整关注数模态框 */}
      <Modal
        title="调整关注数量"
        open={adjustModalVisible}
        onCancel={() => setAdjustModalVisible(false)}
        footer={null}
        width={600}
      >
        <Alert
          message="注意"
          description="调整关注数量将影响计费，请谨慎操作。正数表示增加，负数表示减少。"
          type="info"
          showIcon
          style={{ marginBottom: '1rem' }}
        />

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmitAdjustment}
        >
          <Form.Item
            name="adjustment"
            label="调整数量"
            rules={[
              { required: true, message: '请输入调整数量' },
              { type: 'number', message: '请输入有效数字' },
            ]}
          >
            <InputNumber
              placeholder="请输入调整数量（正数增加，负数减少）"
              style={{ width: '100%' }}
            />
          </Form.Item>

          <Form.Item
            name="reason"
            label="调整原因"
            rules={[{ required: true, message: '请输入调整原因' }]}
          >
            <Select placeholder="请选择调整原因">
              <Option value="manual_adjustment">手动调整</Option>
              <Option value="error_correction">错误修正</Option>
              <Option value="refund">退款处理</Option>
              <Option value="bonus">奖励关注</Option>
              <Option value="other">其他原因</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                确认调整
              </Button>
              <Button onClick={() => setAdjustModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 计算预览模态框 */}
      <Modal
        title="费用计算预览"
        open={previewModalVisible}
        onCancel={() => setPreviewModalVisible(false)}
        footer={null}
        width={500}
      >
        {previewData && (
          <div>
            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
              <DollarOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
            </div>

            <div style={{ fontSize: '16px', marginBottom: '1rem' }}>
              <strong>计费详情：</strong>
            </div>

            <div style={{ background: '#f5f5f5', padding: '1rem', borderRadius: '8px' }}>
              <Row justify="space-between" style={{ marginBottom: '8px' }}>
                <Col>计费类型：</Col>
                <Col>
                  {previewData.billing_type === 'employee_count' ? '员工数计费' : '关注数计费'}
                </Col>
              </Row>
              <Row justify="space-between" style={{ marginBottom: '8px' }}>
                <Col>数量：</Col>
                <Col>{previewData.quantity}</Col>
              </Row>
              <Row justify="space-between" style={{ marginBottom: '8px' }}>
                <Col>单价：</Col>
                <Col>¥{previewData.unit_price?.toFixed(2)}</Col>
              </Row>
              <Divider style={{ margin: '12px 0' }} />
              <Row justify="space-between" style={{ fontSize: '18px', fontWeight: 'bold' }}>
                <Col>总金额：</Col>
                <Col style={{ color: '#1890ff' }}>
                  ¥{previewData.total_amount?.toFixed(2)}
                </Col>
              </Row>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default BillingManagement
