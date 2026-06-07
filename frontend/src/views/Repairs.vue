<template>
  <div class="snap-screen">

    <!-- Top Bar -->
    <header class="snap-topbar">
      <div class="snap-topbar-brand">
        <span class="material-symbols-outlined ms-filled" style="color:#b02a26;font-size:24px">construction</span>
        <span class="brand-name">SnapMend</span>
      </div>
      <div class="snap-topbar-avatar">
        <span class="material-symbols-outlined" style="color:#59413e;font-size:20px">person</span>
      </div>
    </header>

    <main class="snap-main" style="padding-bottom:80px">

      <!-- Page Header -->
      <section style="background:linear-gradient(135deg,#ede0f0 0%,#f5f0f8 100%);padding:24px 16px 20px;border-bottom:1px solid #d6c0d7;">
        <h1 style="font-size:22px;font-weight:700;color:#261817;line-height:1.2">Work Orders</h1>
        <p style="font-size:13px;color:#59413e;margin-top:4px">Manage street repair assignments</p>
      </section>

      <!-- Filter Tabs -->
      <section style="padding:16px 16px 0">
        <div class="filter-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.value"
            class="filter-tab"
            :class="{ active: activeTab === tab.value }"
            @click="activeTab = tab.value"
          >{{ tab.label }}</button>
        </div>
      </section>

      <!-- Loading -->
      <div v-if="loading" style="text-align:center;padding:40px 0">
        <div class="mini-spinner"></div>
        <p style="font-size:13px;color:#59413e;margin-top:10px">Loading work orders...</p>
      </div>

      <!-- Empty -->
      <div v-else-if="filteredOrders.length === 0" class="empty-state">
        <span class="material-symbols-outlined" style="font-size:48px;color:#d6c0d7">build</span>
        <p style="font-weight:600;color:#3f2f50;margin-top:8px">
          {{ activeTab === 'ALL' ? 'No work orders yet' : `No ${activeTab.toLowerCase()} orders` }}
        </p>
        <p style="font-size:13px;color:#59413e">Create a work order from an assessment result.</p>
        <router-link to="/assessment" class="empty-cta">New Assessment →</router-link>
      </div>

      <!-- Work Order Cards -->
      <section v-else style="padding:16px;display:flex;flex-direction:column;gap:12px">
        <div
          v-for="order in filteredOrders"
          :key="order.work_order_id"
          class="snap-card work-order-card"
        >
          <!-- Header row -->
          <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:12px">
            <div>
              <p class="wo-id">{{ order.work_order_id }}</p>
              <h3 class="wo-street">{{ order.street_segment_id }}</h3>
            </div>
            <span class="status-badge" :class="order.status.toLowerCase()">{{ order.status }}</span>
          </div>

          <!-- Details grid -->
          <div class="wo-details-grid">
            <div class="wo-detail-item">
              <span class="detail-label">Priority</span>
              <span class="priority-pill" :class="priorityClass(order.priority_level)">{{ order.priority_level }}</span>
            </div>
            <div class="wo-detail-item">
              <span class="detail-label">Cost</span>
              <span class="detail-value">₹{{ formatCost(order.estimated_cost_inr) }}</span>
            </div>
            <div class="wo-detail-item">
              <span class="detail-label">Created</span>
              <span class="detail-value">{{ formatDate(order.created_date) }}</span>
            </div>
            <div class="wo-detail-item" v-if="order.assigned_crew">
              <span class="detail-label">Crew</span>
              <span class="detail-value">{{ order.assigned_crew }}</span>
            </div>
          </div>

          <!-- Notes -->
          <p v-if="order.notes" class="wo-notes">📝 {{ order.notes }}</p>

          <!-- Actions -->
          <div class="wo-actions">
            <button
              v-if="order.status === 'PENDING'"
              class="wo-btn wo-btn-start"
              @click="updateStatus(order, 'IN_PROGRESS')"
            >Mark In Progress</button>
            <button
              v-if="order.status === 'IN_PROGRESS'"
              class="wo-btn wo-btn-complete"
              @click="updateStatus(order, 'COMPLETED')"
            >Mark Complete</button>
            <span v-if="order.status === 'COMPLETED'" class="wo-done-label">✅ Completed</span>
          </div>
        </div>
      </section>

      <!-- Cost Summary -->
      <section v-if="!loading && workOrders.length > 0" style="padding:0 16px 16px">
        <div class="cost-summary">
          <span>{{ filteredOrders.length }} orders</span>
          <span>Total: ₹{{ totalCost }}</span>
        </div>
      </section>

    </main>

    <!-- Bottom Nav -->
    <nav class="snap-nav">
      <router-link to="/" class="snap-nav-item" style="color:#59413e;">
        <span class="material-symbols-outlined" style="font-size:22px">dashboard</span>
        <span>Dashboard</span>
      </router-link>
      <router-link to="/assessment" class="snap-nav-item" style="color:#59413e;">
        <span class="material-symbols-outlined" style="font-size:22px">assessment</span>
        <span>Assess</span>
      </router-link>
      <div class="snap-nav-item active">
        <span class="material-symbols-outlined ms-filled" style="font-size:22px">build</span>
        <span>Repairs</span>
      </div>
      <div class="snap-nav-item">
        <span class="material-symbols-outlined" style="font-size:22px">settings</span>
        <span>Settings</span>
      </div>
    </nav>

  </div>
