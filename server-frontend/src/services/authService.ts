import { LoginRequest, LoginResponse, User } from '../types'
import { apiClient } from './api'

export const authService = {
  async login(loginData: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post('/api/v1/auth/login', loginData)
    return response.data
  },

  async logout(): Promise<void> {
    await apiClient.post('/api/v1/auth/logout')
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get('/api/v1/auth/me')
    return response.data
  },

  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    await apiClient.post('/api/v1/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    })
  },
}
