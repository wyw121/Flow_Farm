import React, { useState, useEffect } from 'react';
import { Card, Button, Input, Select, Table, message, Space, Descriptions, Tag, Modal, Form } from 'antd';
import { PlayCircleOutlined, ReloadOutlined, PlusOutlined, EyeOutlined } from '@ant-design/icons';
import { useSelector } from 'react-redux';
import { RootState } from '../../store/store';

const { TextArea } = Input;
const { Option } = Select;

interface ApiEndpoint {
  id: string;
  name: string;
  method: string;
  url: string;
  description: string;
  requiresAuth: boolean;
  category: string;
}

interface ApiResponse {
  status: number;
  data: any;
  error?: string;
  timestamp: string;
}

const ApiTestPage: React.FC = () => {
  const [selectedEndpoint, setSelectedEndpoint] = useState<string>('');
  const [requestBody, setRequestBody] = useState<string>('');
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [expenseCategories, setExpenseCategories] = useState<any[]>([]);
  const [expenses, setExpenses] = useState<any[]>([]);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [form] = Form.useForm();

  const { token } = useSelector((state: RootState) => state.auth);

  // 费用管理API端点配置
  const expenseEndpoints: ApiEndpoint[] = [
    {
      id: 'get-expense-categories',
      name: '获取费用类别',
      method: 'GET',
      url: '/api/v1/expense-categories',
      description: '获取所有费用类别列表',
      requiresAuth: true,
      category: '费用类别'
    },
    {
      id: 'create-expense-category',
      name: '创建费用类别',
      method: 'POST',
      url: '/api/v1/expense-categories',
      description: '创建新的费用类别',
      requiresAuth: true,
      category: '费用类别'
    },
    {
      id: 'get-expenses',
      name: '获取费用记录',
      method: 'GET',
      url: '/api/v1/expenses',
      description: '获取费用记录列表（支持分页和筛选）',
      requiresAuth: true,
      category: '费用记录'
    },
    {
      id: 'create-expense',
      name: '创建费用记录',
      method: 'POST',
      url: '/api/v1/expenses',
      description: '创建新的费用记录',
      requiresAuth: true,
      category: '费用记录'
    },
    {
      id: 'submit-expense',
      name: '提交费用审批',
      method: 'POST',
      url: '/api/v1/expenses/submit',
      description: '提交费用记录进行审批',
      requiresAuth: true,
      category: '费用审批'
    },
    {
      id: 'approve-expense',
      name: '审批费用',
      method: 'POST',
      url: '/api/v1/expenses/approve',
      description: '审批费用记录（批准或拒绝）',
      requiresAuth: true,
      category: '费用审批'
    },
    {
      id: 'get-expense-statistics',
      name: '费用统计',
      method: 'GET',
      url: '/api/v1/expenses/statistics',
      description: '获取费用统计数据',
      requiresAuth: true,
      category: '费用统计'
    }
  ];

  // 获取费用类别
  const fetchExpenseCategories = async () => {
    try {
      const response = await fetch('/api/v1/expense-categories', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setExpenseCategories(data.data || []);
      }
    } catch (error) {
      console.error('获取费用类别失败:', error);
    }
  };

  // 获取费用记录
  const fetchExpenses = async () => {
    try {
      const response = await fetch('/api/v1/expenses', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setExpenses(data.data || []);
      }
    } catch (error) {
      console.error('获取费用记录失败:', error);
    }
  };

  useEffect(() => {
    if (token) {
      fetchExpenseCategories();
      fetchExpenses();
    }
  }, [token]);

  // 执行API测试
  const executeApiTest = async () => {
    if (!selectedEndpoint) {
      message.warning('请选择要测试的API端点');
      return;
    }

    const endpoint = expenseEndpoints.find(ep => ep.id === selectedEndpoint);
    if (!endpoint) return;

    setLoading(true);
    const startTime = Date.now();

    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };

      if (endpoint.requiresAuth && token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const requestOptions: RequestInit = {
        method: endpoint.method,
        headers
      };

      if (endpoint.method !== 'GET' && requestBody.trim()) {
        try {
          JSON.parse(requestBody); // 验证JSON格式
          requestOptions.body = requestBody;
        } catch (error) {
          message.error('请求体不是有效的JSON格式');
          setLoading(false);
          return;
        }
      }

      const apiResponse = await fetch(endpoint.url, requestOptions);
      const responseData = await apiResponse.json();

      const testResponse: ApiResponse = {
        status: apiResponse.status,
        data: responseData,
        timestamp: new Date().toISOString()
      };

      if (!apiResponse.ok) {
        testResponse.error = `HTTP ${apiResponse.status}: ${apiResponse.statusText}`;
      }

      setResponse(testResponse);
      
      if (apiResponse.ok) {
        message.success(`API测试成功 (${Date.now() - startTime}ms)`);
        // 如果是获取数据的API，更新本地状态
        if (endpoint.id === 'get-expense-categories') {
          setExpenseCategories(responseData.data || []);
        } else if (endpoint.id === 'get-expenses') {
          setExpenses(responseData.data || []);
        }
      } else {
        message.error(`API测试失败: ${testResponse.error}`);
      }
    } catch (error) {
      const testResponse: ApiResponse = {
        status: 0,
        data: null,
        error: error instanceof Error ? error.message : '网络错误',
        timestamp: new Date().toISOString()
      };
      setResponse(testResponse);
      message.error(`API测试失败: ${testResponse.error}`);
    } finally {
      setLoading(false);
    }
  };

  // 获取请求体模板
  const getRequestTemplate = (endpointId: string): string => {
    const templates: Record<string, any> = {
      'create-expense-category': {
        name: "测试类别",
        code: "TEST_CATEGORY",
        description: "这是一个测试费用类别",
        default_limit: 1000.0
      },
      'create-expense': {
        category_id: 1,
        amount: 100.50,
        description: "测试费用记录",
        expense_date: new Date().toISOString().split('T')[0],
        receipt_number: "TEST001"
      },
      'submit-expense': {
        expense_id: 1
      },
      'approve-expense': {
        expense_id: 1,
        approved: true,
        comment: "审批通过"
      }
    };

    return JSON.stringify(templates[endpointId] || {}, null, 2);
  };

  // 处理端点选择变化
  const handleEndpointChange = (endpointId: string) => {
    setSelectedEndpoint(endpointId);
    setRequestBody(getRequestTemplate(endpointId));
    setResponse(null);
  };

  // 快速创建费用记录
  const handleQuickCreateExpense = () => {
    setShowCreateModal(true);
    form.resetFields();
  };

  // 提交快速创建表单
  const handleCreateSubmit = async (values: any) => {
    try {
      const response = await fetch('/api/v1/expenses', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(values)
      });

      if (response.ok) {
        message.success('费用记录创建成功');
        setShowCreateModal(false);
        fetchExpenses();
      } else {
        const errorData = await response.json();
        message.error(`创建失败: ${errorData.message || '未知错误'}`);
      }
    } catch (error) {
      message.error('创建费用记录失败');
    }
  };

  // 费用状态标签
  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      'Draft': { color: 'default', text: '草稿' },
      'Submitted': { color: 'processing', text: '待审批' },
      'Approved': { color: 'success', text: '已批准' },
      'Rejected': { color: 'error', text: '已拒绝' }
    };
    
    const statusInfo = statusMap[status] || { color: 'default', text: status };
    return <Tag color={statusInfo.color}>{statusInfo.text}</Tag>;
  };

  // 费用记录表格列
  const expenseColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60
    },
    {
      title: '类别',
      dataIndex: 'category_name',
      key: 'category_name'
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount: number) => `¥${amount.toFixed(2)}`
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getStatusTag(status)
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString()
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h2>💰 费用管理 API 测试工具</h2>
        <p>测试 Flow Farm 费用管理系统的各项 API 功能</p>
      </div>

      <div style={{ display: 'flex', gap: '24px' }}>
        {/* 左侧API测试区域 */}
        <div style={{ flex: '1' }}>
          <Card 
            title="API 测试" 
            extra={
              <Space>
                <Button 
                  icon={<PlusOutlined />} 
                  onClick={handleQuickCreateExpense}
                  type="dashed"
                >
                  快速创建费用
                </Button>
                <Button 
                  icon={<ReloadOutlined />} 
                  onClick={() => {
                    fetchExpenseCategories();
                    fetchExpenses();
                  }}
                >
                  刷新数据
                </Button>
              </Space>
            }
            style={{ marginBottom: '24px' }}
          >
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                  选择API端点：
                </label>
                <Select
                  style={{ width: '100%' }}
                  placeholder="请选择要测试的API端点"
                  value={selectedEndpoint}
                  onChange={handleEndpointChange}
                  optionFilterProp="children"
                  showSearch
                >
                  {expenseEndpoints.map(endpoint => (
                    <Option key={endpoint.id} value={endpoint.id}>
                      <Tag color="blue">{endpoint.method}</Tag>
                      {endpoint.name} - {endpoint.description}
                    </Option>
                  ))}
                </Select>
              </div>

              {selectedEndpoint && (
                <div>
                  <Descriptions size="small" column={1} bordered>
                    <Descriptions.Item label="方法">
                      <Tag color="blue">{expenseEndpoints.find(ep => ep.id === selectedEndpoint)?.method}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="URL">
                      {expenseEndpoints.find(ep => ep.id === selectedEndpoint)?.url}
                    </Descriptions.Item>
                    <Descriptions.Item label="描述">
                      {expenseEndpoints.find(ep => ep.id === selectedEndpoint)?.description}
                    </Descriptions.Item>
                    <Descriptions.Item label="需要认证">
                      {expenseEndpoints.find(ep => ep.id === selectedEndpoint)?.requiresAuth ? 
                        <Tag color="red">是</Tag> : <Tag color="green">否</Tag>
                      }
                    </Descriptions.Item>
                  </Descriptions>
                </div>
              )}

              {selectedEndpoint && expenseEndpoints.find(ep => ep.id === selectedEndpoint)?.method !== 'GET' && (
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                    请求体 (JSON)：
                  </label>
                  <TextArea
                    rows={8}
                    value={requestBody}
                    onChange={(e) => setRequestBody(e.target.value)}
                    placeholder="输入JSON格式的请求体..."
                  />
                </div>
              )}

              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={executeApiTest}
                loading={loading}
                disabled={!selectedEndpoint}
                size="large"
                style={{ width: '100%' }}
              >
                执行 API 测试
              </Button>
            </Space>
          </Card>

          {/* API响应区域 */}
          {response && (
            <Card title="API 响应结果">
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <strong>状态码:</strong> 
                  <Tag color={response.status === 200 ? 'success' : 'error'}>
                    {response.status}
                  </Tag>
                  <strong>时间:</strong> {new Date(response.timestamp).toLocaleString()}
                </div>
                
                {response.error && (
                  <div>
                    <strong>错误:</strong>
                    <Tag color="error">{response.error}</Tag>
                  </div>
                )}

                <div>
                  <strong>响应数据:</strong>
                  <TextArea
                    rows={12}
                    value={JSON.stringify(response.data, null, 2)}
                    readOnly
                    style={{ marginTop: '8px' }}
                  />
                </div>
              </Space>
            </Card>
          )}
        </div>

        {/* 右侧数据展示区域 */}
        <div style={{ width: '400px' }}>
          {/* 费用类别 */}
          <Card title="费用类别" size="small" style={{ marginBottom: '16px' }}>
            <div style={{ maxHeight: '200px', overflow: 'auto' }}>
              {expenseCategories.map(category => (
                <div key={category.id} style={{ marginBottom: '8px', padding: '8px', border: '1px solid #f0f0f0', borderRadius: '4px' }}>
                  <div><strong>{category.name}</strong> ({category.code})</div>
                  <div style={{ fontSize: '12px', color: '#666' }}>{category.description}</div>
                  <div style={{ fontSize: '12px', color: '#999' }}>限额: ¥{category.default_limit}</div>
                </div>
              ))}
            </div>
          </Card>

          {/* 费用记录 */}
          <Card title="最近费用记录" size="small">
            <Table
              dataSource={expenses.slice(0, 5)}
              columns={expenseColumns}
              pagination={false}
              size="small"
              rowKey="id"
              scroll={{ y: 300 }}
            />
          </Card>
        </div>
      </div>

      {/* 快速创建费用模态框 */}
      <Modal
        title="快速创建费用记录"
        open={showCreateModal}
        onCancel={() => setShowCreateModal(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateSubmit}
        >
          <Form.Item
            label="费用类别"
            name="category_id"
            rules={[{ required: true, message: '请选择费用类别' }]}
          >
            <Select placeholder="选择费用类别">
              {expenseCategories.map(category => (
                <Option key={category.id} value={category.id}>
                  {category.name} (限额: ¥{category.default_limit})
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="金额"
            name="amount"
            rules={[
              { required: true, message: '请输入金额' },
              { type: 'number', min: 0.01, message: '金额必须大于0' }
            ]}
          >
            <Input type="number" step="0.01" placeholder="请输入金额" addonBefore="¥" />
          </Form.Item>

          <Form.Item
            label="描述"
            name="description"
            rules={[{ required: true, message: '请输入费用描述' }]}
          >
            <TextArea rows={3} placeholder="请描述费用用途..." />
          </Form.Item>

          <Form.Item
            label="费用日期"
            name="expense_date"
            rules={[{ required: true, message: '请选择费用日期' }]}
          >
            <Input type="date" />
          </Form.Item>

          <Form.Item
            label="收据编号"
            name="receipt_number"
          >
            <Input placeholder="收据编号（可选）" />
          </Form.Item>

          <Form.Item>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={() => setShowCreateModal(false)}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                创建费用记录
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ApiTestPage;