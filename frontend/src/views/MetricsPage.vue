<template>
  <div class="metrics-page">
    <!-- Header -->
    <section class="page-hero">
      <h1 class="hero-title">
        <span class="material-symbols-outlined hero-icon">monitoring</span>
        推荐系统评估仪表盘
      </h1>
      <p class="hero-desc">
        离线评估对比：<strong>Popularity 热门推荐</strong>（基线）vs <strong>User-Based CF 协同过滤</strong>
      </p>
      <button class="btn-refresh" :disabled="refreshing" @click="refreshMetrics">
        <span class="material-symbols-outlined" :class="{ spinning: refreshing }">sync</span>
        {{ refreshing ? '重新评估中...' : '重新运行评估' }}
      </button>
    </section>

    <!-- Loading / Error -->
    <section v-if="loading" class="loading-card glass-card">
      <span class="material-symbols-outlined spinning">sync</span>
      <p>正在加载评估数据...</p>
    </section>

    <section v-else-if="error" class="error-card glass-card">
      <span class="material-symbols-outlined">error_outline</span>
      <p>{{ error }}</p>
      <button class="btn-retry" @click="fetchMetrics">重新加载</button>
    </section>

    <template v-else-if="data">
      <!-- Info Bar -->
      <section class="info-bar">
        <div class="info-item">
          <span class="material-symbols-outlined">people</span>
          <div>
            <span class="info-label">可评估用户</span>
            <strong>{{ data.popularity.evaluable_users }}</strong>
          </div>
        </div>
        <div class="info-item">
          <span class="material-symbols-outlined">ac_unit</span>
          <div>
            <span class="info-label">冷启动用户</span>
            <strong>{{ data.popularity.cold_start_count }}</strong>
          </div>
        </div>
        <div class="info-item">
          <span class="material-symbols-outlined">schedule</span>
          <div>
            <span class="info-label">数据切分</span>
            <strong>80/20</strong>
          </div>
        </div>
        <div class="info-item">
          <span class="material-symbols-outlined">trending_up</span>
          <div>
            <span class="info-label">相关性阈值</span>
            <strong>评分 ≥ 4</strong>
          </div>
        </div>
        <div class="info-item">
          <span class="material-symbols-outlined">psychology</span>
          <div>
            <span class="info-label">冷启动阈值</span>
            <strong>≤ {{ data.cold_start_threshold }} 条行为</strong>
          </div>
        </div>
      </section>

      <!-- Metric Cards: K=5 -->
      <section class="section-label">K = 5</section>
      <div class="metric-grid">
        <div class="metric-card glass-card" v-for="m in k5Metrics" :key="m.key">
          <div class="metric-header">
            <span class="material-symbols-outlined metric-icon">{{ m.icon }}</span>
            <span class="metric-name">{{ m.label }}</span>
          </div>
          <div class="metric-compare">
            <div class="metric-algo" :class="{ winner: m.popWins }">
              <span class="algo-tag pop">Popularity</span>
              <span class="algo-value">{{ m.pop }}</span>
            </div>
            <div class="metric-vs">vs</div>
            <div class="metric-algo" :class="{ winner: m.cfWins }">
              <span class="algo-tag cf">CF</span>
              <span class="algo-value">{{ m.cf }}</span>
            </div>
          </div>
          <div class="metric-winner-tag" v-if="m.winner">
            <span class="material-symbols-outlined">emoji_events</span>
            {{ m.winner }} 更优
          </div>
        </div>
      </div>

      <!-- Metric Cards: K=9 -->
      <section class="section-label">K = 9</section>
      <div class="metric-grid">
        <div class="metric-card glass-card" v-for="m in k9Metrics" :key="m.key">
          <div class="metric-header">
            <span class="material-symbols-outlined metric-icon">{{ m.icon }}</span>
            <span class="metric-name">{{ m.label }}</span>
          </div>
          <div class="metric-compare">
            <div class="metric-algo" :class="{ winner: m.popWins }">
              <span class="algo-tag pop">Popularity</span>
              <span class="algo-value">{{ m.pop }}</span>
            </div>
            <div class="metric-vs">vs</div>
            <div class="metric-algo" :class="{ winner: m.cfWins }">
              <span class="algo-tag cf">CF</span>
              <span class="algo-value">{{ m.cf }}</span>
            </div>
          </div>
          <div class="metric-winner-tag" v-if="m.winner">
            <span class="material-symbols-outlined">emoji_events</span>
            {{ m.winner }} 更优
          </div>
        </div>
      </div>

      <!-- Global Metrics -->
      <section class="section-label">全局指标</section>
      <div class="metric-grid metric-grid-2">
        <div class="metric-card glass-card" v-for="m in globalMetrics" :key="m.key">
          <div class="metric-header">
            <span class="material-symbols-outlined metric-icon">{{ m.icon }}</span>
            <span class="metric-name">{{ m.label }}</span>
          </div>
          <div class="metric-compare">
            <div class="metric-algo" :class="{ winner: m.popWins }">
              <span class="algo-tag pop">Popularity</span>
              <span class="algo-value">{{ m.pop }}</span>
            </div>
            <div class="metric-vs">vs</div>
            <div class="metric-algo" :class="{ winner: m.cfWins }">
              <span class="algo-tag cf">CF</span>
              <span class="algo-value">{{ m.cf }}</span>
            </div>
          </div>
          <div class="metric-winner-tag" v-if="m.winner && m.pop !== 'N/A'">
            <span class="material-symbols-outlined">emoji_events</span>
            {{ m.winner }} 更优
          </div>
          <div class="metric-note" v-if="m.note">{{ m.note }}</div>
        </div>
      </div>

      <!-- Bar Chart -->
      <section class="section-label">指标对比图</section>
      <div class="chart-card glass-card">
        <canvas ref="chartCanvas"></canvas>
      </div>

      <!-- Cold-Start Detail -->
      <section class="section-label">冷启动分析</section>
      <div class="cold-start-grid">
        <div class="glass-card cold-card">
          <div class="cold-header">
            <span class="material-symbols-outlined">local_fire_department</span>
            <div>
              <h3>Popularity 冷启动</h3>
              <p class="cold-stat">
                {{ data.popularity.cold_start_hit_count }} / {{ data.popularity.cold_start_count }} 命中
                · 命中率 {{ fmtPct(data.popularity.cold_start_hit_rate) }}
              </p>
            </div>
          </div>
          <div class="cold-bar-wrap">
            <div class="cold-bar">
              <div
                class="cold-fill pop-fill"
                :style="{ width: fmtPct(data.popularity.cold_start_hit_rate) }"
              ></div>
            </div>
          </div>
        </div>
        <div class="glass-card cold-card">
          <div class="cold-header">
            <span class="material-symbols-outlined">local_fire_department</span>
            <div>
              <h3>CF 冷启动</h3>
              <p class="cold-stat">
                {{ data.cf.cold_start_hit_count }} / {{ data.cf.cold_start_count }} 命中
                · 命中率 {{ fmtPct(data.cf.cold_start_hit_rate) }}
              </p>
            </div>
          </div>
          <div class="cold-bar-wrap">
            <div class="cold-bar">
              <div
                class="cold-fill cf-fill"
                :style="{ width: fmtPct(data.cf.cold_start_hit_rate) }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Methodology footer -->
      <section class="methodology glass-card">
        <h3>
          <span class="material-symbols-outlined">info</span>
          评估方法说明
        </h3>
        <ul>
          <li><strong>数据切分：</strong>对每个用户的评分行为按时间排序，前 80% 作为训练集，后 20% 作为测试集</li>
          <li><strong>相关性判定：</strong>测试集中实际评分 ≥ 4 的资源视为"相关"</li>
          <li><strong>Precision@K：</strong>推荐列表前 K 个中相关资源的比例</li>
          <li><strong>Recall@K：</strong>推荐列表前 K 个覆盖了多少用户实际相关的资源</li>
          <li><strong>NDCG@K：</strong>考虑排序位置的相关性质量（用实际评分作为相关性分数）</li>
          <li><strong>Coverage：</strong>所有推荐去重后覆盖的资源种类占总资源的比例</li>
          <li><strong>冷启动命中率：</strong>行为数 ≤ {{ data.cold_start_threshold }} 的冷启动用户中，推荐列表至少有 1 个相关资源的用户比例</li>
        </ul>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import client from '@/api/client'
