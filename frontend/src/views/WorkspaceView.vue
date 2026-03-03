<template>
  <div class="workspace">
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="top-left">
        <router-link to="/rooms" class="back-btn">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M10 3L5 8l5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </router-link>
        <div class="room-divider"></div>
        <span class="room-title">{{ roomStore.roomName || 'Untitled' }}</span>
      </div>
      <div class="top-right">
        <button
          class="users-btn"
          :class="{ active: showUsersPanel }"
          :title="`${canvasStore.userCount} in room`"
          @click="showUsersPanel = !showUsersPanel"
        >
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
            <circle cx="5.5" cy="5" r="2.5" stroke="currentColor" stroke-width="1.4"/>
            <path d="M1 13c0-2.5 2-4 4.5-4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
            <circle cx="10.5" cy="5" r="2.5" stroke="currentColor" stroke-width="1.4"/>
            <path d="M8 13c0-2.5 2-4 4.5-4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
          <span class="users-count">{{ canvasStore.userCount }}</span>
        </button>
        <button v-if="roomStore.isRoomOwner" @click="showInviteModal = true" class="top-btn invite">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M9 2a3 3 0 1 1 0 6 3 3 0 0 1 0-6zM1 12c0-2.2 1.8-4 4-4"
              stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="11" y1="9" x2="11" y2="13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="9" y1="11" x2="13" y2="11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          Share
        </button>
        <button @click="saveCanvas" class="top-btn save">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M2 2h8l2 2v8H2V2z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
            <rect x="4" y="2" width="4" height="3" stroke="currentColor" stroke-width="1.5"/>
            <rect x="3" y="7" width="8" height="5" rx="0.5" stroke="currentColor" stroke-width="1.5"/>
          </svg>
          Save
        </button>
      </div>
    </div>

    <!-- Canvas -->
    <div class="canvas-wrapper" ref="canvasContainer">
      <canvas
        ref="mainCanvas"
        :style="canvasCursor"
        @mousedown="handleMouseDown"
        @mousemove="handleMouseMove"
        @mouseup="handleMouseUp"
        @mouseleave="handleMouseUp"
        @wheel="handleWheel"
      ></canvas>
    </div>

    <!-- Floating Toolbar -->
    <div class="toolbar">
      <div
        v-for="tool in tools"
        :key="tool.id"
        class="tool-btn"
        :class="{ active: canvasStore.selectedTool === tool.id }"
        :title="String(tool.id)"
        @click="canvasStore.setTool(tool.id)"
      >
        <span class="tool-icon">{{ tool.icon }}</span>
      </div>
      <div class="tool-sep"></div>
      <div class="tool-btn" title="Undo" @click="canvasStore.undo()">
        <span class="tool-icon">↶</span>
      </div>
      <div class="tool-btn" title="Redo" @click="canvasStore.redo()">
        <span class="tool-icon">↷</span>
      </div>
    </div>

    <!-- Coordinates -->
    <div class="coords">{{ Math.floor(canvasStore.mousePos.x) }},{{ Math.floor(canvasStore.mousePos.y) }}</div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-ring"></div>
      <p class="loading-label">Loading workspace…</p>
    </div>

    <!-- Text Input Modal -->
    <Transition name="modal-fade">
      <div v-if="showTextModal" class="modal-backdrop" @click.self="cancelTextInput">
        <div class="text-modal">
          <p class="text-modal-label">Enter text</p>
          <input
            ref="textInputRef"
            v-model="textInputValue"
            class="text-modal-input"
            placeholder="Type something…"
            maxlength="200"
            @keydown.enter="confirmTextInput"
            @keydown.esc="cancelTextInput"
          />
          <div class="text-modal-actions">
            <button class="text-modal-cancel" @click="cancelTextInput">Cancel</button>
            <button class="text-modal-confirm" @click="confirmTextInput">Place text</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="toast-slide">
      <div v-if="toastMsg" class="toast" :class="toastType">{{ toastMsg }}</div>
    </Transition>

    <!-- Users Panel -->
    <Transition name="panel-slide">
      <div v-if="showUsersPanel" class="users-panel">
        <div class="panel-header">
          <span class="panel-title">People in room</span>
          <button class="panel-close" @click="showUsersPanel = false">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M1 1l10 10M11 1L1 11" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            </svg>
          </button>
        </div>

        <!-- Self row -->
        <div class="panel-user self">
          <div class="panel-pip" :style="{ background: canvasStore.myColor }"></div>
          <div class="panel-info">
            <span class="panel-name">
              {{ canvasStore.myUsername || authStore.username || 'You' }}
              <em class="panel-you">(you)</em>
            </span>
            <span class="panel-role" :class="canvasStore.canEdit ? 'role-editor' : 'role-viewer'">
              {{ canvasStore.canEdit ? 'Editor' : 'Viewer' }}
            </span>
          </div>
        </div>

        <!-- Other users -->
        <div
          v-for="user in connectedUsersArray"
          :key="user.userId"
          class="panel-user"
        >
          <div class="panel-pip" :style="{ background: user.color }"></div>
          <div class="panel-info">
            <span class="panel-name">{{ user.username }}</span>
            <span class="panel-role" :class="user.canEdit ? 'role-editor' : 'role-viewer'">
              {{ user.canEdit ? 'Editor' : 'Viewer' }}
            </span>
          </div>
        </div>

        <div v-if="connectedUsersArray.length === 0" class="panel-empty">
          Only you are here
        </div>

        <!-- Edit notice for view-only users -->
        <div v-if="!canvasStore.canEdit" class="panel-edit-notice">
          <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
            <circle cx="6.5" cy="6.5" r="5.5" stroke="currentColor" stroke-width="1.3"/>
            <path d="M6.5 5.5v3.5M6.5 4h.01" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
          {{ authStore.isAuthenticated ? 'You have view-only access' : 'Log in to edit this room' }}
        </div>
      </div>
    </Transition>

    <!-- Members / Share Modal -->
    <Transition name="modal-fade">
      <div v-if="showInviteModal" class="modal-backdrop" @click.self="closeInviteModal">
        <div class="members-modal">
          <div class="members-modal-head">
            <div>
              <h2 class="members-title">Manage access</h2>
              <p class="members-sub">{{ roomStore.roomName }}</p>
            </div>
            <button class="members-close" @click="closeInviteModal">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M2 2l10 10M12 2L2 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <!-- Invite form -->
          <div class="invite-row">
            <input
              v-model="inviteInput"
              type="text"
              class="invite-input"
              placeholder="Username or email address"
              :disabled="inviting"
              @keyup.enter="handleInvite"
            />
            <select v-model="invitePermission" class="invite-perm-select" :disabled="inviting">
              <option value="editor">Editor</option>
              <option value="viewer">Viewer</option>
            </select>
            <button class="invite-btn" :disabled="!inviteInput.trim() || inviting" @click="handleInvite">
              {{ inviting ? '…' : 'Invite' }}
            </button>
          </div>
          <p v-if="inviteFeedback.msg" class="invite-feedback" :class="inviteFeedback.kind">
            {{ inviteFeedback.msg }}
          </p>

          <!-- Members list -->
          <div class="members-list-wrap">
            <div v-if="membersLoading" class="members-state">
              <div class="members-spinner"></div>
            </div>
            <div v-else-if="membersError" class="members-state muted">{{ membersError }}</div>
            <div v-else-if="members.length === 0" class="members-state muted">
              No members yet — invite someone above.
            </div>
            <div v-else class="members-list">
              <div v-for="m in members" :key="m.id" class="member-row">
                <div class="member-avatar">{{ (m.user?.username?.[0] || '?').toUpperCase() }}</div>
                <div class="member-info">
                  <span class="member-name">{{ m.user?.username }}</span>
                  <span class="member-email">{{ m.user?.email }}</span>
                </div>
                <select
                  class="member-perm-select"
                  :value="m.permission"
                  :disabled="updatingId === m.id"
                  @change="handleUpdatePermission(m.user_id, ($event.target as HTMLSelectElement).value, m.id)"
                >
                  <option value="editor">Editor</option>
                  <option value="viewer">Viewer</option>
                </select>
                <button
                  class="member-revoke"
                  :disabled="updatingId === m.id"
                  title="Remove access"
                  @click="handleRevoke(m.user_id, m.id)"
                >
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                    <path d="M2 2l8 8M10 2L2 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCanvasStore } from '@/stores/canvas'
import { useRoomStore } from '@/stores/room'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'
import { ShapeType } from '@/types'
import type { Shape, Arrow, Rectangle, Circle } from '@/types'

