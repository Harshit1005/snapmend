import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60s — Gemini can be slow on free tier
})

export const assessmentAPI = {
  /** Submit a new pavement assessment with image files */
  async evaluate(assessmentData) {
    const formData = new FormData()
    formData.append('street_segment_id', assessmentData.street_segment_id)
    formData.append('inspector_name', assessmentData.inspector_name)
    formData.append('gps_latitude', assessmentData.gps_latitude)
    formData.append('gps_longitude', assessmentData.gps_longitude)
    formData.append('notes', assessmentData.notes || '')
    if (assessmentData.images) {
      assessmentData.images.forEach((image) => formData.append('images', image))
    }
    return api.post('/api/assessment/evaluate', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  /** List all past assessments (for Dashboard feed) */
  async list(limit = 20) {
    return api.get('/api/assessment/list', { params: { limit } })
  },

  /** Get aggregate stats for Dashboard header */
  async getStats() {
    return api.get('/api/assessment/stats')
  },

  /** Get a single assessment by ID */
  async getById(assessmentId) {
    return api.get(`/api/assessment/${assessmentId}`)
  },

  /** Health check */
  async getHealth() {
    return api.get('/api/assessment/health')
  },
}


export const repairAPI = {
  /** Get repair history for a street segment */
  async getHistory(streetSegmentId, limit = 10) {
    return api.get(`/api/repair/history/${streetSegmentId}`, { params: { limit } })
  },

  /** Get nearby streets */
  async getNearby(latitude, longitude, radiusMeters = 500, limit = 10) {
    return api.get('/api/repair/nearby', {
      params: { latitude, longitude, radius_meters: radiusMeters, limit },
    })
  },

  /** Create a work order — sends JSON body */
  async createWorkOrder(streetSegmentId, priorityLevel, estimatedCost, assessmentId = null, notes = null) {
    return api.post('/api/repair/work-order', {
      street_segment_id: streetSegmentId,
      priority_level: priorityLevel,
      estimated_cost: estimatedCost,
      assessment_id: assessmentId,
      notes: notes,
    })
  },

  /** List all work orders */
  async listWorkOrders(limit = 50) {
    return api.get('/api/repair/work-orders', { params: { limit } })
  },

  /** Health check */
  async getHealth() {
    return api.get('/api/repair/health')
  },
}

export const systemAPI = {
  async getInfo() { return api.get('/') },
  async getHealth() { return api.get('/health') },
}

export default api
