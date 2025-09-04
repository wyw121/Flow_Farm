import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import naive from 'naive-ui'

// 创建应用
const app = createApp(App)

// 使用 Pinia 状态管理
app.use(createPinia())

// 使用路由
app.use(router)

// 使用 Naive UI 组件库
app.use(naive)

// 挂载应用
app.mount('#app')
