<template>
  <div class="login-container">
    <div class="login-card">
      <n-card size="large">
        <!-- Logo 和标题 -->
        <div class="login-header">
          <div class="logo-section">
            <img src="/logo.svg" alt="Flow Farm" class="logo" />
            <h1 class="app-title">Flow Farm</h1>
            <p class="app-subtitle">员工客户端</p>
          </div>
        </div>

        <!-- 登录表单 -->
        <n-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          size="large"
          class="login-form"
        >
          <n-form-item path="username">
            <n-input
              v-model:value="loginForm.username"
              placeholder="请输入用户名"
              size="large"
              :maxlength="50"
            >
              <template #prefix>
                <n-icon><Person /></n-icon>
              </template>
            </n-input>
          </n-form-item>

          <n-form-item path="password">
            <n-input
              v-model:value="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :maxlength="100"
              show-password-on="click"
              @keydown.enter="handleLogin"
            >
              <template #prefix>
                <n-icon><LockClosed /></n-icon>
              </template>
            </n-input>
          </n-form-item>

          <n-form-item>
            <n-checkbox v-model:checked="rememberMe">
              记住登录状态
            </n-checkbox>
          </n-form-item>

          <n-form-item>
            <n-button
              type="primary"
              size="large"
              :loading="isLoggingIn"
              :block="true"
              @click="handleLogin"
            >
              登录
            </n-button>
          </n-form-item>
        </n-form>

        <!-- 其他操作 -->
        <div class="login-footer">
          <n-space justify="space-between">
            <n-button text @click="showForgotPassword = true">
              忘记密码？
            </n-button>
            <n-button text @click="showSettings = true">
              <template #icon>
                <n-icon><Settings /></n-icon>
              </template>
              服务器设置
            </n-button>
          </n-space>
        </div>

        <!-- 版本信息 -->
        <div class="version-info">
          <n-text depth="3" style="font-size: 12px;">
            版本 1.0.0 | © 2024 Flow Farm Team
          </n-text>
        </div>
      </n-card>
    </div>

    <!-- 服务器设置对话框 -->
    <n-modal v-model:show="showSettings" preset="dialog" title="服务器设置">
      <template #default>
        <n-form :model="serverSettings" label-placement="left" label-width="80px">
          <n-form-item label="服务器地址">
            <n-input
              v-model:value="serverSettings.url"
              placeholder="http://localhost:8000"
            />
          </n-form-item>
          <n-form-item label="连接超时">
            <n-input-number
              v-model:value="serverSettings.timeout"
              :min="1000"
              :max="30000"
              :step="1000"
              placeholder="超时时间(毫秒)"
            />
          </n-form-item>
        </n-form>
      </template>
      <template #action>
        <n-space>
          <n-button @click="resetServerSettings">重置</n-button>
          <n-button @click="showSettings = false">取消</n-button>
          <n-button type="primary" @click="saveServerSettings">保存</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 忘记密码对话框 -->
    <n-modal v-model:show="showForgotPassword" preset="dialog" title="忘记密码">
      <template #default>
        <n-space vertical>
          <n-alert type="info" :show-icon="false">
            请联系管理员重置您的密码
          </n-alert>
          <n-form-item label="用户名">
            <n-input
              v-model:value="forgotPasswordForm.username"
              placeholder="请输入您的用户名"
            />
          </n-form-item>
          <n-form-item label="联系方式">
            <n-input
              v-model:value="forgotPasswordForm.contact"
              placeholder="请输入您的邮箱或手机号"
            />
          </n-form-item>
        </n-space>
      </template>
      <template #action>
        <n-space>
          <n-button @click="showForgotPassword = false">取消</n-button>
          <n-button type="primary" @click="handleForgotPassword">提交申请</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { Person, LockClosed, Settings } from '@vicons/ionicons5'
import { useUserStore } from '../stores/user'

const router = useRouter()
const message = useMessage()
const userStore = useUserStore()

const loginFormRef = ref()
const isLoggingIn = ref(false)
const rememberMe = ref(false)
const showSettings = ref(false)
const showForgotPassword = ref(false)

// 登录表单
const loginForm = ref({
  username: '',
  password: ''
})

// 登录验证规则
const loginRules = {
  username: [
    {
      required: true,
      message: '请输入用户名',
      trigger: ['input', 'blur']
    },
    {
      min: 3,
      max: 50,
      message: '用户名长度应为 3-50 个字符',
      trigger: ['input', 'blur']
    }
  ],
  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: ['input', 'blur']
    },
    {
      min: 6,
      max: 100,
      message: '密码长度应为 6-100 个字符',
      trigger: ['input', 'blur']
    }
  ]
}

// 服务器设置
const serverSettings = ref({
  url: 'http://localhost:8000',
  timeout: 10000
})

// 忘记密码表单
const forgotPasswordForm = ref({
  username: '',
  contact: ''
})

// 方法
const handleLogin = async () => {
  try {
    await loginFormRef.value?.validate()

    isLoggingIn.value = true

    await userStore.login(loginForm.value.username, loginForm.value.password)

    if (rememberMe.value) {
      // 保存登录状态到本地存储
      localStorage.setItem('remember_login', 'true')
    }

    message.success('登录成功')
    router.push('/dashboard')

  } catch (error: any) {
    if (error.name !== 'FormValidateError') {
      message.error(error.message || '登录失败，请检查用户名和密码')
    }
  } finally {
    isLoggingIn.value = false
  }
}

const saveServerSettings = () => {
  // 保存服务器设置到本地存储
  localStorage.setItem('server_settings', JSON.stringify(serverSettings.value))
  message.success('服务器设置已保存')
  showSettings.value = false
}

const resetServerSettings = () => {
  serverSettings.value = {
    url: 'http://localhost:8000',
    timeout: 10000
  }
  message.info('设置已重置')
}

const handleForgotPassword = () => {
  if (!forgotPasswordForm.value.username || !forgotPasswordForm.value.contact) {
    message.error('请填写完整信息')
    return
  }

  message.success('密码重置申请已提交，请等待管理员处理')
  showForgotPassword.value = false

  // 重置表单
  forgotPasswordForm.value = {
    username: '',
    contact: ''
  }
}

// 页面加载时的处理
onMounted(() => {
  // 加载保存的服务器设置
  const savedSettings = localStorage.getItem('server_settings')
  if (savedSettings) {
    try {
      serverSettings.value = JSON.parse(savedSettings)
    } catch (error) {
      console.error('加载服务器设置失败:', error)
    }
  }

  // 检查是否有记住的登录状态
  const rememberLogin = localStorage.getItem('remember_login')
  if (rememberLogin === 'true') {
    rememberMe.value = true
  }

  // 如果已经登录，直接跳转到仪表板
  if (userStore.isLoggedIn) {
    router.push('/dashboard')
  }
})
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  animation: slideInUp 0.6s ease-out;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.logo {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.app-title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #333;
  letter-spacing: 1px;
}

.app-subtitle {
  margin: 0;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.login-form {
  margin: 24px 0;
}

.login-footer {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.version-info {
  text-align: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f5f5f5;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 深色模式下的样式调整 */
:deep(.n-card) {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* 输入框焦点样式 */
:deep(.n-input:focus-within) {
  box-shadow: 0 0 0 2px rgba(24, 160, 88, 0.2);
}

/* 按钮悬停效果 */
:deep(.n-button--primary:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(24, 160, 88, 0.3);
}
</style>
