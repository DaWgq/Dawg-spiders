<template>
  <n-modal
    :show="show"
    @update:show="$emit('update:show', $event)"
    :mask-closable="true"
    preset="card"
    style="max-width: 680px;"
    :title="movie?.title"
    :bordered="false"
    size="huge"
  >
    <template v-if="movie">
      <n-descriptions label-placement="left" :column="2" bordered size="small">
        <n-descriptions-item label="评分">
          <n-tag :color="{ color: ratingColor, textColor: '#fff' }" size="small">
            {{ movie.rating }}
          </n-tag>
        </n-descriptions-item>
        <n-descriptions-item label="排名">#{{ movie.rank }}</n-descriptions-item>
        <n-descriptions-item label="原名">{{ movie.original_title }}</n-descriptions-item>
        <n-descriptions-item label="年份">{{ movie.year }}</n-descriptions-item>
        <n-descriptions-item label="导演">{{ movie.directors.join('、') }}</n-descriptions-item>
        <n-descriptions-item label="国家/地区">{{ movie.country }}</n-descriptions-item>
        <n-descriptions-item label="类型">{{ movie.genres.join('、') }}</n-descriptions-item>
        <n-descriptions-item label="片长">{{ movie.duration }} 分钟</n-descriptions-item>
        <n-descriptions-item label="主演" :span="2">{{ movie.actors.join('、') }}</n-descriptions-item>
        <n-descriptions-item label="简介" :span="2">
          <n-ellipsis :line-clamp="4">{{ movie.summary }}</n-ellipsis>
        </n-descriptions-item>
        <n-descriptions-item label="评论数" :span="2">{{ movie.comments_count.toLocaleString() }}</n-descriptions-item>
      </n-descriptions>
    </template>
  </n-modal>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  show: Boolean,
  movie: Object,
})

defineEmits(['update:show'])

const ratingColor = computed(() => {
  if (!props.movie) return '#999'
  const r = props.movie.rating
  if (r >= 9.5) return '#e50914'
  if (r >= 9.0) return '#f5a623'
  return '#7ed321'
})
</script>
