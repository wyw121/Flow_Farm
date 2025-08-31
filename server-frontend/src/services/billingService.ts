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
}
