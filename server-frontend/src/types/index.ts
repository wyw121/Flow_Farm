export interface User {
  id: number
  username: string
  email?: string
  full_name?: string
  phone?: string
  company?: string
  role: 'system_admin' | 'user_admin' | 'employee'
  is_active: boolean
  is_verified: boolean
  current_employees: number
  max_employees: number
  parent_id?: number
  created_at: string
  last_login?: string
}

export interface UserWithStats extends User {
  total_work_records: number
  today_work_records: number
  total_billing_amount: number
}

export interface LoginRequest {
  identifier: string // 用户名、邮箱或手机号
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface WorkRecord {
  id: number
  employee_id: number
  platform: string
  action_type: string
  target_username?: string
  target_user_id?: string
  target_url?: string
  status: string
  error_message?: string
  device_id?: string
  device_name?: string
  created_at: string
  executed_at?: string
}

export interface BillingRecord {
  id: number
  user_id: number
  billing_type: string
  quantity: number
  unit_price: number
  total_amount: number
  billing_period: string
  period_start: string
  period_end: string
  status: string
  created_at: string
  paid_at?: string
}

export interface PricingRule {
  id: number
  name: string
  description?: string
  rule_type: string
  unit_price: number
  billing_period: string
  rule_config?: any
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface UserCreate {
  username: string
  password: string
  email?: string
  full_name?: string
  phone?: string
  company?: string
  role: string
  max_employees?: number
}

export interface UserUpdate {
  email?: string
  full_name?: string
  phone?: string
  company?: string
  is_active?: boolean
  max_employees?: number
}

export interface CompanyStatistics {
  company_name: string
  user_admin_id: number
  user_admin_name: string
  total_employees: number
  total_follows: number
  today_follows: number
  total_billing_amount: number
  unpaid_amount: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}
