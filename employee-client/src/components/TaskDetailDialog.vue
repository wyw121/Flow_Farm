<template>
  <n-modal v-model:show="show" preset="card" title="任务详情" style="width: 600px;">
    <template v-if="task">
      <n-space vertical size="large">
        <!-- 基本信息 -->
        <n-descriptions :column="2" bordered>
          <n-descriptions-item label="任务名称">
            {{ task.name }}
          </n-descriptions-item>
          <n-descriptions-item label="任务类型">
            <n-tag :type="getTaskTypeTag(task.type)">
              {{ getTaskTypeName(task.type) }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="任务状态">
            <n-tag :type="getStatusTag(task.status)">
              {{ task.status }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="执行进度">
            <n-progress
              type="line"
              :percentage="Math.round(task.progress * 100)"
              :color="getProgressColor(task.status)"
            />
          </n-descriptions-item>
          <n-descriptions-item label="创建时间">
            {{ formatTime(task.createdAt) }}
          </n-descriptions-item>
          <n-descriptions-item label="完成时间">
            {{ task.completedAt ? formatTime(task.completedAt) : '-' }}
          </n-descriptions-item>
        </n-descriptions>

        <!-- 执行设备信息 -->
        <n-card title="执行设备" size="small">
          <div v-if="task.deviceId">
            <n-space align="center">
              <n-avatar size="small" :style="{ backgroundColor: getDeviceStatusColor(deviceInfo?.status) }">
                📱
              </n-avatar>
              <div>
                <div><n-text strong>{{ deviceInfo?.name || task.deviceId }}</n-text></div>
                <div><n-text depth="3" style="font-size: 12px;">{{ deviceInfo?.status || '未知' }}</n-text></div>
              </div>
            </n-space>
          </div>
          <div v-else>
            <n-text depth="3">未分配设备</n-text>
          </div>
        </n-card>

        <!-- 任务参数 -->
        <n-card title="任务参数" size="small">
          <div v-if="task.parameters">
            <n-space vertical size="small">
              <div v-for="(value, key) in task.parameters" :key="key">
                <n-text strong>{{ formatParameterKey(key) }}: </n-text>
                <n-text>{{ formatParameterValue(key, value) }}</n-text>
              </div>
            </n-space>
          </div>
          <div v-else>
            <n-text depth="3">无参数信息</n-text>
          </div>
        </n-card>

        <!-- 执行日志 -->
        <n-card title="执行日志" size="small">
          <n-scrollbar style="max-height: 200px;">
            <n-log
              :log="taskLogs.join('\n')"
              language="text"
              :loading="false"
            />
          </n-scrollbar>
        </n-card>

        <!-- 统计信息 -->
        <n-card title="执行统计" size="small" v-if="taskStats">
          <n-grid :cols="3" :x-gap="16">
            <n-grid-item>
              <n-statistic label="总数" :value="taskStats.total" />
            </n-grid-item>
            <n-grid-item>
              <n-statistic label="成功" :value="taskStats.success" />
            </n-grid-item>
            <n-grid-item>
              <n-statistic label="失败" :value="taskStats.failed" />
            </n-grid-item>
          </n-grid>
        </n-card>
      </n-space>
    </template>

    <template #action>
      <n-space justify="end">
        <n-button @click="exportTaskLog" v-if="task">
          <template #icon>
            <n-icon><Download /></n-icon>
          </template>
          导出日志
        </n-button>
        <n-button @click="show = false">关闭</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { Download } from '@vicons/ionicons5'
import { useDeviceStore } from '../stores/device'
import type { TaskInfo } from '../types'

interface Props {
  show: boolean
  task: TaskInfo | null
}

interface Emits {
  (e: 'update:show', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const message = useMessage()
const deviceStore = useDeviceStore()

// 任务日志（模拟数据）
const taskLogs = ref<string[]>([])

// 任务统计（模拟数据）
const taskStats = ref<{
  total: number
  success: number
  failed: number
} | null>(null)

// 计算属性
const deviceInfo = computed(() => {
  if (!props.task?.deviceId) return null
  return deviceStore.devices.find(device => device.id === props.task?.deviceId)
})

// 监听任务变化，加载对应的日志和统计
watch(() => props.task, (newTask) => {
  if (newTask) {
    loadTaskDetails(newTask)
  }
})

// 方法
const getTaskTypeTag = (type: string) => {
  const typeConfig: { [key: string]: string } = {
    'follow_contacts': 'success',
    'monitor_competitor': 'info'
  }
  return typeConfig[type] || 'default'
}

const getTaskTypeName = (type: string) => {
  const typeNames: { [key: string]: string } = {
    'follow_contacts': '关注通讯录',
    'monitor_competitor': '同行监控'
  }
  return typeNames[type] || type
}

const getStatusTag = (status: string) => {
  const statusConfig: { [key: string]: string } = {
    '等待中': 'default',
    '进行中': 'info',
    '已完成': 'success',
    '失败': 'error'
  }
  return statusConfig[status] || 'default'
}

const getProgressColor = (status: string) => {
  switch (status) {
    case '已完成':
      return '#18a058'
    case '失败':
      return '#d03050'
    default:
      return '#2080f0'
  }
}

const getDeviceStatusColor = (status?: string) => {
  switch (status) {
    case '已连接':
      return '#18a058'
    case '离线':
      return '#909399'
    case '连接中':
      return '#2080f0'
    case '错误':
      return '#d03050'
    default:
      return '#909399'
  }
}

const formatTime = (timeString: string) => {
  return new Date(timeString).toLocaleString('zh-CN')
}

const formatParameterKey = (key: string) => {
  const keyNames: { [key: string]: string } = {
    'contactFile': '通讯录文件',
    'targetAccount': '目标账号',
    'keywords': '关键词',
    'targetCount': '目标数量',
    'skipExisting': '跳过已关注',
    'randomOrder': '随机顺序',
    'interval': '间隔时间',
    'autoStart': '自动开始',
    'scanDepth': '扫描深度'
  }
  return keyNames[key] || key
}

const formatParameterValue = (key: string, value: any) => {
  if (typeof value === 'boolean') {
    return value ? '是' : '否'
  }
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  if (key === 'interval') {
    return `${value}秒`
  }
  return String(value)
}

const loadTaskDetails = (task: TaskInfo) => {
  // 模拟加载任务日志
  taskLogs.value = [
    `[${formatTime(task.createdAt)}] 任务创建: ${task.name}`,
    `[${formatTime(task.createdAt)}] 开始执行任务`,
    `[${new Date().toISOString()}] 任务进行中...`
  ]

  // 模拟加载任务统计
  if (task.status === '已完成' || task.status === '进行中') {
    const total = Math.floor(Math.random() * 100) + 20
    const success = Math.floor(total * task.progress)
    const failed = Math.floor((total - success) * 0.1)

    taskStats.value = {
      total,
      success,
      failed
    }
  } else {
    taskStats.value = null
  }
}

const exportTaskLog = () => {
  if (!props.task) return

  const logContent = taskLogs.value.join('\n')
  const blob = new Blob([logContent], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)

  const a = document.createElement('a')
  a.href = url
  a.download = `task_${props.task.id}_log.txt`
  a.click()

  URL.revokeObjectURL(url)
  message.success('日志文件已下载')
}
</script>

<style scoped>
.n-statistic {
  text-align: center;
}

:deep(.n-log) {
  font-size: 12px;
  line-height: 1.4;
}
</style>
