<template>
  <div id="app">
    <n-config-provider :theme="theme">
      <n-loading-bar-provider>
        <n-dialog-provider>
          <n-notification-provider>
            <n-message-provider>
              <div class="app-container">
                <!-- 顶部导航栏 -->
                <header class="app-header">
                  <div class="header-left">
                    <img src="/logo.svg" alt="Flow Farm" class="logo" />
                    <h1 class="app-title">Flow Farm 员工客户端</h1>
                  </div>
                  <div class="header-right">
                    <n-space>
                      <n-badge :value="connectedDevicesCount" type="success">
                        <n-button text style="font-size: 16px;">
                          <template #icon>
                            <n-icon><PhonePortrait /></n-icon>
                          </template>
                          设备
                        </n-button>
                      </n-badge>
                      <n-dropdown :options="userMenuOptions" @select="handleUserMenuSelect">
                        <n-button text>
                          <template #icon>
                            <n-icon><Person /></n-icon>
                          </template>
                          {{ userStore.currentUser?.username || '未登录' }}
                        </n-button>
                      </n-dropdown>
                    </n-space>
                  </div>
                </header>

                <!-- 主要内容区域 -->
                <main class="app-main">
                  <router-view />
                </main>

                <!-- 状态栏 -->
                <footer class="app-footer">
                  <n-space justify="space-between">
                    <span>连接状态: {{ connectionStatus }}</span>
                    <span>当前时间: {{ currentTime }}</span>
                  </n-space>
                </footer>
              </div>
            </n-message-provider>
          </n-notification-provider>
        </n-dialog-provider>
      </n-loading-bar-provider>
    </n-config-provider>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { darkTheme } from 'naive-ui'
import { PhonePortrait, Person } from '@vicons/ionicons5'
import { useUserStore } from './stores/user'
import { useDeviceStore } from './stores/device'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const deviceStore = useDeviceStore()
const router = useRouter()

// 主题设置
const theme = ref(null) // null 表示亮色主题，darkTheme 表示暗色主题

// 连接的设备数量
const connectedDevicesCount = computed(() => {
  return deviceStore.devices.filter(device => device.status === '已连接').length
})

// 连接状态
const connectionStatus = computed(() => {
  if (connectedDevicesCount.value > 0) {
    return `已连接 ${connectedDevicesCount.value} 台设备`
  }
  return '未连接设备'
})

// 当前时间
const currentTime = ref('')

// 用户菜单选项
const userMenuOptions = computed(() => [
  {
    label: '设置',
    key: 'settings'
  },
  {
    label: '关于',
    key: 'about'
  },
  {
    type: 'divider'
  },
  {
    label: '退出登录',
    key: 'logout'
  }
])

// 处理用户菜单选择
const handleUserMenuSelect = (key: string) => {
  switch (key) {
    case 'settings':
      router.push('/settings')
      break
    case 'about':
      // 显示关于对话框
      break
    case 'logout':
      userStore.logout()
      router.push('/login')
      break
  }
}

// 更新时间
const updateTime = () => {
  currentTime.value = new Date().toLocaleString('zh-CN')
}

let timeInterval: number

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  
  // 初始化应用数据
  deviceStore.loadDevices()
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: white;
  border-bottom: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  width: 32px;
  height: 32px;
}

.app-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
}

.app-main {
  flex: 1;
  overflow: auto;
  padding: 24px;
}

.app-footer {
  padding: 8px 24px;
  background: white;
  border-top: 1px solid #e8e8e8;
  font-size: 12px;
  color: #666;
}
</style>
