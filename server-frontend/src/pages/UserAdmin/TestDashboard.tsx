import React from 'react'
import { useSelector } from 'react-redux'
import { RootState } from '../../store'

const TestDashboard: React.FC = () => {
  const { user, isAuthenticated } = useSelector((state: RootState) => state.auth)

  return (
    <div style={{ padding: '20px' }}>
      <h1>🎉 用户管理员测试页面</h1>
      <p>如果您能看到这个页面，说明权限验证已经成功！</p>

      <div style={{
        background: '#f0f8ff',
        padding: '15px',
        marginTop: '20px',
        border: '1px solid #d1ecf1',
        borderRadius: '4px'
      }}>
        <h3>用户信息</h3>
        <p><strong>认证状态:</strong> {isAuthenticated ? '✅ 已认证' : '❌ 未认证'}</p>
        <p><strong>用户ID:</strong> {user?.id}</p>
        <p><strong>用户名:</strong> {user?.username}</p>
        <p><strong>角色:</strong> {user?.role}</p>
        <p><strong>公司:</strong> {user?.company}</p>
        <p><strong>时间戳:</strong> {new Date().toISOString()}</p>
      </div>

      <div style={{
        background: '#d4edda',
        padding: '15px',
        marginTop: '20px',
        border: '1px solid #c3e6cb',
        borderRadius: '4px'
      }}>
        <h3>✅ 权限验证成功</h3>
        <p>您现在可以安全地访问用户管理员功能区域。</p>
        <ul>
          <li>员工管理</li>
          <li>费用结算</li>
          <li>工作记录查看</li>
          <li>KPI统计</li>
        </ul>
      </div>
    </div>
  )
}

export default TestDashboard
