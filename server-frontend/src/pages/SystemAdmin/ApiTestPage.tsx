import { Alert, Button, Card, Divider, Spin, Typography } from 'antd'
import React, { useEffect, useState } from 'react'
import { billingService } from '../../services/billingService'
import { userService } from '../../services/userService'

const { Title, Text } = Typography

interface ApiTestResult {
  name: string
  status: 'success' | 'error' | 'loading'
  data?: any
  error?: string
}

const ApiTestPage: React.FC = () => {
  const [tests, setTests] = useState<ApiTestResult[]>([])

  const runTest = async (name: string, testFn: () => Promise<any>) => {
    setTests(prev => [...prev.filter(t => t.name !== name), { name, status: 'loading' }])

    try {
      const data = await testFn()
      setTests(prev => [...prev.filter(t => t.name !== name), {
        name,
        status: 'success',
        data: JSON.stringify(data, null, 2)
      }])
    } catch (error: any) {
      setTests(prev => [...prev.filter(t => t.name !== name), {
        name,
        status: 'error',
        error: error.message || '未知错误'
      }])
    }
  }

  const runAllTests = () => {
    setTests([])

    // 测试用户API
    runTest('获取用户列表', () => userService.getUsers(1, 10, 'user_admin'))
    runTest('获取公司统计', () => userService.getCompanyStatistics())

    // 测试计费API
    runTest('获取价格规则', () => billingService.getPricingRules())
    runTest('获取计费记录', () => billingService.getBillingRecords(1, 10))
  }

  useEffect(() => {
    runAllTests()
  }, [])

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>API 连接测试</Title>
      <Text type="secondary">
        测试前端与后端API的连接状态
      </Text>

      <Divider />

      <Button type="primary" onClick={runAllTests} style={{ marginBottom: '16px' }}>
        重新测试所有API
      </Button>

      {tests.map(test => (
        <Card key={test.name} style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
            <Title level={4} style={{ margin: 0, marginRight: '8px' }}>
              {test.name}
            </Title>
            {test.status === 'loading' && <Spin size="small" />}
          </div>

          {test.status === 'success' && (
            <Alert
              type="success"
              message="API调用成功"
              description={
                <pre style={{
                  maxHeight: '200px',
                  overflow: 'auto',
                  fontSize: '12px',
                  background: '#f5f5f5',
                  padding: '8px',
                  borderRadius: '4px'
                }}>
                  {test.data}
                </pre>
              }
            />
          )}

          {test.status === 'error' && (
            <Alert
              type="error"
              message="API调用失败"
              description={test.error}
            />
          )}
        </Card>
      ))}
    </div>
  )
}

export default ApiTestPage
