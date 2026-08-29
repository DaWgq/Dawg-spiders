<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">图书管理</h1>
        <p class="page-subtitle">管理馆藏图书信息</p>
      </div>
      <n-button type="primary" @click="openCreateModal">
        <template #icon>
          <n-icon><AddOutline /></n-icon>
        </template>
        新增图书
      </n-button>
    </div>

    <!-- 筛选工具栏 -->
    <n-card :bordered="true" class="toolbar-card" size="small">
      <div class="toolbar">
        <n-input
          v-model:value="query.keyword"
          placeholder="搜索书名、作者、ISBN、出版社..."
          clearable
          style="width: 320px"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <n-icon><SearchOutline /></n-icon>
          </template>
        </n-input>
        <n-select
          v-model:value="query.category_id"
          :options="categoryOptions"
          placeholder="全部分类"
          clearable
          style="width: 180px"
        />
        <n-select
          v-model:value="query.status"
          :options="statusOptions"
          placeholder="所有状态"
          clearable
          style="width: 160px"
        />
        <n-button type="primary" secondary @click="handleSearch">
          <template #icon>
            <n-icon><SearchOutline /></n-icon>
          </template>
          查询
        </n-button>
        <n-button quaternary @click="handleReset">
          <template #icon>
            <n-icon><RefreshOutline /></n-icon>
          </template>
          重置
        </n-button>
      </div>
    </n-card>

    <!-- 图书表格 -->
    <n-card :bordered="true" class="table-card">
      <n-data-table
        :columns="columns"
        :data="books"
        :loading="loading"
        :row-key="(row) => row.id"
        :pagination="false"
        :bordered="false"
        :scroll-x="900"
      />
      <div class="pagination-row">
        <n-text depth="3" style="font-size: 13px">
          共 {{ total }} 条记录
        </n-text>
        <n-pagination
          v-model:page="query.page"
          :page-size="query.page_size"
          :item-count="total"
          :page-sizes="[10, 20, 50]"
          show-size-picker
          @update:page="fetchBooks"
          @update:page-size="handlePageSizeChange"
        />
      </div>
    </n-card>

    <!-- 新增/编辑 弹窗 -->
    <n-modal
      v-model:show="modalVisible"
      preset="card"
      :title="editingId ? '编辑图书信息' : '新增图书信息'"
      style="width: 640px"
      :mask-closable="false"
    >
      <n-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-placement="left"
        label-width="100"
        require-mark-placement="right-hanging"
      >
        <n-form-item label="ISBN" path="isbn">
          <n-input v-model:value="form.isbn" placeholder="例如: 9787111544937" />
        </n-form-item>
        <n-form-item label="书名" path="title">
          <n-input v-model:value="form.title" placeholder="请输入书名" />
        </n-form-item>
        <n-grid :cols="2" :x-gap="16">
          <n-form-item-gi label="作者" path="author">
            <n-input v-model:value="form.author" placeholder="请输入作者" />
          </n-form-item-gi>
          <n-form-item-gi label="出版社" path="publisher">
            <n-input v-model:value="form.publisher" placeholder="请输入出版社" />
          </n-form-item-gi>
          <n-form-item-gi label="分类" path="category_id">
            <n-select
              v-model:value="form.category_id"
              :options="categoryOptions"
              placeholder="请选择分类"
              clearable
            />
          </n-form-item-gi>
          <n-form-item-gi label="馆藏位置" path="location">
            <n-input v-model:value="form.location" placeholder="如: A区-03架-02层" />
          </n-form-item-gi>
        </n-grid>
        <n-form-item label="总馆藏数量" path="total_copies">
          <n-input-number
            v-model:value="form.total_copies"
            :min="1"
            :max="9999"
            style="width: 100%"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <div class="modal-footer">
          <n-button @click="modalVisible = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="handleSave">保存</n-button>
        </div>
      </template>
    </n-modal>
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
  NFormItemGi,
  NGrid,
  NIcon,
  NInput,
  NInputNumber,
  NModal,
  NPagination,
  NSelect,
  NSpace,
  NTag,
  NText,
  useDialog,
  useMessage
} from 'naive-ui'
import {
  AddOutline,
  BookOutline,
  CreateOutline,
  RefreshOutline,
  SearchOutline,
  TrashOutline
} from '@vicons/ionicons5'
import { createBook, deleteBook, getBookCategories, getBooks, updateBook } from '../api'

const message = useMessage()
const dialog = useDialog()

