import { BillingRecord, PaginatedResponse, PricingRule } from '../types'
import { apiClient } from './api'

export const billingService = {
  // 获取计费记录
  async getBillingRecords(
    page: number = 1,
    size: number = 10,
    userId?: number
  ): Promise<PaginatedResponse<BillingRecord>> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })

    if (userId) params.append('user_id', userId.toString())

    const response = await apiClient.get(`/api/v1/billing/records/?${params}`)
    return response.data
  },

  // 获取价格规则
  async getPricingRules(): Promise<PricingRule[]> {
    const response = await apiClient.get('/api/v1/billing/pricing-rules/')
    return response.data
  },

  // 创建价格规则
  async createPricingRule(ruleData: Omit<PricingRule, 'id' | 'created_at' | 'updated_at'>): Promise<PricingRule> {
    const response = await apiClient.post('/api/v1/billing/pricing-rules/', ruleData)
    return response.data
  },

  // 更新价格规则
  async updatePricingRule(ruleId: number, ruleData: Partial<PricingRule>): Promise<PricingRule> {
    const response = await apiClient.put(`/api/v1/billing/pricing-rules/${ruleId}`, ruleData)
    return response.data
  },

  // 删除价格规则
  async deletePricingRule(ruleId: number): Promise<void> {
    await apiClient.delete(`/api/v1/billing/pricing-rules/${ruleId}`)
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
