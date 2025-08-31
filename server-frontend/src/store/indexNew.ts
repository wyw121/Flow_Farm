/**
 * 重构后的Store配置
 * 使用新的认证模块和中间件
 */

import { configureStore } from '@reduxjs/toolkit'
import authReducer from './authSliceNew'

export const store = configureStore({
  reducer: {
    auth: authReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // 忽略这些 action types 的序列化检查
        ignoredActions: ['auth/checkAuthStatus/pending', 'auth/login/pending'],
        // 忽略这些 paths 的序列化检查
        ignoredPaths: ['auth.lastActivity'],
      },
    }),
  devTools: import.meta.env.DEV,
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

// 导出认证相关的选择器和操作
export {
    changePasswordAsync, checkAuthStatusAsync, clearError, getCurrentUserAsync, loginAsync,
    logoutAsync, resetLoginAttempts,
    selectAuth, selectError, selectIsAuthenticated,
    selectIsLoading, selectIsLocked, selectUser, selectUserRole, updateLastActivity
} from './authSliceNew'
