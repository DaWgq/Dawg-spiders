<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">读者管理</h1>
        <p class="page-subtitle">管理借阅证及读者信息</p>
      </div>
      <n-button type="primary" @click="openCreateModal">
        <template #icon>
          <n-icon><AddOutline /></n-icon>
        </template>
        新增读者
      </n-button>
    </div>

    <!-- 筛选工具栏 -->
    <n-card :bordered="true" class="toolbar-card" size="small">
      <div class="toolbar">
        <n-input
          v-model:value="query.keyword"
          placeholder="搜索姓名、读者编号、手机号、邮箱..."
          clearable
          style="width: 320px"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <n-icon><SearchOutline /></n-icon>
          </template>
        </n-input>
        <n-select
          v-model:value="query.status"
          :options="statusFilterOptions"
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

    <!-- 读者表格 -->
    <n-card :bordered="true" class="table-card">
      <n-data-table
        :columns="columns"
        :data="readers"
        :loading="loading"
        :row-key="(row) => row.id"
        :pagination="false"
        :bordered="false"
        :scroll-x="1000"
      />
      <div class="pagination-row">
        <n-text depth="3" style="font-size: 13px">共 {{ total }} 条记录</n-text>
        <n-pagination
          v-model:page="query.page"
          :page-size="query.page_size"
          :item-count="total"
          :page-sizes="[10, 20, 50]"
          show-size-picker
          @update:page="fetchReaders"
          @update:page-size="handlePageSizeChange"
        />
      </div>
    </n-card>

    <!-- 新增/编辑 弹窗 -->
    <n-modal
      v-model:show="modalVisible"
      preset="card"
      :title="editingId ? '编辑读者信息' : '新增读者信息'"
      style="width: 560px"
      :mask-closable="false"
    >
      <n-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-placement="left"
        label-width="100"
      >
        <n-form-item label="读者编号" path="reader_no">
          <n-input v-model:value="form.reader_no" placeholder="例如: R001" />
        </n-form-item>
        <n-form-item label="姓名" path="name">
          <n-input v-model:value="form.name" placeholder="请输入姓名" />
        </n-form-item>
        <n-grid :cols="2" :x-gap="16">
          <n-form-item-gi label="性别" path="gender">
            <n-select
              v-model:value="form.gender"
              :options="[
                { label: '男', value: '男' },
                { label: '女', value: '女' },
                { label: '其他', value: '其他' }
              ]"
            />
          </n-form-item-gi>
          <n-form-item-gi label="状态" path="status">
            <n-select
              v-model:value="form.status"
              :options="[
                { label: '正常', value: '正常' },
                { label: '冻结', value: '冻结' }
              ]"
            />
          </n-form-item-gi>
          <n-form-item-gi label="手机号" path="phone">
            <n-input v-model:value="form.phone" placeholder="请输入手机号" />
          </n-form-item-gi>
          <n-form-item-gi label="邮箱" path="email">
            <n-input v-model:value="form.email" placeholder="请输入邮箱" />
          </n-form-item-gi>
        </n-grid>
      </n-form>
      <template #footer>
        <div class="modal-footer">
          <n-button @click="modalVisible = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="handleSave">保存</n-button>
        </div>
      </template>
    </n-modal>

    <!-- 借阅历史 抽屉 -->
    <n-drawer v-model:show="historyVisible" :width="640" placement="right">
      <n-drawer-content :title="`借阅历史 - ${historyReaderName}`" closable>
        <n-data-table
          :columns="historyColumns"
          :data="historyRecords"
          :loading="historyLoading"
          :bordered="true"
          :scroll-x="560"
          size="small"
        />
        <n-empty v-if="!historyLoading && historyRecords.length === 0" description="暂无借阅记录" style="margin-top: 24px" />
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup>
import { computed, h, onMounted, reactive, ref } from 'vue'
import {
  NAvatar,
  NButton,
  NCard,
  NDataTable,
  NDrawer,
  NDrawerContent,
  NEmpty,
  NForm,
  NFormItem,
  NFormItemGi,
  NGrid,
  NIcon,
  NInput,
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
  CreateOutline,
  LockOpenOutline,
  ReaderOutline,
  RefreshOutline,
  SearchOutline,
  SnowOutline,
  TimeOutline,
  TrashOutline
} from '@vicons/ionicons5'
import {
  createReader,
  deleteReader,
  getReaderBorrows,
  getReaders,
  setReaderStatus,
  updateReader
} from '../api'

