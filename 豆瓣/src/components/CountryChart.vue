<template>
  <n-card title="国家/地区分布" :bordered="false" class="chart-card">
    <VChart :option="chartOption" autoresize style="height: 420px" />
  </n-card>
</template>

<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import 'echarts'

const props = defineProps({ data: Array })

const colors = ['#e50914', '#f5a623', '#7ed321', '#0f3460', '#9013fe', '#4a90d9', '#f5a623', '#d0021b', '#8b572a', '#417505']

const chartOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: p => `${p.name}<br/>数量: ${p.value}部 (${p.percent}%)` },
  grid: { left: 100, right: 40, top: 20, bottom: 30 },
  xAxis: { type: 'value', name: '电影数量' },
  yAxis: {
    type: 'category',
    data: props.data.map(d => d.country).reverse(),
    axisLabel: { fontSize: 12 },
  },
  series: [{
    type: 'bar',
    data: props.data.map((d, i) => ({
      value: d.count,
      itemStyle: { color: colors[i % colors.length], borderRadius: [0, 3, 3, 0] },
    })),
    label: { show: true, position: 'right', fontSize: 11, formatter: p => p.value },
    barWidth: '60%',
  }],
}))
</script>

<style scoped>
.chart-card { background: #fff; border-radius: 8px; }
</style>
