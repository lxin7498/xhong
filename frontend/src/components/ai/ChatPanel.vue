<template>
  <Teleport to="body">
    <Transition name="panel-slide">
      <aside v-if="aiStore.isOpen" class="chat-panel">
        <!-- Header -->
        <header class="chat-panel__header">
          <div class="chat-panel__header-left">
            <span class="material-symbols-outlined chat-panel__logo">smart_toy</span>
            <h3 class="chat-panel__title">AI 学习助手</h3>
          </div>
          <div class="chat-panel__header-actions">
            <button
              class="chat-panel__btn chat-panel__btn--icon"
              title="新建对话"
              @click="aiStore.newConversation()"
              :disabled="aiStore.isStreaming"
            >
              <span class="material-symbols-outlined">add_comment</span>
            </button>
            <button
              class="chat-panel__btn chat-panel__btn--icon"
              title="关闭"
              @click="aiStore.togglePanel()"
            >
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
        </header>

        <!-- Conversation tabs -->
        <div v-if="aiStore.conversations.length > 0" class="chat-panel__tabs">
          <button
            v-for="c in aiStore.conversations"
            :key="c.id"
            :class="['chat-panel__tab', { 'chat-panel__tab--active': c.id === aiStore.currentConversationId }]"
            @click="aiStore.selectConversation(c.id)"
          >
            <span class="chat-panel__tab-title">{{ c.title }}</span>
            <span
              class="chat-panel__tab-close"
              title="删除对话"
              @click.stop="aiStore.deleteConversation(c.id)"
            >
              <span class="material-symbols-outlined">close</span>
            </span>
          </button>
        </div>

        <!-- Messages area -->
        <div ref="messagesEl" class="chat-panel__messages" @scroll="onScroll">
          <!-- Empty state -->
          <div v-if="!aiStore.hasMessages && !aiStore.isStreaming" class="chat-panel__empty">
            <div class="chat-panel__empty-icon">
              <span class="material-symbols-outlined">psychology</span>
            </div>
            <p class="chat-panel__empty-title">有什么可以帮你的？</p>
            <p class="chat-panel__empty-desc">
              我可以根据你的专业背景和学习记录，为你推荐合适的学习资源
            </p>
            <div class="chat-panel__chips">
              <button
                v-for="q in suggestions"
                :key="q"
                class="chat-panel__chip"
                @click="handleSend(q)"
              >
                {{ q }}
              </button>
            </div>
          </div>

          <!-- Message bubbles -->
          <template v-for="(msg, i) in aiStore.messages" :key="i">
            <div :class="['chat-msg', `chat-msg--${msg.role}`]">
              <div class="chat-msg__bubble" v-html="renderContent(msg.content)"></div>
            </div>
          </template>

          <!-- Streaming bubble -->
          <div
            v-if="aiStore.isStreaming || aiStore.streamingContent"
            class="chat-msg chat-msg--assistant"
          >
            <div class="chat-msg__bubble">
              <span v-if="aiStore.toolStatus" class="chat-msg__tool-status">
                <span class="chat-msg__tool-dot"></span>
                {{ aiStore.toolStatus }}
              </span>
              <span v-if="aiStore.streamingContent" v-html="renderContent(aiStore.streamingContent)"></span>
              <span v-if="aiStore.isStreaming" class="chat-msg__cursor">|</span>
            </div>
          </div>

          <!-- Scroll-to-bottom button -->
          <Transition name="fade">
            <button
              v-if="showScrollBtn"
              class="chat-panel__scroll-btn"
              @click="scrollToBottom()"
            >
              <span class="material-symbols-outlined">keyboard_arrow_down</span>
            </button>
          </Transition>
        </div>

        <!-- Input area -->
        <form class="chat-panel__input" @submit.prevent="handleSend()">
          <input
            v-model="input"
            class="chat-panel__input-native"
            placeholder="输入你的问题..."
            :disabled="aiStore.isStreaming"
            maxlength="500"
            @keydown.enter.exact="handleSend()"
            autocomplete="off"
          />
          <button
            type="submit"
            class="chat-panel__send-btn"
            :disabled="!input.trim() || aiStore.isStreaming"
          >
            <span class="material-symbols-outlined">send</span>
          </button>
        </form>
      </aside>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useAiStore } from '@/stores/ai'