const message = useMessage()
const dialog = useDialog()

const readers = ref([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const modalVisible = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const historyVisible = ref(false)
const historyLoading = ref(false)
const historyRecords = ref([])
const historyReaderName = ref('')

const query = reactive({
  keyword: '',
  status: '',
  page: 1,
  page_size: 10
})

const form = reactive({
  reader_no: '',
  name: '',
  gender: '其他',
  phone: '',
  email: '',
  status: '正常'
})

const rules = {
  reader_no: { required: true, message: '请输入读者编号', trigger: ['blur', 'input'] },
  name: { required: true, message: '请输入姓名', trigger: ['blur', 'input'] }
}

const statusFilterOptions = [
  { label: '正常', value: '正常' },
  { label: '冻结', value: '冻结' }
]

const columns = [
  {
    title: '读者编号',
    key: 'reader_no',
    width: 110,
    render(row) {
      return h(
        NTag,
        { size: 'small', bordered: true, style: 'background:#eff6ff;color:#2563eb;border-color:#bfdbfe' },
        { default: () => row.reader_no }
      )
    }
  },
  {
    title: '姓名',
    key: 'name',
    width: 150,
    render(row) {
      return h('div', { style: 'display:flex;align-items:center;gap:10px' }, [
        h(
          NAvatar,
          {
            round: true,
            size: 'small',
            style: `background-color:${row.gender === '女' ? '#ec4899' : '#3b82f6'}`
          },
          { default: () => row.name.slice(0, 1) }
        ),
        h('span', { style: 'font-size:14px;font-weight:600;color:#1f2937' }, row.name)
      ])
    }
  },
  { title: '性别', key: 'gender', width: 70 },
  { title: '手机号', key: 'phone', width: 140 },
  { title: '邮箱', key: 'email', width: 200 },
  {
    title: '借阅中',
    key: 'borrowed_count',
    width: 90,
    align: 'center',
    render(row) {
      return h(
        'span',
        { style: `font-weight:600;font-size:13px;color:${row.borrowed_count > 0 ? '#8b5cf6' : '#9ca3af'}` },
        String(row.borrowed_count)
      )
    }
  },
  {
    title: '状态',
    key: 'status',
    width: 90,
    render(row) {
      const type = row.status === '正常' ? 'success' : 'error'
      return h(NTag, { type, size: 'small', round: true }, { default: () => row.status })
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 190,
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
              title: '编辑',
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
              title: '借阅历史',
              onClick: () => openHistory(row)
            },
            { icon: () => h(NIcon, { size: 18, color: '#8b5cf6' }, { default: () => h(TimeOutline) }) }
          ),
          h(
            NButton,
            {
              quaternary: true,
              circle: true,
              size: 'small',
              title: row.status === '正常' ? '冻结' : '解冻',
              onClick: () => handleToggleStatus(row)
            },
            {
              icon: () =>
                h(
                  NIcon,
                  {
                    size: 18,
                    color: row.status === '正常' ? '#f59e0b' : '#10b981'
                  },
                  { default: () => h(row.status === '正常' ? SnowOutline : LockOpenOutline) }
                )
            }
          ),
          h(
            NButton,
            {
              quaternary: true,
              circle: true,
              size: 'small',
              title: '删除',
              onClick: () => handleDelete(row)
            },
            { icon: () => h(NIcon, { size: 18, color: '#ef4444' }, { default: () => h(TrashOutline) }) }
          )
        ]
      })
    }
  }
]

