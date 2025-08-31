/**
 * 认证服务主类
 * 统一的认证服务，负责登录、登出、Token管理等核心功能
 */

import axios, { AxiosError, AxiosInstance } from 'axios'
import { apiAdapter, ApiAdapter } from './ApiAdapter'
import { AuthValidator } from './AuthValidator'
import { ErrorHandler } from './ErrorHandler'
import { TokenManager } from './TokenManager'
import {
    ApiResponse,
    AuthConfig,
    AuthResponse,
    AuthState,
    LoginCredentials,
    RefreshTokenResponse,
    User
} from './types'

export class AuthService {
  private readonly api: AxiosInstance
  private readonly tokenManager: TokenManager
  private readonly validator: AuthValidator
  private readonly config: AuthConfig
  private currentState: AuthState

  constructor(config: AuthConfig) {
    this.config = config

    // 初始化API客户端
    this.api = axios.create({
      baseURL: config.apiBaseUrl,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

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

    // 设置拦截器
    this.setupInterceptors()

    // 迁移旧版本Token
    this.tokenManager.migrateFromLegacyStorage()
  }

  /**
   * 设置请求和响应拦截器
   */
  private setupInterceptors(): void {
    // 请求拦截器 - 自动添加Token
    this.api.interceptors.request.use(
      (config) => {
        const authHeader = this.tokenManager.getAuthorizationHeader()
        if (authHeader) {
          config.headers.Authorization = authHeader
        }
        return config
      },
      (error) => Promise.reject(new Error(error.message || '请求失败'))
    )

    // 响应拦截器 - 处理Token过期和错误
    this.api.interceptors.response.use(
      (response) => {
        this.updateLastActivity()
        return response
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as any

        // 处理Token过期，尝试刷新
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          const refreshToken = this.tokenManager.getRefreshToken()
          if (refreshToken) {
            try {
              await this.refreshAccessToken()
              // 重新发送原始请求
              const authHeader = this.tokenManager.getAuthorizationHeader()
              if (authHeader) {
                originalRequest.headers.Authorization = authHeader
              }
              return this.api(originalRequest)
            } catch (refreshError) {
              // 刷新失败，清除Token并跳转到登录页
              console.warn('Token刷新失败:', refreshError)
              this.clearAuthState()
              this.redirectToLogin()
            }
          } else {
            // 没有刷新Token，直接清除状态
            this.clearAuthState()
            this.redirectToLogin()
          }
        }

        return Promise.reject(error)
      }
    )
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
   * 刷新访问Token
   */
  async refreshAccessToken(): Promise<void> {
    const refreshToken = this.tokenManager.getRefreshToken()
    if (!refreshToken) {
      throw new Error('没有刷新Token')
    }

    try {
      const response = await this.api.post<ApiResponse<RefreshTokenResponse>>(
        this.config.endpoints.refresh,
        { refresh_token: refreshToken }
      )

      if (response.data.success && response.data.data) {
        const { token, expiresIn } = response.data.data
        this.tokenManager.updateAccessToken(token, expiresIn)

        this.updateState({
          token,
          error: null
        })
      } else {
        throw new Error(response.data.message || 'Token刷新失败')
      }

    } catch (error: any) {
      // 刷新失败，清除所有Token
      this.clearAuthState()
      throw new Error(ErrorHandler.handleApiError(error))
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
      // Token无效，尝试刷新
      try {
        await this.refreshAccessToken()
        return true
      } catch (error) {
        console.warn('Token刷新失败:', error)
        this.clearAuthState()
        return false
      }
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
   * 跳转到登录页
   */
  private redirectToLogin(): void {
    // 避免在已经在登录页时重复跳转
    if (window.location.pathname !== '/login') {
      window.location.href = '/login'
    }
  }

  /**
   * 销毁服务实例
   */
  destroy(): void {
    this.clearAuthState()
  }
}
