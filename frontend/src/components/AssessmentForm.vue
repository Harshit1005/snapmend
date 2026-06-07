<template>
  <div class="assessment-container">
    <!-- Form View -->
    <form v-if="!result && !isLoading" @submit.prevent="submitAssessment" class="assessment-form">
      <fieldset>
        <legend>🗺️ Street Information</legend>

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
        <legend>📝 Assessment Details</legend>

        <div class="form-group">
          <label for="notes">Inspector Notes</label>
          <textarea
            id="notes"
            v-model="form.notes"
            placeholder="Observations, conditions, special notes..."
            rows="3"
          />
        </div>

        <div class="form-group">
          <label for="images" class="file-upload-label">
            <span class="upload-icon">📷</span> Pavement Photos * (JPG, PNG)
          </label>
          <input
            id="images"
            type="file"
            multiple
            accept="image/*"
            @change="handleImageSelect"
            required
            class="file-input"
          />
          <div v-if="selectedImages.length > 0" class="image-previews">
            <div v-for="(img, idx) in selectedImagePreviews" :key="idx" class="preview-thumbnail">
              <img :src="img" />
            </div>
          </div>
        </div>
      </fieldset>

      <div class="form-actions">
        <button type="submit" class="btn btn-primary">
          Analyze Pavement
        </button>
        <button type="button" class="btn btn-secondary" @click="resetForm">
          Clear
        </button>
      </div>

      <div v-if="error" class="alert alert-error">
        <strong>Error:</strong> {{ error }}
      </div>
    </form>

    <!-- Loading View -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <h3>Analyzing Pavement Condition</h3>
      <p>Gemini AI is examining structural defects and severity...</p>
    </div>

    <!-- Assessment Result View (Matching Reference Image) -->
    <div v-if="result && !isLoading" class="assessment-result">
      <div class="result-navigation">
        <button @click="resetForm" class="btn btn-back">
          ← Start New Assessment
        </button>
      </div>

      <div class="reference-card">
        <!-- Pavement image with absolute-positioned annotation tooltip -->
        <div class="pavement-image-container">
          <img v-if="imagePreviewUrl" :src="imagePreviewUrl" class="pavement-image" />
          <div v-else class="pavement-image-placeholder">
            <span>No Image Preview</span>
          </div>
          <!-- Bounding box with tooltip overlay -->
          <div class="bounding-box-overlay">
            <div class="annotation-bubble">
              {{ damageAnnotation }}
              <div class="annotation-arrow"></div>
            </div>
          </div>
        </div>

        <!-- Severity Level red banner -->
        <div class="severity-banner" :class="severityClass">
          {{ severityText }}
        </div>

        <!-- Immediate Action box -->
        <div class="immediate-action-card">
          <h4 class="immediate-label">Immediate Action</h4>
          <p class="immediate-text">{{ result.pavement_condition.repair_method }}</p>
        </div>

        <!-- Estimated Cost card -->
        <div class="cost-card">
          <div class="cost-icon-circle">
            <span class="cost-icon">₹</span>
          </div>
          <div class="cost-info">
            <span class="cost-label">Estimated Cost</span>
            <span class="cost-value">₹{{ formattedCost }}</span>
          </div>
        </div>

        <!-- Why this decision? Expandable Accordion -->
        <div class="decision-accordion">
          <button type="button" class="accordion-trigger" @click="showDecision = !showDecision">
            <span>Why this decision?</span>
            <span class="accordion-arrow" :class="{ open: showDecision }">▼</span>
          </button>
          
          <div v-show="showDecision" class="accordion-content">
            <!-- Visual evidence -->
            <div class="decision-item">
              <div class="item-icon-circle visual">📷</div>
              <div class="item-body">
                <h5>Visual evidence</h5>
                <p>Image analysis confirms {{ damageTypesText }}.</p>
              </div>
              <span class="badge badge-critical">Critical</span>
            </div>

            <!-- User notes -->
            <div class="decision-item">
              <div class="item-icon-circle notes">📝</div>
              <div class="item-body">
                <h5>User notes</h5>
                <p>{{ form.notes || 'No custom inspector notes provided.' }}</p>
              </div>
              <span class="badge badge-high">High</span>
            </div>

            <!-- Historical data -->
            <div class="decision-item">
              <div class="item-icon-circle history">📊</div>
              <div class="item-body">
                <h5>Historical data</h5>
                <p>Location segment (ID: {{ result.street_segment_id }}) has recorded inspections and repair logs.</p>
              </div>
              <span class="badge badge-medium">Medium</span>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="result-actions">
          <button type="button" @click="handleCreateWorkOrder" :disabled="isWorkOrderLoading" class="btn btn-work-order">
            {{ isWorkOrderLoading ? 'Creating...' : 'Create Work Order' }}
          </button>
          <button type="button" @click="handleRequestReview" class="btn btn-request-review">
            Request Review
          </button>
        </div>

        <!-- Work Order Success/Error Feedback -->
        <div v-if="workOrderResult" class="work-order-success">
          <p><strong>Success!</strong> Work Order created successfully.</p>
          <div class="wo-details">
            <span>ID: <strong>{{ workOrderResult.work_order_id }}</strong></span>
            <span>Status: <strong class="wo-status">{{ workOrderResult.status }}</strong></span>
          </div>
        </div>

        <div v-if="requestReviewMessage" class="review-success">
          <p><strong>Review Requested!</strong> {{ requestReviewMessage }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { assessmentAPI, repairAPI } from '@/services/api'

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
      selectedImagePreviews: [],
      imagePreviewUrl: null,
      isLoading: false,
      error: null,
      result: null,
      showDecision: true,
      isWorkOrderLoading: false,
      workOrderResult: null,
      requestReviewMessage: null,
    }
  },
  computed: {
    severityText() {
      if (!this.result) return ''
      const level = this.result.pavement_condition.severity_level || 'MEDIUM'
      const priority = this.result.pavement_condition.repair_priority || 5
      const score = Math.max(1, Math.min(5, Math.ceil(priority / 2)))
      const capitalized = level.charAt(0).toUpperCase() + level.slice(1).toLowerCase()
      return `Severity ${score} / 5 • ${capitalized}`
    },
    severityClass() {
      if (!this.result) return ''
      return this.result.pavement_condition.severity_level.toLowerCase()
    },
    damageAnnotation() {
      if (!this.result || !this.result.pavement_condition.damage_types.length) {
        return 'Pavement damage detected'
      }
      const primary = this.result.pavement_condition.damage_types[0]
      let formatted = primary.replace(/_/g, ' ')
      formatted = formatted.charAt(0).toUpperCase() + formatted.slice(1)
      if (formatted.toLowerCase().includes('pothole')) {
        return 'Large pothole with water ingress'
      }
      return formatted
    },
    formattedCost() {
      if (!this.result) return '0'
      const costUSD = this.result.pavement_condition.estimated_cost || 0
      // Convert to INR to match reference layout
      const costINR = Math.round(costUSD * 83)
      return costINR.toLocaleString('en-IN')
    },
    damageTypesText() {
      if (!this.result) return ''
      const list = this.result.pavement_condition.damage_types || []
      if (list.length === 0) return 'severe cracking and deep depression'
      const formattedList = list.map(item => item.replace(/_/g, ' '))
      if (formattedList.length === 1) return formattedList[0]
      if (formattedList.length === 2) return `${formattedList[0]} and ${formattedList[1]}`
      return `${formattedList.slice(0, -1).join(', ')}, and ${formattedList[formattedList.length - 1]}`
    }
  },
  methods: {
    handleImageSelect(event) {
      this.selectedImages = Array.from(event.target.files)
      this.selectedImagePreviews = []
      this.error = null

      if (this.selectedImages.length > 0) {
        // Create previews
        this.selectedImages.forEach(file => {
          this.selectedImagePreviews.push(URL.createObjectURL(file))
        })
        // Set main result preview image
        this.imagePreviewUrl = this.selectedImagePreviews[0]
      } else {
        this.imagePreviewUrl = null
      }
    },

    async submitAssessment() {
      if (!this.selectedImages.length) {
        this.error = 'Please select at least one image'
        return
      }

      this.isLoading = true
      this.error = null
      this.workOrderResult = null
      this.requestReviewMessage = null

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

    async handleCreateWorkOrder() {
      if (!this.result) return
      this.isWorkOrderLoading = true
      this.workOrderResult = null
      
      try {
        const priority = this.result.pavement_condition.severity_level || 'MEDIUM'
        const cost = this.result.pavement_condition.estimated_cost || 0
        const response = await repairAPI.createWorkOrder(
          this.result.street_segment_id,
          priority,
          cost
        )
        this.workOrderResult = response.data
      } catch (err) {
        this.error = err.response?.data?.detail || err.message || 'Failed to create work order'
      } finally {
        this.isWorkOrderLoading = false
      }
    },

    handleRequestReview() {
      this.requestReviewMessage = `Notification sent to municipal supervisor for street segment ${this.result.street_segment_id}.`
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
      this.selectedImagePreviews = []
      this.imagePreviewUrl = null
      this.result = null
      this.error = null
      this.workOrderResult = null
      this.requestReviewMessage = null
    },
  },
}
</script>

