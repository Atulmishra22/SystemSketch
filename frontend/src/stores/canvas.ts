/**
 * Canvas Store - Canvas State and Real-time Collaboration
 */
import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'
import { websocketService } from '@/services/websocket'
import { useAuthStore } from './auth'
import { useRoomStore } from './room'
import type {  Shape, ConnectedUser, CursorPosition, WSMessage, WSAction, ShapeType } from '@/types'

// ─── localStorage persistence ────────────────────────────────────────────────
const STORAGE_PREFIX = 'ss:room:'
function storageKey(roomId: string) { return STORAGE_PREFIX + roomId }

function loadShapesFromStorage(roomId: string): Shape[] | null {
  try {
    const raw = localStorage.getItem(storageKey(roomId))
    if (!raw) return null
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : null
  } catch { return null }
}

function writeShapesToStorage(roomId: string, s: Shape[]) {
  try { localStorage.setItem(storageKey(roomId), JSON.stringify(s)) } catch { /* quota / private */ }
}

function deleteShapesFromStorage(roomId: string) {
  try { localStorage.removeItem(storageKey(roomId)) } catch { }
}
// ──────────────────────────────────────────────────────────────────────────────

export const useCanvasStore = defineStore('canvas', () => {
  // State
  const shapes = ref<Shape[]>([])
  const connectedUsers = ref<Map<string, ConnectedUser>>(new Map())
  const currentRoomId = ref('')
  const cursors = ref<Map<string, CursorPosition>>(new Map())
  const selectedTool = ref<ShapeType | 'cursor' | 'pan'>('cursor')
  const selectedColor = ref('#C0431F') // Warm brick accent
  const isDrawing = ref(false)
  // Derived from the WS service's reactive ref so it stays accurate on
  // reconnects and unexpected closes — no manual assignment needed.
  const wsConnected = computed(() => websocketService.connected.value)
  const canvasScale = ref(1)
  const canvasOffset = ref({ x: 0, y: 0 })
  const mousePos = ref({ x: 0, y: 0 })

  // Getters
  const shapeCount = computed(() => shapes.value.length)
  const userCount = computed(() => connectedUsers.value.size + 1) // +1 for self

  // Debounced auto-save — fires on any shapes change (push, replace, clear)
  let _saveTimer: ReturnType<typeof setTimeout> | null = null
  watch(
    shapes,
    () => {
      if (!currentRoomId.value) return
      if (_saveTimer) clearTimeout(_saveTimer)
      _saveTimer = setTimeout(
        () => writeShapesToStorage(currentRoomId.value, shapes.value),
        400
      )
    },
    { deep: true }
  )

  // Self-identity set by the server via room_users message
  const myUserId = ref<string | null>(null)
  const myCanEdit = ref<boolean | null>(null)  // null = not yet received from server
  const myColor = ref<string>('#C0431F')
  const myUsername = ref<string>('')

  // canEdit: use the server-confirmed value once WS has joined;
  // fall back to roomStore logic before the first room_users arrives.
  const canEdit = computed(() => {
    if (myCanEdit.value !== null) return myCanEdit.value
    const roomStore = useRoomStore()
    return roomStore.canEdit
  })

  // Actions
  function addShape(shape: Shape): void {
    shapes.value.push(shape)
    
    // Broadcast via WebSocket if connected
    if (wsConnected.value && canEdit.value) {
      websocketService.drawShape(shape)
    }
  }

  function updateShape(shapeId: string, updates: Partial<Shape>): void {
    const index = shapes.value.findIndex(s => s.id === shapeId)
    if (index !== -1) {
      shapes.value[index] = { ...shapes.value[index], ...updates }
    }
  }

  /** Broadcast a completed move to other users via WebSocket. */
  function broadcastMove(shapeId: string, updates: Partial<Shape>): void {
    if (wsConnected.value && canEdit.value) {
      websocketService.moveShape(shapeId, updates as Record<string, any>)
    }
  }

  function removeShape(shapeId: string): void {
    shapes.value = shapes.value.filter(s => s.id !== shapeId)
  }

  function clearShapes(): void {
    shapes.value = []
    if (currentRoomId.value) deleteShapesFromStorage(currentRoomId.value)
    if (wsConnected.value && canEdit.value) {
      websocketService.clearCanvas()
    }
  }

  function setShapes(newShapes: Shape[]): void {
    shapes.value = newShapes
  }

  function undo(): void {
    if (wsConnected.value && canEdit.value) {
      websocketService.undo()
    }
  }

  function redo(): void {
    if (wsConnected.value && canEdit.value) {
      websocketService.redo()
    }
  }

  function updateCursor(userId: string, x: number, y: number): void {
    if (wsConnected.value) {
      websocketService.moveCursor(x, y, userId)
    }
  }

  function setMousePosition(x: number, y: number): void {
    mousePos.value = { x, y }
  }

  // Prevent duplicate handler registration when connectToRoom() is called
  // multiple times (e.g. navigating away and back without a full disconnect).
  let _handlersRegistered = false

  // WebSocket connection
  async function connectToRoom(roomId: string): Promise<void> {
    const authStore = useAuthStore()

    // Preload cached shapes instantly (optimistic / offline-first)
    currentRoomId.value = roomId
    const cached = loadShapesFromStorage(roomId)
    if (cached) shapes.value = cached
    
    try {
      await websocketService.connect(
        roomId,
        authStore.token || undefined,
        authStore.username || undefined
      )
      
      // wsConnected is driven by websocketService.connected (reactive)
      // Set up message handlers (guarded against duplicate registration)
      if (!_handlersRegistered) {
        setupMessageHandlers()
        _handlersRegistered = true
      }
    } catch (error) {
      console.error('Failed to connect to room:', error)
      throw error
    }
  }

  function disconnectFromRoom(): void {
    websocketService.disconnect()
    // wsConnected updates automatically via websocketService.connected
    connectedUsers.value.clear()
    cursors.value.clear()
    myUserId.value = null
    myCanEdit.value = null
    myColor.value = '#C0431F'
    myUsername.value = ''
    currentRoomId.value = ''
    _handlersRegistered = false  // allow re-registration on next connectToRoom()
  }

  function setupMessageHandlers(): void {
    // Room users — sent once to the new joiner with self-identity + existing users
    websocketService.on('room_users' as WSAction, (message: WSMessage) => {
      if ('myUserId' in message) {
        myUserId.value = message.myUserId
        myCanEdit.value = message.canEdit
        myColor.value = message.myColor || '#C0431F'
        myUsername.value = message.myUsername || ''
      }
      if ('users' in message && Array.isArray(message.users)) {
        message.users.forEach((u: any) => {
          connectedUsers.value.set(u.userId, {
            userId: u.userId,
            username: u.username,
            color: u.color,
            canEdit: u.canEdit ?? false,
          })
        })
      }
    })

    // Sync state
    websocketService.on('sync_state' as WSAction, (message: WSMessage) => {
      if ('shapes' in message) {
        shapes.value = message.shapes
      }
    })

    // Draw shape — use spread to create a new array reference so any
    // watch(() => canvasStore.shapes) reliably fires for remote updates.
    websocketService.on('draw' as WSAction, (message: WSMessage) => {
      if ('shape' in message) {
        shapes.value = [...shapes.value, message.shape]
      }
    })

    // Cursor movement
    websocketService.on('cursor' as WSAction, (message: WSMessage) => {
      if ('userId' in message && 'x' in message && 'y' in message) {
        const user = connectedUsers.value.get(message.userId)
        if (user) {
          cursors.value.set(message.userId, {
            userId: message.userId,
            username: user.username,
            x: message.x,
            y: message.y,
            color: user.color,
          })
        }
      }
    })

    // User joined — include canEdit flag
    websocketService.on('user_joined' as WSAction, (message: WSMessage) => {
      if ('userId' in message && 'username' in message && 'color' in message) {
        connectedUsers.value.set(message.userId, {
          userId: message.userId,
          username: message.username,
          color: message.color,
          canEdit: message.canEdit ?? false,
        })
      }
    })

    // User left
    websocketService.on('user_left' as WSAction, (message: WSMessage) => {
      if ('userId' in message) {
        connectedUsers.value.delete(message.userId)
        cursors.value.delete(message.userId)
      }
    })

    // Clear canvas
    websocketService.on('clear' as WSAction, () => {
      shapes.value = []
    })

    // Remote shape move
    websocketService.on('move_shape' as WSAction, (message: WSMessage) => {
      if ('shapeId' in message && 'updates' in message) {
        const index = shapes.value.findIndex(s => s.id === message.shapeId)
        if (index !== -1) {
          shapes.value[index] = { ...shapes.value[index], ...message.updates }
        }
        // Trigger reactivity
        shapes.value = [...shapes.value]
      }
    })

    // Error
    websocketService.on('error' as WSAction, (message: WSMessage) => {
      console.error('WebSocket error:', message)
    })
  }

  function setTool(tool: ShapeType | 'cursor' | 'pan'): void {
    selectedTool.value = tool
  }

  function setColor(color: string): void {
    selectedColor.value = color
  }

  function zoom(delta: number): void {
    const newScale = canvasScale.value + delta
    canvasScale.value = Math.max(0.1, Math.min(5, newScale))
  }

  function pan(dx: number, dy: number): void {
    canvasOffset.value.x += dx
    canvasOffset.value.y += dy
  }

  function resetView(): void {
    canvasScale.value = 1
    canvasOffset.value = { x: 0, y: 0 }
  }

  return {
    // State
    shapes,
    connectedUsers,
    cursors,
    selectedTool,
    selectedColor,
    isDrawing,
    wsConnected,
    canvasScale,
    canvasOffset,
    mousePos,
    myUserId,
    myCanEdit,
    myColor,
    myUsername,
    // Getters
    shapeCount,
    userCount,
    canEdit,
    // Actions
    addShape,
    updateShape,
    broadcastMove,
    removeShape,
    clearShapes,
    setShapes,
    undo,
    redo,
    updateCursor,
    setMousePosition,
    connectToRoom,
    disconnectFromRoom,
    setTool,
    setColor,
    zoom,
    pan,
    resetView,
  }
})
