<template>
  <div class="home">

    <!-- Fixed Nav -->
    <nav class="site-nav">
      <div class="nav-inner">
        <div class="nav-brand">
          <svg width="26" height="26" viewBox="0 0 26 26" fill="none">
              <!-- Subtle bg -->
              <rect width="26" height="26" rx="5.5" fill="currentColor" fill-opacity="0.06"/>
              <!-- Node 1: Rect top-left -->
              <rect x="1.5" y="3.5" width="10" height="7" rx="1.6"
                    stroke="currentColor" stroke-width="1.5" fill="currentColor" fill-opacity="0.08"/>
              <!-- Node 2: Circle top-right -->
              <circle cx="20" cy="7" r="4.2"
                      stroke="currentColor" stroke-width="1.5" fill="currentColor" fill-opacity="0.06"/>
              <!-- Connector 1→2 -->
              <line x1="12" y1="7" x2="15.4" y2="7"
                    stroke="currentColor" stroke-width="0.9" stroke-dasharray="2,1.5" opacity="0.6"/>
              <polygon points="15.4,5.6 18.4,7 15.4,8.4" fill="currentColor" opacity="0.65"/>
              <!-- Node 3: Rect bottom-center -->
              <rect x="6.5" y="16.5" width="11" height="7" rx="1.6"
                    stroke="currentColor" stroke-width="1.5" fill="currentColor" fill-opacity="0.06"/>
              <!-- Connectors to bottom -->
              <line x1="6.5" y1="11.5" x2="9.5" y2="16.5"
                    stroke="currentColor" stroke-width="0.9" stroke-dasharray="2,1.5" opacity="0.5"/>
              <line x1="18.8" y1="12" x2="16.5" y2="16.5"
                    stroke="currentColor" stroke-width="0.9" stroke-dasharray="2,1.5" opacity="0.5"/>
              <!-- Pencil — bottom-right -->
              <g transform="translate(22.5,21.5) rotate(-42)">
                <rect x="-1.5" y="-6.5" width="3" height="1.8" rx="0.5" fill="currentColor" opacity="0.65"/>
                <rect x="-1.5" y="-4.7" width="3" height="5.5" rx="0.4" fill="currentColor" opacity="0.45"/>
                <polygon points="-1.5,0.8 1.5,0.8 0,4.5" fill="currentColor" opacity="0.75"/>
              </g>
            </svg>
          <span>SystemSketch</span>
        </div>
        <div class="nav-links">
          <a href="#features" class="nav-link">Features</a>
          <a href="#how-it-works" class="nav-link">How it works</a>
          <template v-if="isLoggedIn">
            <router-link to="/rooms" class="nav-link">My rooms</router-link>
            <div class="nav-user-chip">
              <span class="nav-avatar">{{ displayName.charAt(0).toUpperCase() }}</span>
              <span class="nav-username">{{ displayName }}</span>
              <button class="nav-logout" @click="handleLogout">Sign out</button>
            </div>
          </template>
          <template v-else>
            <router-link to="/login" class="nav-link">Sign in</router-link>
            <router-link to="/rooms" class="nav-cta">Get started</router-link>
          </template>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <section class="hero-section">
      <svg class="bg-grid" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="hgrid" x="0" y="0" width="32" height="32" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="2" r="1.5" fill="rgba(26,22,18,0.1)"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#hgrid)"/>
      </svg>

      <div class="hero-inner">
        <div class="hero-badge">Collaborative diagramming</div>
        <h1 class="hero-headline">
          Sketch the way<br>
          <em>systems think.</em>
        </h1>
        <p class="hero-sub">
          SystemSketch is a real-time whiteboard for engineering teams. Draw, annotate,
          and reason about your systems together — wherever you are.
        </p>
        <div class="cta-row">
          <router-link to="/rooms" class="cta-primary">
            Start sketching free
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" stroke-width="1.5"
                stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </router-link>
          <router-link to="/login" class="cta-ghost">Sign in to your account</router-link>
        </div>
        <p class="hero-note">No credit card required &middot; Instant access</p>
      </div>

      <!-- Decorative diagram preview -->
      <div class="hero-diagram" aria-hidden="true">
        <svg width="100%" height="100%" viewBox="0 0 520 300" fill="none" xmlns="http://www.w3.org/2000/svg">
          <pattern id="dg" x="0" y="0" width="24" height="24" patternUnits="userSpaceOnUse">
            <circle cx="1.5" cy="1.5" r="1" fill="#C8C0B7"/>
          </pattern>
          <rect width="520" height="300" fill="url(#dg)"/>
          <rect x="40" y="50" width="120" height="56" rx="3" stroke="#C0431F" stroke-width="1.5" fill="#FEF2EE"/>
          <text x="100" y="82" text-anchor="middle" font-size="12" font-family="Instrument Sans,sans-serif" fill="#C0431F" font-weight="500">API Gateway</text>
          <rect x="220" y="30" width="120" height="56" rx="3" stroke="#7C6D61" stroke-width="1.5" fill="white"/>
          <text x="280" y="62" text-anchor="middle" font-size="12" font-family="Instrument Sans,sans-serif" fill="#1A1612" font-weight="500">Auth Service</text>
          <rect x="220" y="120" width="120" height="56" rx="3" stroke="#7C6D61" stroke-width="1.5" fill="white"/>
          <text x="280" y="152" text-anchor="middle" font-size="12" font-family="Instrument Sans,sans-serif" fill="#1A1612" font-weight="500">User Service</text>
          <rect x="220" y="210" width="120" height="56" rx="3" stroke="#7C6D61" stroke-width="1.5" fill="white"/>
          <text x="280" y="242" text-anchor="middle" font-size="12" font-family="Instrument Sans,sans-serif" fill="#1A1612" font-weight="500">Room Service</text>
          <rect x="390" y="120" width="110" height="56" rx="3" stroke="#4E6B57" stroke-width="1.5" fill="#F0F5F1"/>
          <text x="445" y="152" text-anchor="middle" font-size="12" font-family="Instrument Sans,sans-serif" fill="#4E6B57" font-weight="500">PostgreSQL</text>
          <line x1="160" y1="78" x2="220" y2="58" stroke="#BAA99A" stroke-width="1.5" stroke-dasharray="4 3"/>
          <line x1="160" y1="78" x2="220" y2="148" stroke="#BAA99A" stroke-width="1.5" stroke-dasharray="4 3"/>
          <line x1="160" y1="78" x2="220" y2="238" stroke="#BAA99A" stroke-width="1.5" stroke-dasharray="4 3"/>
          <line x1="340" y1="148" x2="390" y2="148" stroke="#BAA99A" stroke-width="1.5"/>
          <polygon points="218,54 225,58 218,62" fill="#BAA99A"/>
          <polygon points="218,144 225,148 218,152" fill="#BAA99A"/>
          <polygon points="218,234 225,238 218,242" fill="#BAA99A"/>
          <polygon points="388,144 395,148 388,152" fill="#BAA99A"/>
          <polygon points="56,170 64,188 67,181 75,184" fill="#C0431F" opacity="0.85"/>
          <rect x="64" y="190" width="44" height="16" rx="8" fill="#C0431F"/>
          <text x="86" y="202" text-anchor="middle" font-size="9" font-family="Instrument Sans,sans-serif" fill="white">Alex</text>
          <polygon points="374,50 382,68 385,61 393,64" fill="#4E6B57" opacity="0.85"/>
          <rect x="382" y="70" width="42" height="16" rx="8" fill="#4E6B57"/>
          <text x="403" y="82" text-anchor="middle" font-size="9" font-family="Instrument Sans,sans-serif" fill="white">Sam</text>
        </svg>
      </div>
    </section>

    <!-- Social proof bar -->
    <div class="proof-bar">
      <span class="proof-item">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none"><circle cx="7.5" cy="7.5" r="6" stroke="currentColor" stroke-width="1.5"/><path d="M4.5 7.5l2 2 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        Free to use
      </span>
      <span class="proof-sep">·</span>
      <span class="proof-item">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none"><circle cx="7.5" cy="7.5" r="6" stroke="currentColor" stroke-width="1.5"/><path d="M4.5 7.5l2 2 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        Real-time collaboration
      </span>
      <span class="proof-sep">·</span>
      <span class="proof-item">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none"><circle cx="7.5" cy="7.5" r="6" stroke="currentColor" stroke-width="1.5"/><path d="M4.5 7.5l2 2 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        Works without an account
      </span>
      <span class="proof-sep">·</span>
      <span class="proof-item">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none"><circle cx="7.5" cy="7.5" r="6" stroke="currentColor" stroke-width="1.5"/><path d="M4.5 7.5l2 2 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        No install required
      </span>
    </div>

    <!-- Features -->
    <section class="features-section" id="features">
      <div class="section-inner">
        <div class="section-eyebrow">What you get</div>
        <h2 class="section-title">Everything your team needs<br>to think visually.</h2>
        <div class="features-grid">

          <div class="feature-card accent">
            <div class="feature-icon">
              <svg width="26" height="26" viewBox="0 0 26 26" fill="none">
                <circle cx="8" cy="8" r="5" stroke="currentColor" stroke-width="1.8"/>
                <circle cx="20" cy="8" r="5" stroke="currentColor" stroke-width="1.8"/>
                <circle cx="14" cy="19" r="5" stroke="currentColor" stroke-width="1.8"/>
                <line x1="13" y1="8" x2="9" y2="17" stroke="currentColor" stroke-width="1.4"/>
                <line x1="14" y1="8" x2="19" y2="17" stroke="currentColor" stroke-width="1.4"/>
              </svg>
            </div>
            <h3 class="feature-title">Real-time collaboration</h3>
            <p class="feature-desc">See every teammate's cursor live. Changes sync instantly — no refresh, no conflicts, no lost work.</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <svg width="26" height="26" viewBox="0 0 26 26" fill="none">
                <rect x="2" y="2" width="10" height="10" stroke="currentColor" stroke-width="1.8"/>
                <circle cx="20" cy="7" r="5" stroke="currentColor" stroke-width="1.8"/>
                <rect x="2" y="16" width="22" height="8" stroke="currentColor" stroke-width="1.8"/>
              </svg>
            </div>
            <h3 class="feature-title">Rich shape library</h3>
            <p class="feature-desc">Rectangles, circles, arrows and text. Compose complex system diagrams from simple, expressive primitives.</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <svg width="26" height="26" viewBox="0 0 26 26" fill="none">
                <rect x="2" y="5" width="22" height="16" rx="2" stroke="currentColor" stroke-width="1.8"/>
                <line x1="2" y1="9" x2="24" y2="9" stroke="currentColor" stroke-width="1.4"/>
                <circle cx="13" cy="16" r="3.5" stroke="currentColor" stroke-width="1.8"/>
              </svg>
            </div>
            <h3 class="feature-title">Persistent rooms</h3>
            <p class="feature-desc">Each room is its own saved canvas. Come back days later and pick up exactly where your team left off.</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <svg width="26" height="26" viewBox="0 0 26 26" fill="none">
                <path d="M13 2l2.4 5.2 5.7.9-4.1 4 1 5.7-5-2.6-5 2.6 1-5.7L4.9 8.1l5.7-.9z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3 class="feature-title">Permission control</h3>
            <p class="feature-desc">Room owners decide who can view or edit. Invite collaborators with fine-grained viewer or editor roles.</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <svg width="26" height="26" viewBox="0 0 26 26" fill="none">
                <path d="M5 21L9 9l4 8 4-12 4 14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3 class="feature-title">Full undo history</h3>
            <p class="feature-desc">Step back through your entire edit history without losing any of your collaborators' contributions.</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <svg width="26" height="26" viewBox="0 0 26 26" fill="none">
                <rect x="3" y="3" width="8" height="8" stroke="currentColor" stroke-width="1.8"/>
                <rect x="15" y="3" width="8" height="8" stroke="currentColor" stroke-width="1.8"/>
                <rect x="3" y="15" width="8" height="8" stroke="currentColor" stroke-width="1.8"/>
                <line x1="15" y1="19" x2="23" y2="19" stroke="currentColor" stroke-width="1.8"/>
                <line x1="19" y1="15" x2="19" y2="23" stroke="currentColor" stroke-width="1.8"/>
              </svg>
            </div>
            <h3 class="feature-title">Guest access</h3>
            <p class="feature-desc">No account needed. Jump straight into public rooms and start exploring or contributing as a guest.</p>
          </div>

        </div>
      </div>
    </section>

    <!-- How it works -->
    <section class="how-section" id="how-it-works">
      <div class="section-inner">
        <div class="section-eyebrow">How it works</div>
        <h2 class="section-title">Up and running<br>in three steps.</h2>
        <div class="steps">
          <div class="step">
            <div class="step-num">01</div>
            <div class="step-body">
              <h3 class="step-title">Create a room</h3>
              <p class="step-desc">Sign in and hit "New Room". Give your workspace a name — this becomes your persistent canvas where all your diagrams live.</p>
            </div>
          </div>
          <div class="step-connector"></div>
          <div class="step">
            <div class="step-num">02</div>
            <div class="step-body">
              <h3 class="step-title">Start sketching</h3>
              <p class="step-desc">Pick a shape from the toolbar and draw on the canvas. Combine rectangles, circles, arrows and text to map out any system.</p>
            </div>
          </div>
          <div class="step-connector"></div>
          <div class="step">
            <div class="step-num">03</div>
            <div class="step-body">
              <h3 class="step-title">Invite your team</h3>
              <p class="step-desc">Share your room with teammates. Everyone's cursor shows up live and edits appear in real time across all connected browsers.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Use cases -->
    <section class="usecases-section">
      <div class="section-inner">
        <div class="section-eyebrow">Built for</div>
        <h2 class="section-title">Teams who think<br>before they build.</h2>
        <div class="usecases-grid">
          <div class="usecase-card">
            <div class="uc-label">Engineering</div>
            <p class="uc-desc">Map microservices, data flows, and API contracts before writing a line of code.</p>
          </div>
          <div class="usecase-card">
            <div class="uc-label">Product</div>
            <p class="uc-desc">Sketch user journeys, feature specs, and decision trees the whole team can annotate.</p>
          </div>
          <div class="usecase-card">
            <div class="uc-label">DevOps</div>
            <p class="uc-desc">Diagram infrastructure, deployment pipelines, and incident runbooks as living documents.</p>
          </div>
          <div class="usecase-card">
            <div class="uc-label">Research</div>
            <p class="uc-desc">Build concept maps and knowledge graphs to turn scattered notes into shared understanding.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Final CTA -->
    <section class="final-cta-section">
      <div class="final-cta-inner">
        <div class="final-brand-mark" aria-hidden="true">
          <svg width="44" height="44" viewBox="0 0 44 44" fill="none">
            <rect x="2" y="2" width="17" height="17" stroke="white" stroke-width="2" fill="white" fill-opacity="0.15"/>
            <rect x="25" y="2" width="17" height="17" stroke="white" stroke-width="2"/>
            <rect x="2" y="25" width="17" height="17" stroke="white" stroke-width="2" fill="white" fill-opacity="0.08"/>
            <line x1="25" y1="33.5" x2="42" y2="33.5" stroke="white" stroke-width="2"/>
            <line x1="33.5" y1="25" x2="33.5" y2="42" stroke="white" stroke-width="2"/>
          </svg>
        </div>
        <h2 class="final-cta-title">Ready to think visually?</h2>
        <p class="final-cta-sub">Join teams using SystemSketch to align faster and build better systems.</p>
        <router-link to="/rooms" class="final-cta-btn">
          Open the app — it&apos;s free
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </router-link>
      </div>
    </section>

    <!-- Footer -->
    <footer class="site-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <rect x="1" y="1" width="7" height="7" stroke="currentColor" stroke-width="1.5"/>
            <rect x="10" y="1" width="7" height="7" stroke="currentColor" stroke-width="1.5" fill="currentColor" fill-opacity="0.1"/>
            <rect x="1" y="10" width="7" height="7" stroke="currentColor" stroke-width="1.5"/>
            <line x1="10" y1="13.5" x2="17" y2="13.5" stroke="currentColor" stroke-width="1.5"/>
            <line x1="13.5" y1="10" x2="13.5" y2="17" stroke="currentColor" stroke-width="1.5"/>
          </svg>
          <span>SystemSketch</span>
        </div>
        <p class="footer-copy">&copy; 2026 SystemSketch &mdash; Built for teams who sketch before they build.</p>
        <div class="footer-links">
          <router-link to="/login" class="footer-link">Sign in</router-link>
          <router-link to="/register" class="footer-link">Register</router-link>
          <router-link to="/rooms" class="footer-link">Rooms</router-link>
        </div>
      </div>
    </footer>

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isLoggedIn = computed(() => authStore.isAuthenticated)
const displayName = computed(() => authStore.user?.username || authStore.user?.email || 'Account')

