<template>
  <n-data-table
    :columns="columns"
    :data="movies"
    :bordered="false"
    :single-line="false"
    :row-key="row => row.rank"
    size="small"
    :loading="false"
    :max-height="600"
    virtual-scroll
  />
</template>

<script setup>
import { h } from 'vue'
import { NTag, NButton, NIcon, NPopover } from 'naive-ui'
import { EyeOutline } from '@vicons/ionicons5'

defineProps({ movies: Array })
const emit = defineEmits(['viewDetail'])

const columns = [
  { title: '排名', key: 'rank', width: 70, align: 'center', render(row) { return h('span', { style: { fontWeight: row.rank <= 10 ? 'bold' : 'normal', color: row.rank <= 3 ? '#e50914' : '#333' } }, `#${row.rank}`) } },
  { title: '电影名称', key: 'title', width: 180, ellipsis: { tooltip: true } },
  { title: '年份', key: 'year', width: 80, align: 'center' },
  {
    title: '评分', key: 'rating', width: 90, align: 'center',
    render(row) {
      const color = row.rating >= 9.5 ? '#e50914' : row.rating >= 9.0 ? '#f5a623' : '#7ed321'
      return h(NTag, { size: 'small', color: { color, textColor: '#fff' } }, { default: () => row.rating })
    }
  },
  { title: '导演', key: 'directors', width: 140, ellipsis: { tooltip: true }, render(row) { return row.directors.join('、') } },
  { title: '类型', key: 'genres', width: 150, ellipsis: { tooltip: true }, render(row) { return row.genres.join('、') } },
  { title: '国家', key: 'country', width: 100 },
  {
    title: '操作', key: 'actions', width: 80, align: 'center',
    render(row) {
      return h(NButton, { size: 'tiny', quaternary: true, onClick: () => emit('viewDetail', row) }, {
        default: () => h(NIcon, null, { default: () => h(EyeOutline) })
      })
    }
  },
]
</script>
