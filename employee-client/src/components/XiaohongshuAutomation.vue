<template>
  <div class="xiaohongshu-automation">
    <h2 class="module-title">小红书通讯录查找工具</h2>

    <!-- 步骤指示器 -->
    <div class="steps">
      <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
        <div class="step-number">1</div>
        <div class="step-label">导入通讯录</div>
      </div>
      <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
        <div class="step-number">2</div>
        <div class="step-label">连接设备</div>
      </div>
      <div class="step" :class="{ active: currentStep >= 3, completed: currentStep > 3 }">
        <div class="step-number">3</div>
        <div class="step-label">配置任务</div>
      </div>
      <div class="step" :class="{ active: currentStep >= 4 }">
        <div class="step-number">4</div>
        <div class="step-label">执行查找</div>
      </div>
    </div>

    <!-- 步骤1: 导入通讯录 -->
    <div v-if="currentStep === 1" class="step-content">
      <div class="card">
        <h3>导入通讯录文件</h3>
        <p>支持的格式：TXT文件，每行一个联系人信息</p>
        <div class="file-upload">
          <input
            type="file"
            @change="handleFileSelect"
            accept=".txt"
            ref="fileInput"
            style="display: none;"
          >
          <button @click="$refs.fileInput.click()" class="upload-btn">
            选择TXT文件
          </button>
          <span v-if="selectedFile" class="file-name">{{ selectedFile.name }}</span>
        </div>

        <div v-if="loading" class="loading">
          正在解析通讯录文件...
        </div>

        <div v-if="contactList" class="contact-preview">
          <h4>通讯录预览 (共{{ contactList.total_count }}个联系人)</h4>
          <div class="contact-list">
            <div
              v-for="contact in contactList.contacts.slice(0, 5)"
              :key="contact.id"
              class="contact-item"
            >
              <span class="contact-name">{{ contact.name }}</span>
              <span v-if="contact.phone" class="contact-phone">{{ contact.phone }}</span>
              <span v-if="contact.username" class="contact-username">@{{ contact.username }}</span>
            </div>
            <div v-if="contactList.contacts.length > 5" class="more-contacts">
              还有{{ contactList.contacts.length - 5 }}个联系人...
            </div>
          </div>
          <button @click="nextStep" class="next-btn">下一步</button>
        </div>
      </div>
    </div>

    <!-- 步骤2: 连接设备 -->
    <div v-if="currentStep === 2" class="step-content">
      <div class="card">
        <h3>连接ADB设备</h3>
        <button @click="refreshDevices" class="refresh-btn" :disabled="loadingDevices">
          {{ loadingDevices ? '扫描中...' : '刷新设备列表' }}
        </button>

        <div v-if="adbDevices.length === 0" class="no-devices">
          <p>未发现可用设备</p>
          <p class="help-text">请确保：</p>
          <ul class="help-list">
            <li>已启动Android模拟器或连接真实设备</li>
            <li>已开启USB调试模式</li>
            <li>已安装ADB工具</li>
          </ul>
        </div>

        <div v-else class="device-list">
          <div
            v-for="device in adbDevices"
            :key="device.id"
            class="device-item"
            :class="{ selected: selectedDevice?.id === device.id }"
            @click="selectDevice(device)"
          >
            <div class="device-info">
              <h4>{{ device.name }}</h4>
              <p>设备ID: {{ device.id }}</p>
              <p v-if="device.model">型号: {{ device.model }}</p>
              <p v-if="device.android_version">Android版本: {{ device.android_version }}</p>
            </div>
            <div class="device-status" :class="device.status">
              {{ getStatusText(device.status) }}
            </div>
          </div>
        </div>

        <div v-if="selectedDevice" class="device-actions">
          <button @click="checkXiaohongshuApp" class="check-app-btn" :disabled="checking">
            {{ checking ? '检查中...' : '检查小红书应用' }}
          </button>
          <div v-if="appCheckResult !== null" class="app-status">
            {{ appCheckResult ? '✓ 小红书应用可用' : '✗ 未找到小红书应用' }}
          </div>
          <button
            v-if="appCheckResult"
            @click="nextStep"
            class="next-btn"
          >
            下一步
          </button>
        </div>

        <button @click="prevStep" class="prev-btn">上一步</button>
      </div>
    </div>

    <!-- 步骤3: 配置任务 -->
    <div v-if="currentStep === 3" class="step-content">
      <div class="card">
        <h3>配置查找任务</h3>

        <div class="config-form">
          <div class="form-group">
            <label>任务名称</label>
            <input v-model="taskConfig.name" type="text" placeholder="输入任务名称">
          </div>

          <div class="form-group">
            <label>搜索间隔时间 (毫秒)</label>
            <input v-model="taskConfig.search_delay_ms" type="number" min="1000" max="10000">
            <small>建议2000-5000毫秒，避免被检测</small>
          </div>

          <div class="form-group">
            <label>点击间隔时间 (毫秒)</label>
            <input v-model="taskConfig.tap_delay_ms" type="number" min="500" max="3000">
          </div>

          <div class="form-group">
            <label>最大搜索结果数</label>
            <input v-model="taskConfig.max_search_results" type="number" min="1" max="20">
          </div>

          <div class="form-group">
            <label>
              <input v-model="taskConfig.enable_screenshots" type="checkbox">
              启用截图保存
            </label>
          </div>

          <div v-if="taskConfig.enable_screenshots" class="form-group">
            <label>截图保存目录</label>
            <input v-model="taskConfig.screenshot_dir" type="text" placeholder="截图保存路径">
          </div>
        </div>

        <div class="task-summary">
          <h4>任务摘要</h4>
          <p>联系人总数: {{ contactList?.total_count }}</p>
          <p>目标设备: {{ selectedDevice?.name }}</p>
          <p>预计耗时: {{ estimatedTime }}分钟</p>
        </div>

        <div class="step-actions">
          <button @click="prevStep" class="prev-btn">上一步</button>
          <button @click="createTask" class="next-btn" :disabled="!isConfigValid">
            创建任务
          </button>
        </div>
      </div>
    </div>

    <!-- 步骤4: 执行查找 -->
    <div v-if="currentStep === 4" class="step-content">
      <div class="card">
        <h3>任务执行</h3>

        <div v-if="automationTask" class="task-info">
          <h4>{{ automationTask.name }}</h4>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: automationTask.progress + '%' }"
            ></div>
          </div>
          <div class="progress-text">
            {{ Math.round(automationTask.progress) }}% 完成
            ({{ automationTask.current_contact_index }}/{{ contactList?.total_count }})
          </div>

          <div class="task-status" :class="automationTask.status">
            状态: {{ getTaskStatusText(automationTask.status) }}
          </div>

          <div class="task-controls">
            <button
              v-if="automationTask.status === 'created'"
              @click="startTask"
              class="start-btn"
            >
              开始执行
            </button>
            <button
              v-if="automationTask.status === 'running'"
              @click="pauseTask"
              class="pause-btn"
            >
              暂停
            </button>
            <button
              v-if="automationTask.status === 'paused'"
              @click="resumeTask"
              class="resume-btn"
            >
              继续
            </button>
            <button
              v-if="['running', 'paused'].includes(automationTask.status)"
              @click="stopTask"
              class="stop-btn"
            >
              停止
            </button>
          </div>
        </div>

        <!-- 结果展示 -->
        <div v-if="taskResults.length > 0" class="results">
          <h4>搜索结果 ({{ taskResults.length }})</h4>
          <div class="results-summary">
            <span class="success-count">
              成功: {{ taskResults.filter(r => r.found).length }}
            </span>
            <span class="failed-count">
              失败: {{ taskResults.filter(r => !r.found).length }}
            </span>
          </div>

          <div class="results-list">
            <div
              v-for="result in taskResults"
              :key="result.contact_id"
              class="result-item"
              :class="{ found: result.found }"
            >
              <div class="result-contact">
                <h5>{{ result.contact_name }}</h5>
                <span class="keyword">搜索: {{ result.search_keyword }}</span>
              </div>
              <div class="result-status">
                {{ result.found ? '✓ 找到' : '✗ 未找到' }}
              </div>
              <div v-if="result.user_info" class="user-info">
                <p v-if="result.user_info.username">用户名: {{ result.user_info.username }}</p>
                <p v-if="result.user_info.follower_count">粉丝: {{ result.user_info.follower_count }}</p>
              </div>
            </div>
          </div>

          <button @click="exportResults" class="export-btn">
            导出结果
          </button>
        </div>

        <button @click="resetTask" class="prev-btn">重新开始</button>
      </div>
    </div>
  </div>
