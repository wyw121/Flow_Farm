<template>
  <div class="dashboard">
    <n-grid :cols="12" :x-gap="16" :y-gap="16">
      <!-- 设备状态卡片 -->
      <n-grid-item :span="4">
        <n-card title="设备状态" size="small">
          <template #header-extra>
            <n-button text @click="refreshDevices">
              <template #icon>
                <n-icon><Refresh /></n-icon>
              </template>
            </n-button>
          </template>
          <n-space vertical>
            <n-statistic label="已连接设备" :value="connectedDevices.length" />
            <n-statistic label="总设备数" :value="deviceStore.devices.length" />
            <n-progress 
              type="line" 
              :percentage="deviceConnectionPercentage" 
              :color="deviceConnectionPercentage > 50 ? '#18a058' : '#f0a020'"
            />
            <n-button type="primary" size="small" @click="$router.push('/devices')">
              管理设备
            </n-button>
          </n-space>
        </n-card>
      </n-grid-item>

      <!-- 任务状态卡片 -->
      <n-grid-item :span="4">
        <n-card title="任务状态" size="small">
          <n-space vertical>
            <n-statistic label="进行中任务" :value="activeTasks.length" />
            <n-statistic label="今日完成" :value="todayCompletedTasks" />
            <n-progress 
              type="line" 
              :percentage="taskCompletionPercentage" 
              color="#18a058"
            />
            <n-button type="primary" size="small" @click="$router.push('/tasks')">
              查看任务
            </n-button>
          </n-space>
        </n-card>
      </n-grid-item>

      <!-- 关注统计卡片 -->
      <n-grid-item :span="4">
        <n-card title="关注统计" size="small">
          <n-space vertical>
            <n-statistic label="总关注数" :value="statistics.totalFollows" />
            <n-statistic label="今日新增" :value="statistics.dailyFollows" />
            <n-statistic 
              label="账户余额" 
              :value="statistics.balance" 
              :precision="2"
              suffix="元"
            />
            <n-button type="primary" size="small" @click="$router.push('/statistics')">
              详细统计
            </n-button>
          </n-space>
        </n-card>
      </n-grid-item>

      <!-- 快速操作面板 -->
      <n-grid-item :span="8">
        <n-card title="快速操作" size="small">
          <n-grid :cols="2" :x-gap="16" :y-gap="16">
            <n-grid-item>
              <n-card embedded>
                <n-space vertical align="center">
                  <n-icon size="48" color="#18a058">
                    <People />
                  </n-icon>
                  <h4>关注通讯录用户</h4>
                  <p>上传通讯录文件，自动关注联系人</p>
                  <n-button type="primary" @click="showContactFollowDialog = true">
                    开始任务
                  </n-button>
                </n-space>
              </n-card>
            </n-grid-item>
            <n-grid-item>
              <n-card embedded>
                <n-space vertical align="center">
                  <n-icon size="48" color="#2080f0">
                    <Search />
                  </n-icon>
                  <h4>同行监控</h4>
                  <p>监控同行账号，收集潜在用户</p>
                  <n-button type="primary" @click="showMonitorDialog = true">
                    开始监控
                  </n-button>
                </n-space>
              </n-card>
            </n-grid-item>
          </n-grid>
        </n-card>
      </n-grid-item>

      <!-- 最近活动 -->
      <n-grid-item :span="4">
        <n-card title="最近活动" size="small">
          <n-scrollbar style="max-height: 200px;">
            <n-list>
              <n-list-item v-for="activity in recentActivities" :key="activity.id">
                <n-space align="center">
                  <n-avatar size="small" :style="{ backgroundColor: getActivityColor(activity.type) }">
                    {{ getActivityIcon(activity.type) }}
                  </n-avatar>
                  <div>
                    <div>{{ activity.message }}</div>
                    <n-text depth="3" style="font-size: 12px;">
                      {{ formatTime(activity.timestamp) }}
                    </n-text>
                  </div>
                </n-space>
              </n-list-item>
            </n-list>
          </n-scrollbar>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 关注通讯录对话框 -->
    <ContactFollowDialog 
      v-model:show="showContactFollowDialog"
      @submit="handleContactFollow"
    />

    <!-- 同行监控对话框 -->
    <MonitorDialog 
      v-model:show="showMonitorDialog"
      @submit="handleMonitorStart"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { Refresh, People, Search } from '@vicons/ionicons5'
