/**
 * 统一认证服务模块
 * 基于行业最佳实践设计的认证系统
 */

export { apiAdapter } from './ApiAdapter'
export { AuthServiceSimplified as AuthService } from './AuthServiceSimplified'
export { AuthValidator } from './AuthValidator'
export { authConfig } from './config'
export { ErrorHandler } from './ErrorHandler'
export { TokenManager } from './TokenManager'

export type {
    ApiResponse, AuthConfig, AuthError, AuthResponse, AuthState,
    LoginCredentials, RefreshTokenResponse, User, UserRole,
    UserStatus
} from './types'
