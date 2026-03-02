/**
 * API Service - HTTP Client for SystemSketch Backend
 */
import axios, { type AxiosInstance, type AxiosError } from 'axios'
import type { 
  User, 
  Room, 
  LoginCredentials, 
  RegisterData, 
  AuthToken,
  PermissionLevel,
  Shape
} from '@/types'

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || '/api',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  async register(data: RegisterData): Promise<User> {
    const response = await this.client.post('/auth/register', data)
    return response.data
  }

  async login(credentials: LoginCredentials): Promise<AuthToken> {
    const formData = new FormData()
    formData.append('username', credentials.username_or_email)
    formData.append('password', credentials.password)
    
    const response = await this.client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    return response.data
  }

  async getMe(): Promise<User> {
    const response = await this.client.get('/auth/me')
    return response.data
  }

  async refreshToken(): Promise<AuthToken> {
    const response = await this.client.get('/auth/refresh')
    return response.data
  }

  // Room endpoints
  async createRoom(name: string): Promise<Room> {
    const response = await this.client.post('/rooms', { name })
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
