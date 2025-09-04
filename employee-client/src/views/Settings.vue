<template>
  <div class="settings">
    <n-space vertical size="large">
      <!-- 页面标题 -->
      <div>
        <h2>系统设置</h2>
        <n-text depth="3">配置应用程序的各项参数</n-text>
      </div>

      <!-- 设置分组 -->
      <n-tabs type="segment">
        <n-tab-pane name="general" tab="常规设置">
          <n-card>
            <n-form
              :model="generalSettings"
              label-placement="left"
              label-width="120px"
            >
              <n-form-item label="服务器地址">
                <n-input
                  v-model:value="generalSettings.serverUrl"
                  placeholder="http://localhost:8000"
                />
              </n-form-item>

              <n-form-item label="自动连接设备">
                <n-switch v-model:value="generalSettings.autoConnectDevices" />
              </n-form-item>

              <n-form-item label="最大并发任务">
                <n-input-number
                  v-model:value="generalSettings.maxConcurrentTasks"
                  :min="1"
                  :max="10"
                  style="width: 200px;"
                />
              </n-form-item>

              <n-form-item label="日志级别">
                <n-select
                  v-model:value="generalSettings.logLevel"
                  :options="logLevelOptions"
                  style="width: 200px;"
                />
              </n-form-item>

              <n-form-item label="主题设置">
                <n-radio-group v-model:value="generalSettings.theme">
                  <n-radio-button value="light">浅色</n-radio-button>
                  <n-radio-button value="dark">深色</n-radio-button>
                  <n-radio-button value="auto">跟随系统</n-radio-button>
                </n-radio-group>
              </n-form-item>

              <n-form-item label="启动时最小化">
                <n-switch v-model:value="generalSettings.minimizeOnStart" />
              </n-form-item>

              <n-form-item label="关闭到系统托盘">
                <n-switch v-model:value="generalSettings.minimizeToTray" />
              </n-form-item>
            </n-form>
          </n-card>
        </n-tab-pane>

        <n-tab-pane name="device" tab="设备设置">
          <n-card>
            <n-form
              :model="deviceSettings"
              label-placement="left"
              label-width="120px"
            >
              <n-form-item label="ADB 路径">
                <n-input-group>
                  <n-input
                    v-model:value="deviceSettings.adbPath"
                    placeholder="自动检测 ADB 路径"
                    readonly
                  />
                  <n-button @click="selectAdbPath">浏览</n-button>
                </n-input-group>
              </n-form-item>

              <n-form-item label="设备扫描间隔">
                <n-input-number
                  v-model:value="deviceSettings.scanInterval"
                  :min="1"
                  :max="60"
                  suffix="秒"
                  style="width: 200px;"
                />
              </n-form-item>

              <n-form-item label="连接超时时间">
                <n-input-number
                  v-model:value="deviceSettings.connectionTimeout"
                  :min="5"
                  :max="60"
                  suffix="秒"
                  style="width: 200px;"
                />
              </n-form-item>

              <n-form-item label="默认设备分辨率">
                <n-select
                  v-model:value="deviceSettings.defaultResolution"
                  :options="resolutionOptions"
                  style="width: 200px;"
                />
              </n-form-item>

              <n-form-item label="设备性能模式">
                <n-radio-group v-model:value="deviceSettings.performanceMode">
                  <n-radio-button value="auto">自动</n-radio-button>
                  <n-radio-button value="performance">性能优先</n-radio-button>
                  <n-radio-button value="battery">省电优先</n-radio-button>
                </n-radio-group>
              </n-form-item>
            </n-form>
          </n-card>
        </n-tab-pane>

        <n-tab-pane name="task" tab="任务设置">
          <n-card>
            <n-form
              :model="taskSettings"
              label-placement="left"
              label-width="120px"
            >
              <n-form-item label="默认操作间隔">
                <n-input-number
                  v-model:value="taskSettings.defaultInterval"
                  :min="1"
                  :max="10"
                  :step="0.5"
                  suffix="秒"
                  style="width: 200px;"
                />
              </n-form-item>

              <n-form-item label="失败重试次数">
                <n-input-number
                  v-model:value="taskSettings.retryCount"
                  :min="0"
                  :max="5"
                  style="width: 200px;"
                />
              </n-form-item>

              <n-form-item label="任务超时时间">
                <n-input-number
                  v-model:value="taskSettings.taskTimeout"
                  :min="60"
                  :max="3600"
                  suffix="秒"
                  style="width: 200px;"
                />
              </n-form-item>

              <n-form-item label="自动暂停阈值">
                <n-input-number
                  v-model:value="taskSettings.autoPauseThreshold"
                  :min="1"
                  :max="100"
                  suffix="%"
                  style="width: 200px;"
                />
              </n-form-item>

              <n-form-item label="保存任务历史">
                <n-switch v-model:value="taskSettings.saveHistory" />
              </n-form-item>

              <n-form-item label="任务完成通知">
                <n-switch v-model:value="taskSettings.notifyOnComplete" />
              </n-form-item>
            </n-form>
          </n-card>
        </n-tab-pane>

        <n-tab-pane name="advanced" tab="高级设置">
          <n-card>
            <n-form
              :model="advancedSettings"
              label-placement="left"
              label-width="120px"
            >
              <n-form-item label="调试模式">
                <n-switch v-model:value="advancedSettings.debugMode" />
              </n-form-item>

              <n-form-item label="详细日志">
                <n-switch v-model:value="advancedSettings.verboseLogging" />
              </n-form-item>

              <n-form-item label="性能监控">
                <n-switch v-model:value="advancedSettings.performanceMonitoring" />
              </n-form-item>

              <n-form-item label="自动备份配置">
                <n-switch v-model:value="advancedSettings.autoBackup" />
              </n-form-item>

              <n-form-item label="数据目录">
                <n-input-group>
                  <n-input
                    v-model:value="advancedSettings.dataDirectory"
                    placeholder="默认数据目录"
                    readonly
                  />
                  <n-button @click="selectDataDirectory">选择</n-button>
                </n-input-group>
              </n-form-item>

              <n-form-item label="代理设置">
                <n-input
                  v-model:value="advancedSettings.proxyUrl"
                  placeholder="http://proxy:port"
                />
              </n-form-item>
            </n-form>
          </n-card>
        </n-tab-pane>
      </n-tabs>

      <!-- 操作按钮 -->
      <n-card>
        <n-space justify="space-between">
          <n-space>
            <n-button @click="resetToDefaults">
              <template #icon>
                <n-icon><Refresh /></n-icon>
              </template>
              恢复默认
            </n-button>

            <n-button @click="exportSettings">
              <template #icon>
                <n-icon><Download /></n-icon>
              </template>
              导出配置
            </n-button>

            <n-button @click="importSettings">
              <template #icon>
                <n-icon><CloudUpload /></n-icon>
              </template>
              导入配置
            </n-button>
          </n-space>

          <n-space>
            <n-button @click="saveSettings" type="primary">
              <template #icon>
                <n-icon><Save /></n-icon>
              </template>
              保存设置
            </n-button>
          </n-space>
        </n-space>
      </n-card>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import { Refresh, Download, CloudUpload, Save } from '@vicons/ionicons5'

