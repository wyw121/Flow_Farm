<template>
  <n-card 
    :class="['device-card', deviceStatusClass]"
    size="small"
    hoverable
  >
    <template #header>
      <n-space justify="space-between" align="center">
        <span class="device-slot">设备 {{ slotNumber }}</span>
        <n-tag 
          :type="getStatusTagType(device?.status)" 
          :bordered="false" 
          size="small"
        >
          {{ device?.status || '空闲' }}
        </n-tag>
      </n-space>
    </template>

    <div v-if="device" class="device-content">
      <!-- 设备信息 -->
      <n-space vertical size="small">
        <div class="device-name">
          <n-text strong>{{ device.name }}</n-text>
        </div>
        
        <div class="device-details">
          <n-space vertical size="tiny">
            <n-text depth="3" style="font-size: 12px;">
              ID: {{ device.id }}
            </n-text>
            <n-text depth="3" style="font-size: 12px;">
              最后在线: {{ formatLastSeen(device.lastSeen) }}
            </n-text>
          </n-space>
        </div>

        <!-- 设备能力标签 -->
        <div v-if="device.capabilities.length > 0" class="device-capabilities">
          <n-space size="tiny" wrap>
            <n-tag 
              v-for="capability in device.capabilities" 
              :key="capability"
              size="tiny"
              type="info"
            >
              {{ capability }}
            </n-tag>
          </n-space>
        </div>

        <!-- 连接状态指示器 -->
        <div class="connection-indicator">
          <n-space align="center" size="tiny">
            <div :class="['status-dot', getStatusDotClass(device.status)]"></div>
            <n-text style="font-size: 12px;">
              {{ getConnectionText(device.status) }}
            </n-text>
          </n-space>
        </div>
      </n-space>

      <!-- 操作按钮 -->
      <div class="device-actions">
        <n-space size="tiny" justify="center">
          <n-button 
            v-if="device.status === '离线'"
            type="primary"
            size="tiny"
            @click="$emit('connect', device)"
          >
            连接
          </n-button>
          <n-button 
            v-else-if="device.status === '已连接'"
            type="warning"
            size="tiny"
            @click="$emit('disconnect', device)"
          >
            断开
          </n-button>
          <n-button 
            v-else-if="device.status === '连接中'"
            type="info"
            size="tiny"
            disabled
          >
            连接中...
          </n-button>
          
          <n-dropdown :options="deviceMenuOptions" @select="handleMenuSelect">
            <n-button size="tiny" quaternary>
              <template #icon>
                <n-icon><EllipsisVertical /></n-icon>
              </template>
            </n-button>
          </n-dropdown>
        </n-space>
      </div>
    </div>

    <!-- 空插槽状态 -->
    <div v-else class="empty-slot">
      <n-space vertical align="center" justify="center" style="min-height: 120px;">
        <n-icon size="32" depth="3">
          <PhonePortraitOutline />
        </n-icon>
        <n-text depth="3">空闲插槽</n-text>
        <n-text depth="3" style="font-size: 12px;">
          点击添加设备
        </n-text>
      </n-space>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { EllipsisVertical, PhonePortraitOutline } from '@vicons/ionicons5'
import type { DeviceInfo } from '../types'

interface Props {
  device: DeviceInfo | null
  slotNumber: number
}

interface Emits {
  (e: 'connect', device: DeviceInfo): void
  (e: 'disconnect', device: DeviceInfo): void
  (e: 'configure', device: DeviceInfo): void
  (e: 'remove', device: DeviceInfo): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 设备菜单选项
const deviceMenuOptions = computed(() => [
  {
    label: '配置设备',
    key: 'configure',
    disabled: !props.device
  },
  {
    label: '查看详情',
    key: 'details',
    disabled: !props.device
  },
  {
    type: 'divider'
  },
  {
    label: '移除设备',
    key: 'remove',
    disabled: !props.device
  }
])

// 计算属性
const deviceStatusClass = computed(() => {
  if (!props.device) return 'empty-slot-card'
  
  switch (props.device.status) {
    case '已连接':
      return 'connected'
    case '离线':
      return 'offline'
    case '连接中':
      return 'connecting'
    case '错误':
      return 'error'
    default:
      return ''
  }
})

// 方法
const getStatusTagType = (status?: string) => {
  switch (status) {
    case '已连接':
      return 'success'
    case '离线':
      return 'default'
    case '连接中':
      return 'info'
    case '错误':
      return 'error'
    default:
      return 'default'
  }
}

const getStatusDotClass = (status: string) => {
  switch (status) {
    case '已连接':
      return 'connected'
    case '离线':
      return 'offline'
    case '连接中':
      return 'connecting'
    case '错误':
      return 'error'
    default:
      return 'offline'
  }
}

const getConnectionText = (status: string) => {
  switch (status) {
    case '已连接':
      return '设备在线'
    case '离线':
      return '设备离线'
    case '连接中':
      return '正在连接'
    case '错误':
      return '连接错误'
    default:
      return '未知状态'
  }
}

const formatLastSeen = (lastSeen: string) => {
  const date = new Date(lastSeen)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  
  return date.toLocaleDateString('zh-CN')
}

const handleMenuSelect = (key: string) => {
  if (!props.device) return
  
  switch (key) {
    case 'configure':
      emit('configure', props.device)
      break
    case 'details':
      // TODO: 显示设备详情
      break
    case 'remove':
      emit('remove', props.device)
      break
  }
}
</script>

<style scoped>
.device-card {
  transition: all 0.3s ease;
  border-radius: 8px;
  min-height: 180px;
}

.device-card.connected {
  border-color: #18a058;
  box-shadow: 0 0 0 1px rgba(24, 160, 88, 0.2);
}

.device-card.offline {
  border-color: #e0e0e6;
}

.device-card.connecting {
  border-color: #2080f0;
  box-shadow: 0 0 0 1px rgba(32, 128, 240, 0.2);
}

.device-card.error {
  border-color: #d03050;
  box-shadow: 0 0 0 1px rgba(208, 48, 80, 0.2);
}

.device-card.empty-slot-card {
  border: 2px dashed #e0e0e6;
  background-color: #fafafa;
}

.device-slot {
  font-weight: 600;
  font-size: 14px;
}

.device-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 120px;
}

.device-name {
  font-size: 16px;
}

.device-details {
  flex: 1;
}

.device-capabilities {
  margin: 4px 0;
}

.connection-indicator {
  margin: 8px 0;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.connected {
  background-color: #18a058;
  animation: pulse-green 2s infinite;
}

.status-dot.offline {
  background-color: #909399;
}

.status-dot.connecting {
  background-color: #2080f0;
  animation: pulse-blue 1s infinite;
}

.status-dot.error {
  background-color: #d03050;
  animation: pulse-red 1s infinite;
}

.device-actions {
  margin-top: auto;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.empty-slot {
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.empty-slot:hover {
  background-color: #f5f5f5;
}

@keyframes pulse-green {
  0% {
    box-shadow: 0 0 0 0 rgba(24, 160, 88, 0.7);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(24, 160, 88, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(24, 160, 88, 0);
  }
}

@keyframes pulse-blue {
  0% {
    box-shadow: 0 0 0 0 rgba(32, 128, 240, 0.7);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(32, 128, 240, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(32, 128, 240, 0);
  }
}

@keyframes pulse-red {
  0% {
    box-shadow: 0 0 0 0 rgba(208, 48, 80, 0.7);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(208, 48, 80, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(208, 48, 80, 0);
  }
}
</style>
