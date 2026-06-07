<template>
  <div class="snap-screen">

    <!-- ── Top App Bar ── -->
    <header class="snap-topbar">
      <div class="snap-topbar-brand">
        <span class="material-symbols-outlined ms-filled" style="color:#b02a26;font-size:24px">construction</span>
        <span class="brand-name">SnapMend</span>
      </div>
      <div class="snap-topbar-right">
        <!-- API status indicator -->
        <span
          class="status-dot"
          :class="apiStatus === true ? 'online' : apiStatus === false ? 'offline' : 'checking'"
          :title="apiStatus === true ? 'Backend connected' : apiStatus === false ? 'Backend offline' : 'Checking...'"
        ></span>
        <div class="snap-topbar-avatar">
          <span class="material-symbols-outlined" style="color:#59413e;font-size:20px">person</span>
        </div>
      </div>
    </header>

    <!-- ── Main Scroll Area ── -->
    <main class="snap-main">

      <!-- ── Hero Greeting Card ── -->
      <section style="background:linear-gradient(135deg,#fff0ee 0%,#fff8f7 100%);padding:24px 16px 20px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #f0d8d4;">
        <div>
          <h1 style="font-size:22px;font-weight:700;letter-spacing:-0.02em;color:#261817;line-height:1.2">Good {{ greeting }},<br>Inspector 👋</h1>
          <p style="font-size:13px;color:#59413e;margin-top:6px;font-weight:500">Municipal Pavement Assessment</p>
        </div>
        <div style="width:60px;height:60px;border-radius:50%;background:#b02a26;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 4px 12px rgba(176,42,38,0.3);flex-shrink:0;">
          <span style="font-size:18px;font-weight:700;color:#fff;line-height:1">{{ today.day }}</span>
          <span style="font-size:10px;font-weight:600;color:#ffcbc5;letter-spacing:0.05em">{{ today.month }}</span>
        </div>
      </section>

      <!-- ── Stats Bar ── -->
      <section v-if="stats" style="padding:16px 16px 4px">
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
          <div class="stat-card">
            <span class="stat-value">{{ stats.total }}</span>
            <span class="stat-label">Total</span>
          </div>
          <div class="stat-card stat-danger">
            <span class="stat-value">{{ stats.high_severity }}</span>
            <span class="stat-label">High Risk</span>
          </div>
          <div class="stat-card stat-cost">
            <span class="stat-value" style="font-size:14px">₹{{ formatCost(stats.avg_cost_inr) }}</span>
            <span class="stat-label">Avg Cost</span>
          </div>
        </div>
      </section>

      <!-- ── Quick Actions ── -->
      <section style="padding:20px 16px 4px">
        <h2 style="font-size:18px;font-weight:600;letter-spacing:-0.01em;color:#261817;margin-bottom:14px">Quick Actions</h2>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
          <!-- New Assessment -->
          <router-link to="/assessment" style="display:block">
            <div class="snap-card" style="padding:16px;background:linear-gradient(145deg,#fff0ed,#ffe4e0);border-color:#f5c9c4;cursor:pointer">
              <div style="width:44px;height:44px;border-radius:50%;background:rgba(255,109,77,0.15);display:flex;align-items:center;justify-content:center;margin-bottom:14px">
                <span class="material-symbols-outlined ms-filled" style="color:#e65c00;font-size:22px">photo_camera</span>
              </div>
              <h3 style="font-size:15px;font-weight:700;color:#261817;margin-bottom:4px">New Assessment</h3>
              <p style="font-size:12px;color:#59413e;margin-bottom:12px;line-height:1.4">Snap &amp; analyze pavement</p>
              <div style="display:flex;justify-content:flex-end">
                <span class="material-symbols-outlined" style="color:#b02a26;font-size:20px">arrow_forward</span>
              </div>
            </div>
          </router-link>
          <!-- View Repairs -->
          <router-link to="/repairs" style="display:block">
            <div class="snap-card" style="padding:16px;background:linear-gradient(145deg,#f2dbf4,#ede0f0);border-color:#d6c0d7;cursor:pointer">
              <div style="width:44px;height:44px;border-radius:50%;background:rgba(106,89,109,0.15);display:flex;align-items:center;justify-content:center;margin-bottom:14px">
                <span class="material-symbols-outlined ms-filled" style="color:#655468;font-size:22px">build</span>
              </div>
              <h3 style="font-size:15px;font-weight:700;color:#261817;margin-bottom:4px">Work Orders</h3>
              <p style="font-size:12px;color:#59413e;margin-bottom:12px;line-height:1.4">View &amp; manage repairs</p>
              <div style="display:flex;justify-content:flex-end">
                <span class="material-symbols-outlined" style="color:#b02a26;font-size:20px">arrow_forward</span>
              </div>
            </div>
          </router-link>
        </div>
      </section>

      <!-- ── Recent Assessments ── -->
      <section style="padding:20px 16px 80px">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
          <h2 style="font-size:18px;font-weight:600;letter-spacing:-0.01em;color:#261817">Recent Assessments</h2>
          <router-link to="/assessment" style="font-size:13px;font-weight:600;color:#b02a26;text-decoration:none">See all</router-link>
        </div>

        <!-- Loading state -->
        <div v-if="loadingAssessments" style="text-align:center;padding:32px 0;color:#59413e">
          <div class="mini-spinner"></div>
          <p style="font-size:13px;margin-top:10px">Loading assessments...</p>
        </div>

        <!-- Empty state -->
        <div v-else-if="assessments.length === 0" class="empty-state">
          <span class="material-symbols-outlined" style="font-size:48px;color:#d6c0d7">add_road</span>
          <p style="font-weight:600;color:#3f2f50;margin-top:8px">No assessments yet</p>
          <p style="font-size:13px;color:#59413e">Submit your first pavement assessment to get started.</p>
          <router-link to="/assessment" class="empty-cta">Start Assessment →</router-link>
        </div>

        <!-- Real assessment cards -->
        <div v-else style="display:flex;flex-direction:column;gap:10px">
          <router-link
            v-for="item in assessments"
            :key="item.assessment_id"
            :to="'/assessment/' + item.assessment_id"
            style="text-decoration:none"
          >
            <div class="snap-card" style="padding:12px;display:flex;align-items:center;gap:12px;cursor:pointer">
              <!-- Severity icon circle -->
              <div
                class="severity-icon-circle"
                :class="item.severity_level.toLowerCase()"
                style="width:60px;height:60px;border-radius:12px;display:flex;align-items:center;justify-content:center;flex-shrink:0"
              >
                <span class="material-symbols-outlined" style="font-size:26px">add_road</span>
              </div>
              <div style="flex:1;min-width:0">
                <h4 style="font-size:15px;font-weight:700;color:#261817;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
                  {{ item.street_segment_id }}
                </h4>
                <div style="margin-top:4px">
                  <span class="pill" :class="severityPillClass(item.severity_level)">
                    Severity {{ severityScore(item.repair_priority) }}/5 · {{ capitalize(item.severity_level) }}
                  </span>
                </div>
                <p style="font-size:12px;color:#59413e;margin-top:4px">
                  {{ relativeTime(item.timestamp) }} · {{ item.inspector_name }}
                </p>
              </div>
              <span class="material-symbols-outlined" style="color:#59413e;font-size:20px;flex-shrink:0">chevron_right</span>
            </div>
          </router-link>
        </div>
      </section>

    </main>

    <!-- ── Bottom Nav ── -->
    <nav class="snap-nav">
      <div class="snap-nav-item active">
        <span class="material-symbols-outlined ms-filled" style="font-size:22px">dashboard</span>
        <span>Dashboard</span>
      </div>
      <router-link to="/assessment" class="snap-nav-item" style="color:#59413e;">
        <span class="material-symbols-outlined" style="font-size:22px">assessment</span>
        <span>Assess</span>
      </router-link>
      <router-link to="/repairs" class="snap-nav-item" style="color:#59413e;">
        <span class="material-symbols-outlined" style="font-size:22px">build</span>
        <span>Repairs</span>
      </router-link>
      <div class="snap-nav-item">
        <span class="material-symbols-outlined" style="font-size:22px">settings</span>
        <span>Settings</span>
      </div>
    </nav>

  </div>
