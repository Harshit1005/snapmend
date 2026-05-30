<template>
  <div class="assessment-page">
    <div class="page-header">
      <h1>New Assessment</h1>
      <p>Analyze street pavement condition with AI-powered image recognition</p>
    </div>

    <AssessmentForm @assessment-complete="onAssessmentComplete" />

    <RepairHistory v-if="lastAssessmentId" :street-segment-id="lastAssessmentId" />
  </div>
</template>

<script>
import AssessmentForm from '@/components/AssessmentForm.vue'
import RepairHistory from '@/components/RepairHistory.vue'

export default {
  name: 'Assessment',
  components: {
    AssessmentForm,
    RepairHistory,
  },
  data() {
    return {
      lastAssessmentId: null,
    }
  },
  methods: {
    onAssessmentComplete(assessment) {
      this.lastAssessmentId = assessment.street_segment_id
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
    },
  },
}
</script>

<style scoped>
.assessment-page {
  animation: fadeIn 0.6s ease-out;
}

.page-header {
  text-align: center;
  color: white;
  margin-bottom: 3rem;
}

.page-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.page-header p {
  font-size: 1.1rem;
  opacity: 0.9;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 1.8rem;
  }

  .page-header p {
    font-size: 1rem;
  }
}
</style>
