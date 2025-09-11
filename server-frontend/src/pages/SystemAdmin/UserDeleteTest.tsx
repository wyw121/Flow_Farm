import { Button, Card, message, Space } from 'antd'
import React from 'react'
import { userService } from '../../services/userService'

const UserDeleteTest: React.FC = () => {
  const testDeleteUser = async (userId: number) => {
    console.log('🧪 开始测试删除用户，用户ID:', userId)
    try {
      console.log('🔄 调用删除API...')
      await userService.deleteUser(userId)
      console.log('✅ 删除成功')
      message.success(`用户 ${userId} 删除成功`)
    } catch (error: any) {
      console.error('❌ 删除失败:', error)
      message.error(`删除失败: ${error?.message || error}`)
    }
  }

  return (
    <Card title="删除用户测试" style={{ margin: '20px' }}>
      <Space>
        <Button
          danger
          onClick={() => testDeleteUser(19)}
        >
          测试删除用户19
        </Button>
        <Button
          danger
          onClick={() => testDeleteUser(18)}
        >
          测试删除用户18
        </Button>
      </Space>
    </Card>
  )
}

export default UserDeleteTest