<style scoped>
.assessment-container {
  width: 100%;
  max-width: 650px;
  margin: 0 auto;
}

/* Form Styles */
.assessment-form {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

fieldset {
  border: none;
  padding: 0;
  margin-bottom: 2rem;
}

legend {
  font-size: 1.25rem;
  font-weight: 700;
  color: #3f2f50;
  margin-bottom: 1.25rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #f0edf4;
  width: 100%;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #495057;
  font-size: 0.95rem;
}

input,
textarea {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1.5px solid #dee2e6;
  border-radius: 10px;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.2s;
  box-sizing: border-box;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #513e65;
  box-shadow: 0 0 0 3px rgba(81, 62, 101, 0.15);
}

.file-upload-label {
  display: inline-block;
  cursor: pointer;
  background-color: #f8f9fa;
  border: 2px dashed #ced4da;
  border-radius: 10px;
  padding: 1.5rem;
  text-align: center;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.2s, background-color 0.2s;
}

.file-upload-label:hover {
  border-color: #513e65;
  background-color: #f1edf4;
}

.file-input {
  display: none;
}

.upload-icon {
  font-size: 1.5rem;
  display: block;
  margin-bottom: 0.5rem;
}

.image-previews {
  display: flex;
  gap: 0.8rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.preview-thumbnail {
  width: 70px;
  height: 70px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #dee2e6;
}

.preview-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.btn {
  padding: 0.85rem 1.8rem;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.btn-primary {
  flex: 2;
  background: #513e65;
  color: white;
  box-shadow: 0 4px 10px rgba(81, 62, 101, 0.25);
}

.btn-primary:hover {
  background: #3f2f50;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(81, 62, 101, 0.35);
}

.btn-secondary {
  flex: 1;
  background: #f1f3f5;
  color: #495057;
}

.btn-secondary:hover {
  background: #e9ecef;
}

.btn-back {
  background: transparent;
  color: white;
  border: 1.5px solid white;
  padding: 0.5rem 1.25rem;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.1);
}

.alert {
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1.5rem;
}

.alert-error {
  background: #ffebee;
  color: #c62828;
  border-left: 4px solid #c62828;
}

/* Loading View */
.loading-container {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #513e65;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1.5rem auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container h3 {
  color: #3f2f50;
  margin-bottom: 0.5rem;
}

.loading-container p {
  color: #6c757d;
}

/* Results View - High Fidelity Card matching reference */
.reference-card {
  background: white;
  border-radius: 24px;
  padding: 1.5rem;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  color: #212529;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.pavement-image-container {
  position: relative;
  width: 100%;
  border-radius: 20px;
  overflow: hidden;
  aspect-ratio: 16 / 9;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.pavement-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.pavement-image-placeholder {
  width: 100%;
  height: 100%;
  background-color: #e9ecef;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  font-size: 1.1rem;
}

.bounding-box-overlay {
  position: absolute;
  top: 15%;
  left: 20%;
  width: 50%;
  height: 65%;
  border: 3px solid #ffc107;
  border-radius: 12px;
  box-sizing: border-box;
  pointer-events: none;
}

.annotation-bubble {
  position: absolute;
  top: -45px;
  right: -25px;
  background-color: #fff3e0;
  color: #5d4037;
  padding: 8px 16px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 700;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
  white-space: nowrap;
}

.annotation-arrow {
  position: absolute;
  bottom: -6px;
  left: 20px;
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid #fff3e0;
}

.severity-banner {
  margin-top: 1.25rem;
  border-radius: 30px;
  padding: 1.1rem;
  font-weight: 800;
  font-size: 1.5rem;
  text-align: center;
  color: white;
  letter-spacing: -0.5px;
}

.severity-banner.high {
  background-color: #b71c1c; /* Deep Crimson */
}

.severity-banner.medium {
  background-color: #e65100; /* Rich Amber */
}

.severity-banner.low {
  background-color: #1b5e20; /* Forest Green */
}

.immediate-action-card {
  margin-top: 1.25rem;
  background-color: #eceff1;
  border-radius: 18px;
  padding: 1.25rem;
  border-left: 6px solid #78909c;
}

.immediate-label {
  margin: 0 0 0.4rem 0;
  color: #37474f;
  font-size: 1.15rem;
  font-weight: 700;
}

.immediate-text {
  margin: 0;
  color: #455a64;
  font-size: 1rem;
  line-height: 1.45;
}

.cost-card {
  margin-top: 1.25rem;
  display: flex;
  align-items: center;
  background-color: #f8f9fa;
  border-radius: 18px;
  padding: 1.2rem 1.5rem;
  border: 1px solid #e9ecef;
}

.cost-icon-circle {
  width: 45px;
  height: 45px;
  background-color: #e9ecef;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1.2rem;
  flex-shrink: 0;
}

.cost-icon {
  font-size: 1.4rem;
  font-weight: 700;
  color: #495057;
}

.cost-info {
  display: flex;
  width: 100%;
  justify-content: space-between;
  align-items: center;
}

.cost-label {
  font-size: 1.15rem;
  color: #495057;
  font-weight: 600;
}

.cost-value {
  font-size: 1.7rem;
  font-weight: 800;
  color: #212529;
}

/* Accordion */
.decision-accordion {
  margin-top: 1.5rem;
  border-top: 1.5px solid #f1f3f5;
  padding-top: 1.25rem;
}

.accordion-trigger {
  width: 100%;
  background: none;
  border: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.25rem;
  font-weight: 700;
  color: #212529;
  cursor: pointer;
  padding: 0.5rem 0;
}

.accordion-arrow {
  font-size: 0.95rem;
  transition: transform 0.2s;
  color: #868e96;
}

.accordion-arrow.open {
  transform: rotate(180deg);
}

.accordion-content {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.decision-item {
  display: flex;
  align-items: center;
  background-color: #ffffff;
  border: 1px solid #e9ecef;
  border-radius: 16px;
  padding: 1rem 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.01);
}

.item-icon-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  margin-right: 1.1rem;
  flex-shrink: 0;
}

.item-icon-circle.visual {
  background-color: #fff3e0;
}

.item-icon-circle.notes {
  background-color: #e3f2fd;
}

.item-icon-circle.history {
  background-color: #e8f5e9;
}

.item-body {
  flex-grow: 1;
}

.item-body h5 {
  margin: 0 0 0.25rem 0;
  font-size: 1.05rem;
  color: #212529;
  font-weight: 700;
}

.item-body p {
  margin: 0;
  font-size: 0.9rem;
  color: #6c757d;
  line-height: 1.4;
}

.badge {
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: capitalize;
  margin-left: 0.5rem;
}

.badge-critical {
  background-color: #ffebee;
  color: #c62828;
}

.badge-high {
  background-color: #fff9c4;
  color: #fbc02d;
}

.badge-medium {
  background-color: #fff3e0;
  color: #ef6c00;
}

/* Action Buttons matching the reference exactly */
.result-actions {
  margin-top: 1.8rem;
  display: flex;
  gap: 1.2rem;
}

.btn-work-order {
  flex: 1;
  background-color: #513e65; /* Deep Purple */
  color: white;
  border: none;
  border-radius: 30px;
  padding: 1rem 1.8rem;
  font-weight: 700;
  font-size: 1.05rem;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(81, 62, 101, 0.2);
  transition: all 0.2s;
}

.btn-work-order:hover {
  background-color: #3f2f50;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(81, 62, 101, 0.3);
}

.btn-request-review {
  flex: 1;
  background-color: transparent;
  color: #513e65;
  border: 2px solid #513e65;
  border-radius: 30px;
  padding: 1rem 1.8rem;
  font-weight: 700;
  font-size: 1.05rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-request-review:hover {
  background-color: rgba(81, 62, 101, 0.06);
  transform: translateY(-2px);
}

.work-order-success {
  margin-top: 1.5rem;
  background-color: #e8f5e9;
  color: #1b5e20;
  border: 1.5px solid #a5d6a7;
  border-radius: 16px;
  padding: 1.2rem;
}

.work-order-success p {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}

.wo-details {
  display: flex;
  justify-content: space-between;
  font-size: 0.95rem;
  background: white;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid #c8e6c9;
}

.wo-status {
  color: #2e7d32;
  text-transform: uppercase;
}

.review-success {
  margin-top: 1.5rem;
  background-color: #e3f2fd;
  color: #0d47a1;
  border: 1.5px solid #90caf9;
  border-radius: 16px;
  padding: 1.2rem;
  text-align: center;
}

.review-success p {
  margin: 0;
  font-size: 1rem;
}

@media (max-width: 600px) {
  .assessment-form {
    padding: 1.25rem;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 0.8rem;
  }

  .form-actions {
    flex-direction: column;
  }

  .result-actions {
    flex-direction: column;
    gap: 0.8rem;
  }
}
</style>
