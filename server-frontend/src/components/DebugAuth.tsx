import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { useAuthGuard } from '../hooks/useAuthGuard'
import { RootState } from '../store'

const DebugAuth: React.FC = () => {
  const authState = useSelector((state: RootState) => state.auth)
  const { hasRole, getDefaultRoute } = useAuthGuard()
  const [testResults, setTestResults] = useState<Record<string, any>>({})

  const testRoles = ['system_admin', 'user_admin', 'employee'] as const

  useEffect(() => {
    // 测试所有角色
    const results: Record<string, any> = {}
    testRoles.forEach(role => {
      const result = hasRole(role)
      results[role] = {
        result,
        userRole: authState.user?.role,
        userRoleRaw: JSON.stringify(authState.user?.role),
        roleComparison: authState.user?.role === role,
        strictEquality: Object.is(authState.user?.role, role),
        typeCheck: typeof authState.user?.role === 'string' && typeof role === 'string'
      }
    })
    setTestResults(results)
  }, [authState.user, hasRole])

  if (!authState.isAuthenticated) {
    return null
  }

  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      left: '10px',
      background: 'white',
      border: '1px solid #ccc',
      padding: '10px',
      fontSize: '12px',
      maxWidth: '500px',
      zIndex: 9999,
      maxHeight: '80vh',
      overflow: 'auto'
    }}>
      <h4>认证调试信息</h4>

      <div><strong>认证状态:</strong> {authState.isAuthenticated ? '已认证' : '未认证'}</div>
      <div><strong>加载状态:</strong> {authState.loading ? '加载中' : '完成'}</div>
      <div><strong>用户角色:</strong> "{authState.user?.role}" (长度: {authState.user?.role?.length})</div>
      <div><strong>用户名:</strong> {authState.user?.username || '无'}</div>
      <div><strong>错误:</strong> {authState.error || '无'}</div>

      <h5>角色权限测试:</h5>
      {testRoles.map(role => {
        const test = testResults[role]
        return (
          <div key={role} style={{ marginBottom: '5px', padding: '5px', background: test?.result ? '#d4edda' : '#f8d7da' }}>
            <strong>{role}:</strong> {test?.result ? '✅' : '❌'}
            <div style={{ fontSize: '10px' }}>
              比较: {test?.roleComparison ? 'true' : 'false'} |
              严格: {test?.strictEquality ? 'true' : 'false'} |
              类型: {test?.typeCheck ? 'true' : 'false'}
            </div>
          </div>
        )
      })}

      <div><strong>默认路由:</strong> {getDefaultRoute()}</div>

      <details style={{ marginTop: '10px' }}>
        <summary>完整状态</summary>
        <pre style={{ fontSize: '10px', overflow: 'auto', maxHeight: '200px' }}>
          {JSON.stringify({ authState, testResults }, null, 2)}
        </pre>
      </details>
    </div>
  )
}

export default DebugAuth
