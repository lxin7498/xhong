<template>
  <div class="profile-page">
    <div class="page-container">
      <h1 class="page-title">个人中心</h1>

      <div class="profile-layout">
        <div class="profile-sidebar">
          <div class="avatar-section glass-card">
            <div class="avatar-circle">
              <span class="material-symbols-outlined">person</span>
            </div>
            <h3>{{ profile.nickname || profile.username }}</h3>
            <p class="profile-major">{{ profile.major || '未设置专业' }}</p>
          </div>
        </div>

        <div class="profile-main">
          <el-tabs v-model="activeTab" class="profile-tabs" @tab-change="onTabChange">
            <el-tab-pane label="基本信息" name="info">
              <div class="glass-card tab-content">
                <el-form ref="infoFormRef" :model="profile" :rules="infoRules" label-position="top">
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="用户名">
                        <el-input :model-value="profile.username" disabled />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="昵称" prop="nickname">
                        <el-input v-model="profile.nickname" placeholder="给自己起个名字" />
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-form-item label="邮箱" prop="email">
                    <el-input v-model="profile.email" placeholder="请输入邮箱" />
                  </el-form-item>

                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="专业" prop="major">
                        <el-input v-model="profile.major" placeholder="如：计算机科学" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="年级" prop="grade">
                        <el-select v-model="profile.grade" placeholder="选择年级" style="width: 100%">
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
                    <el-checkbox-group v-model="profile.interest_tags">
                      <el-checkbox v-for="tag in tagOptions" :key="tag" :value="tag" :label="tag" />
                    </el-checkbox-group>
                  </el-form-item>

                  <el-form-item>
                    <el-button type="primary" :loading="infoLoading" @click="saveProfile">保存修改</el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>

            <el-tab-pane label="修改密码" name="password">
              <div class="glass-card tab-content">
                <el-form ref="pwdFormRef" :model="passwordForm" :rules="pwdRules" label-position="top">
                  <el-form-item label="原密码" prop="old_password">
                    <el-input v-model="passwordForm.old_password" type="password" placeholder="请输入原密码" show-password />
                  </el-form-item>

                  <el-form-item label="新密码" prop="new_password">
                    <el-input v-model="passwordForm.new_password" type="password" placeholder="至少6位" show-password />
                  </el-form-item>

                  <el-form-item label="确认新密码" prop="new_password2">
                    <el-input v-model="passwordForm.new_password2" type="password" placeholder="再次输入新密码" show-password />
                  </el-form-item>

                  <el-form-item>
                    <el-button type="primary" :loading="pwdLoading" @click="changePassword">修改密码</el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>

            <el-tab-pane label="浏览历史" name="history">
              <div class="tab-content" v-loading="behaviorStore.loading">
                <div v-if="historyList.length" class="resource-grid">
                  <ResourceCard v-for="item in historyList" :key="item.id" :resource="item.resource" />
                </div>
                <div v-else class="empty-hint">
                  <span class="material-symbols-outlined">history</span>
                  <p>还没有浏览记录</p>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="我的收藏" name="favorites">
              <div class="tab-content" v-loading="behaviorStore.loading">
                <div v-if="favoritesList.length" class="resource-grid">
                  <ResourceCard v-for="item in favoritesList" :key="item.id" :resource="item.resource" />
                </div>
                <div v-else class="empty-hint">
                  <span class="material-symbols-outlined">bookmark</span>
                  <p>还没有收藏资源</p>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="我的评分" name="ratings">
              <div class="tab-content" v-loading="behaviorStore.loading">
                <div v-if="ratingsList.length" class="resource-grid">
                  <div v-for="item in ratingsList" :key="item.id" class="rated-item">
                    <ResourceCard :resource="item.resource" />
                    <div class="my-rating">
                      <span v-for="s in 5" :key="s" class="star-icon" :class="{ filled: s <= item.rating }">
                        <span class="material-symbols-outlined">{{ s <= item.rating ? 'star' : 'star_outline' }}</span>
                      </span>
                    </div>
                  </div>
                </div>
                <div v-else class="empty-hint">
                  <span class="material-symbols-outlined">star</span>
                  <p>还没有评分记录</p>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useBehaviorStore } from '@/stores/behavior'
import ResourceCard from '@/components/resource/ResourceCard.vue'
import client from '@/api/client'

const authStore = useAuthStore()
const behaviorStore = useBehaviorStore()
const { history: historyList, favorites: favoritesList, ratings: ratingsList } = storeToRefs(behaviorStore)

