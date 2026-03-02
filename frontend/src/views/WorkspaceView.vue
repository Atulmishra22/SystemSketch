<template>
  <div class="workspace-container">
    <!-- Vertical Room Name (Left Side) -->
    <div class="room-name-vertical">
      <span>{{ roomStore.roomName || 'UNTITLED' }}</span>
    </div>

    <!-- Canvas Area -->
    <div class="canvas-wrapper" ref="canvasContainer">
      <canvas
        ref="mainCanvas"
        @mousedown="handleMouseDown"
        @mousemove="handleMouseMove"
        @mouseup="handleMouseUp"
        @wheel="handleWheel"
      ></canvas>

      <!-- Mouse Coordinates Display (Corners) -->
      <div class="coordinates top-left">
        <span>{{ Math.floor(canvasStore.mousePos.x) }},{{ Math.floor(canvasStore.mousePos.y) }}</span>
      </div>
    </div>

    <!-- Modular Vertical Toolbar (Left Side) -->
    <div class="vertical-toolbar">
      <div
        v-for="tool in tools"
        :key="tool.id"
        class="tool-item"
        :class="{ active: canvasStore.selectedTool === tool.id }"
        @click="canvasStore.setTool(tool.id)"
      >
        <span class="tool-icon">{{ tool.icon }}</span>
      </div>

      <div class="toolbar-divider"></div>

      <div class="tool-item" @click="canvasStore.undo()">
        <span class="tool-icon">↶</span>
      </div>

      <div class="tool-item" @click="canvasStore.redo()">
        <span class="tool-icon">↷</span>
      </div>

      <div class="tool-item" @click="saveCanvas">
        <span class="tool-icon">💾</span>
      </div>
    </div>

    <!-- User Orbit (Bottom Right) -->
    <div class="user-orbit">
      <div v-for="user in connectedUsersArray" :key="user.userId" class="user-entry">
        <div class="user-color-dot" :style="{ backgroundColor: user.color }"></div>
        <span class="user-name">{{ user.username || `USER-${user.userId.slice(0, 4)}` }}</span>
      </div>
    </div>

    <!-- Invite Button (Top Right) -->
    <div class="invite-zone">
      <button v-if="roomStore.isRoomOwner" @click="showInviteModal = true" class="huge-invite-link">
        INVITE
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-text">LOADING WORKSPACE...</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCanvasStore } from '@/stores/canvas'
import { useRoomStore } from '@/stores/room'
import { api } from '@/services/api'
import { ShapeType } from '@/types'
import type { Shape } from '@/types'

const route = useRoute()
const router = useRouter()
const canvasStore = useCanvasStore()
const roomStore = useRoomStore()

const roomId = ref(route.params.roomId as string)
const loading = ref(true)
const showInviteModal = ref(false)
const mainCanvas = ref<HTMLCanvasElement | null>(null)
const canvasContainer = ref<HTMLDivElement | null>(null)

const tools: Array<{ id: ShapeType | 'cursor' | 'pan'; icon: string }> = [
  { id: 'cursor', icon: '⚐' },
  { id: 'rectangle', icon: '▭' },
  { id: 'circle', icon: '○' },
  { id: 'arrow', icon: '→' },
  { id: 'text', icon: 'T' },
]

const connectedUsersArray = computed(() => {
  return Array.from(canvasStore.connectedUsers.values())
})

let ctx: CanvasRenderingContext2D | null = null
let isDrawing = false
let startX = 0
let startY = 0