</template>

<script>
import { assessmentAPI } from '@/services/api'

export default {
  name: 'Dashboard',
  data() {
    const now = new Date()
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    const hour = now.getHours()
    return {
      apiStatus: null,
      today: { day: now.getDate(), month: months[now.getMonth()] },
      greeting: hour < 12 ? 'Morning' : hour < 17 ? 'Afternoon' : 'Evening',
      assessments: [],
      stats: null,
      loadingAssessments: true,
    }
  },
  async mounted() {
    // Check API health
    try {
      const res = await assessmentAPI.getHealth()
      this.apiStatus = res.data.status === 'healthy'
    } catch {
      this.apiStatus = false
    }
    // Load real assessments and stats
    await this.loadDashboard()
  },
  methods: {
    async loadDashboard() {
      this.loadingAssessments = true
      try {
        const [listRes, statsRes] = await Promise.all([
          assessmentAPI.list(10),
          assessmentAPI.getStats(),
        ])
        this.assessments = listRes.data
        this.stats = statsRes.data
      } catch (err) {
        console.error('Dashboard load failed:', err)
        this.assessments = []
      } finally {
        this.loadingAssessments = false
      }
    },
    severityScore(priority) {
      return Math.max(1, Math.min(5, Math.ceil(priority / 2)))
    },
    severityPillClass(level) {
      const l = (level || '').toLowerCase()
      if (l === 'high') return 'pill-red'
      if (l === 'medium') return 'pill-amber'
      return 'pill-green'
    },
    capitalize(str) {
      if (!str) return ''
      return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
    },
    formatCost(cost) {
      if (!cost) return '0'
      if (cost >= 100000) return (cost / 100000).toFixed(1) + 'L'
      if (cost >= 1000) return (cost / 1000).toFixed(1) + 'K'
      return Math.round(cost).toString()
    },
    relativeTime(ts) {
      if (!ts) return ''
      const diff = Date.now() - new Date(ts).getTime()
      const mins = Math.floor(diff / 60000)
      if (mins < 60) return `${mins}m ago`
      const hrs = Math.floor(mins / 60)
      if (hrs < 24) return `${hrs}h ago`
      return `${Math.floor(hrs / 24)}d ago`
    },
  },
}
</script>

