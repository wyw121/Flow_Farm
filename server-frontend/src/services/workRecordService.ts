import { PaginatedResponse, WorkRecord } from '../types'
import { apiClient } from './api'

export const workRecordService = {
  // 获取工作记录列表
  async getWorkRecords(
    page: number = 1,
    size: number = 10,
    employeeId?: number,
    platform?: string,
    actionType?: string,
    startDate?: string,
    endDate?: string
  ): Promise<PaginatedResponse<WorkRecord>> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })

    if (employeeId) params.append('employee_id', employeeId.toString())
    if (platform) params.append('platform', platform)
    if (actionType) params.append('action_type', actionType)
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)

    const response = await apiClient.get(`/api/v1/kpi/work-records/?${params}`)
    return response.data
  },

  // 获取工作统计
  async getWorkStatistics(
    employeeId?: number,
    startDate?: string,
    endDate?: string
  ): Promise<any> {
    const params = new URLSearchParams()

    if (employeeId) params.append('employee_id', employeeId.toString())
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)

    const response = await apiClient.get(`/api/v1/kpi/statistics/?${params}`)
    return response.data
  },

  // 导出工作记录
  async exportWorkRecords(
    employeeId?: number,
    platform?: string,
    actionType?: string,
    startDate?: string,
    endDate?: string
  ): Promise<Blob> {
    const params = new URLSearchParams()

    if (employeeId) params.append('employee_id', employeeId.toString())
    if (platform) params.append('platform', platform)
    if (actionType) params.append('action_type', actionType)
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)

    const response = await apiClient.get(`/api/v1/reports/export/work-records/?${params}`, {
      responseType: 'blob'
    })
    return response.data
  },
}
