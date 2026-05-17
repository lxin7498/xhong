<template>
  <header class="app-header glass-card">
    <div class="header-inner">
      <router-link to="/" class="logo">
        <span class="logo-icon material-symbols-outlined">school</span>
        <span class="logo-text">CS Academy Elite</span>
      </router-link>

      <nav class="nav-links">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/resources" class="nav-link">资源广场</router-link>
        <router-link v-if="authStore.isLoggedIn" to="/profile" class="nav-link">个人中心</router-link>
      </nav>

      <div class="header-actions">
        <button class="theme-toggle" @click="appStore.toggleTheme()" :title="isDark ? '切换亮色' : '切换暗色'">
          <span class="material-symbols-outlined">{{ isDark ? 'light_mode' : 'dark_mode' }}</span>
        </button>

        <template v-if="authStore.isLoggedIn">
          <el-dropdown trigger="click">
            <span class="user-avatar">
              <span class="material-symbols-outlined">account_circle</span>
              <span class="username">{{ authStore.user?.nickname || authStore.user?.username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="authStore.logout()">
                  <span class="dropdown-link">退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>

        <template v-else>
          <router-link to="/login" class="btn-text">登录</router-link>
          <router-link to="/register" class="btn-primary btn-sm">注册</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'

const appStore = useAppStore()
const authStore = useAuthStore()
const { isDark } = storeToRefs(appStore)
</script>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  border-radius: 0;
  border-top: none;
  border-left: none;
  border-right: none;
  height: 64px;
}

.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 var(--space-6);
  display: flex;
  align-items: center;
  height: 100%;
  gap: var(--space-8);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 1.25rem;
  color: var(--color-primary-dark);
  text-decoration: none;
}

.logo-icon {
  font-size: 28px;
  color: var(--color-primary);
}

.nav-links {
  display: flex;
  gap: var(--space-1);
}

.nav-link {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  color: var(--color-text-secondary);
  font-weight: 500;
  font-size: 0.9rem;
  transition: all var(--transition-fast);
}

.nav-link:hover,
.nav-link.router-link-exact-active {
  color: var(--color-primary);
  background: var(--color-primary-bg);
}

.header-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.theme-toggle {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.theme-toggle:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.user-avatar {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
}

.username {
  font-size: 0.9rem;
  font-weight: 500;
}

.btn-primary {
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-full);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary:hover {
  background: var(--color-primary-dark);
}

.btn-sm {
  padding: var(--space-2) var(--space-5);
  font-size: 0.875rem;
}

.btn-text {
  color: var(--color-text-secondary);
  font-weight: 500;
  font-size: 0.9rem;
  padding: var(--space-2) var(--space-3);
}

.btn-text:hover {
  color: var(--color-text-primary);
}

.dropdown-link {
  color: var(--color-text-primary);
  text-decoration: none;
  display: block;
  width: 100%;
}
</style>
