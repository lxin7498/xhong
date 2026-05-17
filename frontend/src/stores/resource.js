import { defineStore } from 'pinia'
import { ref } from 'vue'
import client from '@/api/client'

export const useResourceStore = defineStore('resource', () => {
  const list = ref([])
  const total = ref(0)
  const current = ref(null)
  const popular = ref([])
  const latest = ref([])
  const recommendations = ref([])
  const coldStart = ref(false)
  const loading = ref(false)
  const recommendationsComputing = ref(false)
  let _pollTimer = null

  async function fetchList(params = {}) {
    loading.value = true
    try {
      const { data } = await client.get('/resources/', { params })
      list.value = data.results
      total.value = data.count
      return data
    } finally {
      loading.value = false
    }
  }

  async function fetchDetail(id) {
    const { data } = await client.get(`/resources/${id}/`)
    current.value = data
    return data
  }

  async function fetchPopular() {
    const { data } = await client.get('/resources/', {
      params: { ordering: '-browse_count', page_size: 9 },
    })
    popular.value = data.results
    return data.results
  }

  async function fetchLatest() {
    const { data } = await client.get('/resources/', {
      params: { ordering: '-created_at', page_size: 9 },
    })
    latest.value = data.results
    return data.results
  }

  async function fetchRecommendations() {
    const { data } = await client.get('/recommendations/')
    recommendations.value = data.results
    coldStart.value = data.cold_start
    recommendationsComputing.value = data.computing || false
    if (data.computing) _startPolling()
    return data
  }

  async function refreshRecommendations() {
    const { data } = await client.post('/recommendations/refresh/')
    recommendations.value = data.results
    coldStart.value = data.cold_start
    recommendationsComputing.value = data.computing || false
    if (data.computing) _startPolling()
    return data
  }

  function _startPolling() {
    if (_pollTimer) return
    _pollTimer = setInterval(async () => {
      try {
        const { data } = await client.get('/recommendations/')
        recommendationsComputing.value = data.computing || false
        if (!data.computing) {
          recommendations.value = data.results
          coldStart.value = data.cold_start
          _stopPolling()
        }
      } catch {
        _stopPolling()
      }
    }, 2000)
  }

  function _stopPolling() {
    if (_pollTimer) {
      clearInterval(_pollTimer)
      _pollTimer = null
    }
    recommendationsComputing.value = false
  }

  return {
    list, total, current, popular, latest,
    recommendations, coldStart, loading, recommendationsComputing,
    fetchList, fetchDetail, fetchPopular, fetchLatest,
    fetchRecommendations, refreshRecommendations,
  }
})