async function handleLogout() {
  await authStore.logout()
  router.push({ name: 'home' })
}
</script>

<style scoped>
/* ─── Page shell ──────────────────────────────────────────────────── */
.home {
  width: 100%;
  min-height: 100vh;
  overflow-y: auto;
  background: var(--color-paper);
  display: flex;
  flex-direction: column;
}

/* ─── Nav ─────────────────────────────────────────────────────────── */
.site-nav {
  position: sticky;
  top: 0;
  z-index: 200;
  background: rgba(245, 240, 232, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--color-border);
}

.nav-inner {
  max-width: 1160px;
  margin: 0 auto;
  padding: 0 40px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--color-ink);
  text-decoration: none;
  font-family: var(--font-display);
  font-size: 17px;
  font-weight: 500;
  letter-spacing: -0.02em;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-link {
  color: var(--color-ink-muted);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: var(--radius-xs);
  transition: color 0.15s ease, background 0.15s ease;
}

.nav-link:hover {
  color: var(--color-ink);
  background: rgba(26,22,18,0.05);
}

.nav-cta {
  background: var(--color-accent);
  color: #fff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  padding: 8px 18px;
  border-radius: var(--radius-sm);
  transition: background 0.2s ease;
  margin-left: 8px;
}

.nav-cta:hover { background: var(--color-accent-hover); }

