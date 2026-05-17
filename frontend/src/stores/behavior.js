import { defineStore } from 'pinia'
import { ref } from 'vue'
import client from '@/api/client'

export const useBehaviorStore = defineStore('behavior', () => {
  const history = ref([])
  const favorites = ref([])
  const ratings = ref([])
  const loading = ref(false)

  async function trackBrowse(resourceId) {
    try {
      await client.post('/behaviors/browse/', { resource_id: resourceId })
    } catch {
      // silently ignore — browse tracking is best-effort
    }
  }

  async function toggleBookmark(resourceId) {
    const { data } = await client.post('/behaviors/bookmark/', { resource_id: resourceId })
    return data.is_bookmarked
  }

  async function submitRating(resourceId, rating) {
    const { data } = await client.post('/behaviors/rate/', { resource_id: resourceId, rating })
    return data
  }

  async function fetchHistory() {
    loading.value = true
    try {
      const { data } = await client.get('/behaviors/history/')
      history.value = data.results
      return data
    } finally {
      loading.value = false
    }
  }

  async function fetchFavorites() {
    loading.value = true
    try {
      const { data } = await client.get('/behaviors/favorites/')
      favorites.value = data.results
      return data
    } finally {
      loading.value = false
    }
  }

  async function fetchRatings() {
    loading.value = true
    try {
      const { data } = await client.get('/behaviors/ratings/')
      ratings.value = data.results
      return data
    } finally {
      loading.value = false
    }
  }

  return {
    history, favorites, ratings, loading,
    trackBrowse, toggleBookmark, submitRating,
    fetchHistory, fetchFavorites, fetchRatings,
  }
})
