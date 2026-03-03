/**
 * Auth Store - User Authentication State
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/services/api'
import type { User, LoginCredentials, RegisterData } from '@/types'
import { parseApiError } from '@/utils/errors'

// Fire a proactive silent refresh at 80 % of the access-token lifetime so
// users working continuously are never interrupted.  The backend default is
// 30 min → proactive refresh every 24 min.
const ACCESS_TOKEN_EXPIRE_MINUTES = 30
const PROACTIVE_REFRESH_RATIO = 0.8
const PROACTIVE_REFRESH_MS = ACCESS_TOKEN_EXPIRE_MINUTES * PROACTIVE_REFRESH_RATIO * 60 * 1000

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Internal timer handle — module-scoped so it survives Pinia HMR reloads
  let _proactiveTimer: ReturnType<typeof setTimeout> | null = null

  // Getters
  const isAuthenticated = computed(() => !!user.value && !!token.value)
  const username = computed(() => user.value?.username || null)

  // ── Token storage helpers ────────────────────────────────────────────────
  function _persistTokens(accessToken: string, refreshToken: string) {
    token.value = accessToken
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshToken)
  }

  function _clearTokens() {
    token.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  // ── Proactive refresh timer ──────────────────────────────────────────────
  /**
   * Schedule a silent token refresh to fire before the access token expires.
   * Called after every successful login, register, checkAuth, or refresh.
   * Cancels any previously scheduled timer before setting a new one to
   * prevent duplicate refreshes.
   */
  function _scheduleProactiveRefresh() {
    if (_proactiveTimer) clearTimeout(_proactiveTimer)
    _proactiveTimer = setTimeout(async () => {
      try {
        await refreshToken()
        // refreshToken() calls _scheduleProactiveRefresh() on success,
        // so the timer re-arms itself automatically.
      } catch {
        // Refresh failed → the axios interceptor in api.ts will handle the
        // next 401 or we'll catch it on the next user action.  Either way
        // we don't force-logout here because the user may still have a valid
        // session (e.g. server temporarily unreachable).
      }
    }, PROACTIVE_REFRESH_MS)
  }

  function _cancelProactiveRefresh() {
    if (_proactiveTimer) {
      clearTimeout(_proactiveTimer)
      _proactiveTimer = null
    }
  }

  // ── Actions ──────────────────────────────────────────────────────────────
  async function login(credentials: LoginCredentials): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const authToken = await api.login(credentials)
      _persistTokens(authToken.access_token, authToken.refresh_token)

      const userData = await api.getMe()
      user.value = userData
      localStorage.setItem('user', JSON.stringify(userData))

      _scheduleProactiveRefresh()
    } catch (err: unknown) {
      error.value = parseApiError(err, 'Login failed')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function register(data: RegisterData): Promise<void> {
    loading.value = true
    error.value = null

    try {
      // Backend returns tokens + user on register — use them directly (no second round-trip)
      const authToken = await api.register(data)
      _persistTokens(authToken.access_token, authToken.refresh_token)
      user.value = authToken.user
      localStorage.setItem('user', JSON.stringify(authToken.user))
      _scheduleProactiveRefresh()
    } catch (err: unknown) {
      error.value = parseApiError(err, 'Registration failed')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout(): Promise<void> {
    _cancelProactiveRefresh()
    user.value = null
    _clearTokens()
  }

  async function checkAuth(): Promise<void> {
    const storedToken = localStorage.getItem('access_token')
    const storedRefresh = localStorage.getItem('refresh_token')
    const storedUser = localStorage.getItem('user')

    if (!storedToken || !storedUser) return

    token.value = storedToken
    user.value = JSON.parse(storedUser)

    // Verify the access token is still good; if the server returns 401 the
    // axios interceptor will transparently refresh it using the stored
    // refresh token before this resolves.
    try {
      const userData = await api.getMe()
      user.value = userData
      localStorage.setItem('user', JSON.stringify(userData))
      // Re-arm the proactive timer now that we know tokens are valid
      if (storedRefresh) _scheduleProactiveRefresh()
    } catch {
      // Both the access-token check AND the silent refresh inside the axios
      // interceptor failed — clear everything and let the router redirect.
      _cancelProactiveRefresh()
      _clearTokens()
      user.value = null
    }
  }

  async function refreshToken(): Promise<void> {
    const storedRefresh = localStorage.getItem('refresh_token')
    if (!storedRefresh) throw new Error('No refresh token stored')

    const authToken = await api.refreshToken(storedRefresh)
    _persistTokens(authToken.access_token, authToken.refresh_token)

    // Keep in-memory user in sync if the server sent updated user data
    const anyToken = authToken as any
    if (anyToken.user) {
      user.value = anyToken.user
      localStorage.setItem('user', JSON.stringify(anyToken.user))
    }

    _scheduleProactiveRefresh()
  }

  // ── Cross-tab / interceptor sync ─────────────────────────────────────────
  // The axios interceptor in api.ts dispatches 'token-refreshed' when it
  // silently refreshes tokens on a 401.  We listen here so the Pinia store
  // stays consistent without a circular dependency on the store from api.ts.
  function _handleTokenRefreshedEvent(e: Event) {
    const { access_token, refresh_token } = (e as CustomEvent).detail
    _persistTokens(access_token, refresh_token)
    _scheduleProactiveRefresh()
  }
  window.addEventListener('token-refreshed', _handleTokenRefreshedEvent)

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

