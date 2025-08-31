/**
 * 简化版认证服务
 * 使用API适配器与Rust后端通信
 */

import { apiAdapter, ApiAdapter } from './ApiAdapter'
import { AuthValidator } from './AuthValidator'
import { ErrorHandler } from './ErrorHandler'
import { TokenManager } from './TokenManager'
import {
    AuthConfig,
    AuthResponse,
    AuthState,
    LoginCredentials,
    User
} from './types'

export class AuthServiceSimplified {
  private readonly tokenManager: TokenManager
  private readonly validator: AuthValidator
  private currentState: AuthState

  constructor(config: AuthConfig) {
    // 初始化组件
    this.tokenManager = new TokenManager(config.token)
    this.validator = new AuthValidator(config.password)

    // 初始化状态
    this.currentState = {
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      lastActivity: null
    }

    // 迁移旧版本Token
    this.tokenManager.migrateFromLegacyStorage()
  }

  /**
   * 用户登录
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      this.updateState({ isLoading: true, error: null })

      // 验证输入数据
      const validation = this.validator.validateLoginCredentials(credentials)
      if (!validation.isValid) {
        const errorMessage = Object.values(validation.errors).join(', ')
        throw new Error(errorMessage)
      }

      // 发送登录请求到Rust后端
      const response = await apiAdapter.login(
        this.validator.sanitizeInput(credentials.identifier),
        credentials.password
      )

      // 处理响应
      if (ApiAdapter.isSuccessResponse(response)) {
        const rustUser = response.data.user
        const token = response.data.token

        // 转换用户信息格式
        const user = ApiAdapter.transformUserInfo(rustUser)

        // 存储Token (Rust后端目前不返回refresh token)
        this.tokenManager.storeTokens(
          token,
          undefined, // 暂时没有refresh token
          3600, // 默认1小时过期
          credentials.rememberMe
        )

        // 更新状态
        this.updateState({
          user,
          token,
          refreshToken: null,
          isAuthenticated: true,
          isLoading: false,
          error: null
        })

        this.updateLastActivity()

        return {
          success: true,
          data: { user, token, refreshToken: undefined, expiresIn: 3600 }
        }
      } else {
        throw new Error(response.message || '登录失败')
      }

    } catch (error: any) {
      const errorMessage = ErrorHandler.handleApiError(error)

      this.updateState({
        isLoading: false,
        error: errorMessage,
        isAuthenticated: false,
        user: null,
        token: null,
        refreshToken: null
      })

      // 记录错误
      ErrorHandler.logError(
        ErrorHandler.createAuthError('LOGIN_FAILED', errorMessage),
        { credentials: { identifier: credentials.identifier } }
      )

      return {
        success: false,
        message: errorMessage
      }
    }
  }

  /**
   * 用户登出
   */
  async logout(): Promise<void> {
    try {
      // 发送登出请求（如果有Token的话）
      if (this.tokenManager.getAccessToken()) {
        await apiAdapter.logout()
      }
    } catch (error) {
      // 登出请求失败也要清除本地状态
      console.warn('登出请求失败，但将继续清除本地状态', error)
    } finally {
      this.clearAuthState()
    }
  }

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<User> {
    try {
      this.updateState({ isLoading: true })

      const response = await apiAdapter.getCurrentUser()

      if (ApiAdapter.isSuccessResponse(response)) {
        const user = ApiAdapter.transformUserInfo(response.data)

        this.updateState({
          user,
          isAuthenticated: true,
          isLoading: false,
          error: null
        })

        this.updateLastActivity()
        return user
      } else {
        throw new Error(response.message || '获取用户信息失败')
      }

    } catch (error: any) {
      const errorMessage = ErrorHandler.handleApiError(error)

      // 如果是认证错误，清除状态
      if (ErrorHandler.requiresReauth(error)) {
        this.clearAuthState()
      } else {
        this.updateState({
          isLoading: false,
          error: errorMessage
        })
      }

      throw new Error(errorMessage)
    }
  }

  /**
   * 检查登录状态
   */
  async checkAuthStatus(): Promise<boolean> {
    const token = this.tokenManager.getAccessToken()

    if (!token) {
      this.clearAuthState()
      return false
    }

    if (!this.tokenManager.isTokenValid()) {
      // Token无效，清除状态
      console.warn('Token已过期，清除认证状态')
      this.clearAuthState()
      return false
    }

    // Token有效，但需要验证用户信息
    try {
      await this.getCurrentUser()
      return true
    } catch (error) {
      console.warn('获取用户信息失败:', error)
      this.clearAuthState()
      return false
    }
  }

  /**
   * 修改密码
   */
  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    // 验证新密码
    const validation = this.validator.validatePassword(newPassword)
    if (!validation.isValid) {
      throw new Error(validation.message)
    }

    try {
      const response = await apiAdapter.changePassword(oldPassword, newPassword)

      if (!response.success) {
        throw new Error(response.message || '修改密码失败')
      }
    } catch (error: any) {
      throw new Error(ErrorHandler.handleApiError(error))
    }
  }

  /**
   * 获取当前认证状态
   */
  getAuthState(): AuthState {
    return { ...this.currentState }
  }

  /**
   * 更新状态
   */
  private updateState(updates: Partial<AuthState>): void {
    this.currentState = { ...this.currentState, ...updates }
  }

  /**
   * 清除认证状态
   */
  private clearAuthState(): void {
    this.tokenManager.clearTokens()
    this.updateState({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      error: null
    })
  }

  /**
   * 更新最后活跃时间
   */
  private updateLastActivity(): void {
    this.updateState({ lastActivity: Date.now() })
  }

  /**
   * 销毁服务实例
   */
  destroy(): void {
    this.clearAuthState()
  }
}