.nav-user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 999px;
  padding: 4px 12px 4px 4px;
  margin-left: 8px;
}

.nav-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--color-accent);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-username {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-ink);
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-logout {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-ink-muted);
  padding: 2px 6px;
  border-radius: var(--radius-xs);
  transition: color 0.15s ease, background 0.15s ease;
}

.nav-logout:hover {
  color: var(--color-accent);
  background: rgba(192, 67, 31, 0.06);
}

/* ─── Hero ────────────────────────────────────────────────────────── */
.hero-section {
  position: relative;
  min-height: calc(100vh - 60px);
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  max-width: 1160px;
  margin: 0 auto;
  padding: 80px 40px;
  gap: 60px;
  width: 100%;
}

.bg-grid {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.hero-inner {
  position: relative;
  z-index: 1;
  animation: heroIn 0.7s var(--ease-out);
}

@keyframes heroIn {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}

.hero-badge {
  display: inline-block;
  background: var(--color-accent-dim);
  color: var(--color-accent);
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-ui);
  padding: 5px 12px;
  border-radius: var(--radius-full);
  border: 1px solid #F5C4B6;
  letter-spacing: 0.01em;
  margin-bottom: 28px;
}

.hero-headline {
  font-family: var(--font-display);
  font-size: clamp(44px, 5.5vw, 76px);
  font-weight: 300;
  color: var(--color-ink);
  line-height: 1.0;
  letter-spacing: -0.04em;
  margin-bottom: 24px;
}

