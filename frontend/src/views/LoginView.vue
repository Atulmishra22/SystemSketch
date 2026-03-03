<template>
  <div class="auth-page">
    <!-- Brand Panel -->
    <div class="brand-panel">
      <div class="brand-grid-decoration">
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="dotgrid" x="0" y="0" width="28" height="28" patternUnits="userSpaceOnUse">
              <circle cx="2" cy="2" r="1.5" fill="rgba(255,255,255,0.2)"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#dotgrid)"/>
        </svg>
      </div>
      <div class="brand-logo">
        <svg class="logo-mark" width="36" height="36" viewBox="0 0 36 36" fill="none">
          <!-- Node 1: Rect (amber tint) top-left -->
          <rect x="2" y="5" width="14" height="9" rx="2.2"
                stroke="white" stroke-width="1.6" fill="white" fill-opacity="0.12"/>
          <!-- Node 2: Circle top-right -->
          <circle cx="28" cy="9.5" r="6"
                  stroke="rgba(255,255,255,0.85)" stroke-width="1.6" fill="white" fill-opacity="0.08"/>
          <!-- Connector 1→2 -->
          <line x1="16.5" y1="9.5" x2="21.5" y2="9.5"
                stroke="white" stroke-width="1" stroke-dasharray="2.2,1.8" opacity="0.6"/>
          <polygon points="21.5,7.5 25.5,9.5 21.5,11.5" fill="white" opacity="0.65"/>
          <!-- Node 3: Rect (sage tint) bottom-center -->
          <rect x="10" y="23" width="15" height="9" rx="2.2"
                stroke="rgba(255,255,255,0.75)" stroke-width="1.6" fill="white" fill-opacity="0.07"/>
          <!-- Connector 1→3 -->
          <line x1="10" y1="15" x2="14" y2="23"
                stroke="white" stroke-width="1" stroke-dasharray="2.2,1.8" opacity="0.45"/>
          <!-- Connector 2→3 -->
          <line x1="26" y1="16" x2="23" y2="23"
                stroke="white" stroke-width="1" stroke-dasharray="2.2,1.8" opacity="0.45"/>
          <!-- Pencil — bottom-right -->
          <g transform="translate(31,31) rotate(-42)">
            <rect x="-2" y="-9" width="4" height="2.5" rx="0.7" fill="white" opacity="0.7"/>
            <rect x="-2" y="-6.5" width="4" height="8" rx="0.6" fill="white" opacity="0.5"/>
            <polygon points="-2,1.5 2,1.5 0,6" fill="white" opacity="0.85"/>
          </g>
        </svg>
        <span class="logo-text">SystemSketch</span>
      </div>
      <div class="brand-hero">
        <h2 class="hero-title">Think in<br><em>systems.</em></h2>
        <p class="hero-sub">Collaborative diagramming for teams who ship together.</p>
      </div>
    </div>

    <!-- Form Panel -->
    <div class="form-panel">
      <div class="form-inner">
        <div class="form-header">
          <h1 class="form-title">Welcome back</h1>
          <p class="form-subtitle">Sign in to continue to your workspace.</p>
        </div>

        <form @submit.prevent="handleLogin" class="auth-form">
          <div class="field-group">
            <label class="field-label">Username or email</label>
            <input
              v-model="credentials.username_or_email"
              type="text"
              class="field-input"
              placeholder="you@example.com"
              required
            />
          </div>

          <div class="field-group">
            <label class="field-label">Password</label>
            <input
              v-model="credentials.password"
              type="password"
              class="field-input"
              placeholder="••••••••"
              required
            />
          </div>

          <div v-if="error" class="error-banner">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="error-icon">
              <circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.5"/>
              <path d="M8 5v3.5M8 10.5v.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <span>{{ error }}</span>
          </div>

          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="!loading">Sign in</span>
            <span v-else class="loading-dots"><span></span><span></span><span></span></span>
          </button>
        </form>

        <div class="form-links">
          <p class="link-row">
            New to SystemSketch?
            <router-link to="/register" class="inline-link">Create an account →</router-link>
          </p>
          <div class="link-divider"></div>
          <router-link to="/rooms" class="guest-link">Continue as guest</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { parseApiError } from '@/utils/errors'

const router = useRouter()
const authStore = useAuthStore()

const credentials = ref({
  username_or_email: '',
  password: '',
})