</template>

<script>
import { invoke } from '@tauri-apps/api/core';

export default {
  name: 'XiaohongshuAutomation',
  data() {
    return {
      currentStep: 1,
      selectedFile: null,
      contactList: null,
      adbDevices: [],
      selectedDevice: null,
      appCheckResult: null,
      automationTask: null,
      taskResults: [],
      loading: false,
      loadingDevices: false,
      checking: false,
      taskConfig: {
        name: '小红书通讯录查找任务',
        search_delay_ms: 3000,
        tap_delay_ms: 1000,
        max_search_results: 10,
        enable_screenshots: true,
        screenshot_dir: './screenshots'
      }
    }
  },
  computed: {
    estimatedTime() {
      if (!this.contactList) return 0;
      const totalTime = this.contactList.total_count * (this.taskConfig.search_delay_ms + 2000) / 1000 / 60;
      return Math.ceil(totalTime);
    },
    isConfigValid() {
      return this.taskConfig.name.trim().length > 0 &&
             this.contactList &&
             this.selectedDevice;
    }
  },
  methods: {
    async handleFileSelect(event) {
      const file = event.target.files[0];
      if (!file) return;

      this.selectedFile = file;
      this.loading = true;

      try {
        // 获取文件路径 (注意：在Web环境中这可能需要特殊处理)
        const filePath = file.path || file.webkitRelativePath;

        const contactList = await invoke('load_contacts_from_file', {
          filePath: filePath
        });

        this.contactList = contactList;
      } catch (error) {
        console.error('加载通讯录失败:', error);
        alert('加载通讯录失败: ' + error);
      } finally {
        this.loading = false;
      }
    },

    async refreshDevices() {
      this.loadingDevices = true;
      try {
        // 首先检查ADB是否可用
        const adbAvailable = await invoke('check_adb_available');
        if (!adbAvailable) {
          alert('ADB工具不可用，请检查ADB环境');
          return;
        }

        const devices = await invoke('get_adb_devices');
        this.adbDevices = devices;
      } catch (error) {
        console.error('获取设备列表失败:', error);
        alert('获取设备列表失败: ' + error);
      } finally {
        this.loadingDevices = false;
      }
    },

    selectDevice(device) {
      this.selectedDevice = device;
      this.appCheckResult = null;
    },

    async checkXiaohongshuApp() {
      if (!this.selectedDevice) return;

      this.checking = true;
      try {
        const available = await invoke('check_xiaohongshu_app', {
          deviceId: this.selectedDevice.id
        });
        this.appCheckResult = available;
      } catch (error) {
        console.error('检查应用失败:', error);
        this.appCheckResult = false;
      } finally {
        this.checking = false;
      }
    },

    async createTask() {
      try {
        const config = {
          device_id: this.selectedDevice.id,
          search_delay_ms: this.taskConfig.search_delay_ms,
          scroll_delay_ms: 1000,
          tap_delay_ms: this.taskConfig.tap_delay_ms,
          max_search_results: this.taskConfig.max_search_results,
          enable_screenshots: this.taskConfig.enable_screenshots,
          screenshot_dir: this.taskConfig.screenshot_dir
        };

        const task = await invoke('create_xiaohongshu_task', {
          name: this.taskConfig.name,
          deviceId: this.selectedDevice.id,
          contactListId: this.contactList.id,
          config: config
        });

        this.automationTask = task;
        this.nextStep();
      } catch (error) {
        console.error('创建任务失败:', error);
        alert('创建任务失败: ' + error);
      }
    },

    async startTask() {
      if (!this.automationTask) return;

      try {
        await invoke('start_xiaohongshu_task', {
          taskId: this.automationTask.id
        });

        // 开始轮询任务状态
        this.pollTaskStatus();
      } catch (error) {
        console.error('启动任务失败:', error);
        alert('启动任务失败: ' + error);
      }
    },

    async pauseTask() {
      if (!this.automationTask) return;

      try {
        await invoke('pause_xiaohongshu_task', {
          taskId: this.automationTask.id
        });
      } catch (error) {
        console.error('暂停任务失败:', error);
      }
    },

    async stopTask() {
      if (!this.automationTask) return;

      try {
        await invoke('stop_xiaohongshu_task', {
          taskId: this.automationTask.id
        });
      } catch (error) {
        console.error('停止任务失败:', error);
      }
    },

    async exportResults() {
      if (!this.automationTask) return;

      try {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const fileName = `xiaohongshu_results_${timestamp}.csv`;

        await invoke('export_task_results', {
          taskId: this.automationTask.id,
          filePath: `./${fileName}`
        });

        alert(`结果已导出到: ${fileName}`);
      } catch (error) {
        console.error('导出结果失败:', error);
        alert('导出结果失败: ' + error);
      }
    },

    async pollTaskStatus() {
      if (!this.automationTask) return;

      const poll = async () => {
        try {
          const tasks = await invoke('get_automation_tasks');
          const currentTask = tasks.find(t => t.id === this.automationTask.id);

          if (currentTask) {
            this.automationTask = currentTask;

            // 获取结果
            const results = await invoke('get_task_results', {
              taskId: this.automationTask.id
            });
            this.taskResults = results;

            // 如果任务还在运行，继续轮询
            if (['running', 'paused'].includes(currentTask.status)) {
              setTimeout(poll, 2000);
            }
          }
        } catch (error) {
          console.error('轮询任务状态失败:', error);
        }
      };

      poll();
    },

    nextStep() {
      this.currentStep++;
    },

    prevStep() {
      this.currentStep--;
    },

    resetTask() {
      this.currentStep = 1;
      this.selectedFile = null;
      this.contactList = null;
      this.selectedDevice = null;
      this.appCheckResult = null;
      this.automationTask = null;
      this.taskResults = [];
    },

    getStatusText(status) {
      const statusMap = {
        'device': '在线',
        'offline': '离线',
        'unauthorized': '未授权',
        'unknown': '未知'
      };
      return statusMap[status] || status;
    },

    getTaskStatusText(status) {
      const statusMap = {
        'created': '已创建',
        'running': '运行中',
        'paused': '已暂停',
        'completed': '已完成',
        'stopped': '已停止',
        'failed': '失败'
      };
      return statusMap[status] || status;
    }
  },

  mounted() {
    // 组件加载后自动刷新设备列表
    this.refreshDevices();
  }
}
</script>