const aiStore = useAiStore()

const input = ref('')
const messagesEl = ref(null)
const showScrollBtn = ref(false)
let scrollAuto = true

const suggestions = [
  '推荐适合新手的Python学习资源',
  '有什么数据结构与算法的课程？',
  '推荐机器学习的入门学习路径',
  '适合大三学生的后端开发资源',
]

function handleSend(text) {
  const msg = text || input.value.trim()
  if (!msg || aiStore.isStreaming) return
  input.value = ''
  scrollAuto = true
  aiStore.sendMessage(msg)
}

function scrollToBottom() {
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    scrollAuto = true
    showScrollBtn.value = false
  }
}

function onScroll() {
  if (!messagesEl.value) return
  const el = messagesEl.value
  const dist = el.scrollHeight - el.scrollTop - el.clientHeight
  scrollAuto = dist < 60
  showScrollBtn.value = dist > 200
}

// Auto-scroll on new messages and streaming
watch(
  () => aiStore.streamingContent,
  () => {
    if (scrollAuto) {
      nextTick(() => {
        if (messagesEl.value) {
          messagesEl.value.scrollTop = messagesEl.value.scrollHeight
        }
      })
    }
  }
)

watch(
  () => aiStore.messages.length,
  () => {
    scrollAuto = true
    nextTick(() => {
      if (messagesEl.value) {
        messagesEl.value.scrollTop = messagesEl.value.scrollHeight
      }
    })
  }
)

// Simple markdown-like rendering
function renderContent(text) {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  // bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  // italic
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  // code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  // headers
  html = html.replace(/^### (.+)$/gm, '<h4 class="chat-md-h4">$1</h4>')
  html = html.replace(/^## (.+)$/gm, '<h3 class="chat-md-h3">$1</h3>')
  // dividers
  html = html.replace(/^---$/gm, '<hr class="chat-md-hr">')
  // unordered lists
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
  // numbered lists
  html = html.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>')
  // line breaks
  html = html.replace(/\n\n/g, '<br><br>')
  html = html.replace(/\n/g, '<br>')
  return html
}

// Close on Escape
function onKeydown(e) {
  if (e.key === 'Escape' && aiStore.isOpen) {
    aiStore.togglePanel()
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
/* ===== Panel Layout ===== */
.chat-panel {
  position: fixed;
  top: 64px;
  right: 0;
  bottom: 0;
  width: 420px;
  max-width: 100vw;
  z-index: 999;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-elevated);
  border-left: 1px solid var(--color-border);
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(16px);
}

/* ===== Header ===== */
.chat-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.chat-panel__header-left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.chat-panel__logo {
  font-size: 24px;
  color: var(--color-primary);
}

.chat-panel__title {
  margin: 0;
  font-family: var(--font-heading);
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.chat-panel__header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.chat-panel__btn {
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--color-text-muted);
  transition: color var(--transition-fast), background var(--transition-fast);
  border-radius: var(--radius-sm);
}

.chat-panel__btn--icon {
  width: 36px;
  height: 36px;
}

.chat-panel__btn:hover {
  color: var(--color-text-primary);
  background: var(--color-border-light);
}

.chat-panel__btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ===== Conversation Tabs ===== */
.chat-panel__tabs {
  display: flex;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
  overflow-x: auto;
  flex-shrink: 0;
  border-bottom: 1px solid var(--color-border-light);
}

.chat-panel__tabs::-webkit-scrollbar {
  height: 0;
}

.chat-panel__tab {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  cursor: pointer;
  white-space: nowrap;
  font-size: 13px;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.chat-panel__tab:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.chat-panel__tab--active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

.chat-panel__tab-title {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-panel__tab-close {
  display: flex;
  align-items: center;
  font-size: 14px;
  opacity: 0.6;
  transition: opacity var(--transition-fast);
}

.chat-panel__tab-close:hover {
  opacity: 1;
}

.chat-panel__tab--active .chat-panel__tab-close {
  color: rgba(255, 255, 255, 0.8);
}

/* ===== Messages Area ===== */
.chat-panel__messages {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: var(--space-4);
  position: relative;
  scroll-behavior: smooth;
}

.chat-panel__messages::-webkit-scrollbar {
  width: 4px;
}

.chat-panel__messages::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 4px;
}

/* ===== Empty State ===== */
.chat-panel__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  text-align: center;
  padding: var(--space-8);
}

.chat-panel__empty-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-full);
  background: var(--color-primary-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-4);
}

.chat-panel__empty-icon .material-symbols-outlined {
  font-size: 32px;
  color: var(--color-primary);
}

.chat-panel__empty-title {
  font-family: var(--font-heading);
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 var(--space-2);
}

.chat-panel__empty-desc {
  font-size: 14px;
  color: var(--color-text-muted);
  margin: 0 0 var(--space-6);
  max-width: 280px;
}

.chat-panel__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  justify-content: center;
}

