<template>
  <div class="auth-container">
    <div class="auth-form-wrapper">
      <h1 class="auth-title">SIGN IN</h1>
      
      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label class="form-label">USERNAME OR EMAIL</label>
          <input
            v-model="credentials.username_or_email"
            type="text"
            class="form-input"
            placeholder="Enter your username or email"
            required
          />
        </div>
        
        <div class="form-group">
          <label class="form-label">PASSWORD</label>
          <input
            v-model="credentials.password"
            type="password"
            class="form-input"
            placeholder="Enter your password"
            required
          />
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <button type="submit" class="submit-button" :disabled="loading">
          {{ loading ? 'SIGNING IN...' : 'SIGN IN' }}
        </button>
      </form>
      
      <div class="auth-footer">
        <span class="footer-text">DON'T HAVE AN ACCOUNT?</span>
        <router-link to="/register" class="footer-link">REGISTER</router-link>
      </div>
      
      <div class="skip-auth">
        <router-link to="/rooms" class="skip-link">CONTINUE AS GUEST →</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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
    error.value = err.response?.data?.detail || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-deep-void);
}

.auth-form-wrapper {
  width: 100%;
  max-width: 500px;
  padding: 40px;
}

.auth-title {
  font-family: var(--font-display);
  font-size: 72px;
  font-weight: 800;
  color: var(--color-bone);
  margin-bottom: 60px;
  letter-spacing: -0.05em;
}

.auth-form {
  margin-bottom: 40px;
}

.form-group {
  margin-bottom: 32px;
}

.form-label {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--color-bone);
  text-transform: uppercase;
  display: block;
  margin-bottom: 12px;
  opacity: 0.6;
}

.form-input {
  width: 100%;
  background-color: var(--color-muted-obsidian);
  border: none;
  border-bottom: 2px solid var(--color-muted-obsidian);
  color: var(--color-bone);
  font-family: var(--font-system);
  font-size: 18px;
  padding: 16px 0;
  outline: none;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  border-bottom-color: var(--color-neon-cobalt);
}

.form-input::placeholder {
  color: var(--color-bone);
  opacity: 0.3;
}

.submit-button {
  width: 100%;
  background-color: var(--color-neon-cobalt);
  color: var(--color-deep-void);
  border: none;
  padding: 20px;
  font-family: var(--font-system);
  font-size: 16px;
  font-weight: 600;
  letter-spacing: -0.02em;
  cursor: pointer;
  transition: all 0.2s ease;
  text-transform: uppercase;
}

.submit-button:hover:not(:disabled) {
  background-color: var(--color-bone);
  transform: translateX(5px);
}

.submit-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-message {
  background-color: var(--color-acid-lime);
  color: var(--color-deep-void);
  padding: 16px;
  margin-bottom: 24px;
  font-family: var(--font-mono);
  font-size: 12px;
  text-transform: uppercase;
}

.auth-footer {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.footer-text {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--color-bone);
  opacity: 0.5;
  text-transform: uppercase;
}

.footer-link {
  font-family: var(--font-system);
  font-size: 16px;
  font-weight: 600;
  color: var(--color-neon-cobalt);
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-link:hover {
  color: var(--color-bone);
}

.skip-auth {
  margin-top: 60px;
  text-align: center;
}

.skip-link {
  font-family: var(--font-mono);
  font-size: 14px;
  color: var(--color-bone);
  opacity: 0.4;
  text-decoration: none;
  transition: opacity 0.2s ease;
}

.skip-link:hover {
  opacity: 1;
}
</style>
