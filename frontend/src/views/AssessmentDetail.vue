<template>
  <div class="snap-screen">
    <!-- Top App Bar -->
    <header class="snap-topbar">
      <div style="display:flex;align-items:center;gap:12px">
        <span class="material-symbols-outlined" style="cursor:pointer;color:#59413e" @click="$router.push('/')">arrow_back</span>
        <span class="brand-name" style="font-size:18px;font-weight:600;color:#261817">Assessment Details</span>
      </div>
    </header>

    <main class="snap-main" style="padding:16px;">
      <!-- Loading state -->
      <div v-if="loading" style="text-align:center;padding:40px 0;">
        <div class="mini-spinner"></div>
        <p style="font-size:13px;color:#59413e;margin-top:10px">Loading assessment...</p>
      </div>

      <!-- Error state -->
      <div v-else-if="error" style="text-align:center;padding:40px 0;color:#b02a26;">
        <span class="material-symbols-outlined" style="font-size:48px;">error</span>
        <p style="font-weight:600;margin-top:8px">{{ error }}</p>
      </div>

      <!-- Content -->
      <div v-else-if="assessment">
        <!-- Header -->
        <div style="margin-bottom:24px;">
          <h1 style="font-size:24px;font-weight:800;color:#261817;margin-bottom:8px">
            {{ assessment.street_segment_id }}
          </h1>
          <p style="font-size:13px;color:#59413e;">
            Inspected by <b>{{ assessment.inspector_name }}</b> on {{ new Date(assessment.timestamp).toLocaleString() }}
          </p>
        </div>

        <!-- Status & Progress -->
        <div class="snap-card" style="padding:16px;margin-bottom:16px;background:#f5fdf5;border-color:#c8e6c9;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <span class="material-symbols-outlined ms-filled" style="color:#2e7d32">check_circle</span>
            <span style="font-weight:700;color:#2e7d32;font-size:15px;">Assessment Complete</span>
          </div>
          <p style="font-size:13px;color:#2e7d32;">
            AI analysis generated successfully. Ready for repair work order generation.
          </p>
        </div>

        <!-- Metrics Grid -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:24px;">
          <div class="stat-box">
            <span class="label">Severity Level</span>
            <span class="value" :class="severityClass(assessment.pavement_condition.severity_level)">
              {{ assessment.pavement_condition.severity_level }}
            </span>
          </div>
          <div class="stat-box">
            <span class="label">Repair Priority</span>
            <span class="value">{{ assessment.pavement_condition.repair_priority }} / 10</span>
          </div>
          <div class="stat-box">
            <span class="label">Estimated Cost</span>
            <span class="value">₹{{ formatCost(assessment.pavement_condition.estimated_cost_inr) }}</span>
          </div>
          <div class="stat-box">
            <span class="label">Location</span>
            <span class="value" style="font-size:14px;word-break:break-all;">
              {{ assessment.gps_latitude }}, {{ assessment.gps_longitude }}
            </span>
          </div>
        </div>

        <!-- Detailed Assessment -->
        <h2 class="section-title">Analysis Results</h2>
        <div class="snap-card" style="padding:16px;margin-bottom:24px;">
          <p style="font-size:14px;color:#261817;line-height:1.6;margin-bottom:16px;">
            {{ assessment.pavement_condition.detailed_assessment }}
          </p>

          <h3 style="font-size:13px;font-weight:600;color:#59413e;margin-bottom:8px;text-transform:uppercase;">Identified Damage Types</h3>
          <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;">
            <span v-for="tag in assessment.pavement_condition.damage_types" :key="tag" class="damage-tag">
              {{ tag.replace('_', ' ') }}
            </span>
            <span v-if="!assessment.pavement_condition.damage_types.length" style="font-size:13px;color:#a0a0a0;">No damage types recorded</span>
          </div>

          <h3 style="font-size:13px;font-weight:600;color:#59413e;margin-bottom:8px;text-transform:uppercase;">Recommended Repair</h3>
          <p style="font-size:14px;color:#261817;line-height:1.5;">
            {{ assessment.pavement_condition.repair_method }}
          </p>
        </div>

        <!-- Field Notes -->
        <div v-if="assessment.notes" style="margin-bottom:24px;">
          <h2 class="section-title">Inspector Notes</h2>
          <div class="snap-card" style="padding:16px;background:#fafafa;">
            <p style="font-size:14px;color:#59413e;font-style:italic;">
              "{{ assessment.notes }}"
            </p>
          </div>
        </div>

        <!-- Images -->
        <div style="margin-bottom:40px;">
          <h2 class="section-title">Assessment Images</h2>
          <div v-if="assessment.photo_urls && assessment.photo_urls.length > 0" class="image-gallery">
            <img v-for="url in assessment.photo_urls" :key="url" :src="'http://localhost:8000' + url" class="gallery-image" />
          </div>
          <div v-else class="snap-card" style="padding:24px;text-align:center;background:#f5f5f5;border-style:dashed;">
            <span class="material-symbols-outlined" style="font-size:36px;color:#c0c0c0;margin-bottom:8px;">image</span>
            <p style="font-size:13px;color:#808080;">No images were saved for this assessment.</p>
          </div>
        </div>

      </div>
    </main>
  </div>
</template>

<script>
import { assessmentAPI } from '@/services/api'

export default {
  name: 'AssessmentDetail',
  data() {
    return {
      loading: true,
      error: null,
      assessment: null
    }
  },
  async mounted() {
    await this.fetchAssessment()
  },
  methods: {
    async fetchAssessment() {
      const id = this.$route.params.id
      try {
        this.loading = true
        const res = await assessmentAPI.getById(id)
        this.assessment = res.data
      } catch (err) {
        console.error('Failed to load assessment:', err)
        this.error = 'Assessment not found or failed to load.'
      } finally {
        this.loading = false
      }
    },
    formatCost(cost) {
      if (!cost) return '0'
      return cost.toLocaleString('en-IN')
    },
    severityClass(level) {
      const l = (level || '').toLowerCase()
      if (l === 'high') return 'text-red'
      if (l === 'medium') return 'text-amber'
      return 'text-green'
    }
  }
}
</script>

<style scoped>
.snap-topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  background: #fff8f7;
  border-bottom: 1px solid #e1bfba;
  display: flex;
  align-items: center;
  padding: 0 16px;
  height: 56px;
}
.stat-box {
  background: #fff;
  border: 1px solid #f0d8d4;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.stat-box .label {
  font-size: 11px;
  color: #59413e;
  font-weight: 600;
  text-transform: uppercase;
}
.stat-box .value {
  font-size: 16px;
  font-weight: 800;
  color: #261817;
}
.text-red { color: #b71c1c !important; }
.text-amber { color: #a67c00 !important; }
.text-green { color: #2e7d32 !important; }
.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #261817;
  margin-bottom: 12px;
}
.damage-tag {
  background: #fff0ee;
  color: #b02a26;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
  border: 1px solid #f5c9c4;
}
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
.image-gallery {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
.gallery-image {
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  object-fit: cover;
}
</style>
