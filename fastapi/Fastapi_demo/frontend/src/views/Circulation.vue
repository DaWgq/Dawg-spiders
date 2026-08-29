<template>
  <div class="page-container">
    <h1 class="page-title">借阅流通台</h1>
    <p class="page-subtitle">处理借书、还书、续借等日常操作</p>

    <!-- 借书 / 还书 面板 -->
    <n-grid :cols="2" :x-gap="18" responsive="screen" item-responsive style="margin-bottom: 20px">
      <n-grid-item span="2 m:1">
        <n-card :bordered="true" class="flow-card">
          <template #header>
            <div class="card-header">
              <span class="header-icon icon-borrow">
                <n-icon size="18" color="#3b82f6"><ArrowUpOutline /></n-icon>
              </span>
              <span class="header-title">借书办理</span>
            </div>
          </template>
          <n-form label-placement="top">
            <n-form-item label="读者 (搜索姓名 / 编号)">
              <n-select
                v-model:value="borrowForm.reader_id"
                :options="readerOptions"
                filterable
                remote
                clearable
                placeholder="输入姓名或编号搜索读者"
                :loading="readerLoading"
                @search="searchReaders"
              >
                <template #action v-if="selectedReader">
                  <n-space align="center" justify="space-between">
                    <n-tag :type="selectedReader.status === '冻结' ? 'error' : 'success'" size="small" round>
                      {{ selectedReader.status }}
                    </n-tag>
                    <n-text depth="3" style="font-size: 12px">
                      {{ selectedReader.reader_no }} · {{ selectedReader.name }}
                    </n-text>
                  </n-space>
                </template>
              </n-select>
            </n-form-item>
            <n-form-item label="图书 (搜索书名 / 作者 / ISBN)">
              <n-select
                v-model:value="borrowForm.book_id"
                :options="bookOptions"
                filterable
                remote
                clearable
                placeholder="输入书名、作者或ISBN搜索图书"
                :loading="bookLoading"
                @search="searchBooks"
              >
                <template #action v-if="selectedBook">
                  <n-space align="center" justify="space-between">
                    <n-text depth="3" style="font-size: 12px">
                      可借 {{ selectedBook.available_copies }}/{{ selectedBook.total_copies }} 本
                    </n-text>
                  </n-space>
                </template>
              </n-select>
            </n-form-item>
            <n-form-item label="借期 (天)">
              <n-input-number v-model:value="borrowForm.days" :min="1" :max="365" style="width: 160px" />
            </n-form-item>
            <n-button
              type="primary"
              block
              :loading="borrowing"
              :disabled="!borrowForm.reader_id || !borrowForm.book_id"
              @click="handleBorrow"
            >
              <template #icon>
                <n-icon><AddOutline /></n-icon>
              </template>
              确认借出
            </n-button>
          </n-form>
        </n-card>
      </n-grid-item>

      <n-grid-item span="2 m:1">
        <n-card :bordered="true" class="flow-card">
          <template #header>
            <div class="card-header">
              <span class="header-icon icon-return">
                <n-icon size="18" color="#10b981"><ArrowDownOutline /></n-icon>
              </span>
              <span class="header-title">还书办理</span>
            </div>
          </template>
          <n-form label-placement="top">
            <n-form-item label="图书 (搜索书名 / 作者 / ISBN)">
              <n-select
                v-model:value="returnForm.book_id"
                :options="returnBookOptions"
                filterable
                remote
                clearable
                placeholder="搜索或输入图书条码进行归还"
                :loading="returnBookLoading"
                @search="searchReturnBooks"
              />
            </n-form-item>
            <div class="return-tip">
              <n-icon size="16" color="#f59e0b"><InformationCircleOutline /></n-icon>
              <span>扫描/选择图书后将自动归还该图书最早的借出记录</span>
            </div>
            <n-button
              type="success"
              block
              :loading="returning"
              :disabled="!returnForm.book_id"
              @click="handleReturn"
              style="margin-top: 8px"
            >
              <template #icon>
                <n-icon><ArrowDownOutline /></n-icon>
              </template>
              确认还书
            </n-button>
          </n-form>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 借阅记录 -->
    <n-card :bordered="true" title="借阅记录" size="small">
      <template #header-extra>
        <n-radio-group v-model:value="recordQuery.status" size="small" @update:value="handleRecordSearch">
          <n-radio-button
            v-for="opt in recordStatusOptions"
            :key="opt.value"
            :value="opt.value"
          >
            {{ opt.label }}
          </n-radio-button>
        </n-radio-group>
      </template>
      <n-data-table
        :columns="recordColumns"
        :data="records"
        :loading="recordsLoading"
        :row-key="(row) => row.id"
        :pagination="false"
        :bordered="false"
        :scroll-x="1100"
      />
      <div class="pagination-row">
        <n-text depth="3" style="font-size: 13px">共 {{ recordsTotal }} 条记录</n-text>
        <n-pagination
          v-model:page="recordQuery.page"
          :page-size="recordQuery.page_size"
          :item-count="recordsTotal"
          :page-sizes="[10, 20, 50]"
          show-size-picker
          @update:page="fetchRecords"
          @update:page-size="handleRecordPageSize"
        />
      </div>
    </n-card>
  </div>
