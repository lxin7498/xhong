import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import client from '@/api/client'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const token = ref(localStorage.getItem('access_token'))
  const router = useRouter()

  const isLoggedIn = computed(() => !!token.value)

  async function login(credentials) {
    const { data } = await client.post('/auth/login/', credentials)
    token.value = data.access
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    localStorage.setItem('user', JSON.stringify(data.user))
    user.value = data.user
    return data
  }

  async function register(formData) {
    const { data } = await client.post('/auth/register/', formData)
    return data
  }

  function logout() {
    token.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    user.value = null
    router.push('/')
  }

  async function fetchProfile() {
    const { data } = await client.get('/users/me/')
    user.value = data
    localStorage.setItem('user', JSON.stringify(data))
    return data
  }

  return { user, isLoggedIn, login, register, logout, fetchProfile }
})
