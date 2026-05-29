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
        <a href="https://github.com/lxin7498/xhong" target="_blank" class="github-link" title="GitHub 仓库">
          <svg class="github-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
          </svg>
        </a>

        <button class="theme-toggle" @click="appStore.toggleTheme()" :title="isDark ? '切换亮色' : '切换暗色'">
          <span class="material-symbols-outlined">{{ isDark ? 'light_mode' : 'dark_mode' }}</span>
        </button>

        <a :href="adminUrl" class="icon-btn" title="后台管理">
          <span class="material-symbols-outlined">admin_panel_settings</span>
        </a>

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

const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
const adminUrl = apiBase.replace(/\/api\/?$/, '/admin/')
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

.github-link {
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

.github-link:hover {
  border-color: var(--color-text-primary);
  color: var(--color-text-primary);
}

.github-icon {
  width: 20px;
  height: 20px;
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

.icon-btn {
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
  text-decoration: none;
  transition: all var(--transition-fast);
}

.icon-btn:hover {
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
