<template>
  <router-link :to="`/resource/${resource.id}`" class="resource-card glass-card">
    <div class="card-cover">
      <img v-if="resource.cover_image" :src="resource.cover_image" :alt="resource.title" />
      <div v-else class="cover-placeholder">
        <span class="material-symbols-outlined">{{ typeIcon }}</span>
      </div>
      <span class="type-badge" :class="resource.resource_type">{{ typeLabel }}</span>
    </div>
    <div class="card-body">
      <h3 class="card-title">{{ resource.title }}</h3>
      <p class="card-desc">{{ resource.description }}</p>
      <div class="card-tags" v-if="resource.tags?.length">
        <span class="tag-chip" v-for="tag in resource.tags.slice(0, 3)" :key="tag">{{ tag }}</span>
      </div>
      <div class="card-meta">
        <div class="meta-left">
          <span class="difficulty-badge" :class="resource.difficulty">{{ difficultyLabel }}</span>
          <span class="category">{{ resource.category }}</span>
        </div>
        <div class="meta-right">
          <span class="rating" v-if="resource.avg_rating > 0">
            <span class="material-symbols-outlined star">star</span>
            {{ resource.avg_rating }}
          </span>
          <span class="browse-count">
            <span class="material-symbols-outlined">visibility</span>
            {{ resource.browse_count }}
          </span>
        </div>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  resource: { type: Object, required: true },
})

const typeIcon = computed(() => {
  const icons = { video: 'smart_display', article: 'article', exercise: 'code' }
  return icons[props.resource.resource_type] || 'description'
})

const typeLabel = computed(() => {
  const labels = { video: '视频', article: '文章', exercise: '练习' }
  return labels[props.resource.resource_type] || props.resource.resource_type
})

const difficultyLabel = computed(() => {
  const labels = { beginner: '初级', intermediate: '中级', advanced: '高级' }
  return labels[props.resource.difficulty] || props.resource.difficulty
})
</script>

<style scoped>
.resource-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all var(--transition-normal);
  text-decoration: none;
  color: inherit;
}

.resource-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary);
}

.card-cover {
  position: relative;
  height: 160px;
  overflow: hidden;
  flex-shrink: 0;
}

.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slow);
}

.resource-card:hover .card-cover img {
  transform: scale(1.05);
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary-bg), var(--color-accent-light));
}

.cover-placeholder .material-symbols-outlined {
  font-size: 48px;
  color: var(--color-primary);
}

.type-badge {
  position: absolute;
  top: var(--space-3);
  left: var(--space-3);
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
  color: #fff;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(4px);
}

.type-badge.video { background: rgba(16, 185, 129, 0.85); }
.type-badge.article { background: rgba(59, 130, 246, 0.85); }
.type-badge.exercise { background: rgba(245, 158, 11, 0.85); }

.card-body {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: var(--space-2);
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-desc {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag-chip {
  padding: 2px 8px;
  font-size: 0.72rem;
  border-radius: var(--radius-full);
  background: var(--color-primary-bg);
  color: var(--color-primary-dark);
  font-weight: 500;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: var(--space-2);
  border-top: 1px solid var(--color-border-light);
}

.meta-left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.difficulty-badge {
  padding: 1px 8px;
  border-radius: var(--radius-full);
  font-size: 0.72rem;
  font-weight: 600;
}

.difficulty-badge.beginner { background: #d1fae5; color: #065f46; }
.difficulty-badge.intermediate { background: #fef3c7; color: #92400e; }
.difficulty-badge.advanced { background: #fee2e2; color: #991b1b; }

[data-theme="dark"] .difficulty-badge.beginner { background: #064e3b; color: #6ee7b7; }
[data-theme="dark"] .difficulty-badge.intermediate { background: #78350f; color: #fcd34d; }
[data-theme="dark"] .difficulty-badge.advanced { background: #7f1d1d; color: #fca5a5; }

.category {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.meta-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.rating {
  display: flex;
  align-items: center;
  gap: 2px;
  color: var(--color-accent);
  font-weight: 600;
}

.star {
  font-size: 14px;
}

.browse-count {
  display: flex;
  align-items: center;
  gap: 2px;
}

.browse-count .material-symbols-outlined {
  font-size: 14px;
}
</style>
