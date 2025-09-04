<template>
  <div class="statistics">
    <n-space vertical size="large">
      <!-- 页面标题 -->
      <div>
        <h2>关注统计</h2>
        <n-text depth="3">查看关注数据统计和余额信息</n-text>
      </div>

      <!-- 统计概览卡片 -->
      <n-grid :cols="4" :x-gap="16">
        <n-grid-item>
          <n-card>
            <n-statistic label="总关注人数" :value="statistics.totalFollows">
              <template #prefix>
                <n-icon size="24" color="#18a058">
                  <People />
                </n-icon>
              </template>
            </n-statistic>
          </n-card>
        </n-grid-item>

        <n-grid-item>
          <n-card>
            <n-statistic label="今日新增关注" :value="statistics.dailyFollows">
              <template #prefix>
                <n-icon size="24" color="#2080f0">
                  <TrendingUp />
                </n-icon>
              </template>
            </n-statistic>
          </n-card>
        </n-grid-item>

        <n-grid-item>
          <n-card>
            <n-statistic
              label="账户余额"
              :value="statistics.balance"
              :precision="2"
              suffix="元"
            >
              <template #prefix>
                <n-icon size="24" color="#f0a020">
                  <Wallet />
                </n-icon>
              </template>
            </n-statistic>
          </n-card>
        </n-grid-item>

        <n-grid-item>
          <n-card>
            <n-statistic
              label="单次关注费用"
              :value="statistics.costPerFollow"
              :precision="3"
              suffix="元"
            >
              <template #prefix>
                <n-icon size="24" color="#d03050">
                  <PricetagsOutline />
                </n-icon>
              </template>
            </n-statistic>
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- 余额预警 -->
      <n-alert
        v-if="balanceWarning"
        :type="balanceWarning.type"
        :title="balanceWarning.title"
        :show-icon="true"
        closable
      >
        {{ balanceWarning.message }}
      </n-alert>

      <!-- 图表和详细数据 -->
      <n-grid :cols="2" :x-gap="16">
        <!-- 关注趋势图表 -->
        <n-grid-item>
          <n-card title="关注趋势">
            <div class="chart-container">
              <!-- 这里可以集成 ECharts 或其他图表库 -->
              <div class="chart-placeholder">
                <n-space vertical align="center" justify="center" style="height: 300px;">
                  <n-icon size="48" depth="3">
                    <BarChart />
                  </n-icon>
                  <n-text depth="3">关注趋势图表</n-text>
                  <n-text depth="3" style="font-size: 12px;">
                    最近 30 天的关注数据趋势
                  </n-text>
                </n-space>
              </div>
            </div>
          </n-card>
        </n-grid-item>

        <!-- 设备使用统计 -->
        <n-grid-item>
          <n-card title="设备使用统计">
            <n-scrollbar style="max-height: 300px;">
              <n-list>
                <n-list-item v-for="device in deviceStats" :key="device.id">
                  <n-space justify="space-between" align="center" style="width: 100%;">
                    <div>
                      <div>
                        <n-text strong>{{ device.name }}</n-text>
                      </div>
                      <div>
                        <n-text depth="3" style="font-size: 12px;">
                          今日关注: {{ device.todayFollows }} 人
                        </n-text>
                      </div>
                    </div>
                    <div>
                      <n-progress
                        type="line"
                        :percentage="device.usagePercentage"
                        :show-indicator="false"
                        style="width: 80px;"
                      />
                      <n-text style="font-size: 12px; margin-left: 8px;">
                        {{ device.usagePercentage }}%
                      </n-text>
                    </div>
                  </n-space>
                </n-list-item>
              </n-list>
            </n-scrollbar>
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- 费用详情表格 -->
      <n-card title="费用详情">
        <template #header-extra>
          <n-space>
            <n-date-picker
              v-model:value="dateRange"
              type="daterange"
              clearable
              @update:value="handleDateRangeChange"
            />
            <n-button @click="exportData">
              <template #icon>
                <n-icon><Download /></n-icon>
              </template>
              导出数据
            </n-button>
          </n-space>
        </template>

        <n-data-table
          :columns="expenseColumns"
          :data="expenseData"
          :loading="isLoadingExpenses"
          :pagination="{
            pageSize: 15,
            showSizePicker: true,
            pageSizes: [15, 30, 50]
          }"
        />
      </n-card>

      <!-- 快速操作 -->
      <n-card title="快速操作">
        <n-space>
          <n-button type="primary" @click="refreshStatistics">
            <template #icon>
              <n-icon><Refresh /></n-icon>
            </template>
            刷新统计数据
          </n-button>

          <n-button @click="showBalanceDialog = true">
            <template #icon>
              <n-icon><AddCircleOutline /></n-icon>
            </template>
            充值余额
          </n-button>

          <n-button @click="generateReport">
            <template #icon>
              <n-icon><DocumentTextOutline /></n-icon>
            </template>
            生成报告
          </n-button>
        </n-space>
      </n-card>
    </n-space>

    <!-- 充值对话框 -->
    <n-modal v-model:show="showBalanceDialog" preset="dialog" title="账户充值">
      <template #default>
        <n-space vertical>
          <n-alert type="info" :show-icon="false">
            当前余额: {{ statistics.balance.toFixed(2) }} 元
          </n-alert>

          <n-form-item label="充值金额">
            <n-input-number
              v-model:value="rechargeAmount"
              :min="1"
              :precision="2"
              placeholder="请输入充值金额"
              style="width: 100%;"
            >
              <template #suffix>元</template>
            </n-input-number>
          </n-form-item>

          <n-form-item label="支付方式">
            <n-radio-group v-model:value="paymentMethod">
              <n-radio-button value="alipay">支付宝</n-radio-button>
              <n-radio-button value="wechat">微信支付</n-radio-button>
              <n-radio-button value="bank">银行卡</n-radio-button>
            </n-radio-group>
          </n-form-item>
        </n-space>
      </template>
      <template #action>
        <n-space>
          <n-button @click="showBalanceDialog = false">取消</n-button>
          <n-button type="primary" @click="handleRecharge">确认充值</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import { useMessage } from 'naive-ui'
