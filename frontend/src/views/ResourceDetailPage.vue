<template>
  <div class="detail-page" v-if="resource">
    <div class="page-container">
      <div class="breadcrumb">
        <router-link to="/">首页</router-link>
        <span class="separator">/</span>
        <span class="current">{{ resource.title }}</span>
      </div>

      <div class="detail-layout">
        <div class="detail-main">
          <div class="glass-card detail-content">
            <div class="resource-header">
              <h1 class="resource-title">{{ resource.title }}</h1>
              <div class="header-badges">
                <span class="type-badge" :class="resource.resource_type">{{ typeLabel }}</span>
                <span class="difficulty-badge" :class="resource.difficulty">{{ difficultyLabel }}</span>
                <span class="category-badge">{{ resource.category }}</span>
              </div>
            </div>

            <div class="cover-image" v-if="resource.cover_image">
              <img :src="resource.cover_image" :alt="resource.title" />
            </div>

            <div class="description">
              <h3>资源描述</h3>
              <p>{{ resource.description }}</p>
            </div>

            <div class="tags-section" v-if="resource.tags?.length">
              <h3>相关标签</h3>
              <div class="tags-list">
                <span class="tag-chip" v-for="tag in resource.tags" :key="tag">{{ tag }}</span>
              </div>
            </div>

            <div class="rating-section">
              <h3>我的评分</h3>
              <div class="star-rating">
                <button
                  v-for="s in 5"
                  :key="s"
                  class="star-btn"
                  :class="{ active: s <= userRating }"
                  @click="handleRate(s)"
                  :title="s + ' 星'"
                >
                  <span class="material-symbols-outlined">{{ s <= userRating ? 'star' : 'star_outline' }}</span>
                </button>
                <span class="rating-hint" v-if="ratingMsg">{{ ratingMsg }}</span>
              </div>
            </div>

            <div class="actions">
              <a v-if="resource.url" :href="resource.url" target="_blank" rel="noopener" class="btn-primary">
                <span class="material-symbols-outlined">open_in_new</span>
                访问资源
              </a>
              <button
                class="btn-bookmark"
                :class="{ bookmarked: isBookmarked }"
                @click="handleBookmark"
              >
                <span class="material-symbols-outlined">{{ isBookmarked ? 'bookmark' : 'bookmark_outline' }}</span>
                {{ isBookmarked ? '已收藏' : '收藏' }}
              </button>
            </div>
          </div>
        </div>

        <div class="detail-sidebar">
          <div class="glass-card info-card">
            <h3>资源信息</h3>
            <div class="info-item">
              <span class="material-symbols-outlined">category</span>
              <span class="info-label">类型</span>
              <span class="info-value">{{ typeLabel }}</span>
            </div>
            <div class="info-item">
              <span class="material-symbols-outlined">school</span>
              <span class="info-label">难度</span>
              <span class="info-value">{{ difficultyLabel }}</span>
            </div>
            <div class="info-item">
              <span class="material-symbols-outlined">source</span>
              <span class="info-label">来源</span>
              <span class="info-value">{{ resource.source || '未知' }}</span>
            </div>
            <div class="info-item" v-if="resource.created_by_name">
              <span class="material-symbols-outlined">person</span>
              <span class="info-label">贡献者</span>
              <span class="info-value">{{ resource.created_by_name }}</span>
            </div>
          </div>

          <div class="glass-card stats-card">
            <h3>统计数据</h3>
            <div class="stat-row">
              <div class="stat-item">
                <span class="stat-value">{{ resource.avg_rating || '-' }}</span>
                <span class="stat-label">平均评分</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ resource.rating_count }}</span>
                <span class="stat-label">评分人数</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ resource.browse_count }}</span>
                <span class="stat-label">浏览次数</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="page-container loading-state" v-else>
    <div class="glass-card skeleton-card">
      <div class="skeleton-line w-60"></div>
      <div class="skeleton-line w-40"></div>
      <div class="skeleton-block"></div>
      <div class="skeleton-line w-80"></div>
      <div class="skeleton-line w-80"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useResourceStore } from '@/stores/resource'
import { useBehaviorStore } from '@/stores/behavior'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const resourceStore = useResourceStore()
const behaviorStore = useBehaviorStore()
const authStore = useAuthStore()
const resource = ref(null)
const userRating = ref(0)
const isBookmarked = ref(false)
const ratingMsg = ref('')

const typeLabel = computed(() => {
  const labels = { video: '视频', article: '文章', exercise: '练习' }
  return labels[resource.value?.resource_type] || resource.value?.resource_type
})

const difficultyLabel = computed(() => {
  const labels = { beginner: '初级', intermediate: '中级', advanced: '高级' }
  return labels[resource.value?.difficulty] || resource.value?.difficulty
})

async function load() {
  try {
    const data = await resourceStore.fetchDetail(route.params.id)
    resource.value = data
    userRating.value = data.user_rating || 0
    isBookmarked.value = data.is_bookmarked || false
    ratingMsg.value = ''

    // Track browse if logged in
    if (authStore.isLoggedIn) {
      behaviorStore.trackBrowse(data.id)
    }
  } catch {
    resource.value = null
  }
}

async function handleBookmark() {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    const bookmarked = await behaviorStore.toggleBookmark(resource.value.id)
    isBookmarked.value = bookmarked
    ElMessage.success(bookmarked ? '已收藏' : '已取消收藏')
  } catch {
    ElMessage.error('操作失败')
  }
}

