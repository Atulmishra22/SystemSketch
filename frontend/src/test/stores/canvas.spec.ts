/**
 * Canvas Store Tests
 * Tests canvas state and WebSocket collaboration
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useCanvasStore } from '@/stores/canvas'
import { useRoomStore } from '@/stores/room'
import { websocketService } from '@/services/websocket'
import { ShapeType, PermissionLevel, type Shape, type Rectangle } from '@/types'

vi.mock('@/services/websocket', () => ({
  websocketService: {
    connect: vi.fn(),
    disconnect: vi.fn(),
    on: vi.fn(),
    off: vi.fn(),
    send: vi.fn(),
    drawShape: vi.fn(),
    clearCanvas: vi.fn(),
    moveCursor: vi.fn(),
    undo: vi.fn(),
    redo: vi.fn(),
  },
}))

vi.mock('@/services/api', () => ({
  api: {
    getRoom: vi.fn(),
    createRoom: vi.fn(),
    saveRoom: vi.fn(),
  },
}))

describe('Canvas Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    
    // Setup room store with edit permissions
    const roomStore = useRoomStore()
    roomStore.currentRoom = {
      id: 'test-room',
      name: 'Test Room',
      is_saved: false,
      created_at: '',
      last_activity: '',
      permission_level: 'public',
      user_permission: PermissionLevel.OWNER, // Give owner permissions for tests
    }
  })

  it('initializes with correct default state', () => {
    const store = useCanvasStore()
    
    expect(store.shapes).toEqual([])
    expect(store.connectedUsers.size).toBe(0)
    expect(store.cursors.size).toBe(0)
    expect(store.selectedTool).toBe('cursor')
    expect(store.selectedColor).toBe('#2D5BFF')
    expect(store.wsConnected).toBe(false)
    expect(store.canvasScale).toBe(1)
    expect(store.canvasOffset).toEqual({ x: 0, y: 0 })
  })

  it('adds a shape', () => {
    const store = useCanvasStore()
    // Enable WebSocket for broadcasting
    store.wsConnected = true
    
    const shape: Rectangle = {
      id: 'shape-1',
      type: ShapeType.RECTANGLE,
      x: 100,
      y: 100,
      width: 200,
      height: 150,
      fill: '#2D5BFF',
      stroke: '#F2F2F2',
      strokeWidth: 2,
    }

    store.addShape(shape)

    expect(store.shapes).toHaveLength(1)
    expect(store.shapes[0]).toEqual(shape)
    expect(vi.mocked(websocketService.drawShape)).toHaveBeenCalledWith(shape)
  })

  it('updates a shape', () => {
    const store = useCanvasStore()
    const originalShape: Rectangle = {
      id: 'shape-1',
      type: ShapeType.RECTANGLE,
      x: 100,
      y: 100,
      width: 200,
      height: 150,
      fill: '#2D5BFF',
      stroke: '#F2F2F2',
      strokeWidth: 2,
    }

    store.shapes = [originalShape]

    store.updateShape('shape-1', { x: 150, y: 150 })

    expect(store.shapes[0]?.x).toBe(150)
    expect(store.shapes[0]?.y).toBe(150)
  })

  it('removes a shape', () => {
    const store = useCanvasStore()
    const shape: Rectangle = {
      id: 'shape-1',
      type: ShapeType.RECTANGLE,
      x: 100,
      y: 100,
      width: 200,
      height: 150,
      fill: '#2D5BFF',
      stroke: '#F2F2F2',
      strokeWidth: 2,
    }

    store.shapes = [shape]
    store.removeShape('shape-1')

    expect(store.shapes).toHaveLength(0)
  })

  it('clears all shapes', () => {
    const store = useCanvasStore()
    // Enable WebSocket for broadcasting
    store.wsConnected = true
    
    const shapes: Shape[] = [
      {
        id: 'shape-1',
        type: ShapeType.RECTANGLE,
        x: 0,
        y: 0,
        width: 100,
        height: 100,
        fill: '#2D5BFF',
        stroke: '#F2F2F2',
        strokeWidth: 2,
      },
      {
        id: 'shape-2',
        type: ShapeType.CIRCLE,
        x: 200,
        y: 200,
        radius: 50,
        fill: '#D1FF1A',
        stroke: '#F2F2F2',
        strokeWidth: 2,
      },
    ]

    store.shapes = [...shapes]
    store.clearShapes()

    expect(store.shapes).toEqual([])
    expect(vi.mocked(websocketService.clearCanvas)).toHaveBeenCalled()
  })

  it('updates cursor position', () => {
    const store = useCanvasStore()
    store.wsConnected = true
    
    store.updateCursor('user-1', 100, 200)

    expect(vi.mocked(websocketService.moveCursor)).toHaveBeenCalledWith(100, 200, 'user-1')
  })

  it('zooms in', () => {
    const store = useCanvasStore()
    const initialScale = store.canvasScale

    store.zoom(1.2)

    expect(store.canvasScale).toBeGreaterThan(initialScale)
  })

  it('pans canvas', () => {
    const store = useCanvasStore()

    store.pan(50, 100)

    expect(store.canvasOffset).toEqual({ x: 50, y: 100 })
  })

  it('connects to room WebSocket', async () => {
    const store = useCanvasStore()
    const roomId = 'room-1'

    vi.mocked(websocketService.connect).mockResolvedValue()

    await store.connectToRoom(roomId)

    expect(vi.mocked(websocketService.connect)).toHaveBeenCalled()
    expect(vi.mocked(websocketService.on)).toHaveBeenCalledWith('sync_state', expect.any(Function))
    expect(vi.mocked(websocketService.on)).toHaveBeenCalledWith('draw', expect.any(Function))
    expect(vi.mocked(websocketService.on)).toHaveBeenCalledWith('cursor', expect.any(Function))
    expect(vi.mocked(websocketService.on)).toHaveBeenCalledWith('user_joined', expect.any(Function))
    expect(vi.mocked(websocketService.on)).toHaveBeenCalledWith('user_left', expect.any(Function))
  })

  it('disconnects from room', () => {
    const store = useCanvasStore()

    store.disconnectFromRoom()

    expect(vi.mocked(websocketService.disconnect)).toHaveBeenCalled()
    expect(store.connectedUsers.size).toBe(0)
    expect(store.cursors.size).toBe(0)
    expect(store.wsConnected).toBe(false)
  })

  it('handles undo action', () => {
    const store = useCanvasStore()
    store.wsConnected = true

    store.undo()

    expect(vi.mocked(websocketService.undo)).toHaveBeenCalled()
  })

  it('handles redo action', () => {
    const store = useCanvasStore()
    store.wsConnected = true

    store.redo()

    expect(vi.mocked(websocketService.redo)).toHaveBeenCalled()
  })

  it('selects a tool', () => {
    const store = useCanvasStore()

    store.selectedTool = ShapeType.RECTANGLE

    expect(store.selectedTool).toBe(ShapeType.RECTANGLE)
  })

  it('selects a color', () => {
    const store = useCanvasStore()

    store.selectedColor = '#D1FF1A'

    expect(store.selectedColor).toBe('#D1FF1A')
  })
})