<style scoped>
.xiaohongshu-automation {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.module-title {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

/* 步骤指示器 */
.steps {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0 20px;
  opacity: 0.5;
}

.step.active {
  opacity: 1;
  color: #007bff;
}

.step.completed {
  opacity: 1;
  color: #28a745;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-bottom: 8px;
}

.step.active .step-number {
  background-color: #007bff;
  color: white;
}

.step.completed .step-number {
  background-color: #28a745;
  color: white;
}

/* 卡片样式 */
.card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card h3 {
  margin-bottom: 16px;
  color: #333;
}

/* 文件上传 */
.file-upload {
  margin: 20px 0;
}

.upload-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

.upload-btn:hover {
  background-color: #0056b3;
}

.file-name {
  margin-left: 15px;
  color: #666;
}

/* 联系人预览 */
.contact-preview {
  margin-top: 20px;
}

.contact-list {
  border: 1px solid #ddd;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
}

.contact-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
}

.contact-item:last-child {
  border-bottom: none;
}

.contact-name {
  font-weight: bold;
  margin-right: 15px;
}

.contact-phone, .contact-username {
  color: #666;
  margin-right: 10px;
}

/* 设备列表 */
.device-list {
  margin: 20px 0;
}

.device-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.device-item:hover {
  background-color: #f5f5f5;
}

.device-item.selected {
  border-color: #007bff;
  background-color: #e3f2fd;
}

.device-info h4 {
  margin: 0 0 5px 0;
}

.device-info p {
  margin: 2px 0;
  color: #666;
  font-size: 0.9em;
}

.device-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  font-weight: bold;
}

