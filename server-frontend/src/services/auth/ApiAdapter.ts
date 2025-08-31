/**
 * API适配器
 * 处理新认证系统与Rust后端API的兼容性
 */

import axios, { AxiosInstance } from 'axios'
import { authConfig } from './config'

// 后端API响应格式
interface RustApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  errors?: Array<{
    code: string
    message: string
    field?: string
  }>
}

// 登录请求格式（Rust后端期望的格式）
interface RustLoginRequest {
  username: string  // 后端期望username字段
  password: string
}

// 登录响应格式（Rust后端返回的格式）
interface RustLoginResponse {
  token: string
  user: {
    id: number
    username: string
    email?: string
    phone?: string
    role: string
    status: string
    company_id?: number
    created_at: string
    last_login_at?: string
  }
}

// 用户信息格式转换
interface RustUserInfo {
  id: number
  username: string
  email?: string
  phone?: string
  role: string
  status: string
  company_id?: number
  created_at: string
  last_login_at?: string
}

export class ApiAdapter {
  private readonly api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: authConfig.apiBaseUrl,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors(): void {
    // 请求拦截器
    this.api.interceptors.request.use(
      (config) => {
        // 添加token - 使用TokenManager的键名
        const token = localStorage.getItem('flow_farm_access_token') ||
                     sessionStorage.getItem('flow_farm_access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(new Error(error.message || '请求失败'))
    )

    // 响应拦截器
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        // 统一错误处理
        if (error.response?.status === 401) {
          // 清除token并跳转登录
          localStorage.removeItem('flow_farm_access_token')
          sessionStorage.removeItem('flow_farm_access_token')
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
        }
        return Promise.reject(new Error(error.message || '网络请求失败'))
      }
    )
  }

  /**
   * 登录API适配
   */
  async login(identifier: string, password: string): Promise<RustApiResponse<RustLoginResponse>> {
    const requestData: RustLoginRequest = {
      username: identifier,  // 后端期望username字段
      password
    }

    try {
      const response = await this.api.post<RustApiResponse<RustLoginResponse>>(
        '/api/v1/auth/login',
        requestData
      )
      return response.data
    } catch (error: any) {
      // 适配错误格式
      if (error.response?.data) {
        return error.response.data
      }
      throw error
    }
  }

  /**
   * 获取当前用户信息API适配
   */
  async getCurrentUser(): Promise<RustApiResponse<RustUserInfo>> {
    try {
      const response = await this.api.get<RustApiResponse<RustUserInfo>>('/api/v1/auth/me')
      return response.data
    } catch (error: any) {
      if (error.response?.data) {
        return error.response.data
      }
      throw error
    }
  }

  /**
   * 登出API适配
   */
  async logout(): Promise<void> {
    try {
      await this.api.post('/api/v1/auth/logout')
    } catch (error) {
      // 登出失败也要清除本地状态
      console.warn('登出请求失败:', error)
    }
  }

  /**
   * 修改密码API适配
   */
  async changePassword(oldPassword: string, newPassword: string): Promise<RustApiResponse> {
    try {
      const response = await this.api.post<RustApiResponse>('/api/v1/auth/change-password', {
        old_password: oldPassword,
        new_password: newPassword
      })
      return response.data
    } catch (error: any) {
      if (error.response?.data) {
        return error.response.data
      }
      throw error
    }
  }

  /**
   * 将Rust后端的用户信息转换为前端格式
   */
  static transformUserInfo(rustUser: RustUserInfo) {
    return {
      id: rustUser.id,
      username: rustUser.username,
      email: rustUser.email,
      phone: rustUser.phone,
      role: rustUser.role as any, // 类型转换
      status: rustUser.status as any,
      companyId: rustUser.company_id,
      createdAt: rustUser.created_at,
      lastLoginAt: rustUser.last_login_at
    }
  }

  /**
   * 检查API响应是否成功
   */
  static isSuccessResponse<T>(response: RustApiResponse<T>): response is RustApiResponse<T> & { data: T } {
    return response.success && response.data !== undefined
  }

  /**
   * 获取API实例（供其他服务使用）
   */
  getApiInstance(): AxiosInstance {
    return this.api
  }
}

// 创建全局实例
export const apiAdapter = new ApiAdapter()