const message = useMessage()
const dialog = useDialog()

// 设置数据
const generalSettings = ref({
  serverUrl: 'http://localhost:8000',
  autoConnectDevices: true,
  maxConcurrentTasks: 3,
  logLevel: 'info',
  theme: 'light',
  minimizeOnStart: false,
  minimizeToTray: true
})

const deviceSettings = ref({
  adbPath: '',
  scanInterval: 5,
  connectionTimeout: 10,
  defaultResolution: '1080x1920',
  performanceMode: 'auto'
})

const taskSettings = ref({
  defaultInterval: 3,
  retryCount: 2,
  taskTimeout: 300,
  autoPauseThreshold: 80,
  saveHistory: true,
  notifyOnComplete: true
})

const advancedSettings = ref({
  debugMode: false,
  verboseLogging: false,
  performanceMonitoring: true,
  autoBackup: true,
  dataDirectory: '',
  proxyUrl: ''
})

// 选项数据
const logLevelOptions = [
  { label: '调试', value: 'debug' },
  { label: '信息', value: 'info' },
  { label: '警告', value: 'warn' },
  { label: '错误', value: 'error' }
]

const resolutionOptions = [
  { label: '720×1280', value: '720x1280' },
  { label: '1080×1920', value: '1080x1920' },
  { label: '1440×2560', value: '1440x2560' },
  { label: '自动检测', value: 'auto' }
]

