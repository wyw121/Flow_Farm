/**
 * 新的登录页面组件
 * 基于最佳实践重新设计，减少冗余日志，提供更好的用户体验
 */

import { EyeInvisibleOutlined, EyeTwoTone, LockOutlined, UserOutlined } from '@ant-design/icons'
import {
    Alert,
    Button,
    Card,
    Checkbox,
    Divider,
    Form,
    Input,
    Progress,
    Space,
    Typography
} from 'antd'
import React, { useCallback, useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { AuthValidator, LoginCredentials, authConfig } from '../services/auth'
import { AppDispatch } from '../store'
import {
    checkLockStatus,
    clearError,
    loginAsync,
    selectAuth,
    selectIsLocked
} from '../store/authSliceNew'
import './LoginNew.css'

const { Title, Text } = Typography

interface LoginForm {
  identifier: string
  password: string
  rememberMe: boolean
}

const LoginNew: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>()
  const { isLoading, error, loginAttempts, lockExpiry } = useSelector(selectAuth)
  const isLocked = useSelector(selectIsLocked)

  const [form] = Form.useForm()
  const [passwordStrength, setPasswordStrength] = useState(0)
  const [lockCountdown, setLockCountdown] = useState(0)

  // 创建验证器实例
  const validator = new AuthValidator(authConfig.password)

  // 检查锁定状态
  useEffect(() => {
    dispatch(checkLockStatus())
  }, [dispatch])

  // 锁定倒计时
  useEffect(() => {
    if (isLocked && lockExpiry) {
      const updateCountdown = () => {
        const now = Date.now()
        const remaining = Math.max(0, Math.ceil((lockExpiry - now) / 1000))
        setLockCountdown(remaining)

        if (remaining === 0) {
          dispatch(checkLockStatus())
        }
      }

      updateCountdown()
      const interval = setInterval(updateCountdown, 1000)

      return () => clearInterval(interval)
    }
  }, [isLocked, lockExpiry, dispatch])

  // 清除错误
  const handleClearError = useCallback(() => {
    dispatch(clearError())
  }, [dispatch])

  // 密码强度检查
  const handlePasswordChange = useCallback((value: string) => {
    if (!value) {
      setPasswordStrength(0)
      return
    }

    let strength = 0

    if (value.length >= 6) strength += 25
    if (/[A-Z]/.test(value)) strength += 25
    if (/[a-z]/.test(value)) strength += 25
    if (/\d/.test(value)) strength += 15
    if (/[!@#$%^&*()_+\-={}";':\\|,.<>?]/.test(value)) strength += 10

    setPasswordStrength(Math.min(100, strength))
  }, [])

  // 密码可见性图标渲染
  const renderPasswordIcon = useCallback((visible: boolean) => {
    return visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />
  }, [])

  // 处理登录
  const handleLogin = useCallback(async (values: LoginForm) => {
    const credentials: LoginCredentials = {
      identifier: values.identifier.trim(),
      password: values.password,
      rememberMe: values.rememberMe
    }

    // 客户端验证
    const validation = validator.validateLoginCredentials(credentials)
    if (!validation.isValid) {
      form.setFields([
        {
          name: 'identifier',
          errors: validation.errors.identifier ? [validation.errors.identifier] : []
        },
        {
          name: 'password',
          errors: validation.errors.password ? [validation.errors.password] : []
        }
      ])
      return
    }

    try {
      await dispatch(loginAsync(credentials)).unwrap()
      // 登录成功会自动跳转，由路由处理
    } catch (error) {
      // 错误已经在Redux中处理了
      console.error('登录失败:', error)
    }
  }, [dispatch, validator, form])

  // 格式化倒计时显示
  const formatCountdown = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  // 获取密码强度颜色
  const getPasswordStrengthColor = (): string => {
    if (passwordStrength < 30) return '#ff4d4f'
    if (passwordStrength < 70) return '#faad14'
    return '#52c41a'
  }

  // 获取密码强度文本
  const getPasswordStrengthText = (): string => {
    if (passwordStrength < 30) return '弱'
    if (passwordStrength < 70) return '中'
    return '强'
  }

  return (
    <div className="login-container">
      <Card className="login-card">
        {/* 标题区域 */}
        <div className="login-header">
          <Title level={2} className="login-title">
            Flow Farm 管理系统
          </Title>
          <Text type="secondary" className="login-subtitle">
            企业级流量管理和自动化平台
          </Text>
        </div>

        <Divider />

        {/* 锁定警告 */}
        {isLocked && (
          <Alert
            message="账户已锁定"
            description={`由于多次登录失败，账户已被锁定。请 ${formatCountdown(lockCountdown)} 后重试。`}
            type="warning"
            showIcon
            style={{ marginBottom: 24 }}
          />
        )}

        {/* 错误信息 */}
        {error && !isLocked && (
          <Alert
            message="登录失败"
            description={error}
            type="error"
            showIcon
            closable
            onClose={handleClearError}
            style={{ marginBottom: 24 }}
          />
        )}

        {/* 登录尝试提示 */}
        {loginAttempts > 0 && !isLocked && (
          <Alert
            message={`登录失败次数：${loginAttempts}/${authConfig.security.maxLoginAttempts}`}
            description={`还有 ${authConfig.security.maxLoginAttempts - loginAttempts} 次机会，超过限制将锁定账户。`}
            type="warning"
            style={{ marginBottom: 24 }}
          />
        )}

        {/* 登录表单 */}
        <Form
          form={form}
          name="login"
          onFinish={handleLogin}
          autoComplete="off"
          size="large"
          layout="vertical"
          disabled={isLocked}
        >
          <Form.Item
            name="identifier"
            label="账户信息"
            rules={[
              { required: true, message: '请输入用户名、邮箱或手机号' },
              { min: 3, message: '至少3个字符' },
              { max: 50, message: '不能超过50个字符' }
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名 / 邮箱 / 手机号"
              autoComplete="username"
            />
          </Form.Item>

          <Form.Item
            name="password"
            label="密码"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6个字符' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="请输入密码"
              autoComplete="current-password"
              iconRender={renderPasswordIcon}
              onChange={(e) => handlePasswordChange(e.target.value)}
            />
          </Form.Item>

          {/* 密码强度指示器 */}
          {passwordStrength > 0 && (
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <Text type="secondary" style={{ fontSize: 12 }}>密码强度</Text>
                <Text
                  style={{
                    fontSize: 12,
                    color: getPasswordStrengthColor(),
                    fontWeight: 500
                  }}
                >
                  {getPasswordStrengthText()}
                </Text>
              </div>
              <Progress
                percent={passwordStrength}
                showInfo={false}
                strokeColor={getPasswordStrengthColor()}
                size="small"
              />
            </div>
          )}

          <Form.Item name="rememberMe" valuePropName="checked">
            <Checkbox>记住我 (30天内保持登录)</Checkbox>
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              block
              loading={isLoading}
              disabled={isLocked}
              size="large"
            >
              {isLoading ? '登录中...' : '登录'}
            </Button>
          </Form.Item>
        </Form>

        <Divider />

        {/* 角色说明 */}
        <div className="login-roles">
          <Title level={5} style={{ marginBottom: 16 }}>系统角色说明</Title>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <div className="role-item">
              <Text strong>系统管理员：</Text>
              <Text type="secondary">管理用户管理员，查看全局数据，配置系统</Text>
            </div>
            <div className="role-item">
              <Text strong>用户管理员：</Text>
              <Text type="secondary">管理员工账户(最多10个)，查看公司数据</Text>
            </div>
            <div className="role-item">
              <Text strong>员工：</Text>
              <Text type="secondary">使用桌面客户端进行设备操作和数据上传</Text>
            </div>
          </Space>
        </div>

        {/* 系统信息 */}
        <div className="login-footer">
          <Text type="secondary" style={{ fontSize: 12 }}>
            Flow Farm v2.0 - 企业级自动化流量管理系统
          </Text>
        </div>
      </Card>
    </div>
  )
}

export default LoginNew
