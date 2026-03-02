<template>
  <div class="home-container">
    <!-- Empty State: Rynzhuk Edition -->
    <div class="empty-state">
      <h1 class="display-title">
        SKETCH THE FUTURE
        <span class="blinking-cursor">_</span>
      </h1>
      
      <div class="action-zone">
        <router-link to="/rooms" class="huge-link">
          EXPLORE ROOMS
        </router-link>
        
        <span class="divider">—</span>
        
        <router-link to="/login" class="huge-link">
          SIGN IN
        </router-link>
      </div>
      
      <!-- Coordinate display -->
      <div class="coordinates">
        <span class="coord-label">{{ mouseX }}</span>
        <span class="coord-separator">,</span>
        <span class="coord-label">{{ mouseY }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const mouseX = ref(0)
const mouseY = ref(0)

const updateMousePosition = (e: MouseEvent) => {
  mouseX.value = Math.floor(e.clientX)
  mouseY.value = Math.floor(e.clientY)
}

onMounted(() => {
  window.addEventListener('mousemove', updateMousePosition)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', updateMousePosition)
})
</script>

<style scoped>
.home-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-deep-void);
  position: relative;
  overflow: hidden;
}

.empty-state {
  text-align: center;
  position: relative;
  z-index: 1;
}

.display-title {
  font-family: var(--font-display);
  font-size: 200px;
  font-weight: 800;
  color: var(--color-bone);
  line-height: 0.85;
  letter-spacing: -0.05em;
  margin-bottom: 80px;
}

.blinking-cursor {
  animation: blink 1s infinite;
  color: var(--color-neon-cobalt);
}

@keyframes blink {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0; }
}

.action-zone {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
  margin-bottom: 40px;
}

.huge-link {
  font-family: var(--font-system);
  font-size: 32px;
  font-weight: 600;
  color: var(--color-bone);
  text-decoration: none;
  letter-spacing: -0.04em;
  transition: color 0.2s ease;
  position: relative;
}

.huge-link::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 0;
  height: 2px;
  background-color: var(--color-neon-cobalt);
  transition: width 0.3s ease;
}

.huge-link:hover {
  color: var(--color-neon-cobalt);
}

.huge-link:hover::after {
  width: 100%;
}

.divider {
  color: var(--color-muted-obsidian);
  font-size: 32px;
}

.coordinates {
  position: fixed;
  bottom: 40px;
  right: 40px;
  font-family: var(--font-mono);
  font-size: 14px;
  color: var(--color-bone);
  opacity: 0.3;
}

.coord-label, .coord-separator {
  display: inline-block;
  text-transform: uppercase;
}

.coord-separator {
  margin: 0 8px;
}

@media (max-width: 1024px) {
  .display-title {
    font-size: 80px;
  }
  
  .huge-link {
    font-size: 24px;
  }
}
</style>