.device-status.device {
  background-color: #d4edda;
  color: #155724;
}

.device-status.offline {
  background-color: #f8d7da;
  color: #721c24;
}

/* 配置表单 */
.config-form {
  margin: 20px 0;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input[type="text"],
.form-group input[type="number"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-group small {
  color: #666;
  font-size: 0.8em;
}

/* 任务摘要 */
.task-summary {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  margin: 20px 0;
}

.task-summary h4 {
  margin-bottom: 10px;
}

.task-summary p {
  margin: 5px 0;
}

/* 进度条 */
.progress-bar {
  width: 100%;
  height: 20px;
  background-color: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  margin: 10px 0;
}

.progress-fill {
  height: 100%;
  background-color: #007bff;
  transition: width 0.3s ease;
}

.progress-text {
  text-align: center;
  font-weight: bold;
  margin-bottom: 10px;
}

/* 任务状态 */
.task-status {
  padding: 8px 12px;
  border-radius: 4px;
  margin: 10px 0;
  font-weight: bold;
}

.task-status.running {
  background-color: #cce5ff;
  color: #004080;
}

.task-status.completed {
  background-color: #d4edda;
  color: #155724;
}

.task-status.failed {
  background-color: #f8d7da;
  color: #721c24;
}

/* 结果展示 */
.results-summary {
  margin: 10px 0;
}

.success-count {
  color: #28a745;
  font-weight: bold;
  margin-right: 20px;
}

.failed-count {
  color: #dc3545;
  font-weight: bold;
}

.results-list {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.result-item:last-child {
  border-bottom: none;
}

.result-item.found {
  background-color: #f8fff8;
}

.result-contact h5 {
  margin: 0 0 5px 0;
}

.keyword {
  color: #666;
  font-size: 0.9em;
}

.result-status {
  font-weight: bold;
}

.result-item.found .result-status {
  color: #28a745;
}

.result-item:not(.found) .result-status {
  color: #dc3545;
}

/* 按钮样式 */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.next-btn, .start-btn, .resume-btn {
  background-color: #007bff;
  color: white;
}

.prev-btn {
  background-color: #6c757d;
  color: white;
}

.pause-btn {
  background-color: #ffc107;
  color: #212529;
}

.stop-btn {
  background-color: #dc3545;
  color: white;
}

.export-btn {
  background-color: #28a745;
  color: white;
}

.btn:hover {
  opacity: 0.9;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 帮助文本 */
.help-text {
  color: #666;
  margin: 10px 0 5px 0;
}

.help-list {
  color: #666;
  margin-left: 20px;
}

.no-devices {
  text-align: center;
  padding: 40px;
  color: #666;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

/* 步骤操作按钮 */
.step-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
}

.task-controls {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.device-actions {
  margin-top: 20px;
}

.check-app-btn {
  background-color: #17a2b8;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.check-app-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.app-status {
  margin: 10px 0;
  font-weight: bold;
}

.refresh-btn {
  background-color: #6f42c1;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 20px;
}

.more-contacts {
  padding: 8px 12px;
  color: #666;
  font-style: italic;
  text-align: center;
}
</style>
