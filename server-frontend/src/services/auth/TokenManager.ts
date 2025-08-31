/**
 * Token管理器
 * 负责JWT Token的存储、验证、刷新和清理
 */

import { TokenConfig } from './types'

export class TokenManager {
  private static readonly STORAGE_KEYS = {
    ACCESS_TOKEN: 'flow_farm_access_token',
    REFRESH_TOKEN: 'flow_farm_refresh_token',
    TOKEN_EXPIRY: 'flow_farm_token_expiry',
    REMEMBER_ME: 'flow_farm_remember_me'
  }

  private config: TokenConfig

  constructor(config: TokenConfig) {
    this.config = config
  }

  /**
   * 存储Token
   */
  storeTokens(accessToken: string, refreshToken?: string, expiresIn?: number, rememberMe = false): void {
    const storage = rememberMe ? localStorage : sessionStorage

    // 存储访问Token
    storage.setItem(TokenManager.STORAGE_KEYS.ACCESS_TOKEN, accessToken)

    // 存储刷新Token
    if (refreshToken) {
      storage.setItem(TokenManager.STORAGE_KEYS.REFRESH_TOKEN, refreshToken)
    }

    // 计算并存储过期时间
    if (expiresIn) {
      const expiryTime = Date.now() + (expiresIn * 1000)
      storage.setItem(TokenManager.STORAGE_KEYS.TOKEN_EXPIRY, expiryTime.toString())
    }

    // 记录是否记住登录状态
    storage.setItem(TokenManager.STORAGE_KEYS.REMEMBER_ME, rememberMe.toString())
  }

  /**
   * 获取访问Token
   */
  getAccessToken(): string | null {
    // 优先从sessionStorage获取，再从localStorage获取
    return sessionStorage.getItem(TokenManager.STORAGE_KEYS.ACCESS_TOKEN) ||
           localStorage.getItem(TokenManager.STORAGE_KEYS.ACCESS_TOKEN)
  }

  /**
   * 获取刷新Token
   */
  getRefreshToken(): string | null {
    return sessionStorage.getItem(TokenManager.STORAGE_KEYS.REFRESH_TOKEN) ||
           localStorage.getItem(TokenManager.STORAGE_KEYS.REFRESH_TOKEN)
  }

  /**
   * 检查Token是否过期
   */
  isTokenExpired(): boolean {
    const expiryTimeStr = sessionStorage.getItem(TokenManager.STORAGE_KEYS.TOKEN_EXPIRY) ||
                         localStorage.getItem(TokenManager.STORAGE_KEYS.TOKEN_EXPIRY)

    if (!expiryTimeStr) return true

    const expiryTime = parseInt(expiryTimeStr, 10)
    const now = Date.now()

    // 提前5分钟视为过期，给刷新留出时间
    return now >= (expiryTime - 5 * 60 * 1000)
  }

  /**
   * 检查Token是否存在且有效
   */
  isTokenValid(): boolean {
    const token = this.getAccessToken()
    return !!token && !this.isTokenExpired()
  }

  /**
   * 解析JWT Token载荷（不验证签名，仅用于前端显示）
   */
  parseTokenPayload(token?: string): any {
    const targetToken = token || this.getAccessToken()
    if (!targetToken) return null

    try {
      const parts = targetToken.split('.')
      if (parts.length !== 3) return null

      const payload = parts[1]
      const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
      return JSON.parse(decoded)
    } catch (error) {
      console.error('Token解析失败:', error)
      return null
    }
  }

  /**
   * 获取Token中的用户信息
   */
  getTokenUserInfo(): any {
    const payload = this.parseTokenPayload()
    if (!payload) return null

    return {
      userId: payload.sub || payload.user_id,
      username: payload.username,
      role: payload.role,
      companyId: payload.company_id,
      exp: payload.exp,
      iat: payload.iat
    }
  }

  /**
   * 更新访问Token
   */
  updateAccessToken(accessToken: string, expiresIn?: number): void {
    const rememberMe = this.isRememberMeEnabled()
    const storage = rememberMe ? localStorage : sessionStorage

    storage.setItem(TokenManager.STORAGE_KEYS.ACCESS_TOKEN, accessToken)

    if (expiresIn) {
      const expiryTime = Date.now() + (expiresIn * 1000)
      storage.setItem(TokenManager.STORAGE_KEYS.TOKEN_EXPIRY, expiryTime.toString())
    }
  }

  /**
   * 清除所有Token
   */
  clearTokens(): void {
    // 清除sessionStorage中的Token
    Object.values(TokenManager.STORAGE_KEYS).forEach(key => {
      sessionStorage.removeItem(key)
      localStorage.removeItem(key)
    })

    // 清除旧版本的Token（兼容性处理）
    localStorage.removeItem('token')
    sessionStorage.removeItem('token')
  }

  /**
   * 检查是否启用了记住我
   */
  isRememberMeEnabled(): boolean {
    const rememberMe = sessionStorage.getItem(TokenManager.STORAGE_KEYS.REMEMBER_ME) ||
                      localStorage.getItem(TokenManager.STORAGE_KEYS.REMEMBER_ME)
    return rememberMe === 'true'
  }

  /**
   * 获取Token剩余有效时间（秒）
   */
  getTokenRemainingTime(): number {
    const expiryTimeStr = sessionStorage.getItem(TokenManager.STORAGE_KEYS.TOKEN_EXPIRY) ||
                         localStorage.getItem(TokenManager.STORAGE_KEYS.TOKEN_EXPIRY)

    if (!expiryTimeStr) return 0

    const expiryTime = parseInt(expiryTimeStr, 10)
    const now = Date.now()
    const remaining = Math.max(0, Math.floor((expiryTime - now) / 1000))

    return remaining
  }

  /**
   * 检查是否需要刷新Token
   */
  shouldRefreshToken(): boolean {
    const remainingTime = this.getTokenRemainingTime()
    // 当Token剩余时间少于15分钟时，尝试刷新
    return remainingTime > 0 && remainingTime < (15 * 60)
  }

  /**
   * 从旧版本迁移Token
   */
  migrateFromLegacyStorage(): void {
    const legacyToken = localStorage.getItem('token')
    if (legacyToken && !this.getAccessToken()) {
      // 迁移到新的存储格式
      localStorage.setItem(TokenManager.STORAGE_KEYS.ACCESS_TOKEN, legacyToken)
      localStorage.removeItem('token')

      console.info('已迁移旧版本Token到新格式')
    }
  }

  /**
   * 验证Token格式
   */
  isValidTokenFormat(token: string): boolean {
    if (!token || typeof token !== 'string') return false

    // JWT Token应该有三个部分，用.分隔
    const parts = token.split('.')
    return parts.length === 3
  }

  /**
   * 创建Authorization头
   */
  getAuthorizationHeader(): string | null {
    const token = this.getAccessToken()
    return token ? `Bearer ${token}` : null
  }
}
