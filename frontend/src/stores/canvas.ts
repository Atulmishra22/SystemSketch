/**
 * Canvas Store - Canvas State and Real-time Collaboration
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { websocketService } from '@/services/websocket'
import { useAuthStore } from './auth'
import { useRoomStore } from './room'
import type {  Shape, ConnectedUser, CursorPosition, WSMessage, WSAction, ShapeType } from '@/types'

export const useCanvasStore = defineStore('canvas', () => {
  // State
  const shapes = ref<Shape[]>([])
  const connectedUsers = ref<Map<string, ConnectedUser>>(new Map())
  const cursors = ref<Map<string, CursorPosition>>(new Map())
  const selectedTool = ref<ShapeType | 'cursor' | 'pan'>('cursor')
  const selectedColor = ref('#2D5BFF') // Neon Cobalt
  const isDrawing = ref(false)
  const wsConnected = ref(false)
  const canvasScale = ref(1)
  const canvasOffset = ref({ x: 0, y: 0 })
  const mousePos = ref({ x: 0, y: 0 })

  // Getters
  const shapeCount = computed(() => shapes.value.length)
  const userCount = computed(() => connectedUsers.value.size)
  const canEdit = computed(() => {
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

  function removeShape(shapeId: string): void {
    shapes.value = shapes.value.filter(s => s.id !== shapeId)
  }

  function clearShapes(): void {
    shapes.value = []
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

  // WebSocket connection
  async function connectToRoom(roomId: string): Promise<void> {
    const authStore = useAuthStore()
    
    try {
      await websocketService.connect(
        roomId,
        authStore.token || undefined,
        authStore.username || undefined
      )
      
      wsConnected.value = true
      
      // Set up message handlers
      setupMessageHandlers()
    } catch (error) {
      console.error('Failed to connect to room:', error)
      throw error
    }
  }

  function disconnectFromRoom(): void {
    websocketService.disconnect()
    wsConnected.value = false
    connectedUsers.value.clear()
    cursors.value.clear()
  }

  function setupMessageHandlers(): void {
    // Sync state
    websocketService.on('sync_state' as WSAction, (message: WSMessage) => {
      if ('shapes' in message) {
        shapes.value = message.shapes
      }
    })

    // Draw shape
    websocketService.on('draw' as WSAction, (message: WSMessage) => {
      if ('shape' in message) {
        shapes.value.push(message.shape)
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

    // User joined
    websocketService.on('user_joined' as WSAction, (message: WSMessage) => {
      if ('userId' in message && 'username' in message && 'color' in message) {
        connectedUsers.value.set(message.userId, {
          userId: message.userId,
          username: message.username,
          color: message.color,
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
    // Getters
    shapeCount,
    userCount,
    canEdit,
    // Actions
    addShape,
    updateShape,
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
