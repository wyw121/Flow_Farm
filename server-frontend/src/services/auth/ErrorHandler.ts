/**
 * 统一错误处理器
 * 处理所有认证相关的错误，提供统一的错误消息和用户友好的提示
 */

import { AuthError } from './types'

export class ErrorHandler {
  private static readonly ERROR_MESSAGES: Record<string, string> = {
    // 网络错误
    'NETWORK_ERROR': '网络连接失败，请检查网络连接',
    'TIMEOUT_ERROR': '请求超时，请稍后重试',
    'SERVER_ERROR': '服务器错误，请稍后重试',

    // 认证错误
    'INVALID_CREDENTIALS': '用户名或密码错误',
    'ACCOUNT_LOCKED': '账户已被锁定，请联系管理员',
    'ACCOUNT_SUSPENDED': '账户已被暂停，请联系管理员',
    'TOKEN_EXPIRED': '登录已过期，请重新登录',
    'TOKEN_INVALID': '登录状态无效，请重新登录',
    'UNAUTHORIZED': '没有访问权限',
    'FORBIDDEN': '权限不足',

    // 验证错误
    'VALIDATION_ERROR': '输入数据格式错误',
    'PASSWORD_TOO_WEAK': '密码强度不足',
    'USERNAME_REQUIRED': '请输入用户名',
    'PASSWORD_REQUIRED': '请输入密码',
    'EMAIL_INVALID': '邮箱格式不正确',
    'PHONE_INVALID': '手机号格式不正确',

    // 业务错误
    'USER_NOT_FOUND': '用户不存在',
    'USER_ALREADY_EXISTS': '用户已存在',
    'PERMISSION_DENIED': '操作权限不足',
    'COMPANY_LIMIT_EXCEEDED': '公司用户数量已达上限',

    // 系统错误
    'INTERNAL_ERROR': '系统内部错误',
    'DATABASE_ERROR': '数据库连接错误',
    'CONFIG_ERROR': '系统配置错误'
  }

  /**
   * 处理API错误响应
   */
  static handleApiError(error: any): string {
    // 处理网络错误
    if (!error.response) {
      if (error.code === 'ECONNABORTED') {
        return this.ERROR_MESSAGES.TIMEOUT_ERROR
      }
      return this.ERROR_MESSAGES.NETWORK_ERROR
    }

    const response = error.response
    const status = response.status
    const data = response.data

    // 处理HTTP状态码
    switch (status) {
      case 400:
        return this.handleBadRequest(data)
      case 401:
        return this.ERROR_MESSAGES.UNAUTHORIZED
      case 403:
        return this.ERROR_MESSAGES.FORBIDDEN
      case 404:
        return this.ERROR_MESSAGES.USER_NOT_FOUND
      case 422:
        return this.handleValidationError(data)
      case 429:
        return '请求过于频繁，请稍后重试'
      case 500:
        return this.ERROR_MESSAGES.SERVER_ERROR
      case 502:
      case 503:
      case 504:
        return '服务暂时不可用，请稍后重试'
      default:
        return this.handleUnknownError(data)
    }
  }

  /**
   * 处理400错误
   */
  private static handleBadRequest(data: any): string {
    if (typeof data === 'string') {
      return data
    }

    if (data?.message) {
      return data.message
    }

    if (data?.error) {
      return data.error
    }

    return this.ERROR_MESSAGES.VALIDATION_ERROR
  }

  /**
   * 处理422验证错误
   */
  private static handleValidationError(data: any): string {
    // 处理Rust后端的验证错误格式
    if (data?.message) {
      return data.message
    }

    // 处理FastAPI格式的验证错误
    if (data?.detail && Array.isArray(data.detail)) {
      const errors = data.detail.map((err: any) => {
        if (err.msg) return err.msg
        if (err.message) return err.message
        return '字段验证失败'
      })
      return errors.join(', ')
    }

    // 处理字符串格式的错误
    if (typeof data?.detail === 'string') {
      return data.detail
    }

    return this.ERROR_MESSAGES.VALIDATION_ERROR
  }

  /**
   * 处理未知错误
   */
  private static handleUnknownError(data: any): string {
    if (typeof data === 'string') {
      return data
    }

    if (data?.message) {
      return data.message
    }

    if (data?.error) {
      return data.error
    }

    return this.ERROR_MESSAGES.INTERNAL_ERROR
  }

  /**
   * 创建认证错误对象
   */
  static createAuthError(code: string, message?: string, field?: string): AuthError {
    return {
      code,
      message: message || this.ERROR_MESSAGES[code] || '未知错误',
      field,
      details: {
        timestamp: new Date().toISOString()
      }
    }
  }

  /**
   * 判断是否为认证相关错误
   */
  static isAuthError(error: any): boolean {
    if (!error.response) return false

    const status = error.response.status
    return status === 401 || status === 403
  }

  /**
   * 判断是否需要重新登录
   */
  static requiresReauth(error: any): boolean {
    if (!error.response) return false

    const status = error.response.status
    const data = error.response.data

    // 401错误或Token过期
    if (status === 401) return true

    // 检查具体的错误代码
    if (data?.code === 'TOKEN_EXPIRED' || data?.code === 'TOKEN_INVALID') {
      return true
    }

    return false
  }

  /**
   * 记录错误日志（生产环境中应该发送到日志服务）
   */
  static logError(error: AuthError, context?: Record<string, any>): void {
    const logData = {
      error,
      context,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    }

    // 开发环境下输出到控制台
    if (process.env.NODE_ENV === 'development') {
      console.error('[Auth Error]', logData)
    }

    // 生产环境中应该发送到日志服务
    // 这里可以添加发送到远程日志服务的逻辑
  }
}
