import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { FollowStatistics } from '../types'

export const useStatisticsStore = defineStore('statistics', () => {
  const statistics = ref<FollowStatistics>({
    totalFollows: 0,
    dailyFollows: 0,
    balance: 0,
    costPerFollow: 0.05
  })

  const loadStatistics = async () => {
    try {
      const { invoke } = await import('@tauri-apps/api/tauri')
      const stats = await invoke<FollowStatistics>('get_statistics')
      statistics.value = stats
    } catch (error) {
      console.error('加载统计数据失败:', error)
      // 使用模拟数据
      statistics.value = {
        totalFollows: 1250,
        dailyFollows: 45,
        balance: 127.50,
        costPerFollow: 0.05
      }
    }
  }

  const updateBalance = (amount: number) => {
    statistics.value.balance += amount
  }

  const updateFollowCount = (count: number) => {
    statistics.value.totalFollows += count
    statistics.value.dailyFollows += count
  }

  return {
    statistics,
    loadStatistics,
    updateBalance,
    updateFollowCount
  }
})