</template>

<script>
import { repairAPI } from '@/services/api'

export default {
  name: 'Repairs',
  data() {
    return {
      workOrders: [],
      loading: true,
      activeTab: 'ALL',
      tabs: [
        { label: 'All', value: 'ALL' },
        { label: 'Pending', value: 'PENDING' },
        { label: 'In Progress', value: 'IN_PROGRESS' },
        { label: 'Completed', value: 'COMPLETED' },
      ],
    }
  },
  computed: {
    filteredOrders() {
      if (this.activeTab === 'ALL') return this.workOrders
      return this.workOrders.filter(o => o.status === this.activeTab)
    },
    totalCost() {
      const total = this.filteredOrders.reduce((s, o) => s + (o.estimated_cost_inr || 0), 0)
      return total.toLocaleString('en-IN')
    },
  },
  async mounted() {
    await this.loadOrders()
  },
  methods: {
    async loadOrders() {
      this.loading = true
      try {
        const res = await repairAPI.listWorkOrders(100)
        this.workOrders = res.data
      } catch (err) {
        console.error('Failed to load work orders:', err)
        this.workOrders = []
      } finally {
        this.loading = false
      }
    },
    updateStatus(order, newStatus) {
      // Optimistic UI update (no backend patch endpoint yet — just local state)
      order.status = newStatus
    },
    priorityClass(level) {
      const l = (level || '').toLowerCase()
      if (l === 'high') return 'priority-high'
      if (l === 'medium') return 'priority-medium'
      return 'priority-low'
    },
    formatCost(cost) {
      if (!cost) return '0'
      return Math.round(cost).toLocaleString('en-IN')
    },
    formatDate(ts) {
      if (!ts) return ''
      return new Date(ts).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
    },
  },
}
</script>

<style scoped>
/* Filter tabs */
.filter-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}
.filter-tab {
  padding: 6px 14px;
  border-radius: 20px;
  border: 1.5px solid #d6c0d7;
  background: white;
  font-size: 13px;
  font-weight: 600;
  color: #59413e;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
}
.filter-tab.active {
  background: #3f2f50;
  border-color: #3f2f50;
  color: white;
}

/* Work order card */
.work-order-card {
  padding: 16px;
}
.wo-id {
  font-size: 11px;
  color: #a0a0a0;
  font-family: monospace;
  margin-bottom: 2px;
}
.wo-street {
  font-size: 16px;
  font-weight: 700;
  color: #261817;
}
.status-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.status-badge.pending { background: #fff8e1; color: #a67c00; }
.status-badge.in_progress { background: #e3f2fd; color: #1565c0; }
.status-badge.completed { background: #e8f5e9; color: #2e7d32; }

.wo-details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 12px;
}
.wo-detail-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.detail-label {
  font-size: 11px;
  color: #a0a0a0;
  font-weight: 500;
}
.detail-value {
  font-size: 14px;
  font-weight: 600;
  color: #261817;
}
.priority-pill {
  font-size: 12px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 8px;
  width: fit-content;
}
.priority-high { background: #ffebee; color: #b71c1c; }
.priority-medium { background: #fff8e1; color: #a67c00; }
.priority-low { background: #e8f5e9; color: #2e7d32; }

.wo-notes {
  font-size: 13px;
  color: #59413e;
  padding: 8px 12px;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 12px;
}

.wo-actions { display: flex; gap: 8px; }
.wo-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}
.wo-btn-start { background: #e3f2fd; color: #1565c0; }
.wo-btn-complete { background: #e8f5e9; color: #2e7d32; }
.wo-done-label { font-size: 13px; color: #2e7d32; font-weight: 600; padding: 8px 0; }

/* Cost summary */
.cost-summary {
  display: flex;
  justify-content: space-between;
  background: #f8f9ff;
  border: 1px solid #e8eaf6;
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #261817;
}

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
  width: 28px; height: 28px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #b02a26;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>
