<template>
  <div class="device-management">
    <n-space vertical size="large">
      <!-- 页面标题和操作 -->
      <n-space justify="space-between" align="center">
        <div>
          <h2>设备管理</h2>
          <n-text depth="3">管理最多 10 台设备的连接和状态</n-text>
        </div>
        <n-space>
          <n-button @click="scanDevices" :loading="isScanning">
            <template #icon>
              <n-icon><Search /></n-icon>
            </template>
            扫描设备
          </n-button>
          <n-button type="primary" @click="showAddDeviceDialog = true">
            <template #icon>
              <n-icon><Add /></n-icon>
            </template>
            添加设备
          </n-button>
        </n-space>
      </n-space>

      <!-- 设备统计概览 -->
      <n-grid :cols="4" :x-gap="16">
        <n-grid-item>
          <n-statistic label="总设备数" :value="devices.length" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="已连接" :value="connectedCount" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="离线设备" :value="offlineCount" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="连接率" :value="connectionRate" suffix="%" />
        </n-grid-item>
      </n-grid>

      <!-- 设备列表 -->
      <n-card title="设备列表">
        <n-grid :cols="2" :x-gap="16" :y-gap="16">
          <!-- 10个设备插槽 -->
          <n-grid-item v-for="index in 10" :key="index">
            <DeviceCard 
              :device="getDeviceBySlot(index)" 
              :slot-number="index"
              @connect="handleConnect"
              @disconnect="handleDisconnect"
              @configure="handleConfigure"
              @remove="handleRemove"
            />
          </n-grid-item>
        </n-grid>
      </n-card>

      <!-- 设备日志 -->
      <n-card title="设备日志">
        <n-scrollbar style="max-height: 300px;">
          <n-log 
            :log="deviceLogs.join('\n')"
            language="text"
            :loading="false"
          />
        </n-scrollbar>
      </n-card>
    </n-space>

    <!-- 添加设备对话框 -->
    <n-modal v-model:show="showAddDeviceDialog" preset="dialog" title="添加设备">
      <template #default>
        <n-form ref="addDeviceFormRef" :model="addDeviceForm" :rules="addDeviceRules">
          <n-form-item label="连接方式" path="connectionType">
            <n-radio-group v-model:value="addDeviceForm.connectionType">
              <n-radio-button value="usb">USB 连接</n-radio-button>
              <n-radio-button value="wifi">WiFi 连接</n-radio-button>
            </n-radio-group>
          </n-form-item>
          
          <n-form-item 
            v-if="addDeviceForm.connectionType === 'wifi'" 
            label="设备地址" 
            path="address"
          >
            <n-input 
              v-model:value="addDeviceForm.address" 
              placeholder="例如: 192.168.1.100:5555"
            />
          </n-form-item>
          
          <n-form-item label="设备名称" path="name">
            <n-input 
              v-model:value="addDeviceForm.name" 
              placeholder="给设备起个名字"
            />
          </n-form-item>
        </n-form>
      </template>
      <template #action>
        <n-space>
          <n-button @click="showAddDeviceDialog = false">取消</n-button>
          <n-button type="primary" @click="handleAddDevice">添加</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { Search, Add } from '@vicons/ionicons5'
import { useDeviceStore } from '../stores/device'
import DeviceCard from '../components/DeviceCard.vue'
import type { DeviceInfo } from '../types'

const message = useMessage()
const deviceStore = useDeviceStore()

const isScanning = ref(false)
const showAddDeviceDialog = ref(false)
const addDeviceFormRef = ref()

// 添加设备表单
const addDeviceForm = ref({
  connectionType: 'usb',
  address: '',
  name: ''
})

const addDeviceRules = {
  address: [
    {
      required: true,
      message: '请输入设备地址',
      trigger: ['input', 'blur']
    },
    {
      pattern: /^(\d{1,3}\.){3}\d{1,3}:\d{1,5}$/,
      message: '请输入正确的IP:端口格式',
      trigger: ['input', 'blur']
    }
  ],
  name: [
    {
      required: true,
      message: '请输入设备名称',
      trigger: ['input', 'blur']
    }
  ]
}

