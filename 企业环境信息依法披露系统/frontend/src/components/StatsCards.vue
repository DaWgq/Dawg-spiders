<template>
  <div class="stats-grid">
    <div class="card stat-card" v-for="(stat, idx) in statItems" :key="idx">
      <p class="stat-label">{{ stat.label }}</p>
      <h3 class="stat-value" :class="stat.colorClass">{{ stat.value }}</h3>
      <p class="stat-sub">{{ stat.sub }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stats: { type: Object, required: true },
  config: { type: Object, required: true }
})

const progressPercent = computed(() => {
  if (props.config.totalPages <= 0) return 0
  return Math.min(100, Math.round((props.stats.currentPage / props.config.totalPages) * 100))
})

const statItems = computed(() => [
  {
    label: '抓取进度',
    value: `${progressPercent.value}%`,
    sub: `${props.stats.currentPage} / ${props.config.totalPages} 页`,
    colorClass: 'text-blue'
  },
  {
    label: '已采集数据',
    value: props.stats.totalRecords,
    sub: '条记录 (CSV)',
    colorClass: 'text-emerald'
  },
  {
    label: '成功页面',
    value: props.stats.successPages,
    sub: '响应 200 OK',
    colorClass: 'text-green'
  },
  {
    label: '异常/重试',
    value: props.stats.failedPages,
    sub: '网络波动自动恢复',
    colorClass: 'text-rose'
  }
])
</script>
