import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const AGENT_BASE = import.meta.env.VITE_AGENT_BASE_URL || 'http://127.0.0.1:8100'

export const useAiStore = defineStore('ai', () => {
  const conversations = ref([])
  const currentConversationId = ref(null)
  const messages = ref([])
  const isStreaming = ref(false)
  const isOpen = ref(false)
  const streamingContent = ref('')
  const toolStatus = ref('')

  const currentConversation = computed(() =>
    conversations.value.find(c => c.id === currentConversationId.value)
  )

  const hasMessages = computed(() => messages.value.length > 0)

  // ── Load conversation list from agent ───────────────────────

  async function fetchConversations() {
    try {
      const resp = await fetch(`${AGENT_BASE}/conversations`)
      if (resp.ok) {
        conversations.value = await resp.json()
      }
    } catch {
      // agent not running — keep local state
    }
  }

  // ── Panel toggle ────────────────────────────────────────────

  function togglePanel() {
    isOpen.value = !isOpen.value
    if (isOpen.value) {
      fetchConversations()
    }
  }

  // ── New conversation ────────────────────────────────────────

  function newConversation() {
    currentConversationId.value = null
    messages.value = []
    streamingContent.value = ''
    toolStatus.value = ''
  }

  // ── Send message ────────────────────────────────────────────

  async function sendMessage(content) {
    const userMsg = { role: 'user', content }
    messages.value.push(userMsg)
    streamingContent.value = ''
    toolStatus.value = ''
    isStreaming.value = true

    const token = localStorage.getItem('access_token') || ''

    try {
      const response = await fetch(`${AGENT_BASE}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: content,
          token,
          conversation_id: currentConversationId.value || '',
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let fullContent = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        let currentEvent = ''
        for (const line of lines) {
          const trimmed = line.trim()
          if (!trimmed) continue
          if (trimmed.startsWith('event: ')) {
            currentEvent = trimmed.slice(7)
          } else if (trimmed.startsWith('data: ')) {
            try {
              const data = JSON.parse(trimmed.slice(6))
              if (currentEvent === 'token') {
                const chunk = data.content || ''
                streamingContent.value += chunk
                fullContent += chunk
              } else if (currentEvent === 'status') {
                if (data.type === 'tool_start') {
                  toolStatus.value = `正在${data.tool === 'search_resources' ? '搜索资源' : data.tool === 'get_user_profile' ? '获取用户信息' : '查询'}...`
                } else if (data.type === 'tool_end') {
                  toolStatus.value = ''
                }
              } else if (currentEvent === 'done') {
                // Update conversation_id from server
                if (data.conversation_id) {
                  currentConversationId.value = data.conversation_id
                }
              }
            } catch {
              // skip malformed JSON
            }
          }
        }
      }

      const finalContent = fullContent || streamingContent.value
      if (finalContent) {
        messages.value.push({ role: 'assistant', content: finalContent })
      }
      streamingContent.value = ''

      // Refresh conversation list
      fetchConversations()
    } catch (err) {
      messages.value.push({
        role: 'assistant',
        content: `请求失败: ${err.message}。请确认 Agent 服务已启动。`,
      })
    } finally {
      isStreaming.value = false
      toolStatus.value = ''
    }
  }

  // ── Select conversation ─────────────────────────────────────

  async function selectConversation(id) {
    if (isStreaming.value) return
    try {
      const resp = await fetch(`${AGENT_BASE}/conversations/${id}`)
      if (!resp.ok) throw new Error('not found')
      const conv = await resp.json()
      currentConversationId.value = id
      messages.value = conv.messages || []
      streamingContent.value = ''
      toolStatus.value = ''
    } catch {
      // fallback: try local state
      const local = conversations.value.find(c => c.id === id)
      if (local) {
        currentConversationId.value = id
        messages.value = local.messages || []
        streamingContent.value = ''
        toolStatus.value = ''
      }
    }
  }

  // ── Delete conversation ─────────────────────────────────────

  async function deleteConversation(id) {
    try {
      await fetch(`${AGENT_BASE}/conversations/${id}`, { method: 'DELETE' })
    } catch {
      // best effort
    }
    conversations.value = conversations.value.filter(c => c.id !== id)
    if (currentConversationId.value === id) {
      currentConversationId.value = null
      messages.value = []
      streamingContent.value = ''
      toolStatus.value = ''
    }
  }

  return {
    conversations,
    currentConversationId,
    messages,
    isStreaming,
    isOpen,
    streamingContent,
    toolStatus,
    currentConversation,
    hasMessages,
    fetchConversations,
    togglePanel,
    newConversation,
    sendMessage,
    selectConversation,
    deleteConversation,
  }
})