// 方法
const saveSettings = async () => {
  try {
    const allSettings = {
      general: generalSettings.value,
      device: deviceSettings.value,
      task: taskSettings.value,
      advanced: advancedSettings.value
    }

    // 保存到本地存储
    localStorage.setItem('app_settings', JSON.stringify(allSettings))

    message.success('设置已保存')
  } catch (error) {
    message.error('保存设置失败')
  }
}

const resetToDefaults = () => {
  dialog.warning({
    title: '确认重置',
    content: '确定要恢复所有设置到默认值吗？此操作不可撤销。',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: () => {
      // 重置为默认值
      generalSettings.value = {
        serverUrl: 'http://localhost:8000',
        autoConnectDevices: true,
        maxConcurrentTasks: 3,
        logLevel: 'info',
        theme: 'light',
        minimizeOnStart: false,
        minimizeToTray: true
      }

      deviceSettings.value = {
        adbPath: '',
        scanInterval: 5,
        connectionTimeout: 10,
        defaultResolution: '1080x1920',
        performanceMode: 'auto'
      }

      taskSettings.value = {
        defaultInterval: 3,
        retryCount: 2,
        taskTimeout: 300,
        autoPauseThreshold: 80,
        saveHistory: true,
        notifyOnComplete: true
      }

      advancedSettings.value = {
        debugMode: false,
        verboseLogging: false,
        performanceMonitoring: true,
        autoBackup: true,
        dataDirectory: '',
        proxyUrl: ''
      }

      message.success('已恢复默认设置')
    }
  })
}

const exportSettings = () => {
  try {
    const allSettings = {
      general: generalSettings.value,
      device: deviceSettings.value,
      task: taskSettings.value,
      advanced: advancedSettings.value,
      exportTime: new Date().toISOString()
    }

    const blob = new Blob([JSON.stringify(allSettings, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)

    const a = document.createElement('a')
    a.href = url
    a.download = `flow-farm-settings-${new Date().toISOString().split('T')[0]}.json`
    a.click()

    URL.revokeObjectURL(url)
    message.success('配置文件已导出')
  } catch (error) {
    message.error('导出配置失败')
  }
}

const importSettings = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'

  input.onchange = async (e) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (!file) return

    try {
      const content = await file.text()
      const settings = JSON.parse(content)

      if (settings.general) generalSettings.value = settings.general
      if (settings.device) deviceSettings.value = settings.device
      if (settings.task) taskSettings.value = settings.task
      if (settings.advanced) advancedSettings.value = settings.advanced

      message.success('配置已导入')
    } catch (error) {
      message.error('导入配置失败，请检查文件格式')
    }
  }

  input.click()
}

const selectAdbPath = async () => {
  try {
    // 这里应该调用 Tauri 的文件选择 API
    message.info('请在弹出的文件选择器中选择 ADB 可执行文件')
    // 模拟选择结果
    setTimeout(() => {
      deviceSettings.value.adbPath = 'C:\\Android\\platform-tools\\adb.exe'
      message.success('ADB 路径已设置')
    }, 1000)
  } catch (error) {
    message.error('选择 ADB 路径失败')
  }
}

const selectDataDirectory = async () => {
  try {
    // 这里应该调用 Tauri 的目录选择 API
    message.info('请在弹出的目录选择器中选择数据目录')
    // 模拟选择结果
    setTimeout(() => {
      advancedSettings.value.dataDirectory = 'C:\\Users\\用户\\Documents\\FlowFarm'
      message.success('数据目录已设置')
    }, 1000)
  } catch (error) {
    message.error('选择数据目录失败')
  }
}

const loadSettings = () => {
  try {
    const savedSettings = localStorage.getItem('app_settings')
    if (savedSettings) {
      const settings = JSON.parse(savedSettings)

      if (settings.general) generalSettings.value = { ...generalSettings.value, ...settings.general }
      if (settings.device) deviceSettings.value = { ...deviceSettings.value, ...settings.device }
      if (settings.task) taskSettings.value = { ...taskSettings.value, ...settings.task }
      if (settings.advanced) advancedSettings.value = { ...advancedSettings.value, ...settings.advanced }
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

// 生命周期
onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings {
  padding: 0;
}

h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

:deep(.n-form-item) {
  margin-bottom: 16px;
}

:deep(.n-tabs-nav) {
  margin-bottom: 24px;
}
</style>
