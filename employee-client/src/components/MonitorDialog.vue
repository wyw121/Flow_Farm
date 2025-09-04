<template>
  <n-modal v-model:show="show" preset="dialog" title="同行监控">
    <template #default>
      <n-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-placement="left"
        label-width="100px"
      >
        <n-form-item label="目标账号" path="targetAccount">
          <n-input
            v-model:value="formData.targetAccount"
            placeholder="请输入要监控的同行账号"
            :maxlength="50"
          />
        </n-form-item>

        <n-form-item label="关键词库" path="keywords">
          <n-dynamic-tags
            v-model:value="formData.keywords"
            :max="20"
            placeholder="输入关键词后按回车添加"
          />
        </n-form-item>

        <n-form-item label="目标关注数" path="targetCount">
          <n-input-number
            v-model:value="formData.targetCount"
            :min="1"
            :max="1000"
            placeholder="目标关注数量"
            style="width: 100%;"
          />
        </n-form-item>

        <n-form-item label="执行设备" path="selectedDevices">
          <n-transfer
            v-model:value="formData.selectedDevices"
            :options="deviceOptions"
            source-title="可用设备"
            target-title="选中设备"
            style="width: 100%;"
          />
        </n-form-item>

        <n-form-item label="监控设置">
          <n-space vertical style="width: 100%;">
            <n-checkbox v-model:checked="formData.autoStart">
              收集完成后自动开始关注
            </n-checkbox>
            <n-checkbox v-model:checked="formData.skipExisting">
              跳过已关注的用户
            </n-checkbox>
            <div>
              <n-text>扫描深度:</n-text>
              <n-slider
                v-model:value="formData.scanDepth"
                :min="10"
                :max="100"
                :step="10"
                :marks="{
                  10: '10条',
                  50: '50条',
                  100: '100条'
                }"
                style="margin: 8px 0;"
              />
            </div>
          </n-space>
        </n-form-item>

        <n-form-item label="预估信息">
          <n-alert type="info" :show-icon="false">
            <div>
              <div>关键词数量: {{ formData.keywords.length }} 个</div>
              <div>目标关注数: {{ formData.targetCount }} 人</div>
              <div>选中设备: {{ formData.selectedDevices.length }} 台</div>
              <div>预估费用: ¥{{ estimatedCost.toFixed(3) }}</div>
              <div>当前余额: ¥{{ currentBalance.toFixed(2) }}</div>
              <div v-if="estimatedCost > currentBalance" style="color: #d03050;">
                ⚠️ 余额不足，请先充值
              </div>
            </div>
          </n-alert>
        </n-form-item>
      </n-form>
    </template>

    <template #action>
      <n-space>
        <n-button @click="handleCancel">取消</n-button>
        <n-button
          type="primary"
          @click="handleSubmit"
          :disabled="!canSubmit"
          :loading="isSubmitting"
        >
          开始监控任务
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { useDeviceStore } from '../stores/device'
import { useStatisticsStore } from '../stores/statistics'

interface Props {
  show: boolean
}

interface Emits {
  (e: 'update:show', value: boolean): void
  (e: 'submit', params: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const message = useMessage()
const deviceStore = useDeviceStore()
const statisticsStore = useStatisticsStore()

const formRef = ref()
const isSubmitting = ref(false)

// 表单数据
const formData = ref({
  targetAccount: '',
  keywords: [] as string[],
  targetCount: 50,
  selectedDevices: [] as string[],
  autoStart: true,
  skipExisting: true,
  scanDepth: 50
})

// 表单验证规则
const rules = {
  targetAccount: [
    {
      required: true,
      message: '请输入目标账号',
      trigger: ['input', 'blur']
    }
  ],
  keywords: [
    {
      type: 'array',
      min: 1,
      message: '请至少添加一个关键词',
      trigger: ['change']
    }
  ],
  targetCount: [
    {
      required: true,
      type: 'number',
      min: 1,
      max: 1000,
      message: '目标关注数必须在1-1000之间',
      trigger: ['change']
    }
  ],
  selectedDevices: [
    {
      type: 'array',
      min: 1,
      message: '请至少选择一台设备',
      trigger: ['change']
    }
  ]
}

// 计算属性
const deviceOptions = computed(() => {
  return deviceStore.connectedDevices.map(device => ({
    label: device.name,
    value: device.id,
    disabled: device.status !== '已连接'
  }))
})

const currentBalance = computed(() => statisticsStore.statistics.balance)
const costPerFollow = computed(() => statisticsStore.statistics.costPerFollow)

const estimatedCost = computed(() => {
  return formData.value.targetCount * costPerFollow.value
})

const canSubmit = computed(() => {
  return formData.value.targetAccount &&
         formData.value.keywords.length > 0 &&
         formData.value.targetCount > 0 &&
         formData.value.selectedDevices.length > 0 &&
         estimatedCost.value <= currentBalance.value &&
         !isSubmitting.value
})

// 监听显示状态
watch(() => props.show, (newShow) => {
  if (!newShow) {
    resetForm()
  }
})

// 方法
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()

    isSubmitting.value = true

    const params = {
      targetAccount: formData.value.targetAccount,
      keywords: formData.value.keywords,
      targetCount: formData.value.targetCount,
      devices: formData.value.selectedDevices,
      settings: {
        autoStart: formData.value.autoStart,
        skipExisting: formData.value.skipExisting,
        scanDepth: formData.value.scanDepth
      },
      estimatedCost: estimatedCost.value
    }

    emit('submit', params)

  } catch (error) {
    // 表单验证失败
    console.error('表单验证失败:', error)
  } finally {
    isSubmitting.value = false
  }
}

const handleCancel = () => {
  emit('update:show', false)
}

const resetForm = () => {
  formData.value = {
    targetAccount: '',
    keywords: [],
    targetCount: 50,
    selectedDevices: [],
    autoStart: true,
    skipExisting: true,
    scanDepth: 50
  }
  isSubmitting.value = false
}
</script>

<style scoped>
:deep(.n-transfer) {
  height: 200px;
}

:deep(.n-dynamic-tags .n-tag) {
  margin: 2px;
}
</style>
