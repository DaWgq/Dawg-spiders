<template>
  <n-card title="评分分布" :bordered="false" class="chart-card">
    <VChart :option="chartOption" autoresize style="height: 420px" />
  </n-card>
</template>

<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import 'echarts'

const props = defineProps({ data: Array })

const chartOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: params => `${params[0].name}分<br/>数量: ${params[0].value}部` },
  grid: { left: 50, right: 20, top: 20, bottom: 50 },
  xAxis: {
    type: 'category',
    data: props.data.map(d => d.rating.toFixed(1)),
    axisLabel: { rotate: 45, fontSize: 11 },
    name: '评分',
    nameLocation: 'center',
    nameGap: 35,
  },
  yAxis: { type: 'value', name: '电影数量' },
  series: [{
    type: 'bar',
    data: props.data.map(d => ({
      value: d.count,
      itemStyle: {
        color: d.rating >= 9.5 ? '#e50914' : d.rating >= 9.0 ? '#f5a623' : '#7ed321',
        borderRadius: [3, 3, 0, 0],
      }
    })),
    barWidth: '70%',
    label: { show: true, position: 'top', fontSize: 11, formatter: p => p.value || '' },
  }],
}))
</script>

<style scoped>
.chart-card { background: #fff; border-radius: 8px; }
</style>
