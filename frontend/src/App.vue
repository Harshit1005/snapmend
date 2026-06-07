<template>
  <div id="app" style="font-family:'Inter',sans-serif;background:#fff8f7;color:#261817;min-height:100vh;">
    <router-view />
  </div>
</template>

<script>
export default { name: 'App' }
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Inter', sans-serif; background: #fff8f7; color: #261817; -webkit-font-smoothing: antialiased; }
a { text-decoration: none; color: inherit; }

.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  font-size: 22px;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  vertical-align: middle;
  user-select: none;
}
.ms-filled { font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24; }

.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

/* ── Shared Layout Shell ── */
.snap-screen {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  max-width: 480px;
  margin: 0 auto;
  background: #fff8f7;
  position: relative;
}

/* ── Top App Bar ── */
.snap-topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  background: #fff8f7;
  border-bottom: 1px solid #e1bfba;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  height: 56px;
}
.snap-topbar-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}
.snap-topbar-brand .brand-name {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #b02a26;
}
.snap-topbar-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #fde2df;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* ── Main Scroll Area ── */
.snap-main {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 96px;
}

/* ── Bottom Nav ── */
.snap-nav {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  z-index: 50;
  background: #ffffff;
  border-top: 1px solid #e1bfba;
  display: flex;
  align-items: center;
  justify-content: space-around;
  height: 72px;
}
.snap-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  padding: 6px 12px;
  border-radius: 9999px;
  cursor: pointer;
  transition: background 0.15s;
  color: #59413e;
  font-size: 11px;
  font-weight: 500;
  min-width: 64px;
}
.snap-nav-item:hover { background: #fff0ee; }
.snap-nav-item.active {
  background: #ffcbc5;
  color: #8e0e11;
}
.snap-nav-item.active .material-symbols-outlined {
  font-variation-settings: 'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 24;
}

/* ── Cards ── */
.snap-card {
  background: #ffffff;
  border: 1px solid #e1bfba;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(140,60,40,0.06);
  transition: transform 0.12s ease, box-shadow 0.12s ease;
}
.snap-card:active { transform: scale(0.98); box-shadow: none; }

/* ── Severity Pills ── */
.pill { display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
.pill-red    { background: #ffebeb; color: #8e0e11; }
.pill-amber  { background: #fff8e1; color: #a67c00; }
.pill-green  { background: #e8f5e9; color: #2e7d32; }
.pill-grey   { background: #f5f5f5; color: #59413e; }
.pill-blue   { background: #e3f2fd; color: #1565c0; }

/* ── Micro-interactions ── */
@keyframes pulseRed {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.85); }
}
.pulse-red { animation: pulseRed 1.8s ease-in-out infinite; }
</style>
