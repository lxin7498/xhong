<template>
  <div class="home-page">
    <div class="page-container">
      <section class="hero">
        <h1 class="hero-title">发现你的<span class="highlight">学习路径</span></h1>
        <p class="hero-sub">基于协同过滤算法，为你推荐最合适的计算机学习资源</p>
        <form class="hero-search" @submit.prevent="submitSearch">
          <el-input
            v-model="searchQuery"
            placeholder="搜索资源..."
            size="large"
            :prefix-icon="Search"
            clearable
          />
        </form>
      </section>

      <section class="section" v-if="authStore.isLoggedIn">
        <div class="section-header">
          <h2 class="section-title">为您推荐</h2>
          <button class="refresh-btn" @click="handleRefresh" :disabled="recommendationsComputing">
            <span class="material-symbols-outlined" :class="{ spinning: recommendationsComputing }">refresh</span>
            {{ recommendationsComputing ? '计算中...' : '换一批' }}
          </button>
        </div>
        <div class="resource-grid" v-if="recommendations.length">
          <ResourceCard v-for="r in recommendations" :key="r.id" :resource="r" />
        </div>
        <div class="cold-start-hint" v-else-if="coldStart">
          <span class="material-symbols-outlined">tips_and_updates</span>
          <p>多浏览和评分一些资源，我们将为你生成个性化推荐</p>
          <p class="hint-sub">当前基于热门资源为你展示</p>
        </div>
        <div class="empty-hint" v-else>
          <span class="material-symbols-outlined">auto_awesome</span>
          <p>暂无推荐数据</p>
        </div>
      </section>

      <section class="section" v-else>
        <h2 class="section-title">为您推荐</h2>
        <div class="empty-hint">
          <span class="material-symbols-outlined">login</span>
          <p>登录后开启个性化推荐</p>
          <router-link to="/login" class="btn-primary btn-login">立即登录</router-link>
        </div>
      </section>

      <section class="section" v-if="popularResources.length">
        <div class="section-header">
          <h2 class="section-title">热门资源</h2>
        </div>
        <div class="resource-grid">
          <ResourceCard v-for="r in popularResources" :key="r.id" :resource="r" />
        </div>
      </section>

      <section class="section" v-if="latestResources.length">
        <div class="section-header">
          <h2 class="section-title">最新资源</h2>
        </div>
        <div class="resource-grid">
          <ResourceCard v-for="r in latestResources" :key="r.id" :resource="r" />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { Search } from '@element-plus/icons-vue'
import { useResourceStore } from '@/stores/resource'
import { useAuthStore } from '@/stores/auth'
import ResourceCard from '@/components/resource/ResourceCard.vue'

const resourceStore = useResourceStore()
const authStore = useAuthStore()
const router = useRouter()
const { popular: popularResources, latest: latestResources, recommendations, coldStart, recommendationsComputing } = storeToRefs(resourceStore)
const searchQuery = ref('')

function submitSearch() {
  const keyword = searchQuery.value.trim()
  router.push({
    path: '/resources',
    query: keyword ? { search: keyword } : {},
  })
}

async function handleRefresh() {
  await resourceStore.refreshRecommendations()
}

onMounted(async () => {
  await Promise.all([
    resourceStore.fetchPopular(),
    resourceStore.fetchLatest(),
    authStore.isLoggedIn ? resourceStore.fetchRecommendations() : Promise.resolve(),
  ])
})
</script>

<style scoped>
.page-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: var(--space-6);
}

.hero {
  text-align: center;
  padding: var(--space-16) var(--space-6) var(--space-10);
}

.hero-title {
  font-size: 2.5rem;
  margin-bottom: var(--space-4);
}

.highlight {
  color: var(--color-primary);
}

.hero-sub {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-8);
}

.hero-search {
  max-width: 560px;
  margin: 0 auto;
}

.section {
  margin-top: var(--space-10);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-6);
}

.section-title {
  font-size: 1.5rem;
  padding-bottom: var(--space-3);
  border-bottom: 2px solid var(--color-primary-light);
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-4);
  background: var(--color-primary-bg);
  color: var(--color-primary);
  border: 1px solid var(--color-primary-light);
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.refresh-btn:hover:not(:disabled) {
  background: var(--color-primary);
  color: #fff;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-btn .material-symbols-outlined {
  font-size: 18px;
}

.spinning {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.resource-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-6);
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

.cold-start-hint {
  color: var(--color-text-muted);
  padding: var(--space-10);
  text-align: center;
  background: var(--color-primary-bg);
  border-radius: var(--radius-md);
  border: 1px dashed var(--color-primary-light);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.cold-start-hint .material-symbols-outlined {
  font-size: 40px;
  color: var(--color-primary);
}

.hint-sub {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.btn-login {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  background: var(--color-primary);
  color: #fff;
  border-radius: var(--radius-full);
  font-weight: 600;
  text-decoration: none;
  margin-top: var(--space-2);
  transition: background var(--transition-fast);
}

.btn-login:hover {
  background: var(--color-primary-dark);
}

@media (max-width: 900px) {
  .resource-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .resource-grid {
    grid-template-columns: 1fr;
  }

  .hero-title {
    font-size: 1.75rem;
  }
}
</style>