// 设备日志
const deviceLogs = ref<string[]>([
  '[2024-01-01 10:00:00] 开始扫描设备...',
  '[2024-01-01 10:00:05] 发现设备: 192.168.1.100:5555',
  '[2024-01-01 10:00:10] 设备连接成功: Xiaomi-1'
])

// 计算属性
const devices = computed(() => deviceStore.devices)

const connectedCount = computed(() => 
  devices.value.filter(device => device.status === '已连接').length
)

const offlineCount = computed(() => 
  devices.value.filter(device => device.status === '离线').length
)

const connectionRate = computed(() => {
  if (devices.value.length === 0) return 0
  return Math.round((connectedCount.value / devices.value.length) * 100)
})

// 方法
const getDeviceBySlot = (slotNumber: number): DeviceInfo | null => {
  // 返回指定插槽的设备，如果没有则返回 null
  return devices.value[slotNumber - 1] || null
}

const scanDevices = async () => {
  isScanning.value = true
  try {
    deviceStore.startDeviceScan()
    addLog('开始扫描设备...')
    
    // 模拟扫描过程
    setTimeout(() => {
      addLog('扫描完成')
      isScanning.value = false
      message.success('设备扫描完成')
    }, 3000)
  } catch (error) {
    isScanning.value = false
    message.error('设备扫描失败')
  }
}

const handleConnect = async (device: DeviceInfo) => {
  try {
    addLog(`正在连接设备: ${device.name}`)
    await deviceStore.connectDevice(device.id)
    addLog(`设备连接成功: ${device.name}`)
    message.success(`设备 ${device.name} 连接成功`)
  } catch (error) {
    addLog(`设备连接失败: ${device.name}`)
    message.error('设备连接失败')
  }
}

const handleDisconnect = async (device: DeviceInfo) => {
  try {
    addLog(`正在断开设备: ${device.name}`)
    await deviceStore.disconnectDevice(device.id)
    addLog(`设备已断开: ${device.name}`)
    message.success(`设备 ${device.name} 已断开连接`)
  } catch (error) {
    addLog(`设备断开失败: ${device.name}`)
    message.error('设备断开失败')
  }
}

const handleConfigure = (device: DeviceInfo) => {
  message.info(`配置设备: ${device.name}`)
  // TODO: 实现设备配置功能
}

const handleRemove = (device: DeviceInfo) => {
  deviceStore.removeDevice(device.id)
  addLog(`设备已移除: ${device.name}`)
  message.success(`设备 ${device.name} 已移除`)
}

const handleAddDevice = async () => {
  try {
    await addDeviceFormRef.value?.validate()
    
    const deviceInfo: DeviceInfo = {
      id: addDeviceForm.value.address || `usb-device-${Date.now()}`,
      name: addDeviceForm.value.name,
      status: '离线',
      lastSeen: new Date().toISOString(),
      capabilities: []
    }
    
    deviceStore.addDevice(deviceInfo)
    addLog(`新设备已添加: ${deviceInfo.name}`)
    message.success('设备添加成功')
    
    showAddDeviceDialog.value = false
    
    // 重置表单
    addDeviceForm.value = {
      connectionType: 'usb',
      address: '',
      name: ''
    }
  } catch (error) {
    // 表单验证失败
  }
}

const addLog = (message: string) => {
  const timestamp = new Date().toLocaleString('zh-CN')
  deviceLogs.value.push(`[${timestamp}] ${message}`)
  
  // 保持最新的 50 条日志
  if (deviceLogs.value.length > 50) {
    deviceLogs.value = deviceLogs.value.slice(-50)
  }
}

// 生命周期
onMounted(async () => {
  await deviceStore.loadDevices()
  deviceStore.setupDeviceListener()
})
</script>

<style scoped>
.device-management {
  padding: 0;
}

h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.n-statistic {
  text-align: center;
}
</style>
