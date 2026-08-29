<template>
  <div class="page-container">
    <h1 class="page-title">仪表盘</h1>
    <p class="page-subtitle">系统今日概况 · {{ todayText }}</p>

    <!-- 统计卡片 -->
    <n-grid :cols="4" :x-gap="18" :y-gap="18" responsive="screen" item-responsive>
      <n-grid-item v-for="card in statCards" :key="card.label" span="4 m:4 l:2 xl:1">
        <n-card :bordered="true" class="stat-card" :style="{ borderTop: `3px solid ${card.color}` }">
          <div class="stat-body">
            <div class="stat-icon" :style="{ backgroundColor: card.bg }">
              <n-icon size="26" :color="card.color">
                <component :is="card.icon" />
              </n-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">{{ card.label }}</p>
              <p class="stat-value" :style="{ color: card.color }">{{ card.value }}</p>
              <p class="stat-trend" v-if="card.trend">
                <n-icon size="12" :component="card.trendIcon" />
                {{ card.trend }}
              </p>
            </div>
          </div>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 最新动态 与 热门借阅 -->
    <n-grid :cols="2" :x-gap="18" responsive="screen" item-responsive style="margin-top: 20px">
      <n-grid-item span="2 l:1">
        <n-card title="最新借还动态" size="small">
          <template #header-extra>
            <n-text depth="3" style="font-size: 12px">近 60 条记录</n-text>
          </template>
          <n-empty
            v-if="activities.length === 0"
            description="暂无动态"
            style="padding: 24px 0"
          />
          <ul v-else class="activity-list">
            <li v-for="(item, index) in activities" :key="index" class="activity-item">
              <div class="activity-icon" :class="`icon-${item.type}`">
                <n-icon :component="activityIcon(item.type)" :color="activityColor(item.type)" />
              </div>
              <div class="activity-content">
                <p class="activity-text">
                  <template v-if="item.type === 'borrow'">
                    <n-text strong>读者 {{ item.reader_label }}</n-text> 借出了图书
                    <n-text strong>《{{ item.book_title }}》</n-text>
                  </template>
                  <template v-else-if="item.type === 'return'">
                    <n-text strong>读者 {{ item.reader_label }}</n-text> 归还了图书
                    <n-text strong>《{{ item.book_title }}》</n-text>
                  </template>
                  <template v-else>
                    <n-text type="error" strong>逾期提醒</n-text>
                    致读者 {{ item.reader_label }} — 《{{ item.book_title }}》逾期
                    {{ item.overdue_days }} 天
                  </template>
                </p>
                <p class="activity-time">{{ formatTime(item.time) }}</p>
              </div>
            </li>
          </ul>
        </n-card>
      </n-grid-item>

      <n-grid-item span="2 l:1">
        <n-card title="本月热门借阅" size="small">
          <template #header-extra>
            <n-text depth="3" style="font-size: 12px">借阅次数排行</n-text>
          </template>
          <n-empty v-if="popularBooks.length === 0" description="暂无数据" style="padding: 24px 0" />
          <ul v-else class="popular-list">
            <li v-for="(book, index) in popularBooks" :key="book.isbn" class="popular-item">
              <div class="rank-badge" :class="`rank-${index + 1}`">{{ index + 1 }}</div>
              <div class="popular-info">
                <p class="popular-title">《{{ book.title }}》</p>
                <p class="popular-author">{{ book.author }}</p>
              </div>
              <div class="popular-count">
                <n-text strong type="primary">{{ book.count }}</n-text>
                <n-text depth="3" style="font-size: 12px"> 次借阅</n-text>
              </div>
            </li>
          </ul>
        </n-card>
      </n-grid-item>
    </n-grid>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, h } from 'vue'
import { NEmpty, NCard, NGrid, NGridItem, NText, NIcon } from 'naive-ui'
import {
  AlbumsOutline,
  AlertCircleOutline,
  ArrowDownOutline,
  ArrowUpOutline,
  PeopleOutline,
  SwapHorizontalOutline,
  TrendingUpOutline,
  WarningOutline
} from '@vicons/ionicons5'
import { getDashboardStats, getPopularBooks, getRecentActivities } from '../api'