const activeTab = ref('info')
const infoLoading = ref(false)
const pwdLoading = ref(false)
const infoFormRef = ref(null)
const pwdFormRef = ref(null)

const tagOptions = ['Python', 'Java', 'C++', '数据结构', '算法', '机器学习', '深度学习', '前端', '数据库', '操作系统', '计算机网络', '人工智能']

const profile = reactive({
  username: '',
  email: '',
  nickname: '',
  major: '',
  grade: '',
  interest_tags: [],
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  new_password2: '',
})

const infoRules = {
  email: [{ type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }],
}

const validateNewPwd2 = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次密码不一致'))
  } else {
    callback()
  }
}

const pwdRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, message: '密码至少6位', trigger: 'blur' }],
  new_password2: [{ required: true, message: '请确认新密码', trigger: 'blur' }, { validator: validateNewPwd2, trigger: 'blur' }],
}

onMounted(async () => {
  try {
    const data = await authStore.fetchProfile()
    Object.assign(profile, {
      username: data.username,
      email: data.email || '',
      nickname: data.nickname || '',
      major: data.major || '',
      grade: data.grade || '',
      interest_tags: data.interest_tags || [],
    })
  } catch {
    ElMessage.error('加载个人信息失败')
  }
})

function onTabChange(name) {
  if (name === 'history' && !historyList.value.length) {
    behaviorStore.fetchHistory()
  } else if (name === 'favorites' && !favoritesList.value.length) {
    behaviorStore.fetchFavorites()
  } else if (name === 'ratings' && !ratingsList.value.length) {
    behaviorStore.fetchRatings()
  }
}

async function saveProfile() {
  const valid = await infoFormRef.value.validate().catch(() => false)
  if (!valid) return
  infoLoading.value = true
  try {
    await client.put('/users/me/', {
      email: profile.email,
      nickname: profile.nickname,
      major: profile.major,
      grade: profile.grade,
      interest_tags: profile.interest_tags,
    })
    ElMessage.success('个人信息已更新')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    infoLoading.value = false
  }
}

async function changePassword() {
  const valid = await pwdFormRef.value.validate().catch(() => false)
  if (!valid) return
  pwdLoading.value = true
  try {
    await client.put('/users/me/password/', passwordForm)
    ElMessage.success('密码已修改，请重新登录')
    authStore.logout()
  } catch (e) {
    const detail = e.response?.data?.detail || e.response?.data?.old_password
    ElMessage.error(Array.isArray(detail) ? detail[0] : detail || '修改失败')
  } finally {
    pwdLoading.value = false
  }
}
</script>

<script>
import { ElMessage } from 'element-plus'
</script>

<style scoped>
.page-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: var(--space-8) var(--space-6);
}

.page-title {
  font-size: 1.75rem;
  margin-bottom: var(--space-8);
}

.profile-layout {
  display: flex;
  gap: var(--space-6);
}

.profile-sidebar {
  flex-shrink: 0;
  width: 240px;
}

.avatar-section {
  padding: var(--space-8) var(--space-6);
  text-align: center;
}

.avatar-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--color-primary-bg);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--space-4);
}

.avatar-circle .material-symbols-outlined {
  font-size: 40px;
}

.avatar-section h3 {
  font-size: 1.1rem;
  margin-bottom: var(--space-1);
}

.profile-major {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.profile-main {
  flex: 1;
  min-width: 0;
}

.tab-content {
  padding: var(--space-8);
}

.profile-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
}

.resource-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}

.rated-item {
  position: relative;
}

.my-rating {
  display: flex;
  align-items: center;
  gap: 2px;
  margin-top: var(--space-2);
  justify-content: flex-end;
}

.star-icon {
  color: var(--color-border);
}

.star-icon .material-symbols-outlined {
  font-size: 18px;
}

.star-icon.filled {
  color: #f59e0b;
}

.star-icon.filled .material-symbols-outlined {
  font-variation-settings: 'FILL' 1;
}

.empty-hint {
  color: var(--color-text-muted);
  padding: var(--space-10);
  text-align: center;
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  border: 1px dashed var(--color-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
}

.empty-hint .material-symbols-outlined {
  font-size: 40px;
  color: var(--color-primary);
}

@media (max-width: 768px) {
  .profile-layout {
    flex-direction: column;
  }

  .profile-sidebar {
    width: 100%;
  }

  .resource-grid {
    grid-template-columns: 1fr;
  }
}
</style>