import Chart from 'chart.js/auto'

// -----------------------------------------------------------------------
// Data fetching
// -----------------------------------------------------------------------
const data = ref(null)
const loading = ref(true)
const error = ref(null)
const refreshing = ref(false)

async function fetchMetrics() {
  loading.value = true
  error.value = null
  try {
    const { data: resp } = await client.get('/recommendations/metrics/')
    data.value = resp
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || '无法加载评估数据，请确认后端已运行且数据充足。'
  } finally {
    loading.value = false
  }
}

async function refreshMetrics() {
  refreshing.value = true
  error.value = null
  try {
    const { data: resp } = await client.post('/recommendations/metrics/')
    data.value = resp
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || '评估刷新失败'
  } finally {
    refreshing.value = false
  }
}

onMounted(() => {
  fetchMetrics()
})

// -----------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------
function fmtPct(val) {
  return (val * 100).toFixed(1) + '%'
}

function fmtNum(val) {
  return val.toFixed(4)
}

function makeComparison(label, icon, key, popVal, cfVal) {
  const popWins = popVal > cfVal
  const cfWins = cfVal > popVal
  const winner = popWins ? 'Popularity' : cfWins ? 'CF' : null
  return {
    key, label, icon,
    pop: fmtNum(popVal),
    cf: fmtNum(cfVal),
    popWins, cfWins, winner,
  }
}