</template>

<script setup>
import { computed, h, onMounted, reactive, ref } from 'vue'
import {
  NButton,
  NCard,
  NDataTable,
  NForm,
  NFormItem,
  NGrid,
  NGridItem,
  NIcon,
  NInputNumber,
  NPagination,
  NRadioButton,
  NRadioGroup,
  NSelect,
  NSpace,
  NTag,
  NText,
  useDialog,
  useMessage
} from 'naive-ui'
import {
  AddOutline,
  ArrowDownOutline,
  ArrowUpOutline,
  InformationCircleOutline
} from '@vicons/ionicons5'
import {
  borrowBook,
  getBorrowRecords,
  queryBooks,
  queryReaders,
  renewRecord,
  returnBook
} from '../api'

const message = useMessage()
const dialog = useDialog()

// ---------- 借书 ----------
const borrowForm = reactive({
  reader_id: null,
  book_id: null,
  days: 30
})
const readerOptions = ref([])
const bookOptions = ref([])
const readerLoading = ref(false)
const bookLoading = ref(false)
const borrowing = ref(false)
const selectedReader = computed(() =>
  readerOptions.value.find((o) => o.value === borrowForm.reader_id)
)
const selectedBook = computed(() =>
  bookOptions.value.find((o) => o.value === borrowForm.book_id)
)

async function searchReaders(keyword) {
  if (!keyword) {
    readerOptions.value = []
    return
  }
  readerLoading.value = true
  try {
    const res = await queryReaders(keyword)
    readerOptions.value = res.map((r) => ({
      label: `${r.reader_no} · ${r.name}${r.status === '冻结' ? ' (冻结)' : ''}`,
      value: r.id,
      reader_no: r.reader_no,
      name: r.name,
      status: r.status
    }))
  } catch {
    readerOptions.value = []
  } finally {
    readerLoading.value = false
  }
}

async function searchBooks(keyword) {
  if (!keyword) {
    bookOptions.value = []
    return
  }
  bookLoading.value = true
  try {
    const res = await queryBooks(keyword)
    bookOptions.value = res.map((b) => ({
      label: `${b.isbn} · ${b.title}${b.available_copies <= 0 ? ' (已借完)' : ''}`,
      value: b.id,
      isbn: b.isbn,
      title: b.title,
      available_copies: b.available_copies,
      total_copies: b.total_copies
    }))
  } catch {
    bookOptions.value = []
  } finally {
    bookLoading.value = false
  }
}

async function handleBorrow() {
  borrowing.value = true
  try {
    const res = await borrowBook({
      reader_id: borrowForm.reader_id,
      book_id: borrowForm.book_id,
      days: borrowForm.days || 30
    })
    message.success(
      `借书成功! 《${res.book_title}》 应还日期: ${formatDate(res.due_date)}`
    )
    borrowForm.reader_id = null
    borrowForm.book_id = null
    borrowForm.days = 30
    readerOptions.value = []
    bookOptions.value = []
    fetchRecords()
  } catch {
    // 错误提示已由拦截器统一处理
  } finally {
    borrowing.value = false
  }
}

// ---------- 还书 ----------
const returnForm = reactive({
  book_id: null
})
const returnBookOptions = ref([])
const returnBookLoading = ref(false)
const returning = ref(false)