const route = useRoute()
const router = useRouter()
const canvasStore = useCanvasStore()
const roomStore = useRoomStore()
const authStore = useAuthStore()

const roomId = ref(route.params.roomId as string)
const loading = ref(true)
const showInviteModal = ref(false)
const showUsersPanel = ref(false)

// ── Members modal ─────────────────────────────────────────────────────────────
interface MemberEntry {
  id: string
  user_id: string
  permission: string
  user: { username: string; email: string }
}
const members = ref<MemberEntry[]>([])
const membersLoading = ref(false)
const membersError = ref('')
const inviteInput = ref('')
const invitePermission = ref('editor')
const inviting = ref(false)
const updatingId = ref<string | null>(null)
const inviteFeedback = ref<{ msg: string; kind: 'ok' | 'err' }>({ msg: '', kind: 'ok' })

let feedbackTimer: ReturnType<typeof setTimeout> | null = null
function setFeedback(msg: string, kind: 'ok' | 'err') {
  if (feedbackTimer) clearTimeout(feedbackTimer)
  inviteFeedback.value = { msg, kind }
  feedbackTimer = setTimeout(() => { inviteFeedback.value = { msg: '', kind: 'ok' } }, 4000)
}

async function loadMembers() {
  membersLoading.value = true
  membersError.value = ''
  try {
    members.value = await api.getRoomPermissions(roomId.value)
  } catch {
    membersError.value = 'Could not load members'
  } finally {
    membersLoading.value = false
  }
}

function closeInviteModal() {
  showInviteModal.value = false
  inviteInput.value = ''
  inviteFeedback.value = { msg: '', kind: 'ok' }
}

async function handleInvite() {
  if (!inviteInput.value.trim()) return
  inviting.value = true
  try {
    const { PermissionLevel } = await import('@/types')
    const perm = invitePermission.value === 'editor' ? PermissionLevel.EDITOR : PermissionLevel.VIEWER
    const entry = await api.inviteUser(roomId.value, inviteInput.value.trim(), perm)
    inviteInput.value = ''
    const idx = members.value.findIndex(m => m.user_id === entry.user_id)
    if (idx !== -1) members.value[idx] = entry
    else members.value.push(entry)
    setFeedback(`Invited as ${invitePermission.value}`, 'ok')
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    setFeedback(err?.response?.data?.detail || 'User not found', 'err')
  } finally {
    inviting.value = false
  }
}

