<template>
  <div class="snap-screen">

    <!-- ── Top App Bar ── -->
    <header class="snap-topbar">
      <div style="display:flex;align-items:center;gap:12px">
        <span class="material-symbols-outlined" style="color:#8e0e11;font-size:22px;cursor:pointer" @click="$router.push('/')">arrow_back</span>
        <h1 style="font-size:18px;font-weight:700;color:#8e0e11;letter-spacing:-0.01em">Pothole Assessment</h1>
      </div>
      <span class="material-symbols-outlined" style="color:#8e0e11;font-size:22px;cursor:pointer">more_vert</span>
    </header>

    <!-- ── Scrollable Content ── -->
    <main class="snap-main" style="padding:16px;display:flex;flex-direction:column;gap:14px">

      <!-- 1. Hero Image with Frosted Tooltip -->
      <section style="position:relative;width:100%;aspect-ratio:16/9;border-radius:16px;overflow:hidden;box-shadow:0 4px 16px rgba(140,60,40,0.12)">
        <img src="@/assets/reference.png" alt="Pothole with water ingress" style="width:100%;height:100%;object-fit:cover;display:block" />
        <!-- Frosted Glass Tooltip -->
        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);pointer-events:none">
          <div style="position:relative;background:rgba(255,248,247,0.90);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border:1px solid rgba(225,191,186,0.6);border-radius:12px;padding:8px 14px;display:flex;align-items:center;gap:8px;white-space:nowrap;box-shadow:0 2px 12px rgba(0,0,0,0.1)">
            <span class="pulse-red" style="width:7px;height:7px;border-radius:50%;background:#b02a26;display:inline-block;flex-shrink:0"></span>
            <span style="font-size:12px;font-weight:500;color:#261817">Large pothole with water ingress</span>
            <!-- Triangle pointer -->
            <span style="position:absolute;bottom:-6px;left:50%;transform:translateX(-50%) rotate(45deg);width:11px;height:11px;background:rgba(255,248,247,0.9);border-right:1px solid rgba(225,191,186,0.6);border-bottom:1px solid rgba(225,191,186,0.6)"></span>
          </div>
        </div>
      </section>

      <!-- 2. Severity Banner -->
      <button style="width:100%;height:50px;background:#b02a26;color:#fff;border:none;border-radius:9999px;font-size:13px;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;cursor:pointer;box-shadow:0 4px 14px rgba(176,42,38,0.35);transition:transform 0.12s,box-shadow 0.12s;display:flex;align-items:center;justify-content:center;gap:8px"
        @mousedown="e=>e.currentTarget.style.transform='scale(0.97)'"
        @mouseup="e=>e.currentTarget.style.transform='scale(1)'">
        <span class="material-symbols-outlined ms-filled" style="font-size:18px;color:#ffb4ab">warning</span>
        Severity 4 / 5 &middot; High
      </button>

      <!-- 3. Immediate Action Card -->
      <div style="background:#fff0ee;border:1px solid #e1bfba;border-radius:14px;padding:16px">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
          <span class="material-symbols-outlined ms-filled" style="color:#b02a26;font-size:18px">warning_amber</span>
          <span style="font-size:11px;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;color:#59413e">Immediate Action</span>
        </div>
        <p style="font-size:14px;color:#261817;line-height:1.5">Barricade + patch within 24 hours. Notify school.</p>
      </div>

      <!-- 4. Estimated Cost Row -->
      <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid #e1bfba">
        <div style="display:flex;align-items:center;gap:12px">
          <div style="width:42px;height:42px;border-radius:50%;background:#fde2df;display:flex;align-items:center;justify-content:center;flex-shrink:0">
            <span style="font-size:18px;font-weight:700;color:#59413e">₹</span>
          </div>
          <span style="font-size:13px;font-weight:500;color:#59413e">Estimated Cost</span>
        </div>
        <span style="font-size:20px;font-weight:700;color:#261817">₹14,500</span>
      </div>

      <!-- 5. Why this decision? -->
      <div style="display:flex;align-items:center;justify-content:space-between;cursor:pointer;padding:2px 0" @click="evidenceOpen=!evidenceOpen">
        <h2 style="font-size:18px;font-weight:600;letter-spacing:-0.01em;color:#261817">Why this decision?</h2>
        <span class="material-symbols-outlined" style="color:#59413e;font-size:22px;transition:transform 0.2s" :style="{transform:evidenceOpen?'rotate(180deg)':'rotate(0)'}">expand_more</span>
      </div>

      <!-- 6. Evidence Cards -->
      <div v-show="evidenceOpen" style="display:flex;flex-direction:column;gap:10px">
        <!-- Visual Evidence -->
        <div class="snap-card" style="padding:14px;display:flex;gap:14px;align-items:flex-start">
          <div style="width:42px;height:42px;border-radius:50%;background:#fff1e5;display:flex;align-items:center;justify-content:center;flex-shrink:0">
            <span class="material-symbols-outlined ms-filled" style="color:#e65c00;font-size:20px">photo_camera</span>
          </div>
          <div style="flex:1">
            <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px;margin-bottom:4px">
              <h4 style="font-size:14px;font-weight:700;color:#261817">Visual evidence</h4>
              <span class="pill pill-red" style="flex-shrink:0">Critical</span>
            </div>
            <p style="font-size:13px;color:#59413e;line-height:1.5">Image analysis confirms severe cracking and deep depression.</p>
          </div>
        </div>
        <!-- User Notes -->
        <div class="snap-card" style="padding:14px;display:flex;gap:14px;align-items:flex-start">
          <div style="width:42px;height:42px;border-radius:50%;background:#e5f1ff;display:flex;align-items:center;justify-content:center;flex-shrink:0">
            <span class="material-symbols-outlined ms-filled" style="color:#1565c0;font-size:20px">content_paste</span>
          </div>
          <div style="flex:1">
            <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px;margin-bottom:4px">
              <h4 style="font-size:14px;font-weight:700;color:#261817">User notes</h4>
              <span class="pill pill-amber" style="flex-shrink:0">High</span>
            </div>
            <p style="font-size:13px;color:#59413e;line-height:1.5">Report indicates recent school bus rerouting due to hazard.</p>
          </div>
        </div>
        <!-- Historical Data -->
        <div class="snap-card" style="padding:14px;display:flex;gap:14px;align-items:flex-start">
          <div style="width:42px;height:42px;border-radius:50%;background:#e8f5e9;display:flex;align-items:center;justify-content:center;flex-shrink:0">
            <span class="material-symbols-outlined ms-filled" style="color:#2e7d32;font-size:20px">bar_chart</span>
          </div>
          <div style="flex:1">
            <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px;margin-bottom:4px">
              <h4 style="font-size:14px;font-weight:700;color:#261817">Historical data</h4>
              <span class="pill pill-grey" style="flex-shrink:0">Medium</span>
            </div>
            <p style="font-size:13px;color:#59413e;line-height:1.5">Location has experienced 3 similar failures in the past 2 years.</p>
          </div>
        </div>
      </div>

      <!-- Spacer for fixed buttons -->
      <div style="height:60px"></div>
    </main>

    <!-- ── Fixed Bottom Action Buttons ── -->
    <div style="position:fixed;bottom:72px;left:50%;transform:translateX(-50%);width:100%;max-width:480px;padding:8px 16px;background:linear-gradient(to top,#fff8f7 70%,transparent);z-index:40">
      <div style="display:flex;gap:10px">
        <button style="flex:1;height:48px;background:#655468;color:#fff;border:none;border-radius:9999px;font-size:13px;font-weight:700;letter-spacing:0.02em;cursor:pointer;box-shadow:0 4px 12px rgba(101,84,104,0.3);transition:transform 0.12s"
          @mousedown="e=>e.currentTarget.style.transform='scale(0.97)'"
          @mouseup="e=>e.currentTarget.style.transform='scale(1)'">
          Create Work Order
        </button>
        <button style="flex:1;height:48px;background:#fff;color:#655468;border:2px solid #655468;border-radius:9999px;font-size:13px;font-weight:700;letter-spacing:0.02em;cursor:pointer;transition:transform 0.12s"
          @mousedown="e=>e.currentTarget.style.transform='scale(0.97)'"
          @mouseup="e=>e.currentTarget.style.transform='scale(1)'">
          Request Review
        </button>
      </div>
    </div>

    <!-- ── Bottom Nav ── -->
    <nav class="snap-nav">
      <router-link to="/" class="snap-nav-item" style="color:#59413e">
        <span class="material-symbols-outlined" style="font-size:22px">dashboard</span>
        <span>Dashboard</span>
      </router-link>
      <div class="snap-nav-item active">
        <span class="material-symbols-outlined ms-filled" style="font-size:22px">assessment</span>
        <span>Assessments</span>
      </div>
      <div class="snap-nav-item">
        <span class="material-symbols-outlined" style="font-size:22px">build</span>
        <span>Repairs</span>
      </div>
      <div class="snap-nav-item">
        <span class="material-symbols-outlined" style="font-size:22px">settings</span>
        <span>Settings</span>
      </div>
    </nav>

  </div>
</template>

<script>
export default {
  name: 'Assessment',
  data() {
    return { evidenceOpen: true }
  },
}
</script>
