<template>
  <footer class="app-footer">
    <div class="footer-inner">
      <div class="footer-brand">
        <span class="material-symbols-outlined">school</span>
        <span>CS Academy Elite</span>
      </div>
      <p class="footer-text">个性化学习资源推荐系统 &copy; {{ year }}</p>
    </div>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear()
</script>

<style scoped>
.app-footer {
  margin-top: var(--space-16);
  padding: var(--space-8) var(--space-6);
  border-top: 1px solid var(--color-border);
  text-align: center;
}

.footer-inner {
  max-width: 1280px;
  margin: 0 auto;
}

.footer-brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  font-family: var(--font-heading);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.footer-text {
  color: var(--color-text-muted);
  font-size: 0.85rem;
}
</style>