async function searchReturnBooks(keyword) {
  if (!keyword) {
    returnBookOptions.value = []
    return
  }
  returnBookLoading.value = true
  try {
    const res = await queryBooks(keyword)
    returnBookOptions.value = res.map((b) => ({
      label: `${b.isbn} · ${b.title}`,
      value: b.id
    }))
  } catch {
    returnBookOptions.value = []
  } finally {
    returnBookLoading.value = false
  }
}

async function handleReturn() {
  returning.value = true
  try {
    const res = await returnBook({ book_id: returnForm.book_id })
    message.success(`还书成功! 读者 ${res.reader_name} 归还了《${res.book_title}》`)
    returnForm.book_id = null
    returnBookOptions.value = []
    fetchRecords()
  } catch {
    // 错误提示已由拦截器统一处理
  } finally {
    returning.value = false
  }
}

// ---------- 借阅记录 ----------
const records = ref([])
const recordsTotal = ref(0)
const recordsLoading = ref(false)
const recordQuery = reactive({
  status: '',
  page: 1,
  page_size: 10
})

const recordStatusOptions = [
  { label: '全部', value: '' },
  { label: '借出中', value: '借出中' },
  { label: '已归还', value: '已归还' },
  { label: '逾期', value: '逾期' }
]

const recordColumns = [
  {
    title: '读者',
    key: 'reader',
    width: 150,
    render(row) {
      return h('div', [
        h('div', { style: 'font-size:14px;font-weight:600;color:#1f2937' }, row.reader_name),
        h('div', { style: 'font-size:12px;color:#9ca3af' }, row.reader_no)
      ])
    }
  },
  {
    title: '图书',
    key: 'book',
    minWidth: 220,
    render(row) {
      return h('div', [
        h('div', { style: 'font-size:14px;color:#1f2937' }, row.book_title),
        h('div', { style: 'font-size:12px;color:#9ca3af' }, `ISBN: ${row.book_isbn}`)
      ])
    }
  },
  { title: '借出时间', key: 'borrow_date', width: 160, render: (row) => formatDate(row.borrow_date) },
  {
    title: '应还日期',
    key: 'due_date',
    width: 160,
    render(row) {
      return h('span', { style: `font-weight:500;color:${row.status === '逾期' ? '#ef4444' : 'inherit'}` }, formatDate(row.due_date))
    }
  },
  { title: '归还时间', key: 'return_date', width: 160, render: (row) => (row.return_date ? formatDate(row.return_date) : '-') },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render(row) {
      const map = { 借出中: 'info', 已归还: 'success', 逾期: 'error' }
      return h(NTag, { type: map[row.status] || 'default', size: 'small', round: true }, { default: () => row.status })
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 90,
    align: 'center',
    render(row) {
      if (row.status === '已归还') {
        return h(NText, { depth: 3, style: 'font-size:12px' }, { default: () => '-' })
      }
      return h(
        NButton,
        {
          size: 'small',
          type: 'info',
          secondary: true,
          onClick: () => handleRenew(row)
        },
        { default: () => '续借' }
      )
    }
  }
]

function formatDate(value) {
  if (!value) return '-'
  const d = new Date(value)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function fetchRecords() {
  recordsLoading.value = true
  try {
    const res = await getBorrowRecords({
      status: recordQuery.status,
      page: recordQuery.page,
      page_size: recordQuery.page_size
    })
    records.value = res.items
    recordsTotal.value = res.total
  } catch {
    // 错误提示已由拦截器统一处理
  } finally {
    recordsLoading.value = false
  }
}

function handleRecordSearch() {
  recordQuery.page = 1
  fetchRecords()
}

function handleRecordPageSize(size) {
  recordQuery.page_size = size
  recordQuery.page = 1
  fetchRecords()
}

function handleRenew(row) {
  dialog.info({
    title: '续借确认',
    content: `确定为读者 ${row.reader_name} 续借《${row.book_title}》30天吗?`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        const res = await renewRecord({ record_id: row.id, days: 30 })
        message.success(`续借成功! 新的应还日期: ${formatDate(res.due_date)}`)
        fetchRecords()
      } catch {
        // 错误提示已由拦截器统一处理
      }
    }
  })
}

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-borrow {
  background-color: #eff6ff;
}

.icon-return {
  background-color: #ecfdf5;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.return-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #6b7280;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 8px;
}

.pagination-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 16px;
}
</style>
