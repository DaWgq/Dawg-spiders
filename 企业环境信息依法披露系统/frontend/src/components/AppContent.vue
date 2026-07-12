<template>
  <div class="app-container">
    <AppHeader :status="status" />
    <StatsCards :stats="stats" :config="config" />
    <div class="main-content">
      <div class="left-column">
        <ControlPanel
          :status="status"
          :stats="stats"
          :config="config"
          @start="handleStart"
          @pause="handlePause"
          @reset="handleReset"
          @export="handleExport"
        />
        <ConfigPanel
          :config="config"
          :disabled="status === 'running'"
          @update="handleConfigUpdate"
        />
      </div>
      <div class="right-column">
        <TerminalLogs :logs="logs" />
        <DataPreview :records="previewData" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useMessage } from 'naive-ui'
import AppHeader from './AppHeader.vue'
import StatsCards from './StatsCards.vue'
import ControlPanel from './ControlPanel.vue'
import ConfigPanel from './ConfigPanel.vue'
import TerminalLogs from './TerminalLogs.vue'
import DataPreview from './DataPreview.vue'

const message = useMessage()

// --- 状态 ---
const status = ref('idle')
const config = reactive({
  totalPages: 300,
  pageSize: 20,
  csvFile: 'data.csv',
  checkpointFile: 'checkpoint.json',
  cookie: '',
  retryLimit: 5,
  delay: 2
})

const stats = reactive({
  currentPage: 0,
  successPages: 0,
  failedPages: 0,
  totalRecords: 0
})

const logs = ref([
  { time: new Date().toLocaleTimeString(), msg: '系统初始化完成，等待启动...', type: 'info' }
])

const previewData = ref([])

// --- WebSocket ---
let ws = null
let reconnectTimer = null

function connectWs() {
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${location.host}/ws`

  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    console.log('[WS] 已连接')
  }

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data)
      handleWsMessage(msg)
    } catch (e) {
      console.error('[WS] 解析消息失败:', e)
    }
  }

  ws.onclose = () => {
    console.log('[WS] 连接断开，3秒后重连...')
    reconnectTimer = setTimeout(connectWs, 3000)
  }

  ws.onerror = (err) => {
    console.error('[WS] 错误:', err)
  }
}

function handleWsMessage(msg) {
  switch (msg.type) {
    case 'init':
      // 初始化数据
      status.value = msg.data.status || 'idle'
      if (msg.data.stats) {
        Object.assign(stats, msg.data.stats)
      }
      if (msg.data.logs && msg.data.logs.length > 0) {
        logs.value = msg.data.logs
      }
      break
    case 'log':
      logs.value.push(msg.data)
      // 限制日志条数
      if (logs.value.length > 500) {
        logs.value = logs.value.slice(-300)
      }
      break
    case 'stats':
      Object.assign(stats, msg.data)
      break
    case 'records':
      // 追加新记录到预览
      previewData.value = [...msg.data, ...previewData.value].slice(0, 100)
      break
    case 'status_change':
      status.value = msg.data.status
      break
    case 'clear_data':
      previewData.value = []
      logs.value = [{ time: new Date().toLocaleTimeString(), msg: '已清除断点，下次将从第 1 页重新开始。', type: 'info' }]
      break
  }
}

function sendWs(action, data = {}) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ action, data }))
  }
}

// --- 控制方法 ---
function handleStart() {
  sendWs('start')
  status.value = 'running'
}

function handlePause() {
  sendWs('pause')
  status.value = 'paused'
}

function handleReset() {
  sendWs('reset')
  status.value = 'idle'
  stats.currentPage = 0
  stats.successPages = 0
  stats.failedPages = 0
  stats.totalRecords = 0
}

async function handleExport() {
  try {
    const response = await fetch('/api/export')
    if (response.ok) {
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'enterprise_data.csv'
      a.click()
      URL.revokeObjectURL(url)
      message.success('CSV 导出成功')
    }
  } catch (e) {
    message.error('导出失败')
  }
}

function handleConfigUpdate(newConfig) {
  Object.assign(config, newConfig)
  sendWs('config', newConfig)
}

// --- 生命周期 ---
onMounted(async () => {
  // 先加载初始状态
  try {
    const res = await fetch('/api/status')
    const data = await res.json()
    status.value = data.status
    Object.assign(stats, data.stats)
    Object.assign(config, data.config)
  } catch (e) {
    console.error('加载初始状态失败:', e)
  }

  // 加载历史记录
  try {
    const res = await fetch('/api/records?limit=100')
    const data = await res.json()
    if (data.records && data.records.length > 0) {
      previewData.value = data.records.map(r => ({
        id: (r.id || '').substring(0, 8) + '...',
        name: r.name,
        creditCode: r.credit_code,
        province: r.province,
        city: r.city,
        year: r.year,
        status: r.status,
      }))
    }
  } catch (e) {
    console.error('加载记录失败:', e)
  }

  // 加载日志
  try {
    const res = await fetch('/api/logs')
    const data = await res.json()
    if (data.logs && data.logs.length > 0) {
      logs.value = data.logs
    }
  } catch (e) {
    console.error('加载日志失败:', e)
  }

  // 连接 WebSocket
  connectWs()
})

onUnmounted(() => {
  if (ws) ws.close()
  if (reconnectTimer) clearTimeout(reconnectTimer)
})
</script>
