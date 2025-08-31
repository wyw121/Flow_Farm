import { LoginRequest, LoginResponse, User, ApiResponse } from '../types'
import { apiClient } from './api'

export const authService = {
  async login(loginData: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<ApiResponse<LoginResponse>>('/api/v1/auth/login', loginData)

    // 处理后端的ApiResponse格式
    if (response.data.success && response.data.data) {
      return response.data.data
    } else {
      throw new Error(response.data.message || '登录失败')
    }
  },

  async logout(): Promise<void> {
    await apiClient.post('/api/v1/auth/logout')
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<ApiResponse<User>>('/api/v1/auth/me')

    // 处理后端的ApiResponse格式
    if (response.data.success && response.data.data) {
      return response.data.data
    } else {
      throw new Error(response.data.message || '获取用户信息失败')
    }
  },

  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    await apiClient.post('/api/v1/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    })
  },
}
