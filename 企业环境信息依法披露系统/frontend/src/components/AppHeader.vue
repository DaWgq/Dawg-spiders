<template>
  <header class="card app-header">
    <div class="header-left">
      <div class="header-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <ellipse cx="12" cy="5" rx="9" ry="3"/>
          <path d="M3 5V19A9 3 0 0 0 21 19V5"/>
          <path d="M3 12A9 3 0 0 0 21 12"/>
        </svg>
      </div>
      <div>
        <h1 class="header-title">企业环境信息依法披露系统</h1>
        <p class="header-subtitle">数据爬虫控制台 v1.0</p>
      </div>
    </div>
    <div class="header-badges">
      <span class="badge badge-green">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
        引擎就绪
      </span>
      <span class="badge badge-blue" :class="{ 'status-pulse': status === 'running' }">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
        {{ statusText }}
      </span>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, default: 'idle' }
})

const statusText = computed(() => {
  const map = {
    idle: '断点续爬开启',
    running: '爬虫运行中...',
    paused: '已暂停',
    completed: '任务已完成',
    error: '发生异常',
  }
  return map[props.status] || '断点续爬开启'
})
</script>
