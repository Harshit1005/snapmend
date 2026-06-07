<template>
  <div class="snap-screen">

    <!-- Top Bar -->
    <header class="snap-topbar">
      <div style="display:flex;align-items:center;gap:12px">
        <span
          class="material-symbols-outlined"
          style="color:#8e0e11;font-size:22px;cursor:pointer"
          @click="$router.push('/')"
        >arrow_back</span>
        <h1 style="font-size:18px;font-weight:700;color:#8e0e11;letter-spacing:-0.01em">
          New Assessment
        </h1>
      </div>
      <span class="material-symbols-outlined" style="color:#8e0e11;font-size:22px">more_vert</span>
    </header>

    <!-- Main content — the real assessment form -->
    <main class="snap-main" style="padding:16px;padding-bottom:80px">
      <AssessmentForm @assessment-complete="onAssessmentComplete" />
    </main>

    <!-- Bottom Nav -->
    <nav class="snap-nav">
      <router-link to="/" class="snap-nav-item" style="color:#59413e">
        <span class="material-symbols-outlined" style="font-size:22px">dashboard</span>
        <span>Dashboard</span>
      </router-link>
      <div class="snap-nav-item active">
        <span class="material-symbols-outlined ms-filled" style="font-size:22px">assessment</span>
        <span>Assess</span>
      </div>
      <router-link to="/repairs" class="snap-nav-item" style="color:#59413e">
        <span class="material-symbols-outlined" style="font-size:22px">build</span>
        <span>Repairs</span>
      </router-link>
      <div class="snap-nav-item">
        <span class="material-symbols-outlined" style="font-size:22px">settings</span>
        <span>Settings</span>
      </div>
    </nav>

  </div>
</template>

<script>
import AssessmentForm from '@/components/AssessmentForm.vue'

export default {
  name: 'Assessment',
  components: { AssessmentForm },
  methods: {
    onAssessmentComplete(result) {
      // When an assessment finishes, the form already shows the result inline.
      // Optionally navigate back to dashboard after a delay.
      console.log('Assessment complete:', result.assessment_id)
    },
  },
}
</script>
