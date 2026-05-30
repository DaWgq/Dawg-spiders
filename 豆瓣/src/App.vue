<template>
  <n-config-provider :theme-overrides="themeOverrides" :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <div class="app">
        <n-layout>
          <n-layout-header class="header">
            <div class="header-inner">
              <h1 class="logo">🎬 豆瓣电影 Top 250</h1>
              <span class="subtitle">数据可视化分析平台</span>
            </div>
          </n-layout-header>

          <n-layout-content class="content">
            <SearchFilter
              v-model:search-query="searchQuery"
              v-model:rating-range="ratingRange"
              v-model:year-range="yearRange"
              v-model:selected-genres="selectedGenres"
              v-model:selected-countries="selectedCountries"
              :available-genres="availableGenres"
              :available-countries="availableCountries"
              @reset="resetFilters"
            />

            <n-tabs type="line" animated size="large" class="main-tabs">
              <n-tab-pane name="list" tab="📋 电影列表">
                <MovieTable
                  :movies="filteredMovies"
                  @view-detail="handleViewDetail"
                />
              </n-tab-pane>
              <n-tab-pane name="rating" tab="⭐ 评分分布">
                <RatingChart :data="ratingDistribution" />
              </n-tab-pane>
              <n-tab-pane name="year" tab="📅 年份分布">
                <YearChart :data="yearDistribution" />
              </n-tab-pane>
              <n-tab-pane name="country" tab="🌍 国家/地区">
                <CountryChart :data="countryDistribution" />
              </n-tab-pane>
            </n-tabs>

            <n-divider />

            <n-statistic label="当前筛选结果" :value="filteredMovies.length" />
          </n-layout-content>

          <n-layout-footer class="footer">
            豆瓣电影 Top 250 可视化 | Vue 3 + Naive UI + ECharts
          </n-layout-footer>
        </n-layout>

        <MovieDetail
          v-model:show="detailVisible"
          :movie="selectedMovie"
        />
      </div>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { ref } from 'vue'
import { zhCN, dateZhCN } from 'naive-ui'
import SearchFilter from './components/SearchFilter.vue'
import MovieTable from './components/MovieTable.vue'
import RatingChart from './components/RatingChart.vue'
import YearChart from './components/YearChart.vue'
import CountryChart from './components/CountryChart.vue'
import MovieDetail from './components/MovieDetail.vue'
import { useMovies } from './composables/useMovies'

const {
  searchQuery,
  ratingRange,
  yearRange,
  selectedGenres,
  selectedCountries,
  availableGenres,
  availableCountries,
  filteredMovies,
  ratingDistribution,
  yearDistribution,
  countryDistribution,
  resetFilters,
} = useMovies()

const detailVisible = ref(false)
const selectedMovie = ref(null)

function handleViewDetail(movie) {
  selectedMovie.value = movie
  detailVisible.value = true
}

const themeOverrides = {
  common: {
    primaryColor: '#e50914',
    primaryColorHover: '#ff0a16',
    primaryColorPressed: '#b20710',
  },
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #f5f5f5; }
.app { min-height: 100vh; }
.header {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  padding: 24px 0;
  color: #fff;
}
.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}
.logo { font-size: 28px; font-weight: 700; letter-spacing: 1px; }
.subtitle {
  font-size: 14px;
  color: rgba(255,255,255,0.65);
  margin-left: 16px;
}
.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  min-height: calc(100vh - 160px);
}
.main-tabs { margin-top: 16px; }
.footer {
  text-align: center;
  padding: 16px;
  color: #888;
  font-size: 13px;
  background: #fff;
  border-top: 1px solid #eee;
}
</style>
