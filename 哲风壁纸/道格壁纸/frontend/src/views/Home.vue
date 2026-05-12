<template>
  <n-layout>
    <n-layout-header class="header" bordered>
      <div class="header-inner">
        <div class="logo" @click="resetFilters">
          <n-gradient-text type="primary" :size="24" style="font-weight:700">道格壁纸</n-gradient-text>
        </div>
        <div class="header-right">
          <n-button v-for="t in categories.types" :key="t.type"
            :type="activeType === t.type ? 'primary' : 'default'" size="small" secondary
            style="margin-right:8px"
            @click="filterByType(t.type)">
            {{ t.name }} ({{ t.count }})
          </n-button>
          <n-input v-model:value="keyword" placeholder="搜索标签..." clearable
            style="width:200px" @keyup.enter="search">
            <template #suffix>
              <n-icon @click="search" style="cursor:pointer">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                </svg>
              </n-icon>
            </template>
          </n-input>
        </div>
      </div>
    </n-layout-header>

    <n-layout-content class="content">
      <div class="tag-cloud" v-if="categories.tags.length">
        <span style="font-size:13px;color:#888;margin-right:12px;white-space:nowrap">热门标签：</span>
        <div class="tag-list">
          <a v-for="tag in categories.tags.slice(0, 30)" :key="tag.name"
            class="tag-link" @click="searchByTag(tag.name)">
            {{ tag.name }}
          </a>
        </div>
      </div>

      <div v-if="loading" class="loading-center">
        <n-spin size="large" />
      </div>

      <template v-else-if="wallpapers.length">
        <div class="masonry">
          <div v-for="item in wallpapers" :key="item.wtId" class="masonry-item"
            @click="openPreview(item)">
            <div class="img-wrap">
              <img :src="item.imageUrl" :alt="item.wtId" loading="lazy"
                @error="handleImgError" />
            </div>
            <div class="masonry-overlay">
              <div class="overlay-top">
                <n-tag size="tiny" :bordered="false" round>{{ item.typeName }}</n-tag>
              </div>
              <div class="overlay-bottom">
                <span>{{ item.rw }}×{{ item.rh }}</span>
                <span>↓ {{ item.downCount || 0 }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="pagination-wrap">
          <n-pagination
            v-model:page="currentPage"
            :page-count="totalPages"
            :page-size="24"
            @update:page="loadWallpapers"
          />
        </div>
      </template>

      <div v-else class="loading-center">
        <n-empty description="没有找到壁纸">
          <template #extra>
            <n-btn size="small" @click="resetFilters">重置筛选</n-btn>
          </template>
        </n-empty>
      </div>
    </n-layout-content>

    <n-layout-footer class="footer" bordered>
      <div class="footer-inner">
        <span>道格壁纸 &copy; 2025 - 高清壁纸下载</span>
        <span>数据来源：网络采集</span>
      </div>
    </n-layout-footer>

    <!-- Preview -->
    <n-modal v-model:show="showPreview" :mask-closable="true" transform-origin="center"
      preset="card" :style="modalStyle" :title="null" closable
      @close="showPreview = false">
      <n-image v-if="previewItem" :src="previewItem.imageUrl" object-fit="contain"
        width="100%" style="max-height:70vh" />
      <template v-if="previewItem" #footer>
        <div class="preview-tags">
          <n-tag v-for="label in previewItem.labelList" :key="label" size="small"
            :bordered="false" round style="margin:2px">
            {{ label }}
          </n-tag>
        </div>
        <div class="preview-meta">
          <n-space :size="12">
            <n-text depth="3">{{ previewItem.typeName }}</n-text>
            <n-text depth="3">{{ previewItem.rw }}×{{ previewItem.rh }}</n-text>
            <n-text depth="3">{{ previewItem.fileMb }}</n-text>
            <n-text depth="3">下载 {{ previewItem.downCount || 0 }}</n-text>
            <n-text depth="3">收藏 {{ previewItem.favorCount || 0 }}</n-text>
          </n-space>
        </div>
      </template>
    </n-modal>
  </n-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getWallpapers, getCategories } from '../api/index.js'

