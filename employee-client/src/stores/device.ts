import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { DeviceInfo } from '../types'

export const useDeviceStore = defineStore('device', () => {
  const devices = ref<DeviceInfo[]>([])
  const isScanning = ref(false)

  const connectedDevices = computed(() =>
    devices.value.filter(device => device.status === '已连接')
  )

  const loadDevices = async () => {
    try {
      const { invoke } = await import('@tauri-apps/api/core')
      const deviceList = await invoke<DeviceInfo[]>('get_devices')
      devices.value = deviceList
    } catch (error) {
      console.error('加载设备失败:', error)
    }
  }

  const connectDevice = async (deviceId: string) => {
    try {
      const { invoke } = await import('@tauri-apps/api/core')

      // 更新设备状态为连接中
      const device = devices.value.find(d => d.id === deviceId)
      if (device) {
        device.status = '连接中'
      }

      const result = await invoke<string>('connect_device', { deviceId })

      // 重新加载设备列表
      await loadDevices()

      return result
    } catch (error) {
      // 恢复设备状态
      const device = devices.value.find(d => d.id === deviceId)
      if (device) {
        device.status = '离线'
      }
      console.error('连接设备失败:', error)
      throw error
    }
  }

  const disconnectDevice = async (deviceId: string) => {
    try {
      const { invoke } = await import('@tauri-apps/api/core')
      const result = await invoke<string>('disconnect_device', { deviceId })

      // 重新加载设备列表
      await loadDevices()

      return result
    } catch (error) {
      console.error('断开设备失败:', error)
      throw error
    }
  }

  const startDeviceScan = () => {
    isScanning.value = true
    // 设备扫描由后端自动进行，这里只是更新UI状态
    setTimeout(() => {
      isScanning.value = false
    }, 3000)
  }

  // 监听设备更新事件
  const setupDeviceListener = async () => {
    try {
      const { listen } = await import('@tauri-apps/api/event')
      await listen('devices_updated', (event) => {
        const updatedDevices = event.payload as { [key: string]: DeviceInfo }
        devices.value = Object.values(updatedDevices)
      })
    } catch (error) {
      console.error('设置设备监听器失败:', error)
    }
  }

  // 添加新设备
  const addDevice = (deviceInfo: DeviceInfo) => {
    const existingIndex = devices.value.findIndex(d => d.id === deviceInfo.id)
    if (existingIndex >= 0) {
      devices.value[existingIndex] = deviceInfo
    } else {
      devices.value.push(deviceInfo)
    }
  }

  // 移除设备
  const removeDevice = (deviceId: string) => {
    const index = devices.value.findIndex(d => d.id === deviceId)
    if (index >= 0) {
      devices.value.splice(index, 1)
    }
  }

  return {
    devices,
    isScanning,
    connectedDevices,
    loadDevices,
    connectDevice,
    disconnectDevice,
    startDeviceScan,
    setupDeviceListener,
    addDevice,
    removeDevice
  }
})
