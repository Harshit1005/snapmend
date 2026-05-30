<template>
  <form @submit.prevent="submitAssessment" class="assessment-form">
    <fieldset>
      <legend>Street Information</legend>

      <div class="form-group">
        <label for="street_segment_id">Street Segment ID *</label>
        <input
          id="street_segment_id"
          v-model="form.street_segment_id"
          type="text"
          placeholder="e.g., STR-001-MAIN"
          required
        />
      </div>

      <div class="form-group">
        <label for="inspector_name">Inspector Name *</label>
        <input
          id="inspector_name"
          v-model="form.inspector_name"
          type="text"
          placeholder="Your full name"
          required
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="gps_latitude">GPS Latitude *</label>
          <input
            id="gps_latitude"
            v-model.number="form.gps_latitude"
            type="number"
            step="0.000001"
            placeholder="40.7128"
            required
          />
        </div>
        <div class="form-group">
          <label for="gps_longitude">GPS Longitude *</label>
          <input
            id="gps_longitude"
            v-model.number="form.gps_longitude"
            type="number"
            step="0.000001"
            placeholder="-74.0060"
            required
          />
        </div>
      </div>
    </fieldset>

    <fieldset>
      <legend>Assessment Details</legend>

      <div class="form-group">
        <label for="notes">Inspector Notes</label>
        <textarea
          id="notes"
          v-model="form.notes"
          placeholder="Observations, conditions, special notes..."
          rows="4"
        />
      </div>

      <div class="form-group">
        <label for="images">Pavement Photos * (JPG, PNG)</label>
        <input
          id="images"
          type="file"
          multiple
          accept="image/*"
          @change="handleImageSelect"
          required
        />
        <p v-if="selectedImages.length > 0" class="form-hint">
          {{ selectedImages.length }} image(s) selected
        </p>
      </div>
    </fieldset>

    <div class="form-actions">
      <button type="submit" :disabled="isLoading" class="btn btn-primary">
        {{ isLoading ? 'Analyzing...' : 'Analyze Pavement' }}
      </button>
      <button type="reset" class="btn btn-secondary" @click="resetForm">
        Clear Form
      </button>
    </div>

    <div v-if="error" class="alert alert-error">
      <strong>Error:</strong> {{ error }}
    </div>

    <div v-if="result" class="assessment-result">
      <h3>Assessment Results</h3>
      <div class="result-card">
        <div class="result-header">
          <span class="severity-badge" :class="`severity-${result.pavement_condition.severity_level.toLowerCase()}`">
            {{ result.pavement_condition.severity_level }}
          </span>
          <span class="priority">Priority: {{ result.pavement_condition.repair_priority }}/10</span>
        </div>

        <div class="result-details">
          <p>
            <strong>Repair Method:</strong> {{ result.pavement_condition.repair_method }}
          </p>
          <p v-if="result.pavement_condition.estimated_cost">
            <strong>Est. Cost:</strong> ${{ result.pavement_condition.estimated_cost.toFixed(2) }}
          </p>
          <p>
            <strong>Damage Types:</strong> {{ result.pavement_condition.damage_types.join(', ') }}
          </p>
        </div>

        <details class="raw-assessment">
          <summary>Full Assessment Report</summary>
          <pre>{{ result.raw_assessment }}</pre>
        </details>
      </div>
    </div>
  </form>
</template>

<script>
import { assessmentAPI } from '@/services/api'

export default {
  name: 'AssessmentForm',
  data() {
    return {
      form: {
        street_segment_id: '',
        inspector_name: '',
        gps_latitude: null,
        gps_longitude: null,
        notes: '',
      },
      selectedImages: [],
      isLoading: false,
      error: null,
      result: null,
    }
  },
  methods: {
    handleImageSelect(event) {
      this.selectedImages = Array.from(event.target.files)
      this.error = null
    },

    async submitAssessment() {
      if (!this.selectedImages.length) {
        this.error = 'Please select at least one image'
        return
      }

      this.isLoading = true
      this.error = null

      try {
        const response = await assessmentAPI.evaluate({
          ...this.form,
          images: this.selectedImages,
        })

        this.result = response.data
        this.$emit('assessment-complete', response.data)
      } catch (err) {
        this.error = err.response?.data?.detail || err.message || 'Assessment failed'
      } finally {
        this.isLoading = false
      }
    },

    resetForm() {
      this.form = {
        street_segment_id: '',
        inspector_name: '',
        gps_latitude: null,
        gps_longitude: null,
        notes: '',
      }
      this.selectedImages = []
      this.result = null
      this.error = null
    },
  },
}
</script>

<style scoped>
.assessment-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  margin: 0 auto;
}

fieldset {
  border: none;
  padding: 0;
  margin-bottom: 2rem;
}

legend {
  font-size: 1.2rem;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e0e0e0;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #333;
}

input,
textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-hint {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.5rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.btn {
  flex: 1;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.alert {
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 2rem;
}

.alert-error {
  background: #ffe0e0;
  color: #d32f2f;
  border-left: 4px solid #d32f2f;
}

.assessment-result {
  margin-top: 2rem;
}

.assessment-result h3 {
  color: #667eea;
  margin-bottom: 1rem;
}

.result-card {
  background: #f9f9f9;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.severity-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: bold;
  color: white;
}

.severity-low {
  background: #4caf50;
}

.severity-medium {
  background: #ff9800;
}

.severity-high {
  background: #d32f2f;
}

.priority {
  font-size: 0.9rem;
  color: #666;
}

.result-details {
  background: white;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.result-details p {
  margin: 0.5rem 0;
}

.raw-assessment {
  margin-top: 1rem;
}

.raw-assessment summary {
  cursor: pointer;
  color: #667eea;
  font-weight: 500;
  padding: 0.5rem;
}

.raw-assessment pre {
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1rem;
  margin-top: 0.5rem;
  overflow-x: auto;
  font-size: 0.85rem;
  max-height: 300px;
  overflow-y: auto;
}

@media (max-width: 600px) {
  .assessment-form {
    padding: 1rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }
}
</style>
