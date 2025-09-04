import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { TaskInfo } from '../types'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref<TaskInfo[]>([])
  const isLoading = ref(false)

  const activeTasks = computed(() =>
    tasks.value.filter(task => task.status === '进行中')
  )

  const loadTasks = async () => {
    try {
      const { invoke } = await import('@tauri-apps/api/core')
      const result = await invoke<TaskInfo[]>('get_tasks')
      tasks.value = result
    } catch (error) {
      console.error('Failed to load tasks:', error)
    }
  }

  const createFollowTask = async (params: {
    contactFile: string
    devices: string[]
  }) => {
    try {
      const { invoke } = await import('@tauri-apps/api/core')
      const result = await invoke<string>('create_follow_task', {
        contactFile: params.contactFile,
        devices: params.devices
      })

      await loadTasks()
      return result
    } catch (error) {
      console.error('Failed to create follow task:', error)
      throw error
    }
  }

  const createMonitorTask = async (params: {
    targetAccount: string
    keywords: string[]
    targetCount: number
    devices: string[]
  }) => {
    try {
      const { invoke } = await import('@tauri-apps/api/core')
      const result = await invoke<string>('create_monitor_task', {
        targetAccount: params.targetAccount,
        keywords: params.keywords,
        targetCount: params.targetCount,
        devices: params.devices
      })

      await loadTasks()
      return result
    } catch (error) {
      console.error('Failed to create monitor task:', error)
      throw error
    }
  }

  const startTask = async (taskId: string) => {
    try {
      const { invoke } = await import('@tauri-apps/api/core')
      await invoke('start_task', { taskId })
      await loadTasks()
    } catch (error) {
      console.error('Failed to start task:', error)
      throw error
    }
  }

  const stopTask = async (taskId: string) => {
    try {
      const { invoke } = await import('@tauri-apps/api/core')
      await invoke('stop_task', { taskId })
      await loadTasks()
    } catch (error) {
      console.error('Failed to stop task:', error)
      throw error
    }
  }

  return {
    tasks,
    isLoading,
    activeTasks,
    loadTasks,
    createFollowTask,
    createMonitorTask,
    startTask,
    stopTask
  }
})
