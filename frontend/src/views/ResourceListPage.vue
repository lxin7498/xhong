<template>
  <div class="list-page">
    <div class="page-container">
      <div class="page-header">
        <h1 class="page-title">资源广场</h1>
        <p class="page-sub">探索计算机学习资源</p>
      </div>

      <div class="toolbar glass-card">
        <div class="toolbar-row">
          <el-input
            v-model="search"
            placeholder="搜索资源..."
            :prefix-icon="Search"
            clearable
            class="search-input"
            @clear="updateRouteAndSearch"
            @keyup.enter="updateRouteAndSearch"
          />
          <el-select v-model="sort" class="sort-select" @change="updateRouteAndSearch">
            <el-option label="最新发布" value="-created_at" />
            <el-option label="最多浏览" value="-browse_count" />
            <el-option label="评分最高" value="-avg_rating" />
          </el-select>
        </div>
        <div class="category-chips">
          <button
            class="chip"
            :class="{ active: !category }"
            @click="category = ''; updateRouteAndSearch()"
          >全部</button>
          <button
            v-for="cat in categories"
            :key="cat"
            class="chip"
            :class="{ active: category === cat }"
            @click="category = cat; updateRouteAndSearch()"
          >{{ cat }}</button>
        </div>
      </div>

      <div v-loading="loading" class="resource-grid" v-if="resources.length">
        <ResourceCard v-for="r in resources" :key="r.id" :resource="r" />
      </div>

      <div class="empty-hint" v-else-if="!loading">
        <span class="material-symbols-outlined">search_off</span>
        <p>没有找到匹配的资源</p>
      </div>

      <div class="pagination-wrap" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          background
          @current-change="updatePageAndSearch"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { useResourceStore } from '@/stores/resource'
import ResourceCard from '@/components/resource/ResourceCard.vue'

const resourceStore = useResourceStore()
const route = useRoute()
const router = useRouter()

const resources = ref([])
const total = ref(0)
const loading = ref(false)
const search = ref('')
const category = ref('')
const sort = ref('-created_at')
const page = ref(1)
const pageSize = 12

const categories = [
  'Python', 'Java', 'C++', '数据结构', '算法',
  '机器学习', '深度学习', '人工智能',
  '前端', '数据库', '操作系统', '计算机网络',
]

async function doSearch() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize, ordering: sort.value }
    if (search.value) params.search = search.value
    if (category.value) params.category = category.value
    const data = await resourceStore.fetchList(params)
    resources.value = data.results
    total.value = data.count
  } finally {
    loading.value = false
  }
}

function syncFromRoute() {
  search.value = typeof route.query.search === 'string' ? route.query.search : ''
  category.value = typeof route.query.category === 'string' ? route.query.category : ''
  sort.value = typeof route.query.ordering === 'string' ? route.query.ordering : '-created_at'
  page.value = Number(route.query.page || 1)
  if (!Number.isFinite(page.value) || page.value < 1) page.value = 1
}

function buildQuery() {
  const query = {}
  const keyword = search.value.trim()
  if (keyword) query.search = keyword
  if (category.value) query.category = category.value
  if (sort.value !== '-created_at') query.ordering = sort.value
  if (page.value > 1) query.page = page.value
  return query
}

function updateRouteAndSearch() {
  page.value = 1
  router.push({ path: '/resources', query: buildQuery() })
}

function updatePageAndSearch() {
  router.push({ path: '/resources', query: buildQuery() })
}

watch(
  () => route.query,
  () => {
    syncFromRoute()
    doSearch()
  },
)

onMounted(() => {
  syncFromRoute()
  doSearch()
})
</script>

<style scoped>
.page-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: var(--space-8) var(--space-6);
}

.page-header {
  margin-bottom: var(--space-6);
}

.page-title {
  font-size: 1.75rem;
  margin-bottom: var(--space-1);
}

.page-sub {
  color: var(--color-text-muted);
  font-size: 0.95rem;
}

.toolbar {
  padding: var(--space-5) var(--space-6);
  margin-bottom: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.toolbar-row {
  display: flex;
  gap: var(--space-3);
}

.search-input {
  flex: 1;
}

.sort-select {
  width: 140px;
  flex-shrink: 0;
}

.category-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.chip {
  padding: 6px 16px;
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  font-weight: 500;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.chip:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.chip.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

.resource-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-6);
}

.empty-hint {
  color: var(--color-text-muted);
  padding: var(--space-16) var(--space-6);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.empty-hint .material-symbols-outlined {
  font-size: 48px;
  color: var(--color-text-muted);
}

.pagination-wrap {
  margin-top: var(--space-8);
  display: flex;
  justify-content: center;
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

  .toolbar-row {
    flex-direction: column;
  }

  .sort-select {
    width: 100%;
  }
}
</style>
