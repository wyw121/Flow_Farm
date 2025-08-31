/**
 * 重构后的应用入口文件
 * 使用新的认证系统和组件
 */

import 'antd/dist/reset.css'
import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import './index.css'

import AppNew from './AppNew'
import { store } from './store/indexNew'

// 设置全局错误处理
window.addEventListener('unhandledrejection', (event) => {
  console.error('未处理的Promise错误:', event.reason)
  // 在生产环境中，这里可以发送错误到日志服务
})

window.addEventListener('error', (event) => {
  console.error('全局错误:', event.error)
  // 在生产环境中，这里可以发送错误到日志服务
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <AppNew />
      </BrowserRouter>
    </Provider>
  </React.StrictMode>
)