async function handleRate(score) {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    userRating.value = score
    ratingMsg.value = '已评分'
    await behaviorStore.submitRating(resource.value.id, score)
    // Refresh detail to get updated avg_rating
    const data = await resourceStore.fetchDetail(route.params.id)
    resource.value = data
    setTimeout(() => { ratingMsg.value = '' }, 2000)
  } catch {
    ElMessage.error('评分失败')
  }
}

onMounted(load)
watch(() => route.params.id, load)
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

.breadcrumb {
  margin-bottom: var(--space-6);
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.breadcrumb a {
  color: var(--color-text-secondary);
}

.breadcrumb .separator {
  margin: 0 var(--space-2);
}

.detail-layout {
  display: flex;
  gap: var(--space-6);
}

.detail-main {
  flex: 1;
  min-width: 0;
}

.detail-sidebar {
  flex-shrink: 0;
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.detail-content {
  padding: var(--space-8);
}

.resource-header {
  margin-bottom: var(--space-6);
}

.resource-title {
  font-size: 1.75rem;
  margin-bottom: var(--space-4);
}

.header-badges {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.type-badge {
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 600;
  color: #fff;
}

.type-badge.video { background: var(--color-primary); }
.type-badge.article { background: #3b82f6; }
.type-badge.exercise { background: #f59e0b; }

.difficulty-badge {
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 600;
}

.difficulty-badge.beginner { background: #d1fae5; color: #065f46; }
.difficulty-badge.intermediate { background: #fef3c7; color: #92400e; }
.difficulty-badge.advanced { background: #fee2e2; color: #991b1b; }

[data-theme="dark"] .difficulty-badge.beginner { background: #064e3b; color: #6ee7b7; }
[data-theme="dark"] .difficulty-badge.intermediate { background: #78350f; color: #fcd34d; }
[data-theme="dark"] .difficulty-badge.advanced { background: #7f1d1d; color: #fca5a5; }

.category-badge {
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 500;
  background: var(--color-primary-bg);
  color: var(--color-primary-dark);
}

.cover-image {
  margin-bottom: var(--space-6);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.cover-image img {
  width: 100%;
  max-height: 360px;
  object-fit: cover;
}

.description {
  margin-bottom: var(--space-6);
}

.description h3,
.tags-section h3,
.rating-section h3 {
  font-size: 1rem;
  margin-bottom: var(--space-3);
}

.description p {
  color: var(--color-text-secondary);
  line-height: 1.8;
}

.tags-section {
  margin-bottom: var(--space-6);
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.tag-chip {
  padding: 4px 14px;
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  background: var(--color-primary-bg);
  color: var(--color-primary-dark);
  font-weight: 500;
}

.rating-section {
  margin-bottom: var(--space-6);
}

.star-rating {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.star-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  color: var(--color-border);
}

.star-btn .material-symbols-outlined {
  font-size: 28px;
  font-variation-settings: 'FILL' 0;
}

.star-btn.active {
  color: #f59e0b;
}

.star-btn.active .material-symbols-outlined {
  font-variation-settings: 'FILL' 1;
}

.star-btn:hover {
  transform: scale(1.15);
}

.rating-hint {
  margin-left: var(--space-3);
  font-size: 0.85rem;
  color: var(--color-primary);
  font-weight: 500;
}

.actions {
  display: flex;
  gap: var(--space-3);
  padding-top: var(--space-6);
  border-top: 1px solid var(--color-border-light);
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-full);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: background var(--transition-fast);
}

.btn-primary:hover {
  background: var(--color-primary-dark);
  color: #fff;
}

.btn-bookmark {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-bookmark:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn-bookmark.bookmarked {
  background: var(--color-primary-bg);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn-bookmark.bookmarked .material-symbols-outlined {
  font-variation-settings: 'FILL' 1;
}

/* Sidebar */
.info-card,
.stats-card {
  padding: var(--space-6);
}

.info-card h3,
.stats-card h3 {
  font-size: 1rem;
  margin-bottom: var(--space-4);
}

.info-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  font-size: 0.9rem;
}

.info-item .material-symbols-outlined {
  font-size: 18px;
  color: var(--color-primary);
}

.info-label {
  color: var(--color-text-muted);
  min-width: 48px;
}

.info-value {
  color: var(--color-text-primary);
  font-weight: 500;
}

.stat-row {
  display: flex;
  gap: var(--space-2);
}

.stat-item {
  flex: 1;
  text-align: center;
  padding: var(--space-3);
  background: var(--color-primary-bg);
  border-radius: var(--radius-sm);
}

.stat-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-top: 2px;
}

/* Loading skeleton */
.skeleton-card {
  padding: var(--space-8);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.skeleton-line {
  height: 16px;
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--color-border), var(--color-border-light), var(--color-border));
  animation: shimmer 1.5s infinite;
}

.skeleton-block {
  height: 240px;
  border-radius: var(--radius-md);
  background: linear-gradient(90deg, var(--color-border), var(--color-border-light), var(--color-border));
  animation: shimmer 1.5s infinite;
}

.w-60 { width: 60%; }
.w-40 { width: 40%; }
.w-80 { width: 80%; }

@keyframes shimmer {
  0% { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}

@media (max-width: 768px) {
  .detail-layout {
    flex-direction: column;
  }

  .detail-sidebar {
    width: 100%;
  }

  .resource-title {
    font-size: 1.35rem;
  }
}
</style>