onMounted(async () => {
  loading.value = true

  try {
    // Load room data
    await roomStore.loadRoom(roomId.value)

    // Load room state
    const roomData = await api.getRoom(roomId.value)
    canvasStore.setShapes(roomData.shapes || [])

    // Connect to WebSocket
    await canvasStore.connectToRoom(roomId.value)

    // Initialize canvas
    initCanvas()
  } catch (error) {
    console.error('Failed to load workspace:', error)
    router.push({ name: 'rooms' })
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  canvasStore.disconnectFromRoom()
})

function initCanvas() {
  if (!mainCanvas.value || !canvasContainer.value) return

  const canvas = mainCanvas.value
  const container = canvasContainer.value

  canvas.width = container.clientWidth
  canvas.height = container.clientHeight

  ctx = canvas.getContext('2d')
  if (ctx) {
    ctx.fillStyle = '#080808'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
  }

  // Draw grid
  drawGrid()

  // Draw existing shapes
  drawShapes()

  // Redraw on window resize
  window.addEventListener('resize', handleResize)
}

function handleResize() {
  if (!mainCanvas.value || !canvasContainer.value) return

  const canvas = mainCanvas.value
  const container = canvasContainer.value

  canvas.width = container.clientWidth
  canvas.height = container.clientHeight

  drawGrid()
  drawShapes()
}

function drawGrid() {
  if (!ctx || !mainCanvas.value) return

  const canvas = mainCanvas.value
  ctx.strokeStyle = '#1A1A1A'
  ctx.lineWidth = 1

  const gridSize = 50

  for (let x = 0; x < canvas.width; x += gridSize) {
    for (let y = 0; y < canvas.height; y += gridSize) {
      ctx.fillStyle = '#1A1A1A'
      ctx.fillRect(x, y, 2, 2)
    }
  }
}

function drawShapes() {
  if (!ctx || !mainCanvas.value) return

  const canvas = mainCanvas.value

  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.fillStyle = '#080808'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  drawGrid()

  canvasStore.shapes.forEach((shape) => {
    if (shape.type === 'rectangle') {
      ctx!.strokeStyle = shape.stroke || '#2D5BFF'
      ctx!.lineWidth = shape.strokeWidth || 2
      ctx!.strokeRect(shape.x, shape.y, shape.width || 100, shape.height || 100)
    } else if (shape.type === 'circle') {
      ctx!.beginPath()
      ctx!.arc(shape.x, shape.y, shape.radius || 50, 0, 2 * Math.PI)
      ctx!.strokeStyle = shape.stroke || '#2D5BFF'
      ctx!.lineWidth = shape.strokeWidth || 2
      ctx!.stroke()
    }
  })
}

function handleMouseDown(e: MouseEvent) {
  if (!canvasStore.canEdit) return

  isDrawing = true
  const rect = mainCanvas.value?.getBoundingClientRect()
  if (!rect) return

  startX = e.clientX - rect.left
  startY = e.clientY - rect.top
}

function handleMouseMove(e: MouseEvent) {
  const rect = mainCanvas.value?.getBoundingClientRect()
  if (!rect) return

  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  canvasStore.setMousePosition(x, y)

  if (!isDrawing || !canvasStore.canEdit) return

  // Preview shape while drawing
  drawShapes()

  if (ctx) {
    ctx.strokeStyle = canvasStore.selectedColor
    ctx.lineWidth = 2

    if (canvasStore.selectedTool === 'rectangle') {
      const width = x - startX
      const height = y - startY
      ctx.strokeRect(startX, startY, width, height)
    } else if (canvasStore.selectedTool === 'circle') {
      const radius = Math.sqrt(Math.pow(x - startX, 2) + Math.pow(y - startY, 2))
      ctx.beginPath()
      ctx.arc(startX, startY, radius, 0, 2 * Math.PI)
      ctx.stroke()
    }
  }
}

function handleMouseUp(e: MouseEvent) {
  if (!isDrawing || !canvasStore.canEdit) return
  isDrawing = false

  const rect = mainCanvas.value?.getBoundingClientRect()
  if (!rect) return

  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  const shape: Partial<Shape> & { id: string; type: ShapeType } = {
    id: `shape-${Date.now()}`,
    type: canvasStore.selectedTool,
    x: startX,
    y: startY,
    color: canvasStore.selectedColor,
    stroke: canvasStore.selectedColor,
    strokeWidth: 2,
  }

  if (canvasStore.selectedTool === 'rectangle') {
    shape.width = x - startX
    shape.height = y - startY
  } else if (canvasStore.selectedTool === 'circle') {
    shape.radius = Math.sqrt(Math.pow(x - startX, 2) + Math.pow(y - startY, 2))
  }

  canvasStore.addShape(shape)
  drawShapes()
}

function handleWheel(e: WheelEvent) {
  e.preventDefault()
  const delta = e.deltaY > 0 ? -0.1 : 0.1
  canvasStore.zoom(delta)
}

async function saveCanvas() {
  try {
    await roomStore.saveRoom(canvasStore.shapes)
    alert('Room saved successfully!')
  } catch (error) {
    console.error('Failed to save room:', error)
    alert('Failed to save room')
  }
}
</script>

<style scoped>
.workspace-container {
  width: 100vw;
  height: 100vh;
  background-color: var(--color-deep-void);
  position: relative;
  overflow: hidden;
}

.room-name-vertical {
  position: fixed;
  left: 40px;
  top: 50%;
  transform: translateY(-50%) rotate(-90deg);
  transform-origin: center;
  z-index: 100;
}

.room-name-vertical span {
  font-family: var(--font-display);
  font-size: 48px;
  font-weight: 800;
  color: var(--color-bone);
  letter-spacing: -0.05em;
  white-space: nowrap;
}

.canvas-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

canvas {
  width: 100%;
  height: 100%;
  cursor: crosshair;
}

.coordinates {
  position: fixed;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--color-bone);
  opacity: 0.3;
  text-transform: uppercase;
  pointer-events: none;
}

.coordinates.top-left {
  top: 20px;
  left: 20px;
}

.vertical-toolbar {
  position: fixed;
  left: 40px;
  bottom: 60px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 100;
}

.tool-item {
  width: 48px;
  height: 48px;
  background-color: var(--color-muted-obsidian);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tool-item:hover {
  background-color: var(--color-neon-cobalt);
  transform: translateX(5px);
}

.tool-item.active {
  background-color: var(--color-neon-cobalt);
}

.tool-icon {
  font-size: 20px;
  color: var(--color-bone);
}

.toolbar-divider {
  height: 2px;
  background-color: var(--color-muted-obsidian);
  margin: 8px 0;
}

.user-orbit {
  position: fixed;
  bottom: 40px;
  right: 40px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 100;
}

.user-entry {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-color-dot {
  width: 12px;
  height: 12px;
  border-radius: 0;
}

.user-name {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--color-bone);
  text-transform: uppercase;
}

.invite-zone {
  position: fixed;
  top: 40px;
  right: 40px;
  z-index: 100;
}

.huge-invite-link {
  font-family: var(--font-system);
  font-size: 32px;
  font-weight: 600;
  color: var(--color-bone);
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s ease;
  letter-spacing: -0.04em;
}

.huge-invite-link:hover {
  color: var(--color-neon-cobalt);
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: var(--color-deep-void);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-text {
  font-family: var(--font-mono);
  font-size: 24px;
  color: var(--color-bone);
  opacity: 0.5;
}
</style>