async function handleUpdatePermission(userId: string, newPerm: string, entryId: string) {
  updatingId.value = entryId
  try {
    const { PermissionLevel } = await import('@/types')
    const perm = newPerm === 'editor' ? PermissionLevel.EDITOR : PermissionLevel.VIEWER
    await api.updatePermission(roomId.value, userId, perm)
    const m = members.value.find(m => m.id === entryId)
    if (m) m.permission = newPerm
  } catch {
    setFeedback('Failed to update permission', 'err')
    await loadMembers()
  } finally {
    updatingId.value = null
  }
}

async function handleRevoke(userId: string, entryId: string) {
  updatingId.value = entryId
  try {
    await api.revokePermission(roomId.value, userId)
    members.value = members.value.filter(m => m.id !== entryId)
  } catch {
    setFeedback('Failed to revoke access', 'err')
  } finally {
    updatingId.value = null
  }
}

watch(showInviteModal, (val) => { if (val) loadMembers() })
const mainCanvas = ref<HTMLCanvasElement | null>(null)
const canvasContainer = ref<HTMLDivElement | null>(null)

// Text modal
const showTextModal = ref(false)
const textInputValue = ref('')
const textInputRef = ref<HTMLInputElement | null>(null)
let pendingTextShape: (Partial<Shape> & { id: string; type: ShapeType }) | null = null

// Toast
const toastMsg = ref('')
const toastType = ref<'success' | 'error'>('success')
let toastTimer: ReturnType<typeof setTimeout> | null = null

function showToast(msg: string, type: 'success' | 'error' = 'success') {
  if (toastTimer) clearTimeout(toastTimer)
  toastMsg.value = msg
  toastType.value = type
  toastTimer = setTimeout(() => { toastMsg.value = '' }, 3000)
}

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
let lastCursorBroadcast = 0
let isDrawing = false
let startX = 0
let startY = 0

// Drag-move state
let dragShape: Shape | null = null
let dragOffsetX = 0
let dragOffsetY = 0
const hoveredShapeId = ref<string | null>(null)
const selectedShapeId = ref<string | null>(null)

// Dynamic cursor based on current tool + hover state
const canvasCursor = computed(() => {
  if (canvasStore.selectedTool === 'pan') return { cursor: dragShape ? 'grabbing' : 'grab' }
  if (canvasStore.selectedTool === 'cursor') {
    if (dragShape) return { cursor: 'grabbing' }
    if (hoveredShapeId.value) return { cursor: 'move' }
    return { cursor: 'default' }
  }
  return { cursor: 'crosshair' }
})

