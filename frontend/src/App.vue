<template>
  <div class="app-container">
    <nav class="navbar">
      <div class="nav-brand">
        <h1>🛣️ SnapMend</h1>
        <p class="nav-subtitle">Municipal Pavement Assessment</p>
      </div>
      <div class="nav-links">
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          Dashboard
        </router-link>
        <router-link to="/assessment" class="nav-item" :class="{ active: $route.path === '/assessment' }">
          New Assessment
        </router-link>
      </div>
    </nav>

    <main class="main-content">
      <router-view />
    </main>

    <footer class="footer">
      <p>&copy; 2026 SnapMend | Municipal Street Assessment Platform</p>
      <p class="footer-badge">✅ Zero Billing Required - Free Tier Only</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {}
  },
}
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.navbar {
  background-color: rgba(0, 0, 0, 0.8);
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 3px solid #667eea;
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.nav-brand h1 {
  font-size: 1.8rem;
  margin-bottom: 0.25rem;
}

.nav-subtitle {
  font-size: 0.85rem;
  opacity: 0.8;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-item {
  color: white;
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.nav-item:hover {
  background-color: rgba(102, 126, 234, 0.2);
  color: #a8dadc;
}

.nav-item.active {
  background-color: #667eea;
  color: white;
}

.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

.footer {
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 1.5rem;
  text-align: center;
  border-top: 3px solid #667eea;
  margin-top: 2rem;
}

.footer-badge {
  font-size: 0.85rem;
  margin-top: 0.5rem;
  color: #a8dadc;
}

@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    gap: 1rem;
  }

  .nav-links {
    width: 100%;
    justify-content: center;
  }

  .main-content {
    padding: 1rem;
  }
}
</style>
