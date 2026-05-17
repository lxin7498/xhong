<template>
  <div class="register-page">
    <div class="auth-card glass-card">
      <div class="auth-header">
        <h1>创建账号</h1>
        <p>开启你的个性化学习之旅</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="handleRegister">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" size="large" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱（选填）" size="large" />
        </el-form-item>

        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="给自己起个名字" size="large" />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="专业" prop="major">
              <el-input v-model="form.major" placeholder="如：计算机科学" size="large" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="年级" prop="grade">
              <el-select v-model="form.grade" placeholder="选择年级" size="large" style="width: 100%">
                <el-option label="大一" value="大一" />
                <el-option label="大二" value="大二" />
                <el-option label="大三" value="大三" />
                <el-option label="大四" value="大四" />
                <el-option label="研一" value="研一" />
                <el-option label="研二" value="研二" />
                <el-option label="研三" value="研三" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="兴趣标签" prop="interest_tags">
          <el-checkbox-group v-model="form.interest_tags">
            <el-checkbox v-for="tag in tagOptions" :key="tag" :value="tag" :label="tag" />
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="至少6位" size="large" show-password />
        </el-form-item>

        <el-form-item label="确认密码" prop="password2">
          <el-input v-model="form.password2" type="password" placeholder="再次输入密码" size="large" show-password />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="handleRegister">
            注册
          </el-button>
        </el-form-item>
      </el-form>

      <p class="auth-footer">
        已有账号？<router-link to="/login">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref(null)
const loading = ref(false)

const tagOptions = ['Python', 'Java', 'C++', '数据结构', '算法', '机器学习', '深度学习', '前端', '数据库', '操作系统', '计算机网络', '人工智能']

const form = reactive({
  username: '',
  email: '',
  nickname: '',
  major: '',
  grade: '',
  interest_tags: [],
  password: '',
  password2: '',
})

const validatePassword2 = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码至少6位', trigger: 'blur' }],
  password2: [{ required: true, message: '请确认密码', trigger: 'blur' }, { validator: validatePassword2, trigger: 'blur' }],
}

async function handleRegister() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await authStore.register(form)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (e) {
    const data = e.response?.data
    if (data) {
      const msg = Object.values(data).flat().join('；')
      ElMessage.error(msg || '注册失败')
    } else {
      ElMessage.error('注册失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<script>
import { ElMessage } from 'element-plus'
</script>

<style scoped>
.register-page {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  min-height: calc(100vh - 200px);
  padding: var(--space-6);
}

.auth-card {
  width: 100%;
  max-width: 540px;
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
