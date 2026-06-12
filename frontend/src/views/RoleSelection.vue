<template>
  <div class="snap-screen">
    <div class="snap-topbar">
      <div class="snap-topbar-brand">
        <span class="material-symbols-outlined" style="color:#b02a26;">construction</span>
        <span class="brand-name">SnapMend</span>
      </div>
    </div>

    <div class="snap-main" style="display:flex; flex-direction:column; justify-content:center; padding: 24px;">
      <h1 style="font-size:24px; font-weight:700; margin-bottom: 8px; text-align: center;">Select Your Role</h1>
      <p style="color:#59413e; text-align:center; margin-bottom: 32px;">Choose your workspace to continue.</p>
      
      <div style="display:flex; flex-direction:column; gap: 16px;">
        <button @click="$router.push('/inspector')" class="snap-card" style="padding: 24px; display:flex; flex-direction:column; align-items:center; gap:12px; cursor:pointer; background:#fff0ee; border-color:#e1bfba;">
          <span class="material-symbols-outlined" style="font-size:48px; color:#b02a26;">photo_camera</span>
          <span style="font-size:18px; font-weight:600; color:#261817;">On-Site Inspector</span>
          <span style="font-size:13px; color:#59413e; text-align:center;">Submit pavement assessments and photos from the field.</span>
        </button>

        <button @click="$router.push('/supervisor')" class="snap-card" style="padding: 24px; display:flex; flex-direction:column; align-items:center; gap:12px; cursor:pointer; background:#f0efff; border-color:#d4d1f9;">
          <span class="material-symbols-outlined" style="font-size:48px; color:#4a3fb6;">assignment_ind</span>
          <span style="font-size:18px; font-weight:600; color:#261817;">Supervisor / Manager</span>
          <span style="font-size:13px; color:#59413e; text-align:center;">Review assessments and assign work orders to crews.</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RoleSelection'
}
</script>
