<template>
  <div class="snap-screen">

    <!-- ── Top App Bar ── -->
    <header class="snap-topbar">
      <div class="snap-topbar-brand">
        <span class="material-symbols-outlined ms-filled" style="color:#b02a26;font-size:24px">construction</span>
        <span class="brand-name">SnapMend</span>
      </div>
      <div class="snap-topbar-avatar">
        <span class="material-symbols-outlined" style="color:#59413e;font-size:20px">person</span>
      </div>
    </header>

    <!-- ── Main Scroll Area ── -->
    <main class="snap-main">

      <!-- ── Hero Greeting Card ── -->
      <section style="background:linear-gradient(135deg,#fff0ee 0%,#fff8f7 100%);padding:24px 16px 20px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #f0d8d4;">
        <div>
          <h1 style="font-size:22px;font-weight:700;letter-spacing:-0.02em;color:#261817;line-height:1.2">Good {{ greeting }},<br>Inspector 👋</h1>
          <p style="font-size:13px;color:#59413e;margin-top:6px;font-weight:500">Municipal Pavement Assessment</p>
        </div>
        <div style="width:60px;height:60px;border-radius:50%;background:#b02a26;display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 4px 12px rgba(176,42,38,0.3);flex-shrink:0;">
          <span style="font-size:18px;font-weight:700;color:#fff;line-height:1">{{ today.day }}</span>
          <span style="font-size:10px;font-weight:600;color:#ffcbc5;letter-spacing:0.05em">{{ today.month }}</span>
        </div>
      </section>

      <!-- ── Quick Actions ── -->
      <section style="padding:20px 16px 4px">
        <h2 style="font-size:18px;font-weight:600;letter-spacing:-0.01em;color:#261817;margin-bottom:14px">Quick Actions</h2>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
          <!-- New Assessment -->
          <router-link to="/assessment" style="display:block">
            <div class="snap-card" style="padding:16px;background:linear-gradient(145deg,#fff0ed,#ffe4e0);border-color:#f5c9c4;cursor:pointer">
              <div style="width:44px;height:44px;border-radius:50%;background:rgba(255,109,77,0.15);display:flex;align-items:center;justify-content:center;margin-bottom:14px">
                <span class="material-symbols-outlined ms-filled" style="color:#e65c00;font-size:22px">photo_camera</span>
              </div>
              <h3 style="font-size:15px;font-weight:700;color:#261817;margin-bottom:4px">New Assessment</h3>
              <p style="font-size:12px;color:#59413e;margin-bottom:12px;line-height:1.4">Snap &amp; analyze pavement</p>
              <div style="display:flex;justify-content:flex-end">
                <span class="material-symbols-outlined" style="color:#b02a26;font-size:20px">arrow_forward</span>
              </div>
            </div>
          </router-link>
          <!-- View Reports -->
          <div class="snap-card" style="padding:16px;background:linear-gradient(145deg,#f2dbf4,#ede0f0);border-color:#d6c0d7;cursor:pointer">
            <div style="width:44px;height:44px;border-radius:50%;background:rgba(106,89,109,0.15);display:flex;align-items:center;justify-content:center;margin-bottom:14px">
              <span class="material-symbols-outlined ms-filled" style="color:#655468;font-size:22px">analytics</span>
            </div>
            <h3 style="font-size:15px;font-weight:700;color:#261817;margin-bottom:4px">View Reports</h3>
            <p style="font-size:12px;color:#59413e;margin-bottom:12px;line-height:1.4">Repair history &amp; trends</p>
            <div style="display:flex;justify-content:flex-end">
              <span class="material-symbols-outlined" style="color:#b02a26;font-size:20px">arrow_forward</span>
            </div>
          </div>
        </div>
      </section>

      <!-- ── Recent Assessments ── -->
      <section style="padding:20px 16px 8px">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">
          <h2 style="font-size:18px;font-weight:600;letter-spacing:-0.01em;color:#261817">Recent Assessments</h2>
          <span style="font-size:13px;font-weight:600;color:#b02a26;cursor:pointer">See all</span>
        </div>
        <div style="display:flex;flex-direction:column;gap:10px">
          <!-- Item 1 -->
          <router-link to="/assessment">
            <div class="snap-card" style="padding:12px;display:flex;align-items:center;gap:12px;cursor:pointer">
              <div style="width:60px;height:60px;border-radius:12px;overflow:hidden;flex-shrink:0;background:#fde2df">
                <img src="@/assets/reference.png" alt="Pothole" style="width:100%;height:100%;object-fit:cover" />
              </div>
              <div style="flex:1;min-width:0">
                <h4 style="font-size:15px;font-weight:700;color:#261817;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">MH-47-A Street</h4>
                <div style="margin-top:4px"><span class="pill pill-red">Severity 4/5 · High</span></div>
                <p style="font-size:12px;color:#59413e;margin-top:4px">2 hours ago</p>
              </div>
              <span class="material-symbols-outlined" style="color:#59413e;font-size:20px;flex-shrink:0">chevron_right</span>
            </div>
          </router-link>
          <!-- Item 2 -->
          <div class="snap-card" style="padding:12px;display:flex;align-items:center;gap:12px;cursor:pointer">
            <div style="width:60px;height:60px;border-radius:12px;background:#e8f5e9;display:flex;align-items:center;justify-content:center;flex-shrink:0">
              <span class="material-symbols-outlined" style="color:#2e7d32;font-size:26px">add_road</span>
            </div>
            <div style="flex:1;min-width:0">
              <h4 style="font-size:15px;font-weight:700;color:#261817;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">SH-21-B Avenue</h4>
              <div style="margin-top:4px"><span class="pill pill-green">Severity 2/5 · Low</span></div>
              <p style="font-size:12px;color:#59413e;margin-top:4px">1 day ago</p>
            </div>
            <span class="material-symbols-outlined" style="color:#59413e;font-size:20px;flex-shrink:0">chevron_right</span>
          </div>
          <!-- Item 3 -->
          <div class="snap-card" style="padding:12px;display:flex;align-items:center;gap:12px;cursor:pointer">
            <div style="width:60px;height:60px;border-radius:12px;background:#fff8e1;display:flex;align-items:center;justify-content:center;flex-shrink:0">
              <span class="material-symbols-outlined" style="color:#a67c00;font-size:26px">add_road</span>
            </div>
            <div style="flex:1;min-width:0">
              <h4 style="font-size:15px;font-weight:700;color:#261817;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">NH-48 Main Road</h4>
              <div style="margin-top:4px"><span class="pill pill-amber">Severity 3/5 · Medium</span></div>
              <p style="font-size:12px;color:#59413e;margin-top:4px">3 days ago</p>
            </div>
            <span class="material-symbols-outlined" style="color:#59413e;font-size:20px;flex-shrink:0">chevron_right</span>
          </div>
        </div>
      </section>

    </main>

    <!-- ── Bottom Nav ── -->
    <nav class="snap-nav">
      <div class="snap-nav-item active">
        <span class="material-symbols-outlined ms-filled" style="font-size:22px">dashboard</span>
        <span>Dashboard</span>
      </div>
      <router-link to="/assessment" class="snap-nav-item" style="color:#59413e;">
        <span class="material-symbols-outlined" style="font-size:22px">assessment</span>
        <span>Assessments</span>
      </router-link>
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
import { assessmentAPI } from '@/services/api'

export default {
  name: 'Dashboard',
  data() {
    const now = new Date()
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    const hour = now.getHours()
    return {
      apiStatus: null,
      today: { day: now.getDate(), month: months[now.getMonth()] },
      greeting: hour < 12 ? 'Morning' : hour < 17 ? 'Afternoon' : 'Evening',
    }
  },
  async mounted() {
    try {
      const res = await assessmentAPI.getHealth()
      this.apiStatus = res.data.status === 'healthy'
    } catch {
      this.apiStatus = false
    }
  },
}
</script>
