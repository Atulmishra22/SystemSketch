/**
 * Auth Store Tests
 * Tests authentication state management
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'

// Mock API service
vi.mock('@/services/api', () => ({
  api: {
    login: vi.fn(),
    register: vi.fn(),
    getMe: vi.fn(),
    refreshToken: vi.fn(),
  },
}))

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('initializes with correct default state', () => {
    const store = useAuthStore()
    
    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('handles successful login', async () => {
    const store = useAuthStore()
    const mockToken = { access_token: 'test-token', token_type: 'bearer' }
    const mockUser = { id: '1', username: 'testuser', email: 'test@example.com', created_at: new Date().toISOString() }

    vi.mocked(api.login).mockResolvedValue(mockToken)
    vi.mocked(api.getMe).mockResolvedValue(mockUser)

    await store.login({ username_or_email: 'testuser', password: 'password123' })

    expect(store.user).toEqual(mockUser)
    expect(store.token).toBe('test-token')
    expect(store.isAuthenticated).toBe(true)
    expect(localStorage.setItem).toHaveBeenCalledWith('access_token', 'test-token')
  })

  it('handles login failure', async () => {
    const store = useAuthStore()
    const error = { response: { data: { detail: 'Invalid credentials' } } }

    vi.mocked(api.login).mockRejectedValue(error)

    await expect(store.login({ 
      username_or_email: 'baduser', 
      password: 'wrongpass' 
    })).rejects.toThrow()

    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(store.error).toBe('Invalid credentials')
  })

  it('handles logout correctly', async () => {
    const store = useAuthStore()
    store.user = { id: '1', username: 'test', email: 'test@test.com', created_at: '' }
    store.token = 'test-token'

    await store.logout()

    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(localStorage.removeItem).toHaveBeenCalledWith('access_token')
    expect(localStorage.removeItem).toHaveBeenCalledWith('user')
  })

  it('restores auth from localStorage', async () => {
    const mockUser = { id: '1', username: 'test', email: 'test@test.com', created_at: '' }
    
    vi.mocked(localStorage.getItem).mockImplementation((key) => {
      if (key === 'access_token') return 'stored-token'
      if (key === 'user') return JSON.stringify(mockUser)
      return null
    })
    
    vi.mocked(api.getMe).mockResolvedValue(mockUser)

    const store = useAuthStore()
    await store.checkAuth()

    expect(store.token).toBe('stored-token')
    expect(store.user).toEqual(mockUser)
    expect(store.isAuthenticated).toBe(true)
  })

  it('clears auth when token is invalid', async () => {
    const store = useAuthStore()
    
    vi.mocked(localStorage.getItem).mockImplementation((key) => {
      if (key === 'access_token') return 'invalid-token'
      if (key === 'user') return JSON.stringify({ id: '1', username: 'test', email: 'test@test.com', created_at: '' })
      return null
    })
    
    vi.mocked(api.getMe).mockRejectedValue({ response: { status: 401 } })

    await store.checkAuth()

    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('computes username correctly', () => {
    const store = useAuthStore()
    
    expect(store.username).toBeNull()
    
    store.user = { id: '1', username: 'testuser', email: 'test@test.com', created_at: '' }
    expect(store.username).toBe('testuser')
  })
})
