<template>
  <div class="card control-panel">
    <h2 class="section-header">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="5 3 19 12 5 21 5 3"/>
      </svg>
      任务控制
    </h2>

    <!-- 进度条 -->
    <div class="progress-section">
      <div class="progress-header">
        <span class="progress-label">总体进度</span>
        <span class="progress-value">{{ progressPercent }}%</span>
      </div>
      <div class="progress-bar-bg">
        <div class="progress-bar-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
    </div>

    <!-- 控制按钮 -->
    <div class="control-buttons">
      <button
        v-if="status !== 'running'"
        class="btn btn-primary"
        @click="$emit('start')"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="5 3 19 12 5 21 5 3"/>
        </svg>
        {{ stats.currentPage > 0 ? '继续增量抓取' : '启动爬虫' }}
      </button>
      <button
        v-else
        class="btn btn-warning"
        @click="$emit('pause')"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="6" y="4" width="4" height="16"/>
          <rect x="14" y="4" width="4" height="16"/>
        </svg>
        暂停任务
      </button>

      <button class="btn btn-secondary" @click="handleReset">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="23 4 23 10 17 10"/>
          <polyline points="1 20 1 14 7 14"/>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
        </svg>
        清除断点
      </button>
      <button class="btn btn-secondary" @click="$emit('export')">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        导出 CSV
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useDialog } from 'naive-ui'

const dialog = useDialog()

const props = defineProps({
  status: { type: String, default: 'idle' },
  stats: { type: Object, required: true },
  config: { type: Object, required: true }
})

const emit = defineEmits(['start', 'pause', 'reset', 'export'])

const progressPercent = computed(() => {
  if (props.config.totalPages <= 0) return 0
  return Math.min(100, Math.round((props.stats.currentPage / props.config.totalPages) * 100))
})

function handleReset() {
  dialog.warning({
    title: '确认操作',
    content: '确定要清除断点文件 (checkpoint.json) 并重置数据吗？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: () => {
      emit('reset')
    }
  })
}
</script>
