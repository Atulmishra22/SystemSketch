<template>
  <div class="auth-container">
    <div class="auth-form-wrapper">
      <h1 class="auth-title">REGISTER</h1>
      
      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label class="form-label">USERNAME</label>
          <input
            v-model="formData.username"
            type="text"
            class="form-input"
            placeholder="Choose a username"
            required
          />
        </div>
        
        <div class="form-group">
          <label class="form-label">EMAIL</label>
          <input
            v-model="formData.email"
            type="email"
            class="form-input"
            placeholder="Enter your email"
            required
          />
        </div>
        
        <div class="form-group">
          <label class="form-label">PASSWORD</label>
          <input
            v-model="formData.password"
            type="password"
            class="form-input"
            placeholder="Create a password"
            required
          />
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <button type="submit" class="submit-button" :disabled="loading">
          {{ loading ? 'CREATING ACCOUNT...' : 'CREATE ACCOUNT' }}
        </button>
      </form>
      
      <div class="auth-footer">
        <span class="footer-text">ALREADY HAVE AN ACCOUNT?</span>
        <router-link to="/login" class="footer-link">SIGN IN</router-link>
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

const formData = ref({
  username: '',
  email: '',
  password: '',
})

const loading = ref(false)
const error = ref('')

async function handleRegister() {
  loading.value = true
  error.value = ''
  
  try {
    await authStore.register(formData.value)
    router.push({ name: 'rooms' })
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Registration failed'
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
</style>
