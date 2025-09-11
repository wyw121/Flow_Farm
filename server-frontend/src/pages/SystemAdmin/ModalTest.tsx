import { Modal, Button, message } from 'antd'
import React from 'react'

const ModalTest: React.FC = () => {
  const testModal = () => {
    console.log('🧪 测试Modal.confirm...')
    
    Modal.confirm({
      title: '测试确认对话框',
      content: '这是一个测试对话框，请确认是否正常显示。',
      okText: '确认',
      cancelText: '取消',
      onOk: () => {
        console.log('✅ 用户点击了确认')
        message.success('确认成功！')
      },
      onCancel: () => {
        console.log('❌ 用户点击了取消')
        message.info('取消操作')
      }
    })
  }

  const testNativeConfirm = () => {
    if (window.confirm('这是浏览器原生确认对话框，是否继续？')) {
      message.success('原生确认成功！')
    } else {
      message.info('原生确认取消')
    }
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2>Modal 测试页面</h2>
      <div style={{ marginBottom: '20px' }}>
        <Button type="primary" onClick={testModal} style={{ marginRight: '10px' }}>
          测试 Ant Design Modal.confirm
        </Button>
        <Button onClick={testNativeConfirm}>
          测试浏览器原生 confirm
        </Button>
      </div>
    </div>
  )
}

export default ModalTest
