import { useSelector } from 'react-redux'
import { UserRole } from '../components/ProtectedRoute'
import { RootState } from '../store'

export const useAuthGuard = () => {
  const { isAuthenticated, user, loading } = useSelector((state: RootState) => state.auth)

  const hasRole = (requiredRole: UserRole) => {
    if (!isAuthenticated || !user) {
      console.log(`权限检查失败 - 用户未认证或用户对象为空:`, {
        isAuthenticated,
        user: !!user
      })
      return false
    }

    const userRole = user.role?.trim()
    const required = requiredRole.trim()
    const hasAccess = userRole === required

    console.log(`权限检查 [${requiredRole}]:`, {
      isAuthenticated,
      userRole,
      userRoleRaw: user.role,
      requiredRole: required,
      hasAccess,
      userId: user?.id,
      username: user?.username,
      roleMatch: userRole === required,
      userObject: user
    })
    return hasAccess
  }

  const isSystemAdmin = () => hasRole('system_admin')
  const isUserAdmin = () => hasRole('user_admin')
  const isEmployee = () => hasRole('employee')

  const getDefaultRoute = (): string => {
    if (!isAuthenticated || !user) {
      console.log('用户未认证，返回登录页面')
      return '/login'
    }

    switch (user.role) {
      case 'system_admin':
        console.log('系统管理员，跳转到系统管理员仪表盘')
        return '/system-admin/dashboard'
      case 'user_admin':
        console.log('用户管理员，跳转到用户管理员仪表盘')
        return '/user-admin/dashboard'
      case 'employee':
        console.log('员工，跳转到员工仪表盘')
        return '/employee/dashboard'
      default:
        console.log('未知角色，跳转到无权限页面')
        return '/unauthorized'
    }
  }

  return {
    isAuthenticated,
    user,
    loading,
    hasRole,
    isSystemAdmin,
    isUserAdmin,
    isEmployee,
    getDefaultRoute
  }
}
