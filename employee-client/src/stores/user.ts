import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserSession } from '../types'

export const useUserStore = defineStore('user', () => {
  const currentUser = ref<UserSession | null>(null)
  const isLoggedIn = ref(false)

  const login = async (username: string, password: string) => {
    try {
      // 调用 Tauri 后端 API
      const { invoke } = await import('@tauri-apps/api/core')
      const user = await invoke<UserSession>('login', { username, password })
      
      currentUser.value = user
      isLoggedIn.value = true
      
      // 保存到本地存储
      localStorage.setItem('user_session', JSON.stringify(user))
      
      return user
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      const { invoke } = await import('@tauri-apps/api/core')
      await invoke('logout')
      
      currentUser.value = null
      isLoggedIn.value = false
      
      // 清除本地存储
      localStorage.removeItem('user_session')
    } catch (error) {
      console.error('登出失败:', error)
    }
  }

  const loadSession = () => {
    const saved = localStorage.getItem('user_session')
    if (saved) {
      try {
        const user = JSON.parse(saved)
        // 检查 token 是否过期
        if (new Date(user.expiresAt) > new Date()) {
          currentUser.value = user
          isLoggedIn.value = true
        } else {
          localStorage.removeItem('user_session')
        }
      } catch (error) {
        console.error('加载用户会话失败:', error)
        localStorage.removeItem('user_session')
      }
    }
  }

  // 初始化时加载会话
  loadSession()

  return {
    currentUser,
    isLoggedIn,
    login,
    logout,
    loadSession
  }
})