const stats = ref({
  total_books: 0,
  total_readers: 0,
  borrowed_now: 0,
  overdue: 0,
  new_books_month: 0,
  new_readers_week: 0,
  available_books: 0
})
const activities = ref([])
const popularBooks = ref([])

const todayText = computed(() => {
  const d = new Date()
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 星期${weekdays[d.getDay()]}`
})

const statCards = computed(() => [
  {
    label: '馆藏总数',
    value: stats.value.total_books.toLocaleString(),
    icon: AlbumsOutline,
    color: '#3b82f6',
    bg: '#eff6ff',
    trend: `+${stats.value.new_books_month} 本月`,
    trendIcon: TrendingUpOutline
  },
  {
    label: '活跃读者',
    value: stats.value.total_readers.toLocaleString(),
    icon: PeopleOutline,
    color: '#10b981',
    bg: '#ecfdf5',
    trend: `+${stats.value.new_readers_week} 本周`,
    trendIcon: TrendingUpOutline
  },
  {
    label: '当前借出',
    value: stats.value.borrowed_now.toLocaleString(),
    icon: SwapHorizontalOutline,
    color: '#8b5cf6',
    bg: '#f5f3ff'
  },
  {
    label: '逾期未还',
    value: stats.value.overdue.toLocaleString(),
    icon: AlertCircleOutline,
    color: '#ef4444',
    bg: '#fef2f2',
    trend: '需催还'
  }
])

function activityIcon(type) {
  if (type === 'borrow') return ArrowUpOutline
  if (type === 'return') return ArrowDownOutline
  return WarningOutline
}

function activityColor(type) {
  if (type === 'borrow') return '#3b82f6'
  if (type === 'return') return '#10b981'
  return '#ef4444'
}

function formatTime(value) {
  if (!value) return ''
  const d = new Date(value)
  const now = new Date()
  const diff = (now - d) / 1000
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  if (diff < 172800) return '昨天'
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onMounted(async () => {
  const [statsRes, activityRes, popularRes] = await Promise.allSettled([
    getDashboardStats(),
    getRecentActivities(),
    getPopularBooks()
  ])
  if (statsRes.status === 'fulfilled') stats.value = statsRes.value
  if (activityRes.status === 'fulfilled') activities.value = activityRes.value
  if (popularRes.status === 'fulfilled') popularBooks.value = popularRes.value
})
</script>

<style scoped>
.stat-card {
  border-radius: 12px;
  overflow: hidden;
}

.stat-body {
  display: flex;
  align-items: center;
  gap: 14px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  min-width: 0;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
  margin: 0 0 4px 0;
  white-space: nowrap;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 2px 0;
  line-height: 1.1;
}

.stat-trend {
  font-size: 12px;
  color: #10b981;
  display: flex;
  align-items: center;
  gap: 2px;
  margin: 0;
}

.activity-list,
.popular-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.activity-item {
  display: flex;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px dashed #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-borrow {
  background-color: #eff6ff;
}

.icon-return {
  background-color: #ecfdf5;
}

.icon-overdue {
  background-color: #fef2f2;
}

.activity-content {
  min-width: 0;
}

.activity-text {
  margin: 0 0 3px 0;
  font-size: 13px;
  color: #374151;
  line-height: 1.5;
}

.activity-time {
  margin: 0;
  font-size: 12px;
  color: #9ca3af;
}

.popular-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px dashed #f0f0f0;
}

.popular-item:last-child {
  border-bottom: none;
}

.rank-badge {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background-color: #e5e7eb;
  color: #6b7280;
  font-weight: 700;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.rank-1 {
  background-color: #fef3c7;
  color: #d97706;
}

.rank-2 {
  background-color: #e5e7eb;
  color: #4b5563;
}

.rank-3 {
  background-color: #fde8e8;
  color: #b45309;
}

.popular-info {
  flex: 1;
  min-width: 0;
}

.popular-title {
  margin: 0 0 2px 0;
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.popular-author {
  margin: 0;
  font-size: 12px;
  color: #9ca3af;
}

.popular-count {
  font-size: 13px;
  white-space: nowrap;
}
</style>
