/**
 * Room Store - Room Management State
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/services/api'
import type { Room } from '@/types'
import { PermissionLevel } from '@/types'

export const useRoomStore = defineStore('room', () => {
  // State
  const currentRoom = ref<Room | null>(null)
  const myRooms = ref<Room[]>([])
  const publicRooms = ref<Room[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const roomId = computed(() => currentRoom.value?.id || null)
  const roomName = computed(() => currentRoom.value?.name || '')
  const isRoomOwner = computed(() => currentRoom.value?.is_owner || false)
  const userPermission = computed(() => currentRoom.value?.user_permission || null)
  const canEdit = computed(() => {
    if (!currentRoom.value?.user_permission) return currentRoom.value?.permission_level === 'public'
    return currentRoom.value.user_permission === PermissionLevel.OWNER || 
           currentRoom.value.user_permission === PermissionLevel.EDITOR
  })

  // Actions
  async function createRoom(name: string): Promise<Room> {
    loading.value = true
    error.value = null

    try {
      const room = await api.createRoom(name)
      currentRoom.value = room
      
      // Add to myRooms if not already there
      if (!myRooms.value.find(r => r.id === room.id)) {
        myRooms.value.unshift(room)
      }
      
      return room
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create room'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function loadRoom(roomId: string): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const roomData = await api.getRoom(roomId)
      
      // Get room metadata from list if available
      const existingRoom = myRooms.value.find(r => r.id === roomId) || 
                          publicRooms.value.find(r => r.id === roomId)
      
      if (existingRoom) {
        currentRoom.value = existingRoom
      } else {
        // Create minimal room object
        currentRoom.value = {
          id: roomData.id,
          name: roomData.name,
          is_saved: true,
          created_at: new Date().toISOString(),
          last_activity: new Date().toISOString(),
          permission_level: 'public',
        }
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to load room'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function saveRoom(shapes: unknown[]): Promise<void> {
    if (!currentRoom.value) {
      throw new Error('No active room')
    }

    loading.value = true
    error.value = null

    try {
      const updated = await api.saveRoom(currentRoom.value.id, shapes)
      currentRoom.value = { ...currentRoom.value, ...updated }
      
      // Update in myRooms list
      const index = myRooms.value.findIndex(r => r.id === updated.id)
      if (index !== -1) {
        myRooms.value[index] = updated
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to save room'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteRoom(roomId: string): Promise<void> {
    loading.value = true
    error.value = null

    try {
      await api.deleteRoom(roomId)
      
      // Remove from lists
      myRooms.value = myRooms.value.filter(r => r.id !== roomId)
      publicRooms.value = publicRooms.value.filter(r => r.id !== roomId)
      
      if (currentRoom.value?.id === roomId) {
        currentRoom.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete room'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function loadMyRooms(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      myRooms.value = await api.listMyRooms()
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to load rooms'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function loadPublicRooms(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      publicRooms.value = await api.listRooms()
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to load public rooms'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function inviteUser(usernameOrEmail: string, permission: PermissionLevel): Promise<void> {
    if (!currentRoom.value) {
      throw new Error('No active room')
    }

    try {
      await api.inviteUser(currentRoom.value.id, usernameOrEmail, permission)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to invite user'
      throw err
    }
  }

  function clearCurrentRoom(): void {
    currentRoom.value = null
  }

  return {
    // State
    currentRoom,
    myRooms,
    publicRooms,
    loading,
    error,
    // Getters
    roomId,
    roomName,
    isRoomOwner,
    userPermission,
    canEdit,
    // Actions
    createRoom,
    loadRoom,
    saveRoom,
    deleteRoom,
    loadMyRooms,
    loadPublicRooms,
    inviteUser,
    clearCurrentRoom,
  }
})
