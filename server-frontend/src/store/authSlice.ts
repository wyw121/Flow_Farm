import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit'
import { authService } from '../services/authService'
import { LoginRequest, User } from '../types'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: false, // 初始为false，需要验证token有效性
  loading: !!localStorage.getItem('token'), // 如果有token，开始时就要显示加载状态
  error: null,
}

// 异步actions
export const login = createAsyncThunk(
  'auth/login',
  async (loginData: LoginRequest, { rejectWithValue, dispatch }) => {
    try {
      // 登录前先完全清理之前的状态
      localStorage.removeItem('token')
      dispatch(clearAuthState())

      const response = await authService.login(loginData)
      localStorage.setItem('token', response.token)
      return response
    } catch (error: any) {
      // 登录失败时也要清理状态
      localStorage.removeItem('token')

      // 处理不同类型的错误
      let errorMessage = '登录失败'

      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data
        } else if (error.response.data.detail) {
          // 如果是字符串，直接使用
          if (typeof error.response.data.detail === 'string') {
            errorMessage = error.response.data.detail
          } else if (Array.isArray(error.response.data.detail)) {
            // 如果是验证错误数组，提取错误信息
            errorMessage = error.response.data.detail
              .map((err: any) => err.msg || err.message || '验证失败')
              .join(', ')
          } else {
            errorMessage = '请求格式错误'
          }
        } else {
          errorMessage = '服务器响应错误'
        }
      } else if (error.message) {
        errorMessage = error.message
      }

      return rejectWithValue(errorMessage)
    }
  }
)

export const logout = createAsyncThunk(
  'auth/logout',
  async () => {
    try {
      await authService.logout()
    } catch (error) {
      // 后端登出失败时继续清理前端状态
    }

    // 无论后端登出是否成功，都要清理前端状态
    localStorage.removeItem('token')
    return null
  }
)

export const getCurrentUser = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authService.getCurrentUser()
      return response
    } catch (error: any) {
      localStorage.removeItem('token')

      let errorMessage = '获取用户信息失败'
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail
        }
      }

      return rejectWithValue(errorMessage)
    }
  }
)

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    clearAuthState: (state) => {
      state.user = null
      state.token = null
      state.isAuthenticated = false
      state.loading = false
      state.error = null
    },
    setCredentials: (state, action: PayloadAction<{ user: User; token: string }>) => {
      state.user = action.payload.user
      state.token = action.payload.token
      state.isAuthenticated = true
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state, action) => {
        // 确保完全清理之前的状态后再设置新状态
        state.loading = false
        state.error = null
        state.isAuthenticated = true
        state.user = action.payload.user
        state.token = action.payload.token
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false
        state.isAuthenticated = false
        state.user = null
        state.token = null
        state.error = action.payload as string
      })
      // Logout
      .addCase(logout.fulfilled, (state) => {
        state.isAuthenticated = false
        state.user = null
        state.token = null
        state.error = null
        state.loading = false
      })
      // Get current user
      .addCase(getCurrentUser.pending, (state) => {
        state.loading = true
      })
      .addCase(getCurrentUser.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload
        state.isAuthenticated = true
        state.error = null
      })
      .addCase(getCurrentUser.rejected, (state, action) => {
        state.loading = false
        state.isAuthenticated = false
        state.user = null
        state.token = null
        state.error = action.payload as string
      })
  },
})

export const { clearError, clearAuthState, setCredentials } = authSlice.actions
export default authSlice.reducer
