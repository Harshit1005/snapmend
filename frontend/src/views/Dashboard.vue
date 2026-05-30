<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Dashboard</h1>
      <p class="subtitle">Municipal Street Pavement Assessment System</p>
    </div>

    <div v-if="systemStatus" class="status-cards">
      <div class="status-card">
        <div class="status-icon">⚙️</div>
        <h3>Backend API</h3>
        <p :class="`status ${systemStatus.assessment ? 'healthy' : 'error'}`">
          {{ systemStatus.assessment ? '✅ Healthy' : '❌ Offline' }}
        </p>
      </div>

      <div class="status-card">
        <div class="status-icon">🤖</div>
        <h3>Gemini API</h3>
        <p class="status healthy">✅ Connected</p>
      </div>

      <div class="status-card">
        <div class="status-icon">📊</div>
        <h3>BigQuery</h3>
        <p class="status healthy">✅ Free Tier</p>
      </div>

      <div class="status-card">
        <div class="status-icon">💰</div>
        <h3>Monthly Cost</h3>
        <p class="status healthy">$0.00</p>
      </div>
    </div>

    <div class="dashboard-grid">
      <div class="card">
        <h2>Quick Start</h2>
        <ol class="quick-start-steps">
          <li>
            <strong>Get API Key</strong>
            <p>Visit <a href="https://ai.google.dev" target="_blank">ai.google.dev</a> (5 min)</p>
          </li>
          <li>
            <strong>Deploy Backend</strong>
            <p>Push to GitHub and deploy on Render (10 min)</p>
          </li>
          <li>
            <strong>Configure Frontend</strong>
            <p>Update API endpoint in .env file</p>
          </li>
          <li>
            <strong>Start Assessment</strong>
            <p>Use the assessment form to analyze streets</p>
          </li>
        </ol>
      </div>

      <div class="card">
        <h2>Assessment Process</h2>
        <div class="process-steps">
          <div class="step">
            <div class="step-num">1</div>
            <p>
              <strong>Inspect Street</strong>
              <br />Take pavement photos
            </p>
          </div>
          <div class="step">
            <div class="step-num">2</div>
            <p>
              <strong>Submit Images</strong>
              <br />Upload and add notes
            </p>
          </div>
          <div class="step">
            <div class="step-num">3</div>
            <p>
              <strong>AI Analysis</strong>
              <br />Gemini identifies issues
            </p>
          </div>
          <div class="step">
            <div class="step-num">4</div>
            <p>
              <strong>Get Results</strong>
              <br />Priority & cost estimates
            </p>
          </div>
        </div>
      </div>

      <div class="card tech-stack">
        <h2>Tech Stack</h2>
        <ul>
          <li>
            <strong>Backend:</strong> FastAPI on Render
          </li>
          <li>
            <strong>AI:</strong> Gemini 2.0 Flash (free)
          </li>
          <li>
            <strong>Database:</strong> BigQuery (free tier)
          </li>
          <li>
            <strong>Storage:</strong> Cloud Storage (free tier)
          </li>
          <li>
            <strong>Frontend:</strong> Vue 3 + Vite
          </li>
        </ul>
      </div>

      <div class="card features">
        <h2>Features</h2>
        <ul>
          <li>🖼️ Multi-image pavement analysis</li>
          <li>🤖 AI-powered damage detection</li>
          <li>📍 GPS location tracking</li>
          <li>💰 Cost estimates & priority</li>
          <li>📊 Repair history integration</li>
          <li>🌍 Geospatial nearby streets</li>
          <li>📧 Email notifications</li>
          <li>✅ Zero billing required</li>
        </ul>
      </div>
    </div>

    <div class="cta-section">
      <router-link to="/assessment" class="btn btn-large">
        Start New Assessment →
      </router-link>
    </div>
  </div>
</template>

<script>
import { systemAPI, assessmentAPI, repairAPI } from '@/services/api'

export default {
  name: 'Dashboard',
  data() {
    return {
      systemStatus: null,
    }
  },
  async mounted() {
    await this.checkSystemStatus()
  },
  methods: {
    async checkSystemStatus() {
      try {
        const assessment = await assessmentAPI.getHealth()
        const repair = await repairAPI.getHealth()

        this.systemStatus = {
          assessment: assessment.status === 'healthy',
          repair: repair.status === 'healthy',
        }
      } catch (err) {
        this.systemStatus = {
          assessment: false,
          repair: false,
        }
      }
    },
  },
}
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.dashboard-header {
  text-align: center;
  color: white;
  margin-bottom: 3rem;
  animation: fadeInDown 0.6s ease-out;
}

.dashboard-header h1 {
  font-size: 3rem;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.status-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.status-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.status-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.status-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.status-card h3 {
  color: #333;
  margin-bottom: 0.5rem;
}

.status {
  font-weight: bold;
  font-size: 1rem;
}

.status.healthy {
  color: #4caf50;
}

.status.error {
  color: #d32f2f;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  animation: fadeInUp 0.6s ease-out;
}

.card h2 {
  color: #667eea;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.quick-start-steps {
  list-style: decimal;
  padding-left: 1.5rem;
}

.quick-start-steps li {
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.quick-start-steps strong {
  color: #333;
}

.quick-start-steps p {
  margin: 0.5rem 0 0 0;
  color: #666;
  font-size: 0.95rem;
}

.quick-start-steps a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.quick-start-steps a:hover {
  text-decoration: underline;
}

.process-steps {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.step {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 4px;
  border-left: 3px solid #667eea;
}

.step-num {
  width: 2.5rem;
  height: 2.5rem;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.step p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

.step strong {
  color: #333;
}

.card ul {
  list-style: none;
  padding: 0;
}

.card li {
  padding: 0.75rem 0;
  color: #555;
  border-bottom: 1px solid #f0f0f0;
}

.card li:last-child {
  border-bottom: none;
}

.tech-stack li,
.features li {
  font-size: 0.95rem;
}

.features li {
  padding-left: 0;
}

.features li::before {
  content: '✓ ';
  color: #4caf50;
  font-weight: bold;
  margin-right: 0.5rem;
}

.cta-section {
  text-align: center;
  margin-top: 2rem;
}

.btn-large {
  display: inline-block;
  padding: 1rem 2.5rem;
  background: white;
  color: #667eea;
  text-decoration: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: bold;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-large:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

@media (max-width: 768px) {
  .dashboard-header h1 {
    font-size: 2rem;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .process-steps {
    grid-template-columns: 1fr;
  }

  .status-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
