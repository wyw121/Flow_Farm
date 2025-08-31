/**
 * 认证系统配置
 * 基于环境变量和默认值的统一配置
 */

import { AuthConfig } from './types'

// 获取环境变量，提供默认值
const getEnvVar = (key: string, defaultValue: string): string => {
  return import.meta.env[key] || defaultValue
}

const getEnvNumber = (key: string, defaultValue: number): number => {
  const value = import.meta.env[key]
  return value ? parseInt(value, 10) : defaultValue
}

const getEnvBoolean = (key: string, defaultValue: boolean): boolean => {
  const value = import.meta.env[key]
  return value ? value.toLowerCase() === 'true' : defaultValue
}

// 认证系统配置
export const authConfig: AuthConfig = {
  apiBaseUrl: getEnvVar('VITE_API_BASE_URL', 'http://localhost:8000'),

  endpoints: {
    login: '/api/v1/auth/login',
    logout: '/api/v1/auth/logout',
    refresh: '/api/v1/auth/refresh',
    profile: '/api/v1/auth/me',
    changePassword: '/api/v1/auth/change-password'
  },

  token: {
    accessTokenExpiry: getEnvNumber('VITE_ACCESS_TOKEN_EXPIRY', 3600), // 1小时
    refreshTokenExpiry: getEnvNumber('VITE_REFRESH_TOKEN_EXPIRY', 86400 * 7), // 7天
    issuer: getEnvVar('VITE_JWT_ISSUER', 'flow-farm'),
    audience: getEnvVar('VITE_JWT_AUDIENCE', 'flow-farm-users')
  },

  session: {
    maxInactiveTime: getEnvNumber('VITE_MAX_INACTIVE_TIME', 60), // 60分钟
    enableRememberMe: getEnvBoolean('VITE_ENABLE_REMEMBER_ME', true),
    rememberMeDuration: getEnvNumber('VITE_REMEMBER_ME_DURATION', 30) // 30天
  },

  security: {
    maxLoginAttempts: getEnvNumber('VITE_MAX_LOGIN_ATTEMPTS', 5),
    lockoutDuration: getEnvNumber('VITE_LOCKOUT_DURATION', 15), // 15分钟
    enableTwoFactor: getEnvBoolean('VITE_ENABLE_2FA', false),
    enableDeviceTracking: getEnvBoolean('VITE_ENABLE_DEVICE_TRACKING', true)
  },

  password: {
    minLength: getEnvNumber('VITE_PASSWORD_MIN_LENGTH', 6),
    requireUppercase: getEnvBoolean('VITE_PASSWORD_REQUIRE_UPPERCASE', false),
    requireLowercase: getEnvBoolean('VITE_PASSWORD_REQUIRE_LOWERCASE', false),
    requireNumbers: getEnvBoolean('VITE_PASSWORD_REQUIRE_NUMBERS', false),
    requireSpecialChars: getEnvBoolean('VITE_PASSWORD_REQUIRE_SPECIAL', false)
  }
}

// 开发环境配置覆盖
if (import.meta.env.MODE === 'development') {
  // 开发环境可以使用更宽松的密码策略
  authConfig.password = {
    ...authConfig.password,
    minLength: 6,
    requireUppercase: false,
    requireLowercase: false,
    requireNumbers: false,
    requireSpecialChars: false
  }

  // 开发环境禁用设备跟踪
  authConfig.security.enableDeviceTracking = false
}

// 生产环境配置覆盖
if (import.meta.env.MODE === 'production') {
  // 生产环境使用更严格的安全策略
  authConfig.security = {
    ...authConfig.security,
    maxLoginAttempts: 3,
    lockoutDuration: 30 // 30分钟锁定
  }

  // 生产环境使用更强的密码策略
  authConfig.password = {
    ...authConfig.password,
    minLength: 8,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecialChars: true
  }
}
