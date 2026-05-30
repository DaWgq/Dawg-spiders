<template>
  <n-card title="年份分布" :bordered="false" class="chart-card">
    <VChart :option="chartOption" autoresize style="height: 420px" />
  </n-card>
</template>

<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import 'echarts'

const props = defineProps({ data: Array })

const chartOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: params => `${params[0].name}年<br/>数量: ${params[0].value}部` },
  grid: { left: 50, right: 20, top: 20, bottom: 50 },
  xAxis: {
    type: 'category',
    data: props.data.map(d => d.year),
    axisLabel: { rotate: 45, fontSize: 10, interval: Math.max(0, Math.floor(props.data.length / 30)) },
    name: '年份',
    nameLocation: 'center',
    nameGap: 35,
  },
  yAxis: { type: 'value', name: '电影数量' },
  series: [{
    type: 'bar',
    data: props.data.map(d => ({
      value: d.count,
      itemStyle: { color: '#0f3460', borderRadius: [3, 3, 0, 0], opacity: 0.75 }
    })),
    barWidth: '60%',
    label: { show: true, position: 'top', fontSize: 10, formatter: p => p.value || '' },
  }],
}))
</script>

<style scoped>
.chart-card { background: #fff; border-radius: 8px; }
</style>
