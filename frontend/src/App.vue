<template>
  <div id="app-root" :data-theme="theme">
    <AppHeader />
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <AppFooter />
    <AIChatBubble />
    <AIChatPanel />
  </div>
</template>

<script setup>
import { useAppStore } from '@/stores/app'
import { storeToRefs } from 'pinia'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import AIChatBubble from '@/components/ai/ChatBubble.vue'
import AIChatPanel from '@/components/ai/ChatPanel.vue'

const appStore = useAppStore()
const { theme } = storeToRefs(appStore)
</script>