const k5Metrics = computed(() => {
  if (!data.value) return []
  const p = data.value.popularity
  const c = data.value.cf
  return [
    makeComparison('Precision@5', 'tactic', 'p5', p.precision_5, c.precision_5),
    makeComparison('Recall@5', 'find_in_page', 'r5', p.recall_5, c.recall_5),
    makeComparison('NDCG@5', 'sort', 'n5', p.ndcg_5, c.ndcg_5),
  ]
})

const k9Metrics = computed(() => {
  if (!data.value) return []
  const p = data.value.popularity
  const c = data.value.cf
  return [
    makeComparison('Precision@9', 'tactic', 'p9', p.precision_9, c.precision_9),
    makeComparison('Recall@9', 'find_in_page', 'r9', p.recall_9, c.recall_9),
    makeComparison('NDCG@9', 'sort', 'n9', p.ndcg_9, c.ndcg_9),
  ]
})

const globalMetrics = computed(() => {
  if (!data.value) return []
  const p = data.value.popularity
  const c = data.value.cf
  return [
    makeComparison('Coverage 覆盖率', 'donut_large', 'cov', p.coverage, c.coverage),
    makeComparison('冷启动命中率', 'ac_unit', 'cshr', p.cold_start_hit_rate, c.cold_start_hit_rate),
    {
      key: 'rmse', label: 'RMSE (评分预测)', icon: 'speed',
      pop: 'N/A', cf: fmtNum(c.rmse),
      popWins: false, cfWins: false, winner: 'CF',
      note: '仅 CF 可预测评分',
    },
  ]
})

// -----------------------------------------------------------------------
// Chart.js bar chart
// -----------------------------------------------------------------------
const chartCanvas = ref(null)
let chartInstance = null

function buildChart() {
  if (!data.value || !chartCanvas.value) return
  if (chartInstance) chartInstance.destroy()

  const p = data.value.popularity
  const c = data.value.cf

  const labels = [
    'Precision@5', 'Recall@5', 'NDCG@5',
    'Precision@9', 'Recall@9', 'NDCG@9',
    'Coverage', '冷启动命中率',
  ]

  const popData = [
    p.precision_5, p.recall_5, p.ndcg_5,
    p.precision_9, p.recall_9, p.ndcg_9,
    p.coverage, p.cold_start_hit_rate,
  ]

  const cfData = [
    c.precision_5, c.recall_5, c.ndcg_5,
    c.precision_9, c.recall_9, c.ndcg_9,
    c.coverage, c.cold_start_hit_rate,
  ]

  const ctx = chartCanvas.value.getContext('2d')
  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Popularity (热门)',
          data: popData,
          backgroundColor: 'rgba(245, 158, 11, 0.75)',
          borderColor: '#f59e0b',
          borderWidth: 1.5,
          borderRadius: 6,
        },
        {
          label: 'CF (协同过滤)',
          data: cfData,
          backgroundColor: 'rgba(16, 185, 129, 0.75)',
          borderColor: '#10b981',
          borderWidth: 1.5,
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-primary').trim() || '#334155',
            font: { size: 13 },
            padding: 16,
            usePointStyle: true,
          },
        },
      },
      scales: {
        x: {
          ticks: {
            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary').trim() || '#64748b',
            font: { size: 12 },
          },
          grid: { display: false },
        },
        y: {
          beginAtZero: true,
          max: 1,
          ticks: {
            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary').trim() || '#64748b',
            font: { size: 11 },
            callback: (v) => (v * 100).toFixed(0) + '%',
          },
          grid: {
            color: getComputedStyle(document.documentElement).getPropertyValue('--color-border').trim() || '#e2e8f0',
          },
        },
      },
    },
  })
}