const historyColumns = [
  {
    title: '书名',
    key: 'book_title',
    minWidth: 180,
    render(row) {
      return h('div', { style: 'display:flex;align-items:center;gap:8px' }, [
        h(NIcon, { size: 16, color: '#9ca3af' }, { default: () => h(ReaderOutline) }),
        h('span', row.book_title)
      ])
    }
  },
  { title: 'ISBN', key: 'book_isbn', width: 140 },
  { title: '借出时间', key: 'borrow_date', width: 160, render: (row) => formatDate(row.borrow_date) },
  { title: '应还日期', key: 'due_date', width: 160, render: (row) => formatDate(row.due_date) },
  { title: '归还日期', key: 'return_date', width: 160, render: (row) => (row.return_date ? formatDate(row.return_date) : '-') },
  {
    title: '状态',
    key: 'status',
    width: 90,
    render(row) {
      const map = { 借出中: ['info', '借出中'], 已归还: ['success', '已归还'], 逾期: ['error', '逾期'] }
      const [type, label] = map[row.status] || ['default', row.status]
      return h(NTag, { type, size: 'small', round: true }, { default: () => label })
    }
  }
]

function formatDate(value) {
  if (!value) return '-'
  const d = new Date(value)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

async function fetchReaders() {
  loading.value = true
  try {
    const res = await getReaders({
      keyword: query.keyword,
      status: query.status,
      page: query.page,
      page_size: query.page_size
    })
    readers.value = res.items
    total.value = res.total
  } catch {
    // 错误提示已由拦截器统一处理
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  query.page = 1
  fetchReaders()
}

function handleReset() {
  query.keyword = ''
  query.status = ''
  query.page = 1
  fetchReaders()
}

function handlePageSizeChange(size) {
  query.page_size = size
  query.page = 1
  fetchReaders()
}

function resetForm() {
  form.reader_no = ''
  form.name = ''
  form.gender = '其他'
  form.phone = ''
  form.email = ''
  form.status = '正常'
}

function openCreateModal() {
  editingId.value = null
  resetForm()
  modalVisible.value = true
}

function openEditModal(row) {
  editingId.value = row.id
  Object.assign(form, {
    reader_no: row.reader_no,
    name: row.name,
    gender: row.gender,
    phone: row.phone || '',
    email: row.email || '',
    status: row.status
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
      await updateReader(editingId.value, { ...form })
      message.success('读者信息已更新')
    } else {
      await createReader({ ...form })
      message.success('读者新增成功')
    }
    modalVisible.value = false
    fetchReaders()
  } catch {
    // 错误提示已由拦截器统一处理
  } finally {
    saving.value = false
  }
}

async function openHistory(row) {
  historyReaderName.value = row.name
  historyVisible.value = true
  historyLoading.value = true
  try {
    historyRecords.value = await getReaderBorrows(row.id)
  } catch {
    historyRecords.value = []
  } finally {
    historyLoading.value = false
  }
}

function handleToggleStatus(row) {
  const target = row.status === '正常' ? '冻结' : '正常'
  const title = target === '冻结' ? '冻结确认' : '解冻确认'
  const content =
    target === '冻结'
      ? `确定要冻结读者 ${row.name} 吗? 冻结后将无法借书。`
      : `确定要解冻读者 ${row.name} 吗?`
  dialog.warning({
    title,
    content,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await setReaderStatus(row.id, target)
        message.success(target === '冻结' ? '已冻结' : '已解冻')
        fetchReaders()
      } catch {
        // 错误提示已由拦截器统一处理
      }
    }
  })
}

function handleDelete(row) {
  dialog.warning({
    title: '删除确认',
    content: `确定要删除读者 ${row.name} (${row.reader_no}) 吗? 该操作无法撤销。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteReader(row.id)
        message.success('删除成功')
        if (readers.value.length === 1 && query.page > 1) {
          query.page -= 1
        }
        fetchReaders()
      } catch {
        // 错误提示已由拦截器统一处理
      }
    }
  })
}

onMounted(() => {
  fetchReaders()
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