const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  
  try {
    await authStore.login(credentials.value)
    router.push({ name: 'rooms' })
  } catch (err: any) {
    error.value = parseApiError(err, 'Login failed')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ─── Layout ─────────────────────────────── */
.auth-page {
  display: grid;
  grid-template-columns: 1fr 1fr;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

/* ─── Brand Panel ─────────────────────────── */
.brand-panel {
  background: var(--color-accent);
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 48px;
  overflow: hidden;
  gap: auto;
}

.brand-grid-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 1;
  color: #fff;
  margin-bottom: auto;
}

.logo-mark { color: #fff; flex-shrink: 0; }

.logo-text {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 500;
  color: #fff;
  letter-spacing: -0.02em;
}

.brand-hero {
  position: relative;
  z-index: 1;
  color: #fff;
  padding-bottom: 48px;
  margin-top: auto;
}

.hero-title {
  font-family: var(--font-display);
  font-size: clamp(48px, 5.5vw, 80px);
  font-weight: 300;
  line-height: 1.0;
  letter-spacing: -0.04em;
  margin-bottom: 20px;
  color: #fff;
}

.hero-title em {
  font-style: italic;
  font-weight: 400;
}

.hero-sub {
  font-family: var(--font-ui);
  font-size: 15px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
  max-width: 300px;
}

/* ─── Form Panel ─────────────────────────── */
.form-panel {
  background: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  overflow-y: auto;
}

.form-inner {
  width: 100%;
  max-width: 400px;
  animation: panelIn 0.55s var(--ease-out);
}

@keyframes panelIn {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

.form-header { margin-bottom: 36px; }

.form-title {
  font-family: var(--font-display);
  font-size: 34px;
  font-weight: 400;
  color: var(--color-ink);
  letter-spacing: -0.03em;
  margin-bottom: 8px;
}

.form-subtitle {
  font-size: 14px;
  color: var(--color-ink-muted);
  line-height: 1.5;
}

/* ─── Fields ─────────────────────────────── */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-ink);
}

.field-input {
  width: 100%;
  background: var(--color-paper);
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-ink);
  font-family: var(--font-ui);
  font-size: 15px;
  padding: 11px 14px;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  cursor: text;
}

.field-input::placeholder { color: var(--color-ink-subtle); }

.field-input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-dim);
  background: var(--color-surface);
}

/* ─── Error ──────────────────────────────── */
.error-banner {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #FEF2EE;
  border: 1px solid #F5C4B6;
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  font-size: 13px;
  color: var(--color-accent);
  line-height: 1.5;
}

.error-icon { flex-shrink: 0; margin-top: 1px; }

/* ─── Submit Button ──────────────────────── */
.submit-btn {
  width: 100%;
  background: var(--color-accent);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 13px;
  font-family: var(--font-ui);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
  margin-top: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 50px;
  box-shadow: var(--shadow-sm);
}

.submit-btn:hover:not(:disabled) {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.submit-btn:active:not(:disabled) { transform: translateY(0); }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.loading-dots { display: flex; gap: 5px; align-items: center; }

.loading-dots span {
  width: 6px;
  height: 6px;
  background: #fff;
  border-radius: 50%;
  animation: dotPulse 1.2s ease-in-out infinite;
}

.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotPulse {
  0%, 100% { opacity: 0.3; transform: scale(0.7); }
  50%       { opacity: 1;   transform: scale(1);   }
}

/* ─── Footer Links ───────────────────────── */
.form-links {
  margin-top: 28px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.link-row {
  font-size: 14px;
  color: var(--color-ink-muted);
}

.inline-link {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.15s ease;
}

.inline-link:hover { color: var(--color-accent-hover); }

.link-divider {
  height: 1px;
  background: var(--color-border);
  margin: 2px 0;
}

.guest-link {
  color: var(--color-ink-subtle);
  text-decoration: none;
  font-size: 13px;
  transition: color 0.15s ease;
}

.guest-link:hover { color: var(--color-ink-muted); }

/* ─── Responsive ─────────────────────────── */
@media (max-width: 768px) {
  .auth-page {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }
  .brand-panel {
    padding: 32px;
    min-height: 220px;
  }
  .brand-hero { padding-bottom: 24px; }
  .hero-title  { font-size: 40px; }
  .form-panel  { padding: 36px 24px; }
  .form-inner  { max-width: 100%; }
}
</style>