<style scoped>
.snap-topbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.status-dot.online { background: #2e7d32; }
.status-dot.offline { background: #b71c1c; }
.status-dot.checking { background: #f9a825; }

/* Stats Bar */
.stat-card {
  background: #fff;
  border: 1px solid #f0d8d4;
  border-radius: 14px;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.stat-card.stat-danger { border-color: #ffcdd2; background: #fff8f7; }
.stat-card.stat-cost { border-color: #e8eaf6; background: #f8f9ff; }
.stat-value {
  font-size: 20px;
  font-weight: 800;
  color: #261817;
  line-height: 1;
}
.stat-label {
  font-size: 11px;
  color: #59413e;
  font-weight: 500;
}

/* Severity icon circles */
.severity-icon-circle.high { background: #ffebee; color: #b71c1c; }
.severity-icon-circle.medium { background: #fff8e1; color: #a67c00; }
.severity-icon-circle.low { background: #e8f5e9; color: #2e7d32; }

/* Pills */
.pill { font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 20px; }
.pill-red { background: #ffebee; color: #b71c1c; }
.pill-amber { background: #fff8e1; color: #a67c00; }
.pill-green { background: #e8f5e9; color: #2e7d32; }

/* Empty state */
.empty-state {
  text-align: center;
  padding: 40px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.empty-cta {
  margin-top: 12px;
  background: #b02a26;
  color: white;
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
}

/* Mini spinner */
.mini-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #b02a26;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
