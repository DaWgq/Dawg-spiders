<template>
  <n-card class="filter-card" :bordered="false">
    <n-space vertical>
      <n-grid :cols="24" :x-gap="16" :y-gap="12">
        <n-grid-item :span="24">
          <n-input
            :value="searchQuery"
            @update:value="$emit('update:searchQuery', $event)"
            placeholder="搜索电影标题、导演..."
            clearable
            size="large"
          >
            <template #prefix>
              <n-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg></n-icon>
            </template>
          </n-input>
        </n-grid-item>

        <n-grid-item :span="12">
          <n-space vertical size="small">
            <span class="filter-label">评分范围</span>
            <n-slider
              :value="ratingRange"
              @update:value="$emit('update:ratingRange', $event)"
              :min="8"
              :max="10"
              :step="0.1"
              range
              :marks="{ 8: '8.0', 9: '9.0', 10: '10.0' }"
            />
          </n-space>
        </n-grid-item>

        <n-grid-item :span="12">
          <n-space vertical size="small">
            <span class="filter-label">上映年份</span>
            <n-slider
              :value="yearRange"
              @update:value="$emit('update:yearRange', $event)"
              :min="1950"
              :max="2025"
              :step="1"
              range
              :marks="{ '1950': '1950', '2000': '2000', '2025': '2025' }"
            />
          </n-space>
        </n-grid-item>

        <n-grid-item :span="12">
          <n-select
            :value="selectedGenres"
            @update:value="$emit('update:selectedGenres', $event)"
            :options="genreOptions"
            placeholder="选择类型"
            multiple
            clearable
          />
        </n-grid-item>

        <n-grid-item :span="12">
          <n-select
            :value="selectedCountries"
            @update:value="$emit('update:selectedCountries', $event)"
            :options="countryOptions"
            placeholder="选择国家/地区"
            multiple
            clearable
          />
        </n-grid-item>
      </n-grid>

      <n-button @click="$emit('reset')" tertiary round size="small" style="align-self: flex-end;">
        重置筛选
      </n-button>
    </n-space>
  </n-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  searchQuery: String,
  ratingRange: Array,
  yearRange: Array,
  selectedGenres: Array,
  selectedCountries: Array,
  availableGenres: Array,
  availableCountries: Array,
})

defineEmits(['update:searchQuery', 'update:ratingRange', 'update:yearRange', 'update:selectedGenres', 'update:selectedCountries', 'reset'])

const genreOptions = computed(() =>
  props.availableGenres.map(g => ({ label: g, value: g }))
)
const countryOptions = computed(() =>
  props.availableCountries.map(c => ({ label: c, value: c }))
)
</script>

<style scoped>
.filter-card { background: #fff; border-radius: 8px; }
.filter-label { font-size: 13px; color: #666; padding-left: 4px; }
</style>
