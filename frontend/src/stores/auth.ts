/**
 * Auth Store - User Authentication State
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/services/api'
import type { User, LoginCredentials, RegisterData } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!user.value && !!token.value)
  const username = computed(() => user.value?.username || null)

  // Actions
  async function login(credentials: LoginCredentials): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const authToken = await api.login(credentials)
      token.value = authToken.access_token
      localStorage.setItem('access_token', authToken.access_token)

      // Fetch user details
      const userData = await api.getMe()
      user.value = userData
      localStorage.setItem('user', JSON.stringify(userData))
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function register(data: RegisterData): Promise<void> {
    loading.value = true
    error.value = null

    try {
      await api.register(data)
      // Auto-login after registration
      await login({
        username_or_email: data.username,
        password: data.password
      })
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout(): Promise<void> {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  async function checkAuth(): Promise<void> {
    const storedToken = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      token.value = storedToken
      user.value = JSON.parse(storedUser)

      // Verify token is still valid
      try {
        const userData = await api.getMe()
        user.value = userData
        localStorage.setItem('user', JSON.stringify(userData))
      } catch (err) {
        // Token invalid, clear auth
        await logout()
      }
    }
  }

  async function refreshToken(): Promise<void> {
    try {
      const authToken = await api.refreshToken()
      token.value = authToken.access_token
      localStorage.setItem('access_token', authToken.access_token)
    } catch (err) {
      await logout()
      throw err
    }
  }

  return {
    // State
    user,
    token,
    loading,
    error,
    // Getters
    isAuthenticated,
    username,
    // Actions
    login,
    register,
    logout,
    checkAuth,
    refreshToken,
  }
})
