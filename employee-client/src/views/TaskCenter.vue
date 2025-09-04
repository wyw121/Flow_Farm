<template>
  <div class="task-center">
    <n-space vertical size="large">
      <!-- 页面标题和操作 -->
      <n-space justify="space-between" align="center">
        <div>
          <h2>任务中心</h2>
          <n-text depth="3">管理和监控所有自动化任务</n-text>
        </div>
        <n-space>
          <n-button @click="refreshTasks" :loading="isLoading">
            <template #icon>
              <n-icon><Refresh /></n-icon>
            </template>
            刷新
          </n-button>
          <n-dropdown :options="createTaskOptions" @select="handleCreateTask">
            <n-button type="primary">
              <template #icon>
                <n-icon><Add /></n-icon>
              </template>
              创建任务
            </n-button>
          </n-dropdown>
        </n-space>
      </n-space>

      <!-- 任务统计 -->
      <n-grid :cols="4" :x-gap="16">
        <n-grid-item>
          <n-statistic label="总任务数" :value="totalTasks" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="进行中" :value="activeTasks" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="已完成" :value="completedTasks" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="成功率" :value="successRate" suffix="%" />
        </n-grid-item>
      </n-grid>

      <!-- 任务列表 -->
      <n-card title="任务列表">
        <template #header-extra>
          <n-space>
            <n-select
              v-model:value="statusFilter"
              :options="statusFilterOptions"
              placeholder="筛选状态"
              clearable
              style="width: 120px;"
            />
            <n-select
              v-model:value="typeFilter"
              :options="typeFilterOptions"
              placeholder="筛选类型"
              clearable
              style="width: 120px;"
            />
          </n-space>
        </template>

        <n-data-table
          :columns="taskColumns"
          :data="filteredTasks"
          :loading="isLoading"
          :pagination="{
            pageSize: 10,
            showSizePicker: true,
            pageSizes: [10, 20, 50]
          }"
          striped
        />
      </n-card>
    </n-space>

    <!-- 关注通讯录任务对话框 -->
    <ContactFollowDialog
      v-model:show="showContactDialog"
      @submit="handleContactFollow"
    />

    <!-- 同行监控任务对话框 -->
    <MonitorDialog
      v-model:show="showMonitorDialog"
      @submit="handleMonitorStart"
    />

    <!-- 任务详情对话框 -->
    <TaskDetailDialog
      v-model:show="showTaskDetail"
      :task="selectedTask"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import { useMessage } from 'naive-ui'
import { Refresh, Add, Eye, Pause, Play, Stop } from '@vicons/ionicons5'
import { useTaskStore } from '../stores/task'
import { useDeviceStore } from '../stores/device'
import ContactFollowDialog from '../components/ContactFollowDialog.vue'
import MonitorDialog from '../components/MonitorDialog.vue'
import TaskDetailDialog from '../components/TaskDetailDialog.vue'
import type { TaskInfo } from '../types'

const message = useMessage()
const taskStore = useTaskStore()
const deviceStore = useDeviceStore()

const isLoading = ref(false)
const showContactDialog = ref(false)
const showMonitorDialog = ref(false)
const showTaskDetail = ref(false)
const selectedTask = ref<TaskInfo | null>(null)

// 筛选器
const statusFilter = ref<string | null>(null)
const typeFilter = ref<string | null>(null)

// 筛选选项
const statusFilterOptions = [
  { label: '等待中', value: '等待中' },
  { label: '进行中', value: '进行中' },
  { label: '已完成', value: '已完成' },
  { label: '失败', value: '失败' }
]

const typeFilterOptions = [
  { label: '关注通讯录', value: 'follow_contacts' },
  { label: '同行监控', value: 'monitor_competitor' }
]

// 创建任务选项
const createTaskOptions = [
  {
    label: '关注通讯录用户',
    key: 'follow_contacts',
    icon: () => h('span', '👥')
  },
  {
    label: '同行监控',
    key: 'monitor_competitor',
    icon: () => h('span', '🔍')
  }
]