const books = ref([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const categories = ref([])
const modalVisible = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const query = reactive({
  keyword: '',
  category_id: null,
  status: '',
  page: 1,
  page_size: 10
})

const form = reactive({
  isbn: '',
  title: '',
  author: '',
  publisher: '',
  category_id: null,
  location: '',
  total_copies: 1
})

const rules = {
  isbn: { required: true, message: '请输入 ISBN', trigger: ['blur', 'input'] },
  title: { required: true, message: '请输入书名', trigger: ['blur', 'input'] },
  author: { required: true, message: '请输入作者', trigger: ['blur', 'input'] },
  total_copies: { required: true, message: '请输入总馆藏数量', trigger: 'blur' }
}

const categoryOptions = computed(() =>
  categories.value.map((c) => ({ label: c.name, value: c.id }))
)

const statusOptions = [
  { label: '在馆可借', value: '在馆可借' },
  { label: '全部借出', value: '全部借出' }
]

function statusInfo(book) {
  if (book.available_copies === 0) {
    return { label: '全部借出', type: 'error' }
  }
  if (book.available_copies < book.total_copies * 0.3) {
    return { label: '库存紧张', type: 'warning' }
  }
  return { label: '在馆可借', type: 'success' }
}

const columns = [
  { title: 'ISBN', key: 'isbn', width: 150, fixed: 'left' },
  {
    title: '书名信息',
    key: 'title',
    minWidth: 260,
    render(row) {
      return h('div', { style: 'display:flex;align-items:center;gap:12px' }, [
        h(
          'div',
          {
            style:
              'width:36px;height:44px;border-radius:4px;background:#eef1f5;display:flex;align-items:center;justify-content:center;flex-shrink:0'
          },
          [h(NIcon, { size: 18, color: '#9ca3af' }, { default: () => h(BookOutline) })]
        ),
        h('div', { style: 'min-width:0' }, [
          h(
            'div',
            {
              style:
                'font-size:14px;font-weight:600;color:#1f2937;max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap',
              title: row.title
            },
            row.title
          ),
          h(
            'div',
            { style: 'font-size:12px;color:#9ca3af;margin-top:2px' },
            `${row.author}${row.publisher ? ' | ' + row.publisher : ''}`
          )
        ])
      ])
    }
  },
  {
    title: '分类',
    key: 'category_name',
    width: 110,
    render(row) {
      return h(
        NTag,
        { size: 'small', bordered: true, style: 'background:#f3f4f6;color:#374151;border-color:#e5e7eb' },
        { default: () => row.category_name || '-' }
      )
    }
  },
  {
    title: '库存 (在馆/总数)',
    key: 'stock',
    width: 140,
    render(row) {
      return h(
        'span',
        { style: 'font-size:13px' },
        [
          h(
            'span',
            {
              style: `font-weight:600;color:${row.available_copies > 0 ? '#3b82f6' : '#9ca3af'}`
            },
            String(row.available_copies)
          ),
          ' / ' + String(row.total_copies)
        ]
      )
    }
  },
  {
    title: '状态',
    key: 'status',
    width: 110,
    render(row) {
      const info = statusInfo(row)
      return h(NTag, { type: info.type, size: 'small', round: true }, { default: () => info.label })
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 110,
    align: 'center',
    render(row) {
      return h(NSpace, { justify: 'center' }, {
        default: () => [
          h(
            NButton,
            {
              quaternary: true,
              circle: true,
              size: 'small',
              onClick: () => openEditModal(row)
            },
            { icon: () => h(NIcon, { size: 18, color: '#3b82f6' }, { default: () => h(CreateOutline) }) }
          ),
          h(
            NButton,
            {
              quaternary: true,
              circle: true,
              size: 'small',
              onClick: () => handleDelete(row)
            },
            { icon: () => h(NIcon, { size: 18, color: '#ef4444' }, { default: () => h(TrashOutline) }) }
          )
        ]
      })
    }
  }
]

async function fetchBooks() {
  loading.value = true
  try {
    const params = {
      keyword: query.keyword,
      category_id: query.category_id ?? undefined,
      status: query.status,
      page: query.page,
      page_size: query.page_size
    }
    const res = await getBooks(params)
    books.value = res.items
    total.value = res.total
  } catch {
    // 错误提示已由拦截器统一处理
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  try {
    categories.value = await getBookCategories()
  } catch {
    categories.value = []
  }
}

function handleSearch() {
  query.page = 1
  fetchBooks()
}

function handleReset() {
  query.keyword = ''
  query.category_id = null
  query.status = ''
  query.page = 1
  fetchBooks()
}

function handlePageSizeChange(size) {
  query.page_size = size
  query.page = 1
  fetchBooks()
}

function resetForm() {
  form.isbn = ''
  form.title = ''
  form.author = ''
  form.publisher = ''
  form.category_id = null
  form.location = ''
  form.total_copies = 1
}

function openCreateModal() {
  editingId.value = null
  resetForm()
  modalVisible.value = true
}

function openEditModal(row) {
  editingId.value = row.id
  Object.assign(form, {
    isbn: row.isbn,
    title: row.title,
    author: row.author,
    publisher: row.publisher || '',
    category_id: row.category_id,
    location: row.location || '',
    total_copies: row.total_copies
  })
  modalVisible.value = true
}

async function handleSave() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      await updateBook(editingId.value, { ...form })
      message.success('图书信息已更新')
    } else {
      await createBook({ ...form })
      message.success('图书新增成功')
    }
    modalVisible.value = false
    fetchBooks()
  } catch {
    // 错误提示已由拦截器统一处理
  } finally {
    saving.value = false
  }
}

function handleDelete(row) {
  dialog.warning({
    title: '删除确认',
    content: `确定要删除《${row.title}》吗? 该操作无法撤销。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteBook(row.id)
        message.success('删除成功')
        if (books.value.length === 1 && query.page > 1) {
          query.page -= 1
        }
        fetchBooks()
      } catch {
        // 错误提示已由拦截器统一处理
      }
    }
  })
}

onMounted(() => {
  fetchCategories()
  fetchBooks()
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.toolbar-card {
  margin-bottom: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.table-card {
  padding-bottom: 8px;
}

.pagination-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
