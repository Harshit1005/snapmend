<template>
  <div class="repair-history">
    <h2>Repair History</h2>

    <div v-if="loading" class="loading">
      <p>Loading repair history...</p>
    </div>

    <div v-else-if="error" class="alert alert-error">
      {{ error }}
    </div>

    <div v-else-if="repairs.length === 0" class="empty-state">
      <p>No repair history found for this street segment.</p>
    </div>

    <div v-else class="repairs-list">
      <div v-for="repair in repairs" :key="repair.repair_id" class="repair-card">
        <div class="repair-header">
          <h3>{{ repair.repair_type }}</h3>
          <span class="date">{{ formatDate(repair.date_completed) }}</span>
        </div>

        <div class="repair-details">
          <p>
            <strong>Repair ID:</strong> {{ repair.repair_id }}
          </p>
          <p>
            <strong>Cost:</strong> ${{ repair.cost.toFixed(2) }}
          </p>
          <p>
            <strong>Contractor:</strong> {{ repair.contractor }}
          </p>
          <p v-if="repair.notes">
            <strong>Notes:</strong> {{ repair.notes }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { repairAPI } from '@/services/api'

export default {
  name: 'RepairHistory',
  props: {
    streetSegmentId: {
      type: String,
      required: true,
    },
    limit: {
      type: Number,
      default: 10,
    },
  },
  data() {
    return {
      repairs: [],
      loading: false,
      error: null,
    }
  },
  watch: {
    streetSegmentId: {
      handler() {
        this.fetchHistory()
      },
      immediate: true,
    },
  },
  methods: {
    async fetchHistory() {
      this.loading = true
      this.error = null

      try {
        const response = await repairAPI.getHistory(this.streetSegmentId, this.limit)
        this.repairs = response.data
      } catch (err) {
        this.error = err.response?.data?.detail || err.message || 'Failed to load repair history'
      } finally {
        this.loading = false
      }
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    },
  },
}
</script>

<style scoped>
.repair-history {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-top: 2rem;
}

h2 {
  color: #513e65;
  margin-bottom: 1.5rem;
}

.loading,
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.alert-error {
  padding: 1rem;
  background: #ffe0e0;
  color: #d32f2f;
  border-radius: 8px;
  border-left: 4px solid #d32f2f;
}

.repairs-list {
  display: grid;
  gap: 1rem;
}

.repair-card {
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
  background: #f8f9fa;
  transition: all 0.2s;
}

.repair-card:hover {
  box-shadow: 0 4px 12px rgba(81, 62, 101, 0.1);
  border-color: #513e65;
}

.repair-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 0.5rem;
}

.repair-header h3 {
  color: #212529;
  font-size: 1.1rem;
  margin: 0;
  font-weight: 700;
  text-transform: capitalize;
}

.date {
  color: #6c757d;
  font-size: 0.9rem;
}

.repair-details {
  font-size: 0.95rem;
}

.repair-details p {
  margin: 0.5rem 0;
  color: #495057;
}

strong {
  color: #212529;
}
</style>