.chat-panel__chip {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-body);
}

.chat-panel__chip:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-bg);
}

/* ===== Message Bubbles ===== */
.chat-msg {
  display: flex;
  margin-bottom: var(--space-4);
}

.chat-msg--user {
  justify-content: flex-end;
}

.chat-msg--assistant {
  justify-content: flex-start;
}

.chat-msg__bubble {
  max-width: 85%;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.chat-msg--user .chat-msg__bubble {
  background: var(--color-primary);
  color: #fff;
  border-bottom-right-radius: var(--space-1);
}

.chat-msg--assistant .chat-msg__bubble {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-bottom-left-radius: var(--space-1);
  color: var(--color-text-primary);
}

/* ===== Tool Status ===== */
.chat-msg__tool-status {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: var(--space-2);
  font-size: 12px;
  color: var(--color-text-muted);
}

.chat-msg__tool-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary);
  animation: pulse-dot 1.2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.75); }
}

/* ===== Streaming Cursor ===== */
.chat-msg__cursor {
  display: inline-block;
  color: var(--color-primary);
  animation: blink 0.8s step-end infinite;
  font-weight: 300;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* ===== Markdown Content ===== */
.chat-msg__bubble :deep(strong) {
  font-weight: 600;
  color: inherit;
}

.chat-msg__bubble :deep(em) {
  font-style: italic;
}

.chat-msg__bubble :deep(code) {
  background: var(--color-border-light);
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

.chat-msg__bubble :deep(.chat-md-h3) {
  font-family: var(--font-heading);
  font-size: 15px;
  font-weight: 600;
  margin: var(--space-3) 0 var(--space-2);
  color: inherit;
}

.chat-msg__bubble :deep(.chat-md-h4) {
  font-family: var(--font-heading);
  font-size: 14px;
  font-weight: 600;
  margin: var(--space-2) 0 var(--space-1);
  color: inherit;
}

.chat-msg__bubble :deep(.chat-md-hr) {
  border: none;
  border-top: 1px solid var(--color-border-light);
  margin: var(--space-3) 0;
}

.chat-msg__bubble :deep(ul) {
  margin: var(--space-2) 0;
  padding-left: var(--space-5);
}

.chat-msg__bubble :deep(li) {
  margin-bottom: 2px;
}

/* ===== Scroll Button ===== */
.chat-panel__scroll-btn {
  position: absolute;
  bottom: 8px;
  right: 16px;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
  background: var(--color-bg-elevated);
  box-shadow: var(--shadow-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.chat-panel__scroll-btn:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
}

/* ===== Input Area ===== */
.chat-panel__input {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.chat-panel__input-native {
  flex: 1;
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-bg-card);
  color: var(--color-text-primary);
  font-size: 14px;
  font-family: var(--font-body);
  outline: none;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.chat-panel__input-native:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-bg);
}

.chat-panel__input-native:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chat-panel__input-native::placeholder {
  color: var(--color-text-muted);
}

.chat-panel__send-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: var(--color-primary);
  color: #fff;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.chat-panel__send-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
  transform: scale(1.08);
}

.chat-panel__send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  background: var(--color-text-muted);
}

/* ===== Slide Transition ===== */
.panel-slide-enter-active,
.panel-slide-leave-active {
  transition: transform var(--transition-slow), opacity var(--transition-normal);
}

.panel-slide-enter-from,
.panel-slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* ===== Mobile ===== */
@media (max-width: 640px) {
  .chat-panel {
    width: 100vw;
    top: 56px;
  }
}
</style>
