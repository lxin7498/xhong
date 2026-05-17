<template>
  <button
    v-show="!aiStore.isOpen"
    class="ai-bubble"
    @click="aiStore.togglePanel()"
    aria-label="打开 AI 助手"
  >
    <span class="material-symbols-outlined ai-bubble__icon">smart_toy</span>
    <span v-if="unreadCount > 0" class="ai-bubble__badge">
      {{ unreadCount > 9 ? '9+' : unreadCount }}
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useAiStore } from '@/stores/ai'

const aiStore = useAiStore()

const unreadCount = computed(() => {
  // Count AI responses since last open (simplified: count all assistant messages)
  return aiStore.messages.filter(m => m.role === 'assistant').length
})
</script>

<style scoped>
.ai-bubble {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-full);
  border: 1px solid var(--color-glass-border);
  background: var(--color-bg-elevated);
  backdrop-filter: blur(12px);
  box-shadow: var(--shadow-lg), var(--shadow-glow);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition:
    transform var(--transition-normal),
    box-shadow var(--transition-normal),
    background var(--transition-normal);
  color: var(--color-primary);
  outline: none;
}

.ai-bubble:hover {
  transform: scale(1.08);
  box-shadow: var(--shadow-lg), 0 0 32px rgba(16, 185, 129, 0.25);
}

.ai-bubble:active {
  transform: scale(0.95);
}


.ai-bubble__icon {
  font-size: 28px;
  transition: transform var(--transition-normal);
}

.ai-bubble__badge {
  position: absolute;
  top: -2px;
  right: -2px;
  min-width: 20px;
  height: 20px;
  padding: 0 5px;
  border-radius: var(--radius-full);
  background: #ef4444;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  font-family: var(--font-body);
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}
</style>
