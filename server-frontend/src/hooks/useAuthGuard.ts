import { useSelector } from 'react-redux'
import { UserRole } from '../components/ProtectedRoute'
import { RootState } from '../store'

export const useAuthGuard = () => {
  const { isAuthenticated, user, loading } = useSelector((state: RootState) => state.auth)

  const hasRole = (requiredRole: UserRole) => {
    if (!isAuthenticated || !user) {
      return false
    }

    const userRole = user.role?.trim()
    const required = requiredRole.trim()
    const hasAccess = userRole === required

    return hasAccess
  }

  const isSystemAdmin = () => hasRole('system_admin')
  const isUserAdmin = () => hasRole('user_admin')
  const isEmployee = () => hasRole('employee')

  const getDefaultRoute = (): string => {
    if (!isAuthenticated || !user) {
      return '/login'
    }

    switch (user.role) {
      case 'system_admin':
        return '/system-admin/dashboard'
      case 'user_admin':
        return '/user-admin/dashboard'
      case 'employee':
        return '/employee/dashboard'
      default:
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