watch(data, async (val) => {
  if (val) {
    await nextTick()
    buildChart()
  }
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})
</script>

<style scoped>
.metrics-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-8) var(--space-6);
}

/* Hero */
.page-hero {
  text-align: center;
  margin-bottom: var(--space-10);
}
.hero-icon {
  font-size: 40px;
  color: var(--color-primary);
  vertical-align: middle;
  margin-right: var(--space-3);
}
.hero-title {
  font-family: var(--font-heading);
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
}
.hero-desc {
  color: var(--color-text-secondary);
  margin-top: var(--space-3);
  font-size: 1rem;
}

.btn-refresh {
  margin-top: var(--space-5);
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-6);
  border-radius: var(--radius-full);
  background: var(--color-primary);
  color: #fff;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all var(--transition-fast);
}
.btn-refresh:hover:not(:disabled) {
  background: var(--color-primary-dark);
}
.btn-refresh:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Loading / Error */
.loading-card, .error-card {
  text-align: center;
  padding: var(--space-12);
  color: var(--color-text-secondary);
}
.spinning {
  animation: spin 1s linear infinite;
  font-size: 32px;
  display: block;
  margin-bottom: var(--space-3);
}
@keyframes spin { to { transform: rotate(360deg); } }
.error-card {
  color: var(--color-danger, #ef4444);
}
.btn-retry {
  margin-top: var(--space-4);
  padding: var(--space-2) var(--space-6);
  border-radius: var(--radius-full);
  background: var(--color-primary);
  color: #fff;
  border: none;
  cursor: pointer;
  font-weight: 600;
}

/* Info Bar */
.info-bar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  margin-bottom: var(--space-8);
}
.info-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-5);
  font-size: 0.875rem;
}
.info-item .material-symbols-outlined {
  font-size: 22px;
  color: var(--color-primary);
}
.info-label {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

/* Section */
.section-label {
  font-family: var(--font-heading);
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: var(--space-8) 0 var(--space-4);
  padding-left: var(--space-1);
}

/* Metric Grid */
.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-2);
}
.metric-grid-2 {
  grid-template-columns: repeat(2, 1fr);
}

.metric-card {
  padding: var(--space-5);
  text-align: center;
}
.metric-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}
.metric-icon {
  font-size: 20px;
  color: var(--color-primary);
}
.metric-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--color-text-primary);
}

.metric-compare {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  justify-content: center;
}
.metric-algo {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}
.metric-algo.winner {
  background: var(--color-primary-bg);
}
.algo-tag {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}
.algo-tag.pop {
  background: #fef3c7;
  color: #b45309;
}
.algo-tag.cf {
  background: #d1fae5;
  color: #047857;
}
.algo-value {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text-primary);
}
.metric-vs {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.metric-winner-tag {
  margin-top: var(--space-3);
  font-size: 0.8rem;
  color: var(--color-primary);
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.metric-winner-tag .material-symbols-outlined {
  font-size: 16px;
}

.metric-note {
  margin-top: var(--space-3);
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

/* Chart */
.chart-card {
  padding: var(--space-6);
  height: 420px;
}
.chart-card canvas {
  width: 100% !important;
  height: 100% !important;
}

/* Cold Start */
.cold-start-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}
.cold-card {
  padding: var(--space-5);
}
.cold-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}
.cold-header .material-symbols-outlined {
  font-size: 28px;
  color: var(--color-primary);
}
.cold-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}
.cold-stat {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  margin-top: 2px;
}
.cold-bar-wrap {
  padding: 0 var(--space-1);
}
.cold-bar {
  height: 10px;
  background: var(--color-bg-secondary);
  border-radius: 5px;
  overflow: hidden;
}
.cold-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.6s ease;
}
.pop-fill { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.cf-fill { background: linear-gradient(90deg, #10b981, #34d399); }

/* Methodology */
.methodology {
  margin-top: var(--space-8);
  padding: var(--space-6);
}
.methodology h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}
.methodology ul {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
}
.methodology li {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

/* Responsive */
@media (max-width: 768px) {
  .metric-grid { grid-template-columns: 1fr; }
  .metric-grid-2 { grid-template-columns: 1fr; }
  .cold-start-grid { grid-template-columns: 1fr; }
  .methodology ul { grid-template-columns: 1fr; }
  .chart-card { height: 320px; }
  .hero-title { font-size: 1.5rem; }
}
</style>