.hero-headline em {
  font-style: italic;
  font-weight: 400;
  color: var(--color-accent);
}

.hero-sub {
  font-size: 17px;
  color: var(--color-ink-muted);
  line-height: 1.65;
  max-width: 440px;
  margin-bottom: 40px;
}

.cta-row {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.cta-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--color-accent);
  color: #fff;
  text-decoration: none;
  padding: 14px 24px;
  border-radius: var(--radius-sm);
  font-family: var(--font-ui);
  font-size: 15px;
  font-weight: 600;
  box-shadow: var(--shadow-sm);
  transition: background 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
}

.cta-primary:hover {
  background: var(--color-accent-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.cta-ghost {
  color: var(--color-ink-muted);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 14px 4px;
  border-bottom: 1px solid var(--color-border);
  transition: color 0.15s ease, border-color 0.15s ease;
}

.cta-ghost:hover {
  color: var(--color-ink);
  border-color: var(--color-ink-muted);
}

.hero-note {
  font-size: 12px;
  color: var(--color-ink-subtle);
  font-family: var(--font-mono);
}

.hero-diagram {
  position: relative;
  z-index: 1;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  animation: diagramIn 0.9s var(--ease-out) 0.15s backwards;
}

@keyframes diagramIn {
  from { opacity: 0; transform: translateY(32px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* ─── Proof bar ───────────────────────────────────────────────────── */
.proof-bar {
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 6px 20px;
  padding: 14px 40px;
}

.proof-item {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-ink-muted);
}

.proof-item svg { color: var(--color-sage); flex-shrink: 0; }

.proof-sep {
  color: var(--color-border-hover);
  font-size: 18px;
  line-height: 1;
}

/* ─── Section shared ──────────────────────────────────────────────── */
.section-inner {
  max-width: 1160px;
  margin: 0 auto;
  padding: 96px 40px;
  width: 100%;
}

.section-eyebrow {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 500;
  color: var(--color-accent);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 16px;
}

.section-title {
  font-family: var(--font-display);
  font-size: clamp(32px, 4vw, 52px);
  font-weight: 300;
  color: var(--color-ink);
  letter-spacing: -0.04em;
  line-height: 1.08;
  margin-bottom: 64px;
}

/* ─── Features ────────────────────────────────────────────────────── */
.features-section {
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2px;
  border: 1px solid var(--color-border);
}

.feature-card {
  background: var(--color-surface);
  padding: 36px 32px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  transition: background 0.2s ease;
}

.feature-card:hover { background: var(--color-paper); }

.feature-card.accent { background: var(--color-accent-dim); }
.feature-card.accent:hover { background: #f6e2db; }

.feature-icon { color: var(--color-accent); }
.feature-card:not(.accent) .feature-icon { color: var(--color-ink-muted); }

.feature-title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 500;
  color: var(--color-ink);
  letter-spacing: -0.02em;
}

.feature-desc {
  font-size: 14px;
  color: var(--color-ink-muted);
  line-height: 1.65;
}

/* ─── How it works ────────────────────────────────────────────────── */
.how-section {
  background: var(--color-paper);
  border-top: 1px solid var(--color-border);
}

.steps {
  display: flex;
  align-items: flex-start;
  gap: 0;
}

.step {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.step-num {
  font-family: var(--font-display);
  font-size: 56px;
  font-weight: 300;
  color: var(--color-accent);
  line-height: 1;
  letter-spacing: -0.04em;
  opacity: 0.6;
}

.step-title {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 500;
  color: var(--color-ink);
  letter-spacing: -0.025em;
  margin-bottom: 8px;
}

.step-desc {
  font-size: 15px;
  color: var(--color-ink-muted);
  line-height: 1.65;
  max-width: 260px;
}

.step-connector {
  width: 80px;
  height: 1px;
  background: var(--color-border);
  margin-top: 32px;
  flex-shrink: 0;
}

/* ─── Use cases ───────────────────────────────────────────────────── */
.usecases-section {
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
}

.usecases-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2px;
  border: 1px solid var(--color-border);
}

.usecase-card {
  background: var(--color-surface);
  padding: 32px 28px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: background 0.2s ease;
}

.usecase-card:hover { background: var(--color-paper); }

.uc-label {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 500;
  color: var(--color-ink);
  letter-spacing: -0.03em;
}

.uc-desc {
  font-size: 14px;
  color: var(--color-ink-muted);
  line-height: 1.65;
}

/* ─── Final CTA ───────────────────────────────────────────────────── */
.final-cta-section {
  background: var(--color-accent);
  border-top: 1px solid rgba(255,255,255,0.1);
}

.final-cta-inner {
  max-width: 700px;
  margin: 0 auto;
  padding: 100px 40px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
}

.final-brand-mark { color: white; margin-bottom: 28px; }

.final-cta-title {
  font-family: var(--font-display);
  font-size: clamp(36px, 5vw, 60px);
  font-weight: 300;
  color: #fff;
  letter-spacing: -0.04em;
  line-height: 1.05;
  margin-bottom: 18px;
}

.final-cta-sub {
  font-size: 16px;
  color: rgba(255,255,255,0.75);
  line-height: 1.6;
  max-width: 440px;
  margin-bottom: 44px;
}

.final-cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: #fff;
  color: var(--color-accent);
  text-decoration: none;
  font-family: var(--font-ui);
  font-size: 15px;
  font-weight: 700;
  padding: 15px 28px;
  border-radius: var(--radius-sm);
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  transition: transform 0.15s ease, box-shadow 0.2s ease;
}

.final-cta-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(0,0,0,0.2);
}

/* ─── Footer ──────────────────────────────────────────────────────── */
.site-footer {
  background: var(--color-ink);
  border-top: 1px solid rgba(255,255,255,0.06);
}

.footer-inner {
  max-width: 1160px;
  margin: 0 auto;
  padding: 32px 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255,255,255,0.5);
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 500;
  letter-spacing: -0.02em;
}

.footer-copy {
  font-size: 13px;
  color: rgba(255,255,255,0.35);
}

.footer-links {
  display: flex;
  gap: 20px;
}

.footer-link {
  font-size: 13px;
  color: rgba(255,255,255,0.45);
  text-decoration: none;
  transition: color 0.15s ease;
}

.footer-link:hover { color: rgba(255,255,255,0.85); }

/* ─── Responsive ──────────────────────────────────────────────────── */
@media (max-width: 900px) {
  .hero-section {
    grid-template-columns: 1fr;
    min-height: auto;
    padding: 60px 24px;
    gap: 40px;
  }

  .features-grid { grid-template-columns: 1fr 1fr; }
  .usecases-grid { grid-template-columns: 1fr 1fr; }

  .steps {
    flex-direction: column;
    gap: 32px;
  }

  .step-connector {
    width: 1px;
    height: 32px;
    margin-top: 0;
    margin-left: 24px;
  }

  .nav-inner { padding: 0 20px; }
  .section-inner { padding: 64px 24px; }
  .footer-inner { flex-direction: column; align-items: flex-start; gap: 12px; }
}

@media (max-width: 600px) {
  .features-grid { grid-template-columns: 1fr; }
  .usecases-grid { grid-template-columns: 1fr; }
  .nav-links .nav-link { display: none; }
  .proof-bar { gap: 8px 12px; }
  .proof-sep { display: none; }
}
</style>