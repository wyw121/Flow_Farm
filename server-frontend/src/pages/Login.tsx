import { LockOutlined, UserOutlined } from '@ant-design/icons'
import { Alert, Button, Card, Form, Input, Spin, Typography } from 'antd'
import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { AppDispatch, RootState } from '../store'
import { clearAuthState, clearError, login } from '../store/authSlice'
import { LoginRequest } from '../types'

const { Title } = Typography

const Login: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>()
  const { loading, error } = useSelector((state: RootState) => state.auth)

  useEffect(() => {
    // 进入登录页面时，清除之前的所有认证状态和错误
    dispatch(clearAuthState())
    dispatch(clearError())
  }, [dispatch])

  const onFinish = (values: LoginRequest) => {
    dispatch(login(values))
  }

  // 验证用户名/邮箱/手机号格式
  const validateLoginField = (_: any, value: string) => {
    if (!value) {
      return Promise.reject(new Error('请输入用户名、邮箱或手机号!'))
    }

    if (value.length < 3) {
      return Promise.reject(new Error('至少3个字符!'))
    }

    // 邮箱格式验证
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    // 手机号格式验证（中国手机号）
    const phoneRegex = /^1[3-9]\d{9}$/

    // 如果是邮箱或手机号格式，直接通过
    if (emailRegex.test(value) || phoneRegex.test(value)) {
      return Promise.resolve()
    }

    // 如果不是邮箱或手机号，检查是否是有效的用户名
    // 用户名可以包含字母、数字、下划线、中文字符
    if (value.length >= 3) {
      return Promise.resolve()
    }

    return Promise.reject(new Error('请输入有效的用户名、邮箱或手机号!'))
  }

  return (
    <div className="login-container">
      <Card className="login-form">
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <Title level={2}>Flow Farm 管理系统</Title>
          <p style={{ color: '#666' }}>支持用户名、邮箱或手机号登录</p>
        </div>

        {error && (
          <Alert
            message="登录失败"
            description={error}
            type="error"
            showIcon
            style={{ marginBottom: '1rem' }}
            closable
            onClose={() => dispatch(clearError())}
          />
        )}

        <Form
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[
              { validator: validateLoginField },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名 / 邮箱 / 手机号"
              disabled={loading}
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码!' },
              { min: 6, message: '密码至少6个字符!' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
              disabled={loading}
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              block
              loading={loading}
              disabled={loading}
            >
              {loading ? <Spin size="small" /> : '登录'}
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center', color: '#666', fontSize: '12px' }}>
          <p>💡 登录方式：用户名、邮箱地址 或 手机号码</p>
          <p>系统管理员请使用管理员账号登录</p>
          <p>用户管理员请使用分配的账号登录</p>
        </div>
      </Card>
    </div>
  )
}

export default Login