const wallpapers = ref([])
const loading = ref(true)
const currentPage = ref(1)
const totalPages = ref(1)
const keyword = ref('')
const activeType = ref(null)
const categories = ref({ types: [], tags: [] })
const showPreview = ref(false)
const previewItem = ref(null)
const modalStyle = { maxWidth: '900px', width: '90vw', borderRadius: '12px' }

async function loadWallpapers() {
  loading.value = true
  try {
    const params = { page: currentPage.value, pageSize: 24 }
    if (activeType.value) params.type = activeType.value
    if (keyword.value) params.keyword = keyword.value
    const { data } = await getWallpapers(params)
    wallpapers.value = data.items
    totalPages.value = data.totalPages
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  try {
    const { data } = await getCategories()
    categories.value = data
  } catch (e) {
    console.error(e)
  }
}

function filterByType(type) {
  activeType.value = activeType.value === type ? null : type
  currentPage.value = 1
  loadWallpapers()
}

function search() {
  currentPage.value = 1
  loadWallpapers()
}

function searchByTag(tag) {
  keyword.value = tag
  currentPage.value = 1
  loadWallpapers()
}

function resetFilters() {
  activeType.value = null
  keyword.value = ''
  currentPage.value = 1
  loadWallpapers()
}

function openPreview(item) {
  previewItem.value = item
  showPreview.value = true
}

function handleImgError(e) {
  e.target.style.display = 'none'
}

onMounted(() => {
  loadWallpapers()
  loadCategories()
})
</script>

<style scoped>
.header {
  padding: 12px 24px;
  position: sticky;
  top: 0;
  z-index: 100;
  background: #fff;
}
.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  gap: 16px;
}
.logo { cursor: pointer; flex-shrink: 0; }
.header-right {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px;
  min-height: calc(100vh - 110px);
}

.tag-cloud {
  display: flex;
  align-items: center;
  padding: 10px 0;
  margin-bottom: 16px;
  border-bottom: 1px solid #eee;
  overflow-x: auto;
}
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.tag-link {
  font-size: 13px;
  color: #666;
  cursor: pointer;
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
  transition: all 0.2s;
}
.tag-link:hover {
  color: #18a058;
  background: #f0faf5;
}

.masonry {
  column-count: 4;
  column-gap: 16px;
}
.masonry-item {
  break-inside: avoid;
  margin-bottom: 16px;
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  background: #f5f5f5;
}
.masonry-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}
.masonry-item:hover .masonry-overlay {
  opacity: 1;
}
.img-wrap {
  width: 100%;
  display: flex;
}
.img-wrap img {
  width: 100%;
  height: auto;
  display: block;
}

.masonry-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(transparent 50%, rgba(0,0,0,0.6));
  opacity: 0;
  transition: opacity 0.25s;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 10px;
  pointer-events: none;
}
.overlay-bottom {
  display: flex;
  justify-content: space-between;
  color: #fff;
  font-size: 12px;
  text-shadow: 0 1px 3px rgba(0,0,0,0.5);
}

.loading-center {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 500px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding: 32px 0 24px;
}

.footer {
  padding: 16px 24px;
}
.footer-inner {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  color: #999;
  font-size: 13px;
}

.preview-tags {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.preview-meta {
  display: flex;
  flex-wrap: wrap;
}

@media (max-width: 1024px) {
  .masonry { column-count: 3; }
}
@media (max-width: 768px) {
  .masonry { column-count: 2; }
  .header-inner { flex-direction: column; }
  .header-right { width: 100%; }
  .header-right .n-input { width: 100% !important; margin-top: 4px; }
}
@media (max-width: 480px) {
  .masonry { column-count: 1; }
}
</style>
