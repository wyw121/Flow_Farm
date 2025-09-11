// 简单测试页面，用于验证修复
import React from 'react'

const TestPage: React.FC = () => {
  return (
    <div style={{ padding: '20px' }}>
      <h1>🎉 登录成功！</h1>
      <p>如果您看到这个页面，说明无限循环问题已修复。</p>
      <p>当前时间: {new Date().toLocaleString()}</p>
      <button onClick={() => window.location.href = '/system-admin/dashboard'}>
        前往系统管理仪表板
      </button>
    </div>
  )
}

export default TestPage