onMounted(async () => {
  loading.value = true

  try {
    // loadRoom fetches room metadata + canvas state + permission check in parallel.
    // It returns the shapes directly so we don't need a second api.getRoom() call.
    const initialShapes = await roomStore.loadRoom(roomId.value)
    canvasStore.setShapes(initialShapes)

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
  window.removeEventListener('resize', handleResize)
  if (toastTimer) clearTimeout(toastTimer)
  if (feedbackTimer) clearTimeout(feedbackTimer)
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
    ctx.fillStyle = '#ECEADE'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
  }

  // Draw grid
  drawGrid()

  // Draw existing shapes
  drawShapes()

  // Redraw on window resize
  window.addEventListener('resize', handleResize)

  // Redraw whenever shapes array reference changes (covers sync_state, remote draw,
  // clear, undo/redo — all of which assign a new array reference).
  watch(
    () => canvasStore.shapes,
    () => drawShapes()
  )

  // Redraw whenever a remote cursor moves
  watch(
    () => canvasStore.cursors,
    () => drawShapes(),
    { deep: true }
  )
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
  ctx.strokeStyle = '#D5CEC5'
  ctx.lineWidth = 1

  const gridSize = 50

  for (let x = 0; x < canvas.width; x += gridSize) {
    for (let y = 0; y < canvas.height; y += gridSize) {
      ctx.fillStyle = '#C8C0B7'
      ctx.fillRect(x, y, 2, 2)
    }
  }
}

function drawShapes() {
  if (!ctx || !mainCanvas.value) return

  const canvas = mainCanvas.value

  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.fillStyle = '#ECEADE'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  drawGrid()

  canvasStore.shapes.forEach((shape) => {
    const isSelected = shape.id === selectedShapeId.value
    const isHovered = shape.id === hoveredShapeId.value

    if (shape.type === 'rectangle') {
      const s = shape as Rectangle
      const w = s.width || 100
      const h = s.height || 100
      if (isSelected || isHovered) {
        ctx!.strokeStyle = 'rgba(192,67,31,0.25)'
        ctx!.lineWidth = (s.strokeWidth || 2) + 4
        ctx!.strokeRect(s.x, s.y, w, h)
      }
      ctx!.strokeStyle = s.stroke || '#C0431F'
      ctx!.lineWidth = s.strokeWidth || 2
      ctx!.strokeRect(s.x, s.y, w, h)

    } else if (shape.type === 'circle') {
      const s = shape as Circle
      const r = s.radius || 50
      if (isSelected || isHovered) {
        ctx!.beginPath()
        ctx!.arc(s.x, s.y, r, 0, 2 * Math.PI)
        ctx!.strokeStyle = 'rgba(192,67,31,0.25)'
        ctx!.lineWidth = (s.strokeWidth || 2) + 4
        ctx!.stroke()
      }
      ctx!.beginPath()
      ctx!.arc(s.x, s.y, r, 0, 2 * Math.PI)
      ctx!.strokeStyle = s.stroke || '#C0431F'
      ctx!.lineWidth = s.strokeWidth || 2
      ctx!.stroke()

    } else if (shape.type === 'arrow') {
      const s = shape as Arrow
      const pts = s.points || [s.x, s.y, s.x + 100, s.y]
      const color = s.stroke || '#C0431F'
      const sw = s.strokeWidth || 2
      if (isSelected || isHovered) drawArrow(ctx!, pts[0], pts[1], pts[2], pts[3], 'rgba(192,67,31,0.25)', sw + 4)
      drawArrow(ctx!, pts[0], pts[1], pts[2], pts[3], color, sw)

    } else if (shape.type === 'text') {
      const s = shape as any
      ctx!.fillStyle = s.fill || s.stroke || '#1A1612'
      ctx!.font = `${s.fontSize || 16}px 'Instrument Sans', sans-serif`
      if (isSelected || isHovered) {
        const w = ctx!.measureText(s.text || '').width
        const fh = s.fontSize || 16
        ctx!.fillStyle = 'rgba(192,67,31,0.12)'
        ctx!.fillRect(s.x - 3, s.y - fh - 2, w + 6, fh + 6)
        ctx!.fillStyle = s.fill || s.stroke || '#1A1612'
      }
      ctx!.fillText(s.text || '', s.x, s.y)
    }

    // Creator badge on selected shapes
    if (isSelected) drawCreatorBadge(shape)
  })

  // Draw remote cursors on top of shapes
  drawRemoteCursors()
}

function drawCreatorBadge(shape: Shape) {
  if (!ctx) return
  const s = shape as any

  // Resolve label + color: prefer stamped fields, then live user lookup, then self-check
  let label: string | null = s.createdByUsername || null
  let badgeColor: string = s.createdByColor || ''

  if (!label) {
    if (s.userId && s.userId === canvasStore.myUserId) {
      label = canvasStore.myUsername || 'You'
      badgeColor = badgeColor || canvasStore.myColor
    } else if (s.userId) {
      const user = canvasStore.connectedUsers.get(s.userId)
      if (user) {
        label = user.username
        badgeColor = badgeColor || user.color
      }
    }
  }

  if (!label) return   // truly no creator info available
  if (!badgeColor) badgeColor = '#888'

  // Find the top-center of the shape bounding box
  let bx = s.x
  let by = s.y
  if (shape.type === 'rectangle') {
    bx = s.x + (s.width || 0) / 2
    by = s.y - 10
  } else if (shape.type === 'circle') {
    bx = s.x
    by = s.y - (s.radius || 50) - 10
  } else if (shape.type === 'arrow') {
    const pts = s.points || [s.x, s.y, s.x + 100, s.y]
    bx = (pts[0] + pts[2]) / 2
    by = Math.min(pts[1], pts[3]) - 10
  } else if (shape.type === 'text') {
    ctx!.font = `${s.fontSize || 16}px 'Instrument Sans', sans-serif`
    const tw = ctx!.measureText(s.text || '').width
    bx = s.x + tw / 2
    by = s.y - (s.fontSize || 16) - 8
  }

  ctx!.save()
  ctx!.font = "600 11px 'Instrument Sans', sans-serif"
  const tw = ctx!.measureText(label).width
  const pillW = tw + 16
  const pillH = 20
  const pillX = bx - pillW / 2
  const pillY = by - pillH - 4
  const r = pillH / 2

  // Shadow
  ctx!.shadowColor = 'rgba(0,0,0,0.18)'
  ctx!.shadowBlur = 4
  ctx!.shadowOffsetY = 2

  // Pill
  ctx!.fillStyle = badgeColor
  ctx!.beginPath()
  ctx!.moveTo(pillX + r, pillY)
  ctx!.arcTo(pillX + pillW, pillY, pillX + pillW, pillY + pillH, r)
  ctx!.arcTo(pillX + pillW, pillY + pillH, pillX, pillY + pillH, r)
  ctx!.arcTo(pillX, pillY + pillH, pillX, pillY, r)
  ctx!.arcTo(pillX, pillY, pillX + pillW, pillY, r)
  ctx!.closePath()
  ctx!.fill()

  ctx!.shadowColor = 'transparent'
  ctx!.shadowBlur = 0
  ctx!.shadowOffsetY = 0

  // Label
  ctx!.fillStyle = '#ffffff'
  ctx!.fillText(label, pillX + 8, pillY + 14)
  ctx!.restore()
}

function drawRemoteCursors() {
  if (!ctx) return
  canvasStore.cursors.forEach((cursor) => {
    const { x, y, username, color } = cursor
    ctx!.save()
    ctx!.translate(x, y)

    // Classic OS-style arrow cursor (tip at origin, pointing up-left)
    ctx!.beginPath()
    ctx!.moveTo(0, 0)          // tip
    ctx!.lineTo(0, 15)         // left edge down
    ctx!.lineTo(3.5, 11.5)     // inner notch
    ctx!.lineTo(6.5, 17)       // tail bottom-right
    ctx!.lineTo(8.5, 16)       // tail top-right
    ctx!.lineTo(5.5, 10.5)     // inner right
    ctx!.lineTo(10, 10.5)      // right shoulder
    ctx!.closePath()

    // Fill with user color
    ctx!.fillStyle = color
    ctx!.fill()
    // White outline so it's visible over any canvas content
    ctx!.strokeStyle = '#ffffff'
    ctx!.lineWidth = 1.5
    ctx!.lineJoin = 'round'
    ctx!.stroke()

    // Name pill — sits just below and right of the cursor tip
    const label = username || 'User'
    ctx!.font = '600 11px \'Instrument Sans\', sans-serif'
    const tw = ctx!.measureText(label).width
    const pillW = tw + 14
    const pillH = 20
    const pillX = 12
    const pillY = 14
    const r = pillH / 2

    ctx!.fillStyle = color
    ctx!.beginPath()
    ctx!.moveTo(pillX + r, pillY)
    ctx!.arcTo(pillX + pillW, pillY, pillX + pillW, pillY + pillH, r)
    ctx!.arcTo(pillX + pillW, pillY + pillH, pillX, pillY + pillH, r)
    ctx!.arcTo(pillX, pillY + pillH, pillX, pillY, r)
    ctx!.arcTo(pillX, pillY, pillX + pillW, pillY, r)
    ctx!.closePath()
    ctx!.fill()

    ctx!.fillStyle = '#ffffff'
    ctx!.fillText(label, pillX + 7, pillY + 14)

    ctx!.restore()
  })
}

function handleMouseDown(e: MouseEvent) {
  const rect = mainCanvas.value?.getBoundingClientRect()
  if (!rect) return

  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  // ── Cursor / move tool ──────────────────────────────
  if (canvasStore.selectedTool === 'cursor') {
    const hit = findShapeAt(x, y)
    if (hit) {
      selectedShapeId.value = hit.id
      drawShapes() // show badge immediately on click
      // Only start drag if user can edit
      if (canvasStore.canEdit) {
        dragShape = hit
        if (hit.type === 'arrow') {
          const s = hit as Arrow
          const pts = s.points || [s.x, s.y, s.x + 100, s.y]
          dragOffsetX = x - pts[0]
          dragOffsetY = y - pts[1]
        } else {
          dragOffsetX = x - hit.x
          dragOffsetY = y - hit.y
        }
      }
    } else {
      selectedShapeId.value = null
      dragShape = null
      drawShapes() // clear badge immediately
    }
    return
  }

  if (!canvasStore.canEdit) return

  // ── Drawing tools ───────────────────────────────────
  isDrawing = true
  startX = x
  startY = y
}

function handleMouseMove(e: MouseEvent) {
  const rect = mainCanvas.value?.getBoundingClientRect()
  if (!rect) return

  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  canvasStore.setMousePosition(x, y)

  // Broadcast cursor position to other users (throttled to ~25 fps)
  const now = Date.now()
  if (now - lastCursorBroadcast > 40 && canvasStore.myUserId) {
    lastCursorBroadcast = now
    canvasStore.updateCursor(canvasStore.myUserId, x, y)
  }

  // ── Dragging an existing shape ──────────────────────
  if (dragShape && canvasStore.canEdit) {
    const current = canvasStore.shapes.find(s => s.id === dragShape!.id)
    if (current) {
      const newX = x - dragOffsetX
      const newY = y - dragOffsetY
      if (current.type === 'arrow') {
        const s = current as Arrow
        const pts = s.points || [s.x, s.y, s.x + 100, s.y]
        const dx = newX - pts[0]
        const dy = newY - pts[1]
        canvasStore.updateShape(current.id, {
          x: newX, y: newY,
          points: [pts[0] + dx, pts[1] + dy, pts[2] + dx, pts[3] + dy],
        })
      } else {
        canvasStore.updateShape(current.id, { x: newX, y: newY })
      }
      drawShapes()
    }
    return
  }

  // ── Hover detection for cursor tool ────────────────
  if (canvasStore.selectedTool === 'cursor') {
    const prevHovered = hoveredShapeId.value
    const hit = findShapeAt(x, y)
    hoveredShapeId.value = hit ? hit.id : null
    // Redraw if the hovered shape changed in either direction
    if (hit !== null || prevHovered !== null) drawShapes()
    return
  }

  if (!isDrawing || !canvasStore.canEdit) return

  // ── Drawing preview ─────────────────────────────────
  drawShapes()
  if (ctx) {
    ctx.strokeStyle = canvasStore.selectedColor
    ctx.lineWidth = 2
    if (canvasStore.selectedTool === 'rectangle') {
      ctx.strokeRect(startX, startY, x - startX, y - startY)
    } else if (canvasStore.selectedTool === 'circle') {
      const radius = Math.sqrt((x - startX) ** 2 + (y - startY) ** 2)
      ctx.beginPath()
      ctx.arc(startX, startY, radius, 0, 2 * Math.PI)
      ctx.stroke()
    } else if (canvasStore.selectedTool === 'arrow') {
      drawArrow(ctx, startX, startY, x, y, canvasStore.selectedColor, 2)
    }
  }
}

function handleMouseUp(e: MouseEvent) {
  // ── End drag ────────────────────────────────────────
  if (dragShape) {
    // Broadcast the final resting position to other users
    const moved = canvasStore.shapes.find(s => s.id === dragShape!.id)
    if (moved && canvasStore.canEdit) {
      if (moved.type === 'arrow') {
        canvasStore.broadcastMove(moved.id, { x: moved.x, y: moved.y, points: (moved as any).points })
      } else {
        canvasStore.broadcastMove(moved.id, { x: moved.x, y: moved.y })
      }
    }
    dragShape = null
    return
  }

  if (!isDrawing || !canvasStore.canEdit) return
  isDrawing = false

  const rect = mainCanvas.value?.getBoundingClientRect()
  if (!rect) return

  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  const shape: Partial<Shape> & { id: string; type: ShapeType } = {
    id: `shape-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    type: canvasStore.selectedTool,
    x: startX,
    y: startY,
    color: canvasStore.selectedColor,
    stroke: canvasStore.selectedColor,
    strokeWidth: 2,
    userId: canvasStore.myUserId ?? undefined,
    createdByUsername: canvasStore.myUsername || authStore.user?.username || 'You',
    createdByColor: canvasStore.myColor,
  }

  if (canvasStore.selectedTool === 'rectangle') {
    const w = x - startX
    const h = y - startY
    if (Math.abs(w) < 5 || Math.abs(h) < 5) { isDrawing = false; drawShapes(); return }
    shape.width = w
    shape.height = h
  } else if (canvasStore.selectedTool === 'circle') {
    const r = Math.sqrt(Math.pow(x - startX, 2) + Math.pow(y - startY, 2))
    if (r < 5) { isDrawing = false; drawShapes(); return }
    shape.radius = r
  } else if (canvasStore.selectedTool === 'arrow') {
    const arrowLen = Math.sqrt(Math.pow(x - startX, 2) + Math.pow(y - startY, 2))
    if (arrowLen < 5) { isDrawing = false; drawShapes(); return }
    ;(shape as any).points = [startX, startY, x, y]
  } else if (canvasStore.selectedTool === 'text') {
    // Open custom modal instead of browser prompt
    pendingTextShape = shape
    textInputValue.value = ''
    showTextModal.value = true
    // Focus the input on next tick after the element renders
    setTimeout(() => textInputRef.value?.focus(), 50)
    return // shape will be committed in confirmTextInput()
  }

  canvasStore.addShape(shape)
  drawShapes()
}

function confirmTextInput() {
  if (!pendingTextShape) return
  const text = textInputValue.value.trim()
  if (!text) { cancelTextInput(); return }
  ;(pendingTextShape as any).text = text
  ;(pendingTextShape as any).fontSize = 16
  canvasStore.addShape(pendingTextShape)
  drawShapes()
  pendingTextShape = null
  showTextModal.value = false
  textInputValue.value = ''
}

function cancelTextInput() {
  pendingTextShape = null
  showTextModal.value = false
  textInputValue.value = ''
}

// ─── Drawing helpers ────────────────────────────────────────────────────────

/** Render an arrow with a filled triangular head at any angle. */
function drawArrow(
  c: CanvasRenderingContext2D,
  x1: number, y1: number,
  x2: number, y2: number,
  color: string,
  lineWidth: number,
) {
  const angle = Math.atan2(y2 - y1, x2 - x1)
  const headLen = 14
  const headAngle = Math.PI / 6
  // Shaft stops just before the arrowhead base so the head looks clean
  const shaftEndX = x2 - (headLen - 2) * Math.cos(angle)
  const shaftEndY = y2 - (headLen - 2) * Math.sin(angle)

  c.save()
  c.strokeStyle = color
  c.fillStyle = color
  c.lineWidth = lineWidth
  c.lineCap = 'round'

  // Shaft
  c.beginPath()
  c.moveTo(x1, y1)
  c.lineTo(shaftEndX, shaftEndY)
  c.stroke()

  // Filled triangle head
  c.beginPath()
  c.moveTo(x2, y2)
  c.lineTo(x2 - headLen * Math.cos(angle - headAngle), y2 - headLen * Math.sin(angle - headAngle))
  c.lineTo(x2 - headLen * Math.cos(angle + headAngle), y2 - headLen * Math.sin(angle + headAngle))
  c.closePath()
  c.fill()
  c.restore()
}

/** Squared distance from point (px, py) to line segment (ax,ay)-(bx,by). */
function distToSegmentSq(px: number, py: number, ax: number, ay: number, bx: number, by: number): number {
  const dx = bx - ax, dy = by - ay
  const lenSq = dx * dx + dy * dy
  if (lenSq === 0) return (px - ax) ** 2 + (py - ay) ** 2
  const t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / lenSq))
  return (px - (ax + t * dx)) ** 2 + (py - (ay + t * dy)) ** 2
}

/** Hit-test a single shape at canvas coords (x, y). */
function hitTest(shape: Shape, x: number, y: number): boolean {
  if (shape.type === 'rectangle') {
    const s = shape as Rectangle
    const x1 = Math.min(s.x, s.x + (s.width || 0))
    const x2 = Math.max(s.x, s.x + (s.width || 0))
    const y1 = Math.min(s.y, s.y + (s.height || 0))
    const y2 = Math.max(s.y, s.y + (s.height || 0))
    // hit inner area OR within 6px of the stroke
    return x >= x1 - 6 && x <= x2 + 6 && y >= y1 - 6 && y <= y2 + 6
  }
  if (shape.type === 'circle') {
    const s = shape as Circle
    const dist = Math.sqrt((x - s.x) ** 2 + (y - s.y) ** 2)
    return dist <= (s.radius || 50) + 6
  }
  if (shape.type === 'arrow') {
    const s = shape as Arrow
    const pts = s.points || [s.x, s.y, s.x + 100, s.y]
    return distToSegmentSq(x, y, pts[0], pts[1], pts[2], pts[3]) <= 64  // 8px threshold
  }
  if (shape.type === 'text') {
    const s = shape as any
    const fh = s.fontSize || 16
    const w = (s.text?.length || 1) * fh * 0.6
    return x >= s.x - 4 && x <= s.x + w + 4 && y >= s.y - fh - 4 && y <= s.y + 4
  }
  return false
}

/** Return the top-most shape under (x, y), or null. */
function findShapeAt(x: number, y: number): Shape | null {
  const arr = canvasStore.shapes
  for (let i = arr.length - 1; i >= 0; i--) {
    if (hitTest(arr[i], x, y)) return arr[i]
  }
  return null
}

function handleWheel(e: WheelEvent) {
  e.preventDefault()
  const delta = e.deltaY > 0 ? -0.1 : 0.1
  canvasStore.zoom(delta)
}

async function saveCanvas() {
  try {
    await roomStore.saveRoom(canvasStore.shapes)
    showToast('Room saved successfully!', 'success')
  } catch (error) {
    console.error('Failed to save room:', error)
    showToast('Failed to save room', 'error')
  }
}
</script>

<style scoped>
/* ─── Text modal ───────────────────────────── */
.modal-backdrop {
  position: absolute;
  inset: 0;
  z-index: 300;
  background: rgba(26, 22, 18, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
}

.text-modal {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: 28px 28px 24px;
  width: 340px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.text-modal-label {
  font-family: var(--font-display);
  font-size: 17px;
  font-weight: 500;
  color: var(--color-ink);
  letter-spacing: -0.02em;
  margin: 0;
}

.text-modal-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-paper);
  font-family: var(--font-ui);
  font-size: 15px;
  color: var(--color-ink);
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s ease;
}

.text-modal-input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(192, 67, 31, 0.12);
}

.text-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.text-modal-cancel {
  padding: 8px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-ink-muted);
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s ease;
}

.text-modal-cancel:hover { background: var(--color-paper); }

.text-modal-confirm {
  padding: 8px 18px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--color-accent);
  color: #fff;
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.text-modal-confirm:hover { background: var(--color-accent-hover); }

/* modal transition */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.18s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }

/* ─── Toast ─────────────────────────────────── */
.toast {
  position: absolute;
  bottom: 28px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 400;
  padding: 10px 20px;
  border-radius: var(--radius-sm);
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 500;
  pointer-events: none;
  white-space: nowrap;
  box-shadow: var(--shadow-md);
}

.toast.success {
  background: #1A1612;
  color: #fff;
}

.toast.error {
  background: var(--color-accent);
  color: #fff;
}

.toast-slide-enter-active, .toast-slide-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.toast-slide-enter-from, .toast-slide-leave-to { opacity: 0; transform: translateX(-50%) translateY(8px); }

/* ─── Users button ────────────────────────── */
.users-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 32px;
  padding: 0 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-ink-muted);
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}
.users-btn:hover, .users-btn.active {
  background: var(--color-paper);
  color: var(--color-ink);
  border-color: var(--color-ink-muted);
}
.users-count {
  font-family: var(--font-mono);
  font-size: 12px;
}

/* ─── Users panel ────────────────────────── */
.users-panel {
  position: absolute;
  top: 52px;
  right: 0;
  width: 240px;
  bottom: 0;
  background: var(--color-surface);
  border-left: 1px solid var(--color-border);
  z-index: 100;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.panel-title {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 500;
  color: var(--color-ink);
  letter-spacing: -0.02em;
}

.panel-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--color-ink-muted);
  cursor: pointer;
  border-radius: var(--radius-xs);
  transition: background 0.15s ease, color 0.15s ease;
}
.panel-close:hover { background: var(--color-paper); color: var(--color-ink); }

.panel-user {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--color-border);
}
.panel-user.self { background: rgba(192, 67, 31, 0.04); }

.panel-pip {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.panel-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.panel-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.panel-you {
  font-style: normal;
  font-weight: 400;
  color: var(--color-ink-muted);
  font-size: 12px;
  margin-left: 4px;
}

.panel-role {
  font-size: 11px;
  font-weight: 600;
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 1px 6px;
  border-radius: var(--radius-full);
  display: inline-block;
  width: fit-content;
}

.role-editor {
  background: rgba(78, 107, 87, 0.12);
  color: #4E6B57;
}

.role-viewer {
  background: rgba(124, 109, 97, 0.1);
  color: var(--color-ink-muted);
}

.panel-empty {
  padding: 16px;
  font-size: 13px;
  color: var(--color-ink-subtle);
  text-align: center;
}

.panel-edit-notice {
  display: flex;
  align-items: center;
  gap: 7px;
  margin: auto 16px 16px;
  padding: 10px 12px;
  background: var(--color-accent-dim);
  border: 1px solid #F5C4B6;
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--color-accent);
  font-weight: 500;
}

/* panel transition */
.panel-slide-enter-active, .panel-slide-leave-active { transition: transform 0.2s var(--ease-out), opacity 0.2s ease; }
.panel-slide-enter-from, .panel-slide-leave-to { transform: translateX(100%); opacity: 0; }

/* ─── Workspace shell ───────────────────────── */
.workspace {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  background: var(--color-canvas-bg);
}

/* ─── Top Bar ────────────────────────────── */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  height: 52px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
  z-index: 100;
  box-shadow: var(--shadow-xs);
}

.top-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  color: var(--color-ink-muted);
  text-decoration: none;
  border-radius: var(--radius-xs);
  transition: background 0.15s ease, color 0.15s ease;
}

.back-btn:hover {
  background: var(--color-paper);
  color: var(--color-ink);
}

.room-divider {
  width: 1px;
  height: 20px;
  background: var(--color-border);
}

.room-title {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 500;
  color: var(--color-ink);
  letter-spacing: -0.02em;
  max-width: 280px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.top-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.users-row {
  display: flex;
  align-items: center;
  gap: -4px;
}

.user-pip {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 2px solid var(--color-surface);
  margin-left: -6px;
  box-shadow: var(--shadow-xs);
  transition: transform 0.15s ease;
  cursor: default;
}

.user-pip:first-child { margin-left: 0; }
.user-pip:hover { transform: scale(1.15); z-index: 1; }

.top-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: var(--radius-xs);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-ink-muted);
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.top-btn:hover {
  background: var(--color-paper);
  border-color: var(--color-border-hover);
  color: var(--color-ink);
}

.top-btn.invite {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: #fff;
}

.top-btn.invite:hover {
  background: var(--color-accent-hover);
  border-color: var(--color-accent-hover);
}

/* ─── Canvas ─────────────────────────────── */
.canvas-wrapper {
  flex: 1;
  position: relative;
  overflow: hidden;
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
  cursor: crosshair;
}

/* ─── Floating Toolbar ─────────────────────── */
.toolbar {
  position: fixed;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 2px;
  z-index: 200;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 6px;
  box-shadow: var(--shadow-md);
  animation: toolbarIn 0.4s var(--ease-out);
}

@keyframes toolbarIn {
  from { opacity: 0; transform: translateY(-50%) translateX(-10px); }
  to   { opacity: 1; transform: translateY(-50%) translateX(0); }
}

.tool-btn {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-xs);
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
  color: var(--color-ink-muted);
  font-size: 16px;
  position: relative;
}

.tool-btn:hover {
  background: var(--color-paper);
  color: var(--color-ink);
}

.tool-btn.active {
  background: var(--color-accent-dim);
  color: var(--color-accent);
}

.tool-icon {
  display: block;
  line-height: 1;
  font-style: normal;
}

.tool-sep {
  height: 1px;
  background: var(--color-border);
  margin: 4px 0;
}

/* ─── Coordinates ─────────────────────────── */
.coords {
  position: fixed;
  bottom: 14px;
  left: 70px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--color-ink-subtle);
  pointer-events: none;
  letter-spacing: 0.02em;
  z-index: 200;
}

/* ─── Loading overlay ─────────────────────── */
.loading-overlay {
  position: fixed;
  inset: 0;
  background: var(--color-canvas-bg);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  z-index: 9999;
}

.loading-ring {
  width: 36px;
  height: 36px;
  border: 2.5px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-label {
  font-family: var(--font-ui);
  font-size: 14px;
  color: var(--color-ink-muted);
}

/* ── Members modal ─────────────────────────────────────────────────── */
.members-modal {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  width: 480px;
  max-width: calc(100vw - 32px);
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.members-modal-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 22px 24px 16px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}
.members-title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 500;
  color: var(--color-ink);
  letter-spacing: -0.02em;
  margin: 0 0 2px;
}
.members-sub {
  font-size: 12px;
  color: var(--color-ink-muted);
  margin: 0;
  font-family: var(--font-mono);
}
.members-close {
  background: none; border: none; cursor: pointer;
  color: var(--color-ink-muted); padding: 4px;
  border-radius: var(--radius-xs);
  display: flex; align-items: center;
  transition: color 0.15s, background 0.15s; flex-shrink: 0;
}
.members-close:hover { color: var(--color-ink); background: var(--color-paper); }

.invite-row {
  display: flex; gap: 8px;
  padding: 16px 24px 0; flex-shrink: 0;
}
.invite-input {
  flex: 1; min-width: 0;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-paper);
  font-family: var(--font-ui); font-size: 13px; color: var(--color-ink);
  transition: border-color 0.15s;
}
.invite-input:focus { outline: none; border-color: var(--color-accent); }
.invite-input:disabled { opacity: 0.5; }
.invite-perm-select {
  padding: 8px 10px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-paper);
  font-family: var(--font-ui); font-size: 13px; color: var(--color-ink);
  cursor: pointer; flex-shrink: 0;
}
.invite-btn {
  padding: 8px 16px;
  background: var(--color-accent); color: #fff;
  border: none; border-radius: var(--radius-sm);
  font-family: var(--font-ui); font-size: 13px; font-weight: 600;
  cursor: pointer; white-space: nowrap; flex-shrink: 0;
  transition: background 0.2s;
}
.invite-btn:hover:not(:disabled) { background: var(--color-accent-hover); }
.invite-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.invite-feedback {
  padding: 7px 24px 0; font-size: 12px;
  font-family: var(--font-ui); margin: 0; flex-shrink: 0;
}
.invite-feedback.ok { color: #2d8a4e; }
.invite-feedback.err { color: var(--color-accent); }

.members-list-wrap {
  flex: 1; overflow-y: auto;
  padding: 12px 24px 20px;
}
.members-state {
  display: flex; align-items: center; justify-content: center; padding: 28px 0;
}
.members-state.muted {
  font-size: 13px; color: var(--color-ink-muted); font-family: var(--font-ui);
}
.members-spinner {
  width: 24px; height: 24px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
.members-list { display: flex; flex-direction: column; gap: 4px; margin-top: 6px; }
.member-row {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 10px; border-radius: var(--radius-sm);
  transition: background 0.12s;
}
.member-row:hover { background: var(--color-paper); }
.member-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--color-accent-dim); color: var(--color-accent);
  font-size: 13px; font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.member-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 1px; }
.member-name { font-size: 13px; font-weight: 600; color: var(--color-ink); font-family: var(--font-ui); }
.member-email {
  font-size: 11px; color: var(--color-ink-muted); font-family: var(--font-mono);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.member-perm-select {
  padding: 5px 8px;
  border: 1px solid var(--color-border); border-radius: var(--radius-xs);
  background: var(--color-surface);
  font-family: var(--font-ui); font-size: 12px; font-weight: 500; color: var(--color-ink);
  cursor: pointer; flex-shrink: 0;
}
.member-perm-select:disabled { opacity: 0.5; }
.member-revoke {
  background: none; border: none; cursor: pointer;
  color: var(--color-ink-subtle); padding: 4px; border-radius: var(--radius-xs);
  display: flex; align-items: center;
  transition: color 0.15s, background 0.15s; flex-shrink: 0;
}
.member-revoke:hover:not(:disabled) { color: var(--color-accent); background: rgba(192,67,31,0.07); }
.member-revoke:disabled { opacity: 0.35; cursor: not-allowed; }
</style>
