/**
 * 认证系统类型定义
 * 遵循TypeScript最佳实践，确保类型安全
 */

// 用户角色枚举
export enum UserRole {
  SYSTEM_ADMIN = 'system_admin',
  USER_ADMIN = 'user_admin',
  EMPLOYEE = 'employee'
}

// 用户状态枚举
export enum UserStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  SUSPENDED = 'suspended'
}

// 登录凭证接口
export interface LoginCredentials {
  identifier: string // 用户名、邮箱或手机号
  password: string
  rememberMe?: boolean
}

// 用户信息接口
export interface User {
  id: number
  username: string
  email?: string
  phone?: string
  role: UserRole
  status: UserStatus
  companyId?: number
  createdAt: string
  lastLoginAt?: string
  permissions?: string[]
}

// 认证响应接口
export interface AuthResponse {
  success: boolean
  data?: {
    user: User
    token: string
    refreshToken?: string
    expiresIn: number
  }
  message?: string
  errors?: AuthError[]
}

// 刷新Token响应
export interface RefreshTokenResponse {
  token: string
  expiresIn: number
}

// 认证状态接口
export interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  lastActivity: number | null
}

// 认证错误接口
export interface AuthError {
  code: string
  message: string
  field?: string
  details?: Record<string, any>
}

// API响应基础结构
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  errors?: AuthError[]
  timestamp?: string
}

// 密码策略配置
export interface PasswordPolicy {
  minLength: number
  requireUppercase: boolean
  requireLowercase: boolean
  requireNumbers: boolean
  requireSpecialChars: boolean
}

// Token配置
export interface TokenConfig {
  accessTokenExpiry: number // 访问token过期时间(秒)
  refreshTokenExpiry: number // 刷新token过期时间(秒)
  issuer: string
  audience: string
}

// 会话配置
export interface SessionConfig {
  maxInactiveTime: number // 最大非活跃时间(分钟)
  enableRememberMe: boolean
  rememberMeDuration: number // 记住我持续时间(天)
}

// 安全配置
export interface SecurityConfig {
  maxLoginAttempts: number
  lockoutDuration: number // 锁定时间(分钟)
  enableTwoFactor: boolean
  enableDeviceTracking: boolean
}

// 认证配置接口
export interface AuthConfig {
  apiBaseUrl: string
  endpoints: {
    login: string
    logout: string
    refresh: string
    profile: string
    changePassword: string
  }
  token: TokenConfig
  session: SessionConfig
  security: SecurityConfig
  password: PasswordPolicy
}
