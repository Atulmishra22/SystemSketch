/**
 * Room Store Tests
 * Tests room management state
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useRoomStore } from '@/stores/room'
import { api } from '@/services/api'
import { PermissionLevel } from '@/types'

vi.mock('@/services/api', () => ({
  api: {
    createRoom: vi.fn(),
    getRoom: vi.fn(),
    saveRoom: vi.fn(),
    deleteRoom: vi.fn(),
    listMyRooms: vi.fn(),
    listRooms: vi.fn(),
    inviteUser: vi.fn(),
  },
}))

describe('Room Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initializes with correct default state', () => {
    const store = useRoomStore()
    
    expect(store.currentRoom).toBeNull()
    expect(store.myRooms).toEqual([])
    expect(store.publicRooms).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('creates a new room', async () => {
    const store = useRoomStore()
    const mockRoom = {
      id: 'room-1',
      name: 'Test Room',
      is_saved: false,
      created_at: new Date().toISOString(),
      last_activity: new Date().toISOString(),
      permission_level: 'public',
    }

    vi.mocked(api.createRoom).mockResolvedValue(mockRoom)

    const result = await store.createRoom('Test Room')

    expect(result).toEqual(mockRoom)
    expect(store.currentRoom).toEqual(mockRoom)
    expect(store.myRooms).toContainEqual(mockRoom)
  })

  it('loads a room', async () => {
    const store = useRoomStore()
    const mockRoomData = {
      id: 'room-1',
      name: 'Test Room',
      shapes: [],
    }

    vi.mocked(api.getRoom).mockResolvedValue(mockRoomData)

    await store.loadRoom('room-1')

    expect(store.currentRoom).toBeDefined()
    expect(store.currentRoom?.id).toBe('room-1')
  })

  it('saves room state', async () => {
    const store = useRoomStore()
    store.currentRoom = {
      id: 'room-1',
      name: 'Test Room',
      is_saved: false,
      created_at: '',
      last_activity: '',
      permission_level: 'public',
    }

    const mockUpdated = { ...store.currentRoom, is_saved: true }
    vi.mocked(api.saveRoom).mockResolvedValue(mockUpdated)

    await store.saveRoom([])

    expect(store.currentRoom?.is_saved).toBe(true)
  })

  it('deletes a room', async () => {
    const store = useRoomStore()
    const roomId = 'room-1'
    
    store.myRooms = [{
      id: roomId,
      name: 'Test Room',
      is_saved: false,
      created_at: '',
      last_activity: '',
      permission_level: 'public',
    }]

    vi.mocked(api.deleteRoom).mockResolvedValue()

    await store.deleteRoom(roomId)

    expect(store.myRooms).not.toContainEqual(expect.objectContaining({ id: roomId }))
  })

  it('computes canEdit correctly for owner', () => {
    const store = useRoomStore()
    
    store.currentRoom = {
      id: 'room-1',
      name: 'Test Room',
      is_saved: false,
      created_at: '',
      last_activity: '',
      permission_level: 'public',
      user_permission: PermissionLevel.OWNER,
    }

    expect(store.canEdit).toBe(true)
  })

  it('computes canEdit correctly for editor', () => {
    const store = useRoomStore()
    
    store.currentRoom = {
      id: 'room-1',
      name: 'Test Room',
      is_saved: false,
      created_at: '',
      last_activity: '',
      permission_level: 'private',
      user_permission: PermissionLevel.EDITOR,
    }

    expect(store.canEdit).toBe(true)
  })

  it('computes canEdit correctly for viewer', () => {
    const store = useRoomStore()
    
    store.currentRoom = {
      id: 'room-1',
      name: 'Test Room',
      is_saved: false,
      created_at: '',
      last_activity: '',
      permission_level: 'private',
      user_permission: PermissionLevel.VIEWER,
    }

    expect(store.canEdit).toBe(false)
  })

  it('loads my rooms', async () => {
    const store = useRoomStore()
    const mockRooms = [
      { id: 'room-1', name: 'Room 1', is_saved: true, created_at: '', last_activity: '', permission_level: 'public' },
      { id: 'room-2', name: 'Room 2', is_saved: false, created_at: '', last_activity: '', permission_level: 'public' },
    ]

    vi.mocked(api.listMyRooms).mockResolvedValue(mockRooms)

    await store.loadMyRooms()

    expect(store.myRooms).toEqual(mockRooms)
  })

  it('invites user to room', async () => {
    const store = useRoomStore()
    store.currentRoom = {
      id: 'room-1',
      name: 'Test Room',
      is_saved: false,
      created_at: '',
      last_activity: '',
      permission_level: 'public',
    }

    vi.mocked(api.inviteUser).mockResolvedValue({})

    await expect(
      store.inviteUser('user@example.com', PermissionLevel.EDITOR)
    ).resolves.not.toThrow()
  })

  it('throws error when inviting without active room', async () => {
    const store = useRoomStore()

    await expect(
      store.inviteUser('user@example.com', PermissionLevel.EDITOR)
    ).rejects.toThrow('No active room')
  })
})