import { useDeviceStore } from '../stores/device'
import { useTaskStore } from '../stores/task'
import { useStatisticsStore } from '../stores/statistics'
import ContactFollowDialog from '../components/ContactFollowDialog.vue'
import MonitorDialog from '../components/MonitorDialog.vue'

const message = useMessage()
const deviceStore = useDeviceStore()
const taskStore = useTaskStore()
const statisticsStore = useStatisticsStore()

const showContactFollowDialog = ref(false)
const showMonitorDialog = ref(false)

// 计算属性
const connectedDevices = computed(() => deviceStore.connectedDevices)
const activeTasks = computed(() => taskStore.activeTasks)
const statistics = computed(() => statisticsStore.statistics)

const deviceConnectionPercentage = computed(() => {
  if (deviceStore.devices.length === 0) return 0
  return Math.round((connectedDevices.value.length / deviceStore.devices.length) * 100)
})

const taskCompletionPercentage = computed(() => {
  const total = taskStore.tasks.length
  if (total === 0) return 0
  const completed = taskStore.tasks.filter(task => task.status === '已完成').length
  return Math.round((completed / total) * 100)
})

const todayCompletedTasks = computed(() => {
  const today = new Date().toDateString()
  return taskStore.tasks.filter(task => 
    task.status === '已完成' && 
    task.completedAt && 
    new Date(task.completedAt).toDateString() === today
  ).length
})

// 最近活动
const recentActivities = ref([
  {
    id: '1',
    type: 'device',
    message: '设备 Xiaomi-1 已连接',
    timestamp: new Date(Date.now() - 300000) // 5分钟前
  },
  {
    id: '2',
    type: 'task',
    message: '关注任务已完成，共关注 15 个用户',
    timestamp: new Date(Date.now() - 600000) // 10分钟前
  },
  {
    id: '3',
    type: 'follow',
    message: '成功关注用户 @张三',
    timestamp: new Date(Date.now() - 900000) // 15分钟前
  }
])

// 方法
const refreshDevices = async () => {
  try {
    await deviceStore.loadDevices()
    message.success('设备列表已刷新')
  } catch (error) {
    message.error('刷新设备列表失败')
  }
}

const handleContactFollow = async (params: any) => {
  try {
    await taskStore.createFollowTask(params)
    message.success('关注任务已创建')
    showContactFollowDialog.value = false
  } catch (error) {
    message.error('创建关注任务失败')
  }
}

const handleMonitorStart = async (params: any) => {
  try {
    await taskStore.createMonitorTask(params)
    message.success('监控任务已启动')
    showMonitorDialog.value = false
  } catch (error) {
    message.error('启动监控任务失败')
  }
}

const getActivityColor = (type: string) => {
  const colors: { [key: string]: string } = {
    device: '#18a058',
    task: '#2080f0',
    follow: '#f0a020',
    error: '#d03050'
  }
  return colors[type] || '#909399'
}

const getActivityIcon = (type: string) => {
  const icons: { [key: string]: string } = {
    device: '📱',
    task: '⚡',
    follow: '👥',
    error: '❌'
  }
  return icons[type] || '📌'
}

const formatTime = (date: Date) => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  
  const days = Math.floor(hours / 24)
  return `${days}天前`
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    deviceStore.loadDevices(),
    taskStore.loadTasks(),
    statisticsStore.loadStatistics()
  ])
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.n-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.n-statistic {
  text-align: center;
}

h4 {
  margin: 8px 0;
  font-weight: 600;
}

p {
  margin: 4px 0 12px 0;
  color: #909399;
  font-size: 14px;
}
</style>
