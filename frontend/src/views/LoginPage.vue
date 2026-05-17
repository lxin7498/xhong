<template>
  <div class="login-page">
    <div class="auth-card glass-card">
      <div class="auth-header">
        <h1>欢迎回来</h1>
        <p>登录你的账号，继续学习之旅</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="handleLogin">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" size="large" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large" show-password />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <p class="auth-footer">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await authStore.login(form)
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (e) {
    const detail = e.response?.data?.detail
    ElMessage.error(detail || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<script>
import { ElMessage } from 'element-plus'
</script>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 200px);
  padding: var(--space-6);
}

.auth-card {
  width: 100%;
  max-width: 420px;
  padding: var(--space-10);
}

.auth-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.auth-header h1 {
  font-size: 1.75rem;
  margin-bottom: var(--space-2);
}

.auth-header p {
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.submit-btn {
  width: 100%;
}

.auth-footer {
  text-align: center;
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.auth-footer a {
  color: var(--color-primary);
  font-weight: 500;
}
</style>
