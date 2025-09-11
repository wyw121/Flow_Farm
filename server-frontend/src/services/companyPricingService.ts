import { CompanyOperationPricing, CompanyPricingPlan } from "../types";
import { apiClient } from "./api";

export const companyPricingService = {
  // 公司收费计划管理

  // 获取所有公司收费计划
  async getCompanyPricingPlans(): Promise<CompanyPricingPlan[]> {
    const response = await apiClient.get("/api/v1/company-pricing/plans");
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.message || "获取公司收费计划失败");
    }
  },

  // 根据公司名获取收费计划
  async getCompanyPricingPlan(
    companyName: string
  ): Promise<CompanyPricingPlan | null> {
    const response = await apiClient.get(
      `/api/v1/company-pricing/plans/by-company/${companyName}`
    );
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.message || "获取公司收费计划失败");
    }
  },

  // 创建公司收费计划
  async createCompanyPricingPlan(planData: {
    company_name: string;
    plan_name: string;
    employee_monthly_fee: number;
  }): Promise<CompanyPricingPlan> {
    const response = await apiClient.post(
      "/api/v1/company-pricing/plans",
      planData
    );
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.message || "创建公司收费计划失败");
    }
  },

  // 更新公司收费计划
  async updateCompanyPricingPlan(
    planId: number,
    planData: {
      plan_name?: string;
      employee_monthly_fee?: number;
      is_active?: boolean;
    }
  ): Promise<CompanyPricingPlan> {
    const response = await apiClient.put(
      `/api/v1/company-pricing/plans/by-id/${planId}`,
      planData
    );
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.message || "更新公司收费计划失败");
    }
  },

  // 删除公司收费计划
  async deleteCompanyPricingPlan(planId: number): Promise<void> {
    const response = await apiClient.delete(
      `/api/v1/company-pricing/plans/by-id/${planId}`
    );
    if (!response.data.success) {
      throw new Error(response.data.message || "删除公司收费计划失败");
    }
  },

  // 公司操作收费规则管理

  // 获取公司操作收费规则
  async getCompanyOperationPricing(
    companyName?: string
  ): Promise<CompanyOperationPricing[]> {
    const params = companyName
      ? `?company_name=${encodeURIComponent(companyName)}`
      : "";
    const response = await apiClient.get(
      `/api/v1/company-pricing/operations${params}`
    );
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.message || "获取公司操作收费规则失败");
    }
  },

  // 创建公司操作收费规则
  async createCompanyOperationPricing(pricingData: {
    company_name: string;
    platform: string;
    operation_type: string;
    unit_price: number;
  }): Promise<CompanyOperationPricing> {
    const response = await apiClient.post(
      "/api/v1/company-pricing/operations",
      pricingData
    );
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.message || "创建公司操作收费规则失败");
    }
  },

  // 更新公司操作收费规则
  async updateCompanyOperationPricing(
    pricingId: number,
    pricingData: {
      unit_price?: number;
      is_active?: boolean;
    }
  ): Promise<CompanyOperationPricing> {
    const response = await apiClient.put(
      `/api/v1/company-pricing/operations/${pricingId}`,
      pricingData
    );
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.message || "更新公司操作收费规则失败");
    }
  },

  // 删除公司操作收费规则
  async deleteCompanyOperationPricing(pricingId: number): Promise<void> {
    const response = await apiClient.delete(
      `/api/v1/company-pricing/operations/${pricingId}`
    );
    if (!response.data.success) {
      throw new Error(response.data.message || "删除公司操作收费规则失败");
    }
  },

  // 查询价格

  // 获取操作价格
  async getOperationPrice(
    companyName: string,
    platform: string,
    operationType: string
  ): Promise<number> {
    const params = new URLSearchParams({
      company_name: companyName,
      platform: platform,
      operation_type: operationType,
    });
    const response = await apiClient.get(
      `/api/v1/company-pricing/operation-price?${params}`
    );
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.message || "获取操作价格失败");
    }
  },

  // 获取员工月费
  async getEmployeeMonthlyFee(companyName: string): Promise<number> {
    const response = await apiClient.get(
      `/api/v1/company-pricing/employee-fee/${companyName}`
    );
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.message || "获取员工月费失败");
    }
  },
};
