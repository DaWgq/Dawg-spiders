<template>
  <n-layout has-sider style="height: 100vh">
    <!-- 侧边栏 -->
    <n-layout-sider
      bordered
      collapse-mode="width"
      :width="232"
      :collapsed-width="64"
      :collapsed="collapsed"
      :native-scrollbar="false"
      style="background: #fff"
    >
      <div class="logo-area">
        <n-icon size="26" color="#3b82f6">
          <LibraryOutline />
        </n-icon>
        <span v-if="!collapsed" class="logo-text">LibraryPro</span>
      </div>

      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="20"
        :options="menuOptions"
        :value="activeKey"
        @update:value="handleMenuSelect"
      />

      <div class="user-card" v-if="!collapsed">
        <n-avatar round size="small" style="background-color: #3b82f6">
          {{ (user.real_name || user.username || 'A').slice(0, 1) }}
        </n-avatar>
        <div class="user-info">
          <p class="user-name">{{ user.real_name || user.username }}</p>
          <p class="user-role">管理员</p>
        </div>
      </div>
    </n-layout-sider>

    <!-- 主区域 -->
    <n-layout>
      <n-layout-header bordered class="layout-header">
        <div class="header-left">
          <n-button quaternary circle @click="collapsed = !collapsed">
            <template #icon>
              <n-icon size="20">
                <MenuOutline />
              </n-icon>
            </template>
          </n-button>
          <div class="header-title">
            <span class="current-page">{{ currentTitle }}</span>
          </div>
        </div>

        <div class="header-right">
          <n-dropdown :options="userMenuOptions" trigger="click" @select="handleUserMenu">
            <div class="user-trigger">
              <n-avatar round size="small" style="background-color: #3b82f6">
                {{ (user.real_name || user.username || 'A').slice(0, 1) }}
              </n-avatar>
              <span class="user-name-text">{{ user.real_name || user.username }}</span>
              <n-icon size="16" color="#9ca3af">
                <ChevronDownOutline />
              </n-icon>
            </div>
          </n-dropdown>
        </div>
      </n-layout-header>

      <n-layout-content
        :native-scrollbar="false"
        style="background-color: #f5f7fa"
        content-style="min-height: calc(100vh - 56px);"
      >
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup>
import { computed, h, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NIcon,
  NLayout,
  NLayoutSider,
  NLayoutHeader,
  NLayoutContent,
  NMenu,
  NAvatar,
  NButton,
  NDropdown,
  useDialog
} from 'naive-ui'
import {
  BookOutline,
  ChevronDownOutline,
  GridOutline,
  LibraryOutline,
  LogOutOutline,
  MenuOutline,
  PeopleOutline,
  PersonCircleOutline,
  SwapHorizontalOutline
} from '@vicons/ionicons5'
import { getUser, clearAuth } from '../utils/auth'

const route = useRoute()
const router = useRouter()
const dialog = useDialog()

const collapsed = ref(false)
const user = ref(getUser())

const currentTitle = computed(() => route.meta.title || '图书管理系统')

function renderIcon(icon) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

const menuOptions = [
  { label: '仪表盘', key: 'dashboard', icon: renderIcon(GridOutline) },
  { label: '图书管理', key: 'books', icon: renderIcon(BookOutline) },
  { label: '读者管理', key: 'readers', icon: renderIcon(PeopleOutline) },
  { label: '借阅流通', key: 'circulation', icon: renderIcon(SwapHorizontalOutline) }
]

const activeKey = computed(() => {
  const current = route.path.split('/')[1] || 'dashboard'
  return ['dashboard', 'books', 'readers', 'circulation'].includes(current)
    ? current
    : 'dashboard'
})

const userMenuOptions = [
  {
    label: '个人信息',
    key: 'profile',
    icon: () => h(NIcon, null, { default: () => h(PersonCircleOutline) })
  },
  {
    label: '退出登录',
    key: 'logout',
    icon: () => h(NIcon, null, { default: () => h(LogOutOutline) })
  }
]

function handleMenuSelect(key) {
  router.push(`/${key}`)
}

function handleUserMenu(key) {
  if (key === 'logout') {
    dialog.warning({
      title: '退出登录',
      content: '确定要退出当前账号吗?',
      positiveText: '确定',
      negativeText: '取消',
      onPositiveClick: () => {
        clearAuth()
        router.push('/login')
      }
    })
  } else if (key === 'profile') {
    dialog.info({
      title: '管理员信息',
      content: () =>
        h('div', { style: 'line-height: 2' }, [
          h('p', `用户名: ${user.value.username}`),
          h('p', `姓名: ${user.value.real_name || '-'}`),
          h('p', `角色: ${user.value.role === 'admin' ? '系统管理员' : user.value.role}`)
        ]),
      positiveText: '知道了'
    })
  }
}

onMounted(() => {
  user.value = getUser()
})
</script>

<style scoped>
.logo-area {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.logo-text {
  font-size: 19px;
  font-weight: 700;
  color: #1f2937;
  letter-spacing: 0.3px;
}

.user-card {
  padding: 14px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  line-height: 1.3;
}

.user-name {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

.user-role {
  margin: 2px 0 0 0;
  font-size: 11px;
  color: #9ca3af;
}

.layout-header {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: #fff;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title .current-page {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.user-trigger:hover {
  background-color: #f3f4f6;
}

.user-name-text {
  font-size: 13px;
  color: #374151;
  font-weight: 500;
}
</style>
