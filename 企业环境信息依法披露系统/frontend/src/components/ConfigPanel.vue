<template>
  <div class="card config-panel">
    <h2 class="section-header">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#475569" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="3"/>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
      </svg>
      爬虫配置
    </h2>

    <div class="config-form">
      <div>
        <label class="form-label">目标总页数 (TOTAL_PAGES)</label>
        <input
          type="number"
          class="form-input"
          :value="config.totalPages"
          :disabled="disabled"
          @change="update('totalPages', $event.target.value)"
        />
      </div>

      <div class="form-row">
        <div>
          <label class="form-label">每页条数</label>
          <input
            type="number"
            class="form-input"
            :value="config.pageSize"
            :disabled="disabled"
            @change="update('pageSize', $event.target.value)"
          />
        </div>
        <div>
          <label class="form-label">请求延时(秒)</label>
          <input
            type="number"
            class="form-input"
            :value="config.delay"
            :disabled="disabled"
            @change="update('delay', $event.target.value)"
          />
        </div>
      </div>

      <div>
        <label class="form-label">会话 Cookie (JSESSIONID)</label>
        <input
          type="text"
          class="form-input form-input-mono"
          :value="config.cookie"
          placeholder="JSESSIONID=..."
          @change="update('cookie', $event.target.value)"
        />
      </div>

      <div class="file-tags">
        <div class="file-tag">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
          </svg>
          {{ config.csvFile }}
        </div>
        <div class="file-tag">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
          </svg>
          {{ config.checkpointFile }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  config: { type: Object, required: true },
  disabled: { type: Boolean, default: false }
})

const emit = defineEmits(['update'])

function update(field, value) {
  const val = ['totalPages', 'pageSize', 'delay', 'retryLimit'].includes(field)
    ? Number(value)
    : value
  emit('update', { [field]: val })
}
</script>
