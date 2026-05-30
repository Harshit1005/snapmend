import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const assessmentAPI = {
  // Submit pavement assessment with images
  async evaluate(assessmentData) {
    const formData = new FormData()
    formData.append('street_segment_id', assessmentData.street_segment_id)
    formData.append('inspector_name', assessmentData.inspector_name)
    formData.append('gps_latitude', assessmentData.gps_latitude)
    formData.append('gps_longitude', assessmentData.gps_longitude)
    formData.append('notes', assessmentData.notes || '')

    // Add images
    if (assessmentData.images) {
      assessmentData.images.forEach((image) => {
        formData.append('images', image)
      })
    }

    return api.post('/api/assessment/evaluate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // Get assessment health status
  async getHealth() {
    return api.get('/api/assessment/health')
  },
}

export const repairAPI = {
  // Get repair history for a street
  async getHistory(street_segment_id, limit = 10) {
    return api.get(`/api/repair/history/${street_segment_id}`, {
      params: { limit },
    })
  },

  // Get nearby streets
  async getNearby(latitude, longitude, radiusMeters = 500, limit = 10) {
    return api.get('/api/repair/nearby', {
      params: {
        latitude,
        longitude,
        radius_meters: radiusMeters,
        limit,
      },
    })
  },

  // Create work order
  async createWorkOrder(street_segment_id, priority_level, estimated_cost) {
    return api.post('/api/repair/work-order', {
      street_segment_id,
      priority_level,
      estimated_cost,
    })
  },

  // Get repair health status
  async getHealth() {
    return api.get('/api/repair/health')
  },
}

export const systemAPI = {
  // Get API info
  async getInfo() {
    return api.get('/')
  },

  // Get system health
  async getHealth() {
    return api.get('/health')
  },
}

export default api
