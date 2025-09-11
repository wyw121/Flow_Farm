export interface User {
  id: number;
  username: string;
  email?: string;
  full_name?: string;
  phone?: string;
  company?: string; // 重命名自company_id，匹配后端
  role: "system_admin" | "user_admin" | "employee";
  is_active: boolean;
  is_verified: boolean;
  current_employees: number;
  max_employees: number;
  parent_id?: number;
  created_at: string;
  last_login?: string;
}

export interface UserWithStats extends User {
  total_work_records: number;
  today_work_records: number;
  total_billing_amount: number;
}

export interface LoginRequest {
  username: string; // 用户名、邮箱或手机号
  password: string;
}

export interface LoginResponse {
  token: string;
  user: User;
}

// 后端API响应格式
export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
}

export interface WorkRecord {
  id: number;
  employee_id: number;
  platform: string;
  action_type: string;
  target_username?: string;
  target_user_id?: string;
  target_url?: string;
  status: string;
  error_message?: string;
  device_id?: string;
  device_name?: string;
  created_at: string;
  executed_at?: string;
}

export interface BillingRecord {
  id: number;
  user_id: number;
  billing_type: string;
  quantity: number;
  unit_price: number;
  total_amount: number;
  billing_period: string;
  period_start: string;
  period_end: string;
  status: string;
  created_at: string;
  paid_at?: string;
}

export interface PricingRule {
  id: number;
  name?: string; // 规则名称 (可选)
  rule_name: string; // 规则名称
  rule_type?: string; // 计费类型：employee_count | follow_count (可选)
  billing_type: string; // 计费类型
  billing_period?: string; // 计费周期：monthly | yearly | one_time (可选)
  unit_price: number;
  description?: string; // 规则描述
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

// 公司收费计划
export interface CompanyPricingPlan {
  id: number;
  company_name: string;
  plan_name: string;
  employee_monthly_fee: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

// 公司操作收费规则
export interface CompanyOperationPricing {
  id: number;
  company_name: string;
  platform: string; // xiaohongshu, douyin
  operation_type: string; // follow, like, favorite, comment
  unit_price: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface UserCreate {
  username: string;
  password: string;
  email?: string;
  full_name?: string;
  phone?: string;
  company?: string;
  role: string;
  max_employees?: number;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  phone?: string;
  company?: string;
  is_active?: boolean;
  max_employees?: number;
}

export interface CompanyStatistics {
  company_name: string;
  user_admin_id: number;
  user_admin_name: string;
  total_employees: number;
  total_follows: number;
  today_follows: number;
  total_billing_amount: number;
  unpaid_amount: number;
  balance: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
