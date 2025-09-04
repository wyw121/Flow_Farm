<template>
  <n-modal v-model:show="show" preset="dialog" title="关注通讯录用户">
    <template #default>
      <n-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-placement="left"
        label-width="100px"
      >
        <n-form-item label="通讯录文件" path="contactFile">
          <n-upload
            :file-list="fileList"
            :max="1"
            accept=".txt,.csv,.json"
            @update:file-list="handleFileChange"
            @before-upload="beforeUpload"
          >
            <n-upload-dragger>
              <div style="margin-bottom: 12px;">
                <n-icon size="48" :depth="3">
                  <DocumentTextOutline />
                </n-icon>
              </div>
              <n-text style="font-size: 16px;">
                点击或拖拽文件到此区域上传
              </n-text>
              <n-p depth="3" style="margin: 8px 0 0 0;">
                支持 TXT、CSV、JSON 格式的通讯录文件
              </n-p>
            </n-upload-dragger>
          </n-upload>
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

        <n-form-item label="任务设置">
          <n-space vertical style="width: 100%;">
            <n-checkbox v-model:checked="formData.skipExisting">
              跳过已关注的用户
            </n-checkbox>
            <n-checkbox v-model:checked="formData.randomOrder">
              随机执行顺序
            </n-checkbox>
            <div>
              <n-text>关注间隔:</n-text>
              <n-slider
                v-model:value="formData.interval"
                :min="1"
                :max="10"
                :step="0.5"
                :marks="{
                  1: '1秒',
                  5: '5秒',
                  10: '10秒'
                }"
                style="margin: 8px 0;"
              />
            </div>
          </n-space>
        </n-form-item>

        <n-form-item label="预估费用">
          <n-alert type="info" :show-icon="false">
            <div>
              <div>文件联系人数量: {{ contactCount }} 个</div>
              <div>选中设备数量: {{ formData.selectedDevices.length }} 台</div>
              <div>预估总费用: ¥{{ estimatedCost.toFixed(3) }}</div>
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
          开始关注任务
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { UploadFileInfo } from 'naive-ui'
import { useMessage } from 'naive-ui'
import { DocumentTextOutline } from '@vicons/ionicons5'
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
const fileList = ref<UploadFileInfo[]>([])
const contactCount = ref(0)
const isSubmitting = ref(false)

// 表单数据
const formData = ref({
  contactFile: '',
  selectedDevices: [] as string[],
  skipExisting: true,
  randomOrder: false,
  interval: 3
})

// 表单验证规则
const rules = {
  contactFile: [
    {
      required: true,
      message: '请上传通讯录文件',
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
  return contactCount.value * costPerFollow.value
})

const canSubmit = computed(() => {
  return formData.value.contactFile &&
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
const handleFileChange = (fileList: UploadFileInfo[]) => {
  if (fileList.length > 0) {
    const file = fileList[0]
    formData.value.contactFile = file.name

    // 解析文件内容获取联系人数量
    parseContactFile(file.file!)
  } else {
    formData.value.contactFile = ''
    contactCount.value = 0
  }
}

const beforeUpload = (data: { file: UploadFileInfo; fileList: UploadFileInfo[] }) => {
  const file = data.file
  const fileSize = file.file?.size || 0
  const fileName = file.name || ''

  // 检查文件大小（限制10MB）
  if (fileSize > 10 * 1024 * 1024) {
    message.error('文件大小不能超过 10MB')
    return false
  }

  // 检查文件类型
  const allowedExtensions = ['.txt', '.csv', '.json']
  const extension = fileName.toLowerCase().substring(fileName.lastIndexOf('.'))
  if (!allowedExtensions.includes(extension)) {
    message.error('只支持 TXT、CSV、JSON 格式的文件')
    return false
  }

  return true
}

const parseContactFile = async (file: File) => {
  try {
    const content = await file.text()
    const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))

    let count = 0

    switch (extension) {
      case '.json':
        try {
          const data = JSON.parse(content)
          count = Array.isArray(data) ? data.length : 0
        } catch {
          message.error('JSON 文件格式错误')
        }
        break

      case '.csv':
        const csvLines = content.split('\n').filter(line => line.trim())
        count = Math.max(0, csvLines.length - 1) // 减去标题行
        break

      case '.txt':
        const txtLines = content.split('\n').filter(line => line.trim())
        count = txtLines.length
        break
    }

    contactCount.value = count
    message.success(`解析完成，发现 ${count} 个联系人`)

  } catch (error) {
    message.error('文件解析失败')
    contactCount.value = 0
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()

    isSubmitting.value = true

    const params = {
      contactFile: formData.value.contactFile,
      devices: formData.value.selectedDevices,
      settings: {
        skipExisting: formData.value.skipExisting,
        randomOrder: formData.value.randomOrder,
        interval: formData.value.interval
      },
      estimatedCost: estimatedCost.value
    }

    emit('submit', params)

  } catch (error) {
    // 表单验证失败
  } finally {
    isSubmitting.value = false
  }
}

const handleCancel = () => {
  emit('update:show', false)
}

const resetForm = () => {
  formData.value = {
    contactFile: '',
    selectedDevices: [],
    skipExisting: true,
    randomOrder: false,
    interval: 3
  }
  fileList.value = []
  contactCount.value = 0
  isSubmitting.value = false
}
</script>

<style scoped>
:deep(.n-upload-dragger) {
  text-align: center;
  padding: 40px 20px;
}

:deep(.n-transfer) {
  height: 200px;
}
</style>
