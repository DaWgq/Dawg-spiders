<template>
  <div class="login-page">
    <!-- 左侧品牌区 -->
    <div class="brand-panel">
      <div class="brand-content">
        <div class="brand-logo">
          <n-icon size="48" color="#ffffff">
            <LibraryOutline />
          </n-icon>
        </div>
        <h1 class="brand-title">LibraryPro 图书管理系统</h1>
        <p class="brand-desc">高效、专业的馆藏管理与借阅流通平台</p>
        <div class="brand-features">
          <div class="feature-item">
            <n-icon size="20"><BookOutline /></n-icon>
            <span>馆藏管理</span>
          </div>
          <div class="feature-item">
            <n-icon size="20"><PeopleOutline /></n-icon>
            <span>读者管理</span>
          </div>
          <div class="feature-item">
            <n-icon size="20"><SwapHorizontalOutline /></n-icon>
            <span>借阅流通</span>
          </div>
          <div class="feature-item">
            <n-icon size="20"><TrendingUpOutline /></n-icon>
            <span>数据看板</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录表单区 -->
    <div class="login-panel">
      <div class="login-card">
        <h2 class="login-title">欢迎登录</h2>
        <p class="login-subtitle">请输入您的账号密码以继续</p>

        <n-form ref="formRef" :model="form" :rules="rules" size="large" label-placement="top">
          <n-form-item label="用户名" path="username">
            <n-input
              v-model:value="form.username"
              placeholder="请输入用户名"
              :input-props="{ autocomplete: 'username' }"
            >
              <template #prefix>
                <n-icon :component="PersonOutline" />
              </template>
            </n-input>
          </n-form-item>

          <n-form-item label="密码" path="password">
            <n-input
              v-model:value="form.password"
              type="password"
              show-password-on="click"
              placeholder="请输入密码"
              @keyup.enter="handleLogin"
              :input-props="{ autocomplete: 'current-password' }"
            >
              <template #prefix>
                <n-icon :component="LockClosedOutline" />
              </template>
            </n-input>
          </n-form-item>

          <n-button
            type="primary"
            block
            size="large"
            :loading="loading"
            @click="handleLogin"
            style="margin-top: 8px"
          >
            登 录
          </n-button>
        </n-form>

        <n-alert type="info" :show-icon="true" class="demo-tip" title="默认账号">
          <template #icon>
            <n-icon :component="InformationCircleOutline" />
          </template>
          管理员账号: <b>admin</b> &nbsp; 密码: <b>admin123</b>
        </n-alert>
      </div>
      <p class="copyright">LibraryPro 图书管理系统 v1.0</p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  BookOutline,
  InformationCircleOutline,
  LibraryOutline,
  LockClosedOutline,
  PeopleOutline,
  PersonOutline,
  SwapHorizontalOutline,
  TrendingUpOutline
} from '@vicons/ionicons5'
import { login } from '../api'
import { setToken, setUser } from '../utils/auth'

const router = useRouter()
const message = useMessage()

const formRef = ref(null)
const loading = ref(false)
const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: { required: true, message: '请输入用户名', trigger: ['blur', 'input'] },
  password: { required: true, message: '请输入密码', trigger: ['blur', 'input'] }
}

async function handleLogin() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    const res = await login({ ...form })
    setToken(res.access_token)
    setUser(res.user)
    message.success('登录成功, 欢迎回来!')
    router.push('/dashboard')
  } catch {
    // 错误提示已由拦截器统一处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.brand-panel {
  flex: 1.1;
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 50%, #60a5fa 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.brand-panel::before {
  content: '';
  position: absolute;
  width: 420px;
  height: 420px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  top: -100px;
  right: -120px;
}

.brand-panel::after {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
  bottom: -80px;
  left: -80px;
}

.brand-content {
  color: #fff;
  position: relative;
  z-index: 1;
  max-width: 440px;
  padding: 40px;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.brand-title {
  font-size: 30px;
  font-weight: 700;
  margin: 0 0 12px 0;
}

.brand-desc {
  font-size: 15px;
  opacity: 0.85;
  margin: 0 0 36px 0;
}

.brand-features {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 10px;
  padding: 14px 16px;
  font-size: 14px;
  backdrop-filter: blur(4px);
}

.login-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  position: relative;
}

.login-card {
  width: 380px;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
  border: 1px solid #eef0f2;
  padding: 40px 36px 32px;
}

.login-title {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 6px 0;
}

.login-subtitle {
  font-size: 13px;
  color: #6b7280;
  margin: 0 0 28px 0;
}

.demo-tip {
  margin-top: 22px;
}

.copyright {
  position: absolute;
  bottom: 24px;
  font-size: 12px;
  color: #9ca3af;
  margin: 0;
}

@media (max-width: 900px) {
  .brand-panel {
    display: none;
  }
}
</style>
