<template>
  <div class="card terminal">
    <div class="terminal-header">
      <span class="terminal-title">
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="4 17 10 11 4 5"/>
          <line x1="12" y1="19" x2="20" y2="19"/>
        </svg>
        python code.py
      </span>
      <span class="terminal-badge">UTF-8</span>
    </div>
    <div class="terminal-body" ref="terminalBody">
      <div
        v-for="(log, idx) in logs"
        :key="idx"
        class="log-line"
      >
        <span class="log-time">[{{ log.time }}]</span>
        <span :class="logMsgClass(log.type)">{{ log.msg }}</span>
      </div>
      <div ref="logsEnd"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  logs: { type: Array, default: () => [] }
})

const terminalBody = ref(null)
const logsEnd = ref(null)

function logMsgClass(type) {
  const map = {
    info: 'log-msg-info',
    error: 'log-msg-error',
    warning: 'log-msg-warning',
    success: 'log-msg-success'
  }
  return map[type] || 'log-msg-info'
}

// 自动滚动到底部
watch(() => props.logs.length, () => {
  nextTick(() => {
    if (logsEnd.value) {
      logsEnd.value.scrollIntoView({ behavior: 'smooth' })
    }
  })
})
</script>
