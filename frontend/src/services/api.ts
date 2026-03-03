/**
 * API Service - HTTP Client for SystemSketch Backend
 */
import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import type { 
  User, 
  Room, 
  LoginCredentials, 
  RegisterData, 
  AuthToken,
  PermissionLevel,
  Shape
} from '@/types'

// ── Token refresh queue ──────────────────────────────────────────────────────
// Prevents multiple simultaneous calls to /auth/refresh when several requests
// hit 401 at the same time (e.g. on reconnect after a long absence).
let _isRefreshing = false
let _refreshQueue: Array<(token: string) => void> = []

function _enqueueRefresh(cb: (token: string) => void) {
  _refreshQueue.push(cb)
}

function _drainRefreshQueue(token: string) {
  _refreshQueue.forEach(cb => cb(token))
  _refreshQueue = []
}

function _abortRefreshQueue() {
  _refreshQueue = []
}
// ────────────────────────────────────────────────────────────────────────────


class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || '/api',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor — attach the current access token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Response interceptor — on 401 attempt a silent token refresh once,
    // then replay the original request.  Concurrent 401s are queued so only
    // one refresh call goes to the server.
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

        // Only intercept 401s that haven't already been retried
        if (error.response?.status === 401 && !original._retry) {
          const storedRefresh = localStorage.getItem('refresh_token')

          // No refresh token at all → go straight to login
          if (!storedRefresh) {
            this._forceLogout()
            return Promise.reject(error)
          }

          // Another in-flight refresh is happening — queue this request
          if (_isRefreshing) {
            return new Promise((resolve, reject) => {
              _enqueueRefresh((newToken) => {
                original.headers.Authorization = `Bearer ${newToken}`
                resolve(this.client(original))
              })
              // If the refresh ultimately fails the queue will be drained in
              // the catch block below and these promises will stay pending
              // until _abortRefreshQueue clears them — safe because the
              // force-logout redirect will unload the page.
            })
          }

          original._retry = true
          _isRefreshing = true

          try {
            // Exchange the refresh token for a new pair (server rotates it)
            const resp = await this.client.post('/auth/refresh', {
              refresh_token: storedRefresh,
            })
            const { access_token, refresh_token: new_refresh } = resp.data
            localStorage.setItem('access_token', access_token)
            localStorage.setItem('refresh_token', new_refresh)

            // Also keep the in-memory Pinia store in sync without importing
            // it here (avoids circular dependencies) — the store watches
            // localStorage on checkAuth; a storage event achieves the same
            // for cross-tab sync, but a direct patch is cleaner for same tab.
            // The store will re-sync on the next navigation or can listen on
            // 'storage' event.  Emitting a custom event is the lightest touch:
            window.dispatchEvent(new CustomEvent('token-refreshed', {
              detail: { access_token, refresh_token: new_refresh },
            }))

            // Replay queued requests with the new token
            _drainRefreshQueue(access_token)
            _isRefreshing = false

            original.headers.Authorization = `Bearer ${access_token}`
            return this.client(original)
          } catch {
            _isRefreshing = false
            _abortRefreshQueue()
            this._forceLogout()
            return Promise.reject(error)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  private _forceLogout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    window.location.href = '/login'
  }

  // Auth endpoints
  async register(data: RegisterData): Promise<AuthToken & { user: User }> {
    const response = await this.client.post('/auth/register', data)
    return response.data
  }

  async login(credentials: LoginCredentials): Promise<AuthToken> {
    const response = await this.client.post('/auth/login', {
      username: credentials.username_or_email,
      password: credentials.password,
    })
    return response.data
  }

  async getMe(): Promise<User> {
    const response = await this.client.get('/auth/me')
    return response.data
  }

  /** Exchange a refresh token for a new access + refresh pair. */
  async refreshToken(refreshToken: string): Promise<AuthToken> {
    const response = await this.client.post('/auth/refresh', { refresh_token: refreshToken })
    return response.data
  }

  // Room endpoints
  async createRoom(name: string, isPublic = true): Promise<Room> {
    const response = await this.client.post('/rooms', { name, is_public: isPublic })
    return response.data
  }

  async getRoom(roomId: string): Promise<{ id: string; name: string; shapes: Shape[] }> {
    const response = await this.client.get(`/rooms/${roomId}`)
    return response.data
  }

  async saveRoom(roomId: string, shapes: Shape[]): Promise<Room> {
    const response = await this.client.put(`/rooms/${roomId}/save`, { shapes })
    return response.data
  }

  async deleteRoom(roomId: string): Promise<void> {
    await this.client.delete(`/rooms/${roomId}`)
  }

  async renameRoom(roomId: string, name: string): Promise<Room> {
    const response = await this.client.patch(`/rooms/${roomId}`, { name })
    return response.data
  }

  async toggleRoomVisibility(roomId: string, isPublic: boolean): Promise<Room> {
    const response = await this.client.patch(`/rooms/${roomId}/visibility`, { is_public: isPublic })
    return response.data
  }

  async listRooms(limit = 10, offset = 0): Promise<Room[]> {
    const response = await this.client.get('/rooms', {
      params: { limit, offset }
    })
    return response.data
  }

  async listMyRooms(limit = 50, offset = 0): Promise<Room[]> {
    const response = await this.client.get('/users/me/rooms', {
      params: { limit, offset }
    })
    return response.data
  }

  // Permission endpoints
  async inviteUser(roomId: string, usernameOrEmail: string, permission: PermissionLevel): Promise<any> {
    const response = await this.client.post(`/permissions/rooms/${roomId}/invite`, {
      username_or_email: usernameOrEmail,
      permission
    })
    return response.data
  }

  async getRoomPermissions(roomId: string): Promise<any[]> {
    const response = await this.client.get(`/permissions/rooms/${roomId}`)
    return response.data
  }

  async updatePermission(roomId: string, userId: string, permission: PermissionLevel): Promise<any> {
    const response = await this.client.put(`/permissions/rooms/${roomId}/users/${userId}`, {
      permission
    })
    return response.data
  }

  async revokePermission(roomId: string, userId: string): Promise<void> {
    await this.client.delete(`/permissions/rooms/${roomId}/users/${userId}`)
  }

  async checkRoomAccess(roomId: string): Promise<{
    has_access: boolean
    permission?: PermissionLevel
    is_owner: boolean
  }> {
    const response = await this.client.get(`/permissions/rooms/${roomId}/check`)
    return response.data
  }
}

export const api = new ApiService()