import {
  People, TrendingUp, Wallet, PricetagsOutline, BarChart,
  Download, Refresh, AddCircleOutline, DocumentTextOutline
} from '@vicons/ionicons5'
import { useStatisticsStore } from '../stores/statistics'
import { useDeviceStore } from '../stores/device'

const message = useMessage()
const statisticsStore = useStatisticsStore()
const deviceStore = useDeviceStore()

const isLoadingExpenses = ref(false)
const showBalanceDialog = ref(false)
const rechargeAmount = ref(0)
const paymentMethod = ref('alipay')
const dateRange = ref<[number, number] | null>(null)

// 计算属性
const statistics = computed(() => statisticsStore.statistics)

const balanceWarning = computed(() => {
  const balance = statistics.value.balance
  const costPerFollow = statistics.value.costPerFollow

  if (balance <= 0) {
    return {
      type: 'error',
      title: '余额不足',
      message: '账户余额已用完，请及时充值以继续使用服务。'
    }
  } else if (balance < costPerFollow * 10) {
    return {
      type: 'warning',
      title: '余额预警',
      message: `账户余额不足以完成 10 次关注操作，建议及时充值。`
    }
  } else if (balance < costPerFollow * 50) {
    return {
      type: 'info',
      title: '余额提醒',
      message: `账户余额较低，建议适时充值以避免服务中断。`
    }
  }

  return null
})

// 设备使用统计（模拟数据）
const deviceStats = computed(() => {
  return deviceStore.devices.map(device => ({
    id: device.id,
    name: device.name,
    todayFollows: Math.floor(Math.random() * 50),
    usagePercentage: Math.floor(Math.random() * 100)
  }))
})

// 费用详情数据（模拟数据）
const expenseData = ref([
  {
    id: '1',
    date: '2024-01-15 14:30:00',
    type: '关注操作',
    target: '@用户123',
    cost: 0.05,
    device: '设备1',
    status: '成功'
  },
  {
    id: '2',
    date: '2024-01-15 14:25:00',
    type: '关注操作',
    target: '@用户456',
    cost: 0.05,
    device: '设备2',
    status: '成功'
  }
])

// 费用表格列定义
const expenseColumns: DataTableColumns<any> = [
  {
    title: '时间',
    key: 'date',
    width: 150
  },
  {
    title: '操作类型',
    key: 'type',
    width: 100
  },
  {
    title: '目标',
    key: 'target',
    width: 120
  },
  {
    title: '费用',
    key: 'cost',
    width: 80,
    render: (row) => `¥${row.cost.toFixed(3)}`
  },
  {
    title: '设备',
    key: 'device',
    width: 100
  },
  {
    title: '状态',
    key: 'status',
    width: 80,
    render: (row) => {
      const statusConfig = {
        '成功': { type: 'success' },
        '失败': { type: 'error' },
        '进行中': { type: 'info' }
      }
      const config = statusConfig[row.status as keyof typeof statusConfig]
      return h('n-tag', {
        type: config?.type as any,
        bordered: false
      }, row.status)
    }
  }
]

// 方法
const refreshStatistics = async () => {
  try {
    await statisticsStore.loadStatistics()
    message.success('统计数据已刷新')
  } catch (error) {
    message.error('刷新统计数据失败')
  }
}

const handleDateRangeChange = (value: [number, number] | null) => {
  if (value) {
    // 根据日期范围筛选费用数据
    console.log('日期范围变更:', value)
  }
}

const exportData = () => {
  // 导出统计数据
  message.info('开始导出数据...')

  // 模拟导出过程
  setTimeout(() => {
    message.success('数据导出完成')
  }, 2000)
}

const handleRecharge = () => {
  if (rechargeAmount.value <= 0) {
    message.error('请输入有效的充值金额')
    return
  }

  message.info(`正在使用${paymentMethod.value === 'alipay' ? '支付宝' : paymentMethod.value === 'wechat' ? '微信支付' : '银行卡'}充值 ¥${rechargeAmount.value}`)

  // 模拟充值过程
  setTimeout(() => {
    statistics.value.balance += rechargeAmount.value
    message.success('充值成功')
    showBalanceDialog.value = false
    rechargeAmount.value = 0
  }, 2000)
}

const generateReport = () => {
  message.info('正在生成统计报告...')

  // 模拟报告生成
  setTimeout(() => {
    message.success('统计报告已生成并保存到本地')
  }, 3000)
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    statisticsStore.loadStatistics(),
    deviceStore.loadDevices()
  ])
})
</script>

<style scoped>
.statistics {
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

.chart-container {
  height: 300px;
}

.chart-placeholder {
  border: 2px dashed #e0e0e6;
  border-radius: 8px;
  background-color: #fafafa;
}
</style>
