/**
 * 新的认证状态管理模块
 * 使用Redux Toolkit和新的认证服务
 */

import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import {
    AuthService,
    LoginCredentials,
    User,
    authConfig
} from '../services/auth'

// 创建认证服务实例
const authService = new AuthService(authConfig)

// Redux状态接口
interface AuthSliceState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  lastActivity: number | null
  loginAttempts: number
  isLocked: boolean
  lockExpiry: number | null
}

// 初始状态
const initialState: AuthSliceState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  lastActivity: null,
  loginAttempts: 0,
  isLocked: false,
  lockExpiry: null
}

// 异步操作
export const loginAsync = createAsyncThunk(
  'auth/login',
  async (credentials: LoginCredentials, { rejectWithValue, getState }) => {
    try {
      const state = getState() as { auth: AuthSliceState }

      // 检查是否被锁定
      if (state.auth.isLocked && state.auth.lockExpiry) {
        const now = Date.now()
        if (now < state.auth.lockExpiry) {
          const remaining = Math.ceil((state.auth.lockExpiry - now) / 1000 / 60)
          throw new Error(`账户已锁定，请${remaining}分钟后重试`)
        }
      }

      const response = await authService.login(credentials)

      if (response.success && response.data) {
        return {
          user: response.data.user,
          token: response.data.token
        }
      } else {
        throw new Error(response.message || '登录失败')
      }
    } catch (error: any) {
      return rejectWithValue(error.message || '登录失败')
    }
  }
)

export const logoutAsync = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      await authService.logout()
      return null
    } catch (error: any) {
      return rejectWithValue(error.message || '登出失败')
    }
  }
)

export const getCurrentUserAsync = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const user = await authService.getCurrentUser()
      return user
    } catch (error: any) {
      return rejectWithValue(error.message || '获取用户信息失败')
    }
  }
)

export const checkAuthStatusAsync = createAsyncThunk(
  'auth/checkAuthStatus',
  async (_, { rejectWithValue }) => {
    try {
      const isAuthenticated = await authService.checkAuthStatus()
      if (isAuthenticated) {
        const authState = authService.getAuthState()
        return authState.user
      }
      return null
    } catch (error: any) {
      return rejectWithValue(error.message || '验证登录状态失败')
    }
  }
)

export const changePasswordAsync = createAsyncThunk(
  'auth/changePassword',
  async ({ oldPassword, newPassword }: { oldPassword: string; newPassword: string }, { rejectWithValue }) => {
    try {
      await authService.changePassword(oldPassword, newPassword)
      return true
    } catch (error: any) {
      return rejectWithValue(error.message || '修改密码失败')
    }
  }
)

// 认证切片
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },

    updateLastActivity: (state) => {
      state.lastActivity = Date.now()
    },

    resetLoginAttempts: (state) => {
      state.loginAttempts = 0
      state.isLocked = false
      state.lockExpiry = null
    },

    lockAccount: (state) => {
      state.isLocked = true
      state.lockExpiry = Date.now() + (authConfig.security.lockoutDuration * 60 * 1000)
    },

    checkLockStatus: (state) => {
      if (state.isLocked && state.lockExpiry) {
        const now = Date.now()
        if (now >= state.lockExpiry) {
          state.isLocked = false
          state.lockExpiry = null
          state.loginAttempts = 0
        }
      }
    },

    forceLogout: (state) => {
      state.user = null
      state.isAuthenticated = false
      state.error = null
      state.lastActivity = null
      authService.logout().catch(console.warn)
    }
  },

  extraReducers: (builder) => {
    builder
      // 登录
      .addCase(loginAsync.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(loginAsync.fulfilled, (state, action) => {
        state.isLoading = false
        state.user = action.payload.user
        state.isAuthenticated = true
        state.error = null
        state.lastActivity = Date.now()
        state.loginAttempts = 0
        state.isLocked = false
        state.lockExpiry = null
      })
      .addCase(loginAsync.rejected, (state, action) => {
        state.isLoading = false
        state.user = null
        state.isAuthenticated = false
        state.error = action.payload as string

        // 增加登录失败次数
        state.loginAttempts += 1

        // 检查是否需要锁定账户
        if (state.loginAttempts >= authConfig.security.maxLoginAttempts) {
          state.isLocked = true
          state.lockExpiry = Date.now() + (authConfig.security.lockoutDuration * 60 * 1000)
        }
      })

      // 登出
      .addCase(logoutAsync.pending, (state) => {
        state.isLoading = true
      })
      .addCase(logoutAsync.fulfilled, (state) => {
        state.isLoading = false
        state.user = null
        state.isAuthenticated = false
        state.error = null
        state.lastActivity = null
      })
      .addCase(logoutAsync.rejected, (state, action) => {
        state.isLoading = false
        state.user = null
        state.isAuthenticated = false
        state.error = action.payload as string
        state.lastActivity = null
      })

      // 获取当前用户
      .addCase(getCurrentUserAsync.pending, (state) => {
        state.isLoading = true
      })
      .addCase(getCurrentUserAsync.fulfilled, (state, action) => {
        state.isLoading = false
        state.user = action.payload
        state.isAuthenticated = true
        state.error = null
        state.lastActivity = Date.now()
      })
      .addCase(getCurrentUserAsync.rejected, (state, action) => {
        state.isLoading = false
        state.user = null
        state.isAuthenticated = false
        state.error = action.payload as string
      })

      // 检查认证状态
      .addCase(checkAuthStatusAsync.pending, (state) => {
        state.isLoading = true
      })
      .addCase(checkAuthStatusAsync.fulfilled, (state, action) => {
        state.isLoading = false
        if (action.payload) {
          state.user = action.payload
          state.isAuthenticated = true
          state.lastActivity = Date.now()
        } else {
          state.user = null
          state.isAuthenticated = false
        }
        state.error = null
      })
      .addCase(checkAuthStatusAsync.rejected, (state, action) => {
        state.isLoading = false
        state.user = null
        state.isAuthenticated = false
        state.error = action.payload as string
      })

      // 修改密码
      .addCase(changePasswordAsync.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(changePasswordAsync.fulfilled, (state) => {
        state.isLoading = false
        state.error = null
      })
      .addCase(changePasswordAsync.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
  }
})

// 导出actions
export const {
  clearError,
  updateLastActivity,
  resetLoginAttempts,
  lockAccount,
  checkLockStatus,
  forceLogout
} = authSlice.actions

// 选择器
export const selectAuth = (state: { auth: AuthSliceState }) => state.auth
export const selectUser = (state: { auth: AuthSliceState }) => state.auth.user
export const selectIsAuthenticated = (state: { auth: AuthSliceState }) => state.auth.isAuthenticated
export const selectIsLoading = (state: { auth: AuthSliceState }) => state.auth.isLoading
export const selectError = (state: { auth: AuthSliceState }) => state.auth.error
export const selectUserRole = (state: { auth: AuthSliceState }) => state.auth.user?.role
export const selectIsLocked = (state: { auth: AuthSliceState }) => state.auth.isLocked

// 导出reducer
export default authSlice.reducer

// 导出认证服务实例供其他地方使用
export { authService }
