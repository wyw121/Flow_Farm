import { BillingRecord, PaginatedResponse, PricingRule } from '../types'
import { apiClient } from './api'
import { callApiWithFallback, callPaginatedApiWithFallback } from './apiAdapter'

export const billingService = {
  // 获取计费记录
  async getBillingRecords(
    page: number = 1,
    size: number = 10,
    userId?: number
  ): Promise<PaginatedResponse<BillingRecord>> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: size.toString(),  // 适配Rust后端
    })

    if (userId) params.append('user_id', userId.toString())

    return callPaginatedApiWithFallback<BillingRecord>(
      () => apiClient.get(`/api/v1/billing/records?${params}`),
      page,
      size,
      () => {
        // 备用Python API调用
        const params2 = new URLSearchParams({
          page: page.toString(),
          size: size.toString(),
        })
        if (userId) params2.append('user_id', userId.toString())
        return apiClient.get(`/api/v1/billing/billing-records/?${params2}`)
      }
    )
  },

  // 获取价格规则
  async getPricingRules(): Promise<PricingRule[]> {
    return callApiWithFallback<PricingRule[]>(
      () => apiClient.get('/api/v1/billing/pricing-rules'),
      () => apiClient.get('/api/v1/billing/pricing-rules/')
    )
  },

  // 创建价格规则
  async createPricingRule(ruleData: Omit<PricingRule, 'id' | 'created_at' | 'updated_at'>): Promise<PricingRule> {
    const response = await apiClient.post('/api/v1/billing/pricing-rules', ruleData)
    if (response.data.success) {
      return response.data.data
    } else {
      throw new Error(response.data.message || '创建价格规则失败')
    }
  },

  // 更新价格规则
  async updatePricingRule(ruleId: number, ruleData: Partial<PricingRule>): Promise<PricingRule> {
    const response = await apiClient.put(`/api/v1/billing/pricing-rules/${ruleId}`, ruleData)
    if (response.data.success) {
      return response.data.data
    } else {
      throw new Error(response.data.message || '更新价格规则失败')
    }
  },

  // 删除价格规则
  async deletePricingRule(ruleId: number): Promise<void> {
    const response = await apiClient.delete(`/api/v1/billing/pricing-rules/${ruleId}`)
    if (!response.data.success) {
      throw new Error(response.data.message || '删除价格规则失败')
    }
  },

  // 计算费用预览
  async calculateBilling(
    userId: number,
    billingType: string,
    quantity: number
  ): Promise<{ unit_price: number; total_amount: number }> {
    const response = await apiClient.post('/api/v1/billing/calculate', {
      user_id: userId,
      billing_type: billingType,
      quantity: quantity,
    })
    return response.data
  },

  // 调整关注数量
  async adjustFollowCount(
    userId: number,
    adjustment: number,
    reason?: string
  ): Promise<BillingRecord> {
    const response = await apiClient.post('/api/v1/billing/adjust-follow-count', {
      user_id: userId,
      adjustment: adjustment,
      reason: reason,
    })
    return response.data
  },

  // 获取用户余额
  async getUserBalance(userId?: number): Promise<number> {
    try {
      const params = userId ? `?user_id=${userId}` : ''
      const response = await apiClient.get(`/api/v1/billing/balance${params}`)
      return response.data.data || 0
    } catch (error) {
      console.warn('获取余额失败，返回默认值:', error)
      return 0
    }
  },

  // 获取我的计费信息（用户管理员）
  async getMyBillingInfo(): Promise<{
    balance: number
    total_spent: number
    employee_count: number
    monthly_fee: number
  }> {
    try {
      console.log('🌐 发送API请求: /api/v1/billing/my-billing-info')
      const response = await apiClient.get('/api/v1/billing/my-billing-info')
      console.log('🌐 API响应成功:', response.data)
      return response.data.data
    } catch (error: any) {
      console.error('🌐 API请求失败:', error)
      console.error('Error status:', error.response?.status)
      console.error('Error data:', error.response?.data)
      return {
        balance: 0,
        total_spent: 0,
        employee_count: 0,
        monthly_fee: 300
      }
    }
  },

  // 获取指定用户的计费信息（系统管理员专用）
  async getUserBillingInfo(userId: number): Promise<{
    balance: number
    total_spent: number
    employee_count: number
    monthly_fee: number
  }> {
    try {
      const response = await apiClient.get(`/api/v1/billing/user-billing-info/${userId}`)
      return response.data.data
    } catch (error) {
      console.warn('获取用户计费信息失败:', error)
      return {
        balance: 0,
        total_spent: 0,
        employee_count: 0,
        monthly_fee: 300
      }
    }
  },
}