// 任务表格列定义
const taskColumns: DataTableColumns<TaskInfo> = [
  {
    title: '任务名称',
    key: 'name',
    width: 200,
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: '类型',
    key: 'type',
    width: 120,
    render: (row) => {
      const typeMap: { [key: string]: string } = {
        follow_contacts: '关注通讯录',
        monitor_competitor: '同行监控'
      }
      return typeMap[row.type] || row.type
    }
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) => {
      const statusConfig = {
        '等待中': { type: 'default', color: '#909399' },
        '进行中': { type: 'info', color: '#2080f0' },
        '已完成': { type: 'success', color: '#18a058' },
        '失败': { type: 'error', color: '#d03050' }
      }
      const config = statusConfig[row.status as keyof typeof statusConfig]
      return h('n-tag', {
        type: config?.type as any,
        bordered: false,
        style: { color: config?.color }
      }, row.status)
    }
  },
  {
    title: '进度',
    key: 'progress',
    width: 120,
    render: (row) => {
      return h('n-progress', {
        type: 'line',
        percentage: Math.round(row.progress * 100),
        showIndicator: false,
        height: 6,
        color: row.status === '已完成' ? '#18a058' : '#2080f0'
      })
    }
  },
  {
    title: '设备',
    key: 'deviceId',
    width: 120,
    render: (row) => {
      if (!row.deviceId) return '-'
      const device = deviceStore.devices.find(d => d.id === row.deviceId)
      return device?.name || row.deviceId
    }
  },
  {
    title: '创建时间',
    key: 'createdAt',
    width: 160,
    render: (row) => {
      return new Date(row.createdAt).toLocaleString('zh-CN')
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render: (row) => {
      return h('n-space', { size: 'small' }, [
        h('n-button', {
          size: 'tiny',
          onClick: () => viewTaskDetail(row)
        }, {
          icon: () => h('n-icon', null, h(Eye)),
          default: () => '详情'
        }),
        h('n-button', {
          size: 'tiny',
          type: row.status === '进行中' ? 'warning' : 'primary',
          disabled: row.status === '已完成' || row.status === '失败',
          onClick: () => toggleTask(row)
        }, {
          icon: () => h('n-icon', null,
            row.status === '进行中' ? h(Pause) : h(Play)
          ),
          default: () => row.status === '进行中' ? '暂停' : '开始'
        }),
        h('n-button', {
          size: 'tiny',
          type: 'error',
          disabled: row.status === '已完成',
          onClick: () => stopTask(row)
        }, {
          icon: () => h('n-icon', null, h(Stop)),
          default: () => '停止'
        })
      ])
    }
  }
]

// 计算属性
const totalTasks = computed(() => taskStore.tasks.length)
const activeTasks = computed(() =>
  taskStore.tasks.filter(task => task.status === '进行中').length
)
const completedTasks = computed(() =>
  taskStore.tasks.filter(task => task.status === '已完成').length
)
const successRate = computed(() => {
  if (totalTasks.value === 0) return 0
  return Math.round((completedTasks.value / totalTasks.value) * 100)
})

const filteredTasks = computed(() => {
  let tasks = taskStore.tasks

  if (statusFilter.value) {
    tasks = tasks.filter(task => task.status === statusFilter.value)
  }

  if (typeFilter.value) {
    tasks = tasks.filter(task => task.type === typeFilter.value)
  }

  return tasks
})

// 方法
const refreshTasks = async () => {
  isLoading.value = true
  try {
    await taskStore.loadTasks()
    message.success('任务列表已刷新')
  } catch (error) {
    message.error('刷新任务列表失败')
  } finally {
    isLoading.value = false
  }
}

const handleCreateTask = (key: string) => {
  switch (key) {
    case 'follow_contacts':
      showContactDialog.value = true
      break
    case 'monitor_competitor':
      showMonitorDialog.value = true
      break
  }
}

const handleContactFollow = async (params: any) => {
  try {
    await taskStore.createFollowTask(params)
    message.success('关注任务已创建')
    showContactDialog.value = false
    await refreshTasks()
  } catch (error) {
    message.error('创建关注任务失败')
  }
}

const handleMonitorStart = async (params: any) => {
  try {
    await taskStore.createMonitorTask(params)
    message.success('监控任务已启动')
    showMonitorDialog.value = false
    await refreshTasks()
  } catch (error) {
    message.error('启动监控任务失败')
  }
}

const viewTaskDetail = (task: TaskInfo) => {
  selectedTask.value = task
  showTaskDetail.value = true
}

const toggleTask = async (task: TaskInfo) => {
  try {
    if (task.status === '进行中') {
      // 暂停任务
      message.info(`任务 ${task.name} 已暂停`)
    } else {
      // 开始任务
      message.info(`任务 ${task.name} 已开始`)
    }
    await refreshTasks()
  } catch (error) {
    message.error('操作任务失败')
  }
}

const stopTask = async (task: TaskInfo) => {
  try {
    message.info(`任务 ${task.name} 已停止`)
    await refreshTasks()
  } catch (error) {
    message.error('停止任务失败')
  }
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    taskStore.loadTasks(),
    deviceStore.loadDevices()
  ])
})
</script>

<style scoped>
.task-center {
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
