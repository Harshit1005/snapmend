<template>
  <div class="snap-screen">
    <div class="snap-topbar" style="background:#f0efff; border-color:#d4d1f9;">
      <div class="snap-topbar-brand">
        <span class="material-symbols-outlined" style="color:#4a3fb6;">assignment_ind</span>
        <span class="brand-name" style="color:#4a3fb6;">Supervisor Portal</span>
      </div>
      <button @click="$router.push('/')" style="background:none; border:none; cursor:pointer;">
        <span class="material-symbols-outlined">logout</span>
      </button>
    </div>

    <div class="snap-main" style="padding: 16px;">
      <h2 style="font-size: 18px; font-weight: 600; margin-bottom: 16px;">All Pending Assessments</h2>
      
      <div v-if="loading" style="text-align:center; padding: 32px; color:#59413e;">Loading...</div>
      <div v-else-if="assessments.length === 0" style="text-align:center; padding: 32px; color:#59413e;">No assessments submitted yet.</div>
      
      <div v-else style="display:flex; flex-direction:column; gap: 12px;">
        <div v-for="assessment in assessments" :key="assessment.assessment_id" class="snap-card" style="padding: 16px;">
          <div style="display:flex; justify-content:space-between; margin-bottom: 8px;">
            <span style="font-weight: 600; font-size: 15px;">{{ assessment.street_segment_id }}</span>
            <span :class="['pill', severityClass(assessment.severity_level)]">{{ assessment.severity_level }}</span>
          </div>
          <div style="font-size: 13px; color: #59413e; margin-bottom: 4px;">
            <span class="material-symbols-outlined" style="font-size: 14px;">person</span>
            {{ assessment.inspector_name }}
          </div>
          <div style="font-size: 13px; color: #59413e; margin-bottom: 12px;">
            <span class="material-symbols-outlined" style="font-size: 14px;">schedule</span>
            {{ new Date(assessment.timestamp).toLocaleString() }}
          </div>
          
          <div style="display:flex; justify-content:space-between; align-items:center; border-top: 1px solid #e1bfba; padding-top: 12px;">
            <div style="font-size: 13px; font-weight: 600;">Est. Cost: ₹{{ formatCostRange(assessment.estimated_cost_inr) }}</div>
            <button @click="createWorkOrder(assessment)" style="background:#4a3fb6; color:white; border:none; border-radius: 8px; padding: 8px 16px; font-weight: 600; font-size: 13px; cursor:pointer;">
              Assign Work
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { assessmentAPI, repairAPI } from '@/services/api';

export default {
  name: 'SupervisorDashboard',
  data() {
    return {
      assessments: [],
      loading: true
    }
  },
  async created() {
    await this.fetchAssessments();
  },
  methods: {
    severityClass(severity) {
      if (severity === 'HIGH') return 'pill-red';
      if (severity === 'MEDIUM') return 'pill-amber';
      return 'pill-green';
    },
    formatCostRange(cost) {
      if (!cost) return '0'
      const lower = Math.round((cost * 0.85) / 100) * 100
      const upper = Math.round((cost * 1.15) / 100) * 100
      return `${lower.toLocaleString('en-IN')} - ${upper.toLocaleString('en-IN')}`
    },
    async fetchAssessments() {
      this.loading = true;
      try {
        const response = await assessmentAPI.list(50);
        this.assessments = response.data;
      } catch (err) {
        console.error("Failed to fetch", err);
        alert("Failed to load assessments from Supabase.");
      } finally {
        this.loading = false;
      }
    },
    async createWorkOrder(assessment) {
      const crew = prompt(`Assign work for ${assessment.street_segment_id} to which crew?`);
      if (!crew) return;
      
      try {
        await repairAPI.createWorkOrder(
          assessment.street_segment_id,
          assessment.severity_level,
          assessment.estimated_cost_inr / 83.5, // Convert back to USD for internal DB structure
          assessment.assessment_id,
          `Assigned to ${crew}`
        );
        alert(`Work order assigned to ${crew}!`);
      } catch (err) {
        console.error(err);
        alert("Failed to assign work order");
      }
    }
  }
}
</script>
