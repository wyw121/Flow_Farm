// 类型定义
export interface DeviceInfo {
  id: string
  name: string
  status: '已连接' | '离线' | '连接中' | '错误'
  lastSeen: string
  capabilities: string[]
  platform?: string
  resolution?: string
  androidVersion?: string
}

export interface TaskInfo {
  id: string
  name: string
  type: 'follow_contacts' | 'monitor_competitor'
  status: '等待中' | '进行中' | '已完成' | '失败'
  progress: number
  deviceId?: string
  createdAt: string
  completedAt?: string
  parameters?: any
}

export interface UserSession {
  userId: string
  username: string
  role: string
  token: string
  expiresAt: string
}

export interface ContactInfo {
  name: string
  phone: string
  platformId?: string
}

export interface FollowStatistics {
  totalFollows: number
  dailyFollows: number
  balance: number
  costPerFollow: number
}

export interface MonitorTask {
  targetAccount: string
  keywords: string[]
  targetCount: number
  collectedUsers: string[]
  progress: number
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message: string
  code?: number
}

export interface AppConfig {
  serverUrl: string
  autoConnectDevices: boolean
  maxConcurrentTasks: number
  logLevel: string
}
