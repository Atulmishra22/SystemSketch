<template>
  <div class="rooms-page" @click="closeAllMenus">

    <!-- Top Nav -->
    <nav class="top-nav">
      <div class="nav-brand">
        <svg class="nav-logo" width="28" height="28" viewBox="0 0 28 28" fill="none">
          <!-- Subtle tinted bg -->
          <rect width="28" height="28" rx="6" fill="currentColor" fill-opacity="0.06"/>
          <!-- Node 1: Rect top-left -->
          <rect x="2" y="4" width="11" height="7" rx="1.8"
                stroke="currentColor" stroke-width="1.5" fill="currentColor" fill-opacity="0.08"/>
          <!-- Node 2: Circle top-right -->
          <circle cx="21.5" cy="7.5" r="4.5"
                  stroke="currentColor" stroke-width="1.5" fill="currentColor" fill-opacity="0.06"/>
          <!-- Connector 1→2 -->
          <line x1="13.5" y1="7.5" x2="16.5" y2="7.5"
                stroke="currentColor" stroke-width="1" stroke-dasharray="2,1.5" opacity="0.6"/>
          <polygon points="16.5,6 19.5,7.5 16.5,9" fill="currentColor" opacity="0.65"/>
          <!-- Node 3: Rect bottom-center -->
          <rect x="7" y="17.5" width="12" height="7" rx="1.8"
                stroke="currentColor" stroke-width="1.5" fill="currentColor" fill-opacity="0.06"/>
          <!-- Connector 1→3 -->
          <line x1="7" y1="12" x2="10" y2="17.5"
                stroke="currentColor" stroke-width="1" stroke-dasharray="2,1.5" opacity="0.5"/>
          <!-- Connector 2→3 -->
          <line x1="20" y1="13" x2="18" y2="17.5"
                stroke="currentColor" stroke-width="1" stroke-dasharray="2,1.5" opacity="0.5"/>
          <!-- Pencil — bottom-right -->
          <g transform="translate(24,23) rotate(-42)">
            <rect x="-1.6" y="-7" width="3.2" height="2" rx="0.5" fill="currentColor" opacity="0.65"/>
            <rect x="-1.6" y="-5" width="3.2" height="6" rx="0.5" fill="currentColor" opacity="0.45"/>
            <polygon points="-1.6,1 1.6,1 0,5" fill="currentColor" opacity="0.75"/>
          </g>
        </svg>
        <span class="nav-brand-name">SystemSketch</span>
      </div>

      <div class="nav-actions">
        <button @click.stop="showCreateModal = true" class="create-btn">
          <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
            <line x1="6.5" y1="1" x2="6.5" y2="12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="1" y1="6.5" x2="12" y2="6.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          New room
        </button>

        <template v-if="authStore.isAuthenticated">
          <div class="user-menu-wrap" @click.stop>
            <button class="user-chip" :class="{ open: userDropdownOpen }" @click="userDropdownOpen = !userDropdownOpen">
              <div class="user-avatar">{{ (authStore.user?.username?.[0] || '?').toUpperCase() }}</div>
              <span class="user-chip-name">{{ authStore.user?.username }}</span>
              <svg class="chevron" width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <Transition name="dropdown">
              <div v-if="userDropdownOpen" class="user-dropdown">
                <div class="dropdown-header">
                  <p class="dropdown-name">{{ authStore.user?.username }}</p>
                  <p class="dropdown-email">{{ authStore.user?.email }}</p>
                </div>
                <div class="dropdown-divider"></div>
                <button class="dropdown-item danger" @click="handleLogout">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M5 2H2v10h3M9 10l3-3-3-3M12 7H5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  Sign out
                </button>
              </div>
            </Transition>
          </div>
        </template>
        <template v-else>
          <router-link to="/login" class="nav-signin">Sign in</router-link>
        </template>
      </div>
    </nav>

    <!-- Page Body -->
    <main class="rooms-body">
      <div class="page-hero">
        <h1 class="page-title">{{ authStore.isAuthenticated ? 'Your rooms' : 'Public rooms' }}</h1>
        <p class="page-sub">{{ authStore.isAuthenticated ? 'All your collaborative workspaces in one place.' : 'Explore shared workspaces. Sign in to create your own.' }}</p>
      </div>

      <div v-if="loading" class="rooms-grid">
        <div v-for="n in 6" :key="n" class="skeleton-card"></div>
      </div>

      <div v-else-if="loadError" class="error-state">
        <p class="empty-desc">{{ loadError }}</p>
        <button class="empty-cta" @click="loadRooms">Try again</button>
      </div>

      <div v-else-if="displayRooms.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg width="52" height="52" viewBox="0 0 52 52" fill="none">
            <rect x="6" y="6" width="18" height="18" stroke="currentColor" stroke-width="2" stroke-dasharray="4 3"/>
            <rect x="28" y="6" width="18" height="18" stroke="currentColor" stroke-width="2" stroke-dasharray="4 3"/>
            <rect x="6" y="28" width="18" height="18" stroke="currentColor" stroke-width="2" stroke-dasharray="4 3"/>
            <line x1="28" y1="37" x2="46" y2="37" stroke="currentColor" stroke-width="2" stroke-dasharray="4 3"/>
            <line x1="37" y1="28" x2="37" y2="46" stroke="currentColor" stroke-width="2" stroke-dasharray="4 3"/>
          </svg>
        </div>
        <h3 class="empty-title">No rooms yet</h3>
        <p class="empty-desc">Create your first workspace to start sketching.</p>
        <button @click="showCreateModal = true" class="empty-cta">Create a room</button>
      </div>

      <div v-else class="rooms-grid">
        <div v-for="(room, idx) in displayRooms" :key="room.id"
          class="room-card" :style="{ animationDelay: `${idx * 0.05}s` }"
          @click="openRoom(room.id)">

          <div class="card-header">
            <div class="card-icon">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <rect x="1.5" y="1.5" width="6.5" height="6.5" stroke="currentColor" stroke-width="1.5"/>
                <rect x="10" y="1.5" width="6.5" height="6.5" stroke="currentColor" stroke-width="1.5" fill="currentColor" fill-opacity="0.1"/>
                <rect x="1.5" y="10" width="6.5" height="6.5" stroke="currentColor" stroke-width="1.5" fill="currentColor" fill-opacity="0.06"/>
                <line x1="10" y1="13.25" x2="16.5" y2="13.25" stroke="currentColor" stroke-width="1.5"/>
                <line x1="13.25" y1="10" x2="13.25" y2="16.5" stroke="currentColor" stroke-width="1.5"/>
              </svg>
            </div>
            <div class="card-header-right">
              <span class="card-vis-badge" :class="room.is_public ? 'public' : 'private'" :title="room.is_public ? 'Public — anyone can view' : 'Private — invite only'">
                <!-- Globe (public) -->
                <svg v-if="room.is_public" width="10" height="10" viewBox="0 0 10 10" fill="none">
                  <circle cx="5" cy="5" r="4" stroke="currentColor" stroke-width="1.3"/>
                  <path d="M1 5h8M5 1c-1 1.4-1.5 2.8-1.5 4s.5 2.6 1.5 4M5 1c1 1.4 1.5 2.8 1.5 4S6 7.6 5 9" stroke="currentColor" stroke-width="1.3"/>
                </svg>
                <!-- Lock (private) -->
                <svg v-else width="10" height="10" viewBox="0 0 10 10" fill="none">
                  <rect x="2" y="4.5" width="6" height="5" rx="1" stroke="currentColor" stroke-width="1.3"/>
                  <path d="M3.5 4.5V3a1.5 1.5 0 013 0v1.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                </svg>
                {{ room.is_public ? 'Public' : 'Private' }}
              </span>
              <span class="card-badge owner" v-if="room.is_owner">Owner</span>
              <span class="card-badge guest" v-else-if="room.user_permission">{{ room.user_permission }}</span>
              <div v-if="room.is_owner && authStore.isAuthenticated" class="card-menu-wrap" @click.stop>
                <button class="card-menu-btn" :class="{ active: openMenuId === room.id }"
                  @click="toggleCardMenu(room.id)" title="Room options">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <circle cx="7" cy="2.5" r="1.2" fill="currentColor"/>
                    <circle cx="7" cy="7" r="1.2" fill="currentColor"/>
                    <circle cx="7" cy="11.5" r="1.2" fill="currentColor"/>
                  </svg>
                </button>
                <Transition name="dropdown">
                  <div v-if="openMenuId === room.id" class="card-dropdown">
                    <button class="card-dd-item" @click.stop="toggleVisibility(room)">
                      <!-- Globe (make public) -->
                      <svg v-if="!room.is_public" width="13" height="13" viewBox="0 0 13 13" fill="none">
                        <circle cx="6.5" cy="6.5" r="5" stroke="currentColor" stroke-width="1.3"/>
                        <path d="M1.5 6.5h10M6.5 1.5c-1.2 1.7-1.8 3.3-1.8 5s.6 3.3 1.8 5M6.5 1.5c1.2 1.7 1.8 3.3 1.8 5s-.6 3.3-1.8 5" stroke="currentColor" stroke-width="1.3"/>
                      </svg>
                      <!-- Lock (make private) -->
                      <svg v-else width="13" height="13" viewBox="0 0 13 13" fill="none">
                        <rect x="2.5" y="6" width="8" height="6.5" rx="1.3" stroke="currentColor" stroke-width="1.3"/>
                        <path d="M4.5 6V4a2 2 0 014 0v2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                      </svg>
                      {{ room.is_public ? 'Make private' : 'Make public' }}
                    </button>
                    <div class="card-dd-divider"></div>
                    <button class="card-dd-item" @click.stop="startRename(room)">
                      <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                        <path d="M8.5 1.5l3 3-7 7H1.5v-3l7-7z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
                      </svg>
                      Rename
                    </button>
                    <div class="card-dd-divider"></div>
                    <button class="card-dd-item danger" @click.stop="startDelete(room)">
                      <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                        <path d="M2 3.5h9M4.5 3.5V2h4v1.5M5 6v4M8 6v4M3 3.5l.5 7h6l.5-7" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      Delete
                    </button>
                  </div>
                </Transition>
              </div>
            </div>
          </div>

          <h3 class="card-name">{{ room.name }}</h3>
          <p class="card-date">{{ formatDate(room.created_at) }}</p>
          <div class="card-arrow">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
      </div>
    </main>

    <!-- Create Room Modal -->
    <Transition name="modal">
      <div v-if="showCreateModal" class="modal-backdrop" @click.self="showCreateModal = false">
        <div class="modal-box">
          <div class="modal-top">
            <h2 class="modal-title">New room</h2>
            <button class="modal-close" @click="showCreateModal = false">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M3 3l10 10M13 3L3 13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <p class="modal-desc">Give your workspace a clear, descriptive name.</p>

          <!-- Visibility toggle -->
          <div class="modal-vis-toggle">
            <button class="vis-opt" :class="{ active: newRoomIsPublic }" @click="newRoomIsPublic = true" type="button">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <circle cx="7" cy="7" r="5.5" stroke="currentColor" stroke-width="1.5"/>
                <path d="M1.5 7h11M7 1.5c-1.5 2-2.2 3.7-2.2 5.5S5.5 10.5 7 12.5M7 1.5c1.5 2 2.2 3.7 2.2 5.5S8.5 10.5 7 12.5" stroke="currentColor" stroke-width="1.5"/>
              </svg>
              Public
            </button>
            <button class="vis-opt" :class="{ active: !newRoomIsPublic }" @click="newRoomIsPublic = false" type="button">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <rect x="3" y="7" width="8" height="6" rx="1.3" stroke="currentColor" stroke-width="1.5"/>
                <path d="M5 7V5a2 2 0 014 0v2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              Private
            </button>
          </div>
          <p class="vis-hint">
            <template v-if="newRoomIsPublic">Anyone can discover and view this workspace.</template>
            <template v-else>Only you and people you invite can access this workspace.</template>
          </p>

          <input v-model="newRoomName" type="text" class="modal-input"
            placeholder="e.g. Product Architecture v2"
            @keyup.enter="createRoom" autofocus maxlength="100"/>
          <div class="modal-actions">
            <button @click="showCreateModal = false" class="btn-ghost">Cancel</button>
            <button @click="createRoom" class="btn-primary" :disabled="!newRoomName.trim() || creating">
              {{ creating ? 'Creating…' : 'Create room' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Rename Room Modal -->
    <Transition name="modal">
      <div v-if="showRenameModal" class="modal-backdrop" @click.self="showRenameModal = false">
        <div class="modal-box">
          <div class="modal-top">
            <h2 class="modal-title">Rename room</h2>
            <button class="modal-close" @click="showRenameModal = false">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M3 3l10 10M13 3L3 13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <p class="modal-desc">Enter a new name for <strong>{{ renameTarget?.name }}</strong>.</p>
          <input v-model="renameValue" ref="renameInputRef" type="text" class="modal-input"
            placeholder="Room name" @keyup.enter="confirmRename" maxlength="100"/>
          <div class="modal-actions">
            <button @click="showRenameModal = false" class="btn-ghost">Cancel</button>
            <button @click="confirmRename" class="btn-primary"
              :disabled="!renameValue.trim() || renameValue.trim() === renameTarget?.name || renaming">
              {{ renaming ? 'Saving…' : 'Save name' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Delete Confirm Modal -->
    <Transition name="modal">
      <div v-if="showDeleteModal" class="modal-backdrop" @click.self="showDeleteModal = false">
        <div class="modal-box modal-box--danger">
          <div class="modal-top">
            <h2 class="modal-title">Delete room?</h2>
            <button class="modal-close" @click="showDeleteModal = false">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M3 3l10 10M13 3L3 13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <p class="modal-desc"><strong>{{ deleteTarget?.name }}</strong> will be permanently deleted. This cannot be undone.</p>
          <div class="modal-actions">
            <button @click="showDeleteModal = false" class="btn-ghost">Cancel</button>
            <button @click="confirmDelete" class="btn-danger" :disabled="deleting">
              {{ deleting ? 'Deleting…' : 'Delete room' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toastMsg" class="toast" :class="toastKind">{{ toastMsg }}</div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRoomStore } from '@/stores/room'
import type { Room } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const roomStore = useRoomStore()

const loading = ref(true)
const loadError = ref('')

const displayRooms = computed(() =>
  authStore.isAuthenticated ? roomStore.myRooms : roomStore.publicRooms
)

onMounted(loadRooms)

async function loadRooms() {
  loading.value = true
  loadError.value = ''
  try {
    if (authStore.isAuthenticated) {
      await roomStore.loadMyRooms()
    } else {
      await roomStore.loadPublicRooms()
    }
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    loadError.value = err?.response?.data?.detail || 'Failed to load rooms'
  } finally {
    loading.value = false
  }
}

function openRoom(roomId: string) {
  router.push({ name: 'workspace', params: { roomId } })
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

// User dropdown
const userDropdownOpen = ref(false)

async function handleLogout() {
  userDropdownOpen.value = false
  await authStore.logout()
  router.push({ name: 'home' })
}

// Card menus
const openMenuId = ref<string | null>(null)

function toggleCardMenu(roomId: string) {
  openMenuId.value = openMenuId.value === roomId ? null : roomId
}

function closeAllMenus() {
  openMenuId.value = null
  userDropdownOpen.value = false
}

// Create room
const showCreateModal = ref(false)
const newRoomName = ref('')
const newRoomIsPublic = ref(true)
const creating = ref(false)

async function createRoom() {
  if (!newRoomName.value.trim()) return
  creating.value = true
  try {
    const room = await roomStore.createRoom(newRoomName.value.trim(), newRoomIsPublic.value)
    showCreateModal.value = false
    newRoomName.value = ''
    newRoomIsPublic.value = true
    router.push({ name: 'workspace', params: { roomId: room.id } })
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    showToast(err?.response?.data?.detail || 'Failed to create room', 'error')
  } finally {
    creating.value = false
  }
}

// Toggle room visibility
async function toggleVisibility(room: Room) {
  openMenuId.value = null
  try {
    await roomStore.toggleVisibility(room.id, !room.is_public)
    showToast(room.is_public ? 'Room is now private' : 'Room is now public', 'success')
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    showToast(err?.response?.data?.detail || 'Failed to update visibility', 'error')
  }
}

// Rename room
const showRenameModal = ref(false)
const renameTarget = ref<Room | null>(null)
const renameValue = ref('')
const renaming = ref(false)
const renameInputRef = ref<HTMLInputElement | null>(null)

function startRename(room: Room) {
  openMenuId.value = null
  renameTarget.value = room
  renameValue.value = room.name
  showRenameModal.value = true
  nextTick(() => renameInputRef.value?.select())
}

async function confirmRename() {
  if (!renameTarget.value || !renameValue.value.trim()) return
  renaming.value = true
  try {
    await roomStore.renameRoom(renameTarget.value.id, renameValue.value.trim())
    showRenameModal.value = false
    showToast('Room renamed', 'success')
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    showToast(err?.response?.data?.detail || 'Failed to rename room', 'error')
  } finally {
    renaming.value = false
  }
}

// Delete room
const showDeleteModal = ref(false)
const deleteTarget = ref<Room | null>(null)
const deleting = ref(false)

function startDelete(room: Room) {
  openMenuId.value = null
  deleteTarget.value = room
  showDeleteModal.value = true
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await roomStore.deleteRoom(deleteTarget.value.id)
    showDeleteModal.value = false
    showToast('Room deleted', 'success')
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    showToast(err?.response?.data?.detail || 'Failed to delete room', 'error')
  } finally {
    deleting.value = false
  }
}

// Toast
const toastMsg = ref('')
const toastKind = ref<'success' | 'error'>('success')
let toastTimer: ReturnType<typeof setTimeout> | null = null

function showToast(msg: string, kind: 'success' | 'error' = 'success') {
  if (toastTimer) clearTimeout(toastTimer)
  toastMsg.value = msg
  toastKind.value = kind
  toastTimer = setTimeout(() => { toastMsg.value = '' }, 3200)
}
</script>

<style scoped>
.rooms-page {
  display: flex; flex-direction: column;
  width: 100vw; min-height: 100vh;
  background: var(--color-paper);
}

/* Top Nav */
.top-nav {
  position: sticky; top: 0; z-index: 50;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 32px; height: 60px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}
.nav-brand { display: flex; align-items: center; gap: 10px; }
.nav-logo { color: var(--color-accent); }
.nav-brand-name {
  font-family: var(--font-display); font-size: 18px; font-weight: 500;
  color: var(--color-ink); letter-spacing: -0.02em;
}
.nav-actions { display: flex; align-items: center; gap: 12px; }
.create-btn {
  display: inline-flex; align-items: center; gap: 7px;
  background: var(--color-accent); color: #fff;
  border: none; border-radius: var(--radius-sm);
  padding: 8px 16px; font-family: var(--font-ui); font-size: 13px; font-weight: 600;
  cursor: pointer; transition: background 0.2s, transform 0.15s; box-shadow: var(--shadow-sm);
}
.create-btn:hover { background: var(--color-accent-hover); transform: translateY(-1px); }
.nav-signin { font-size: 14px; font-weight: 500; color: var(--color-accent); text-decoration: none; }
.nav-signin:hover { color: var(--color-accent-hover); }

/* User chip + dropdown */
.user-menu-wrap { position: relative; }
.user-chip {
  display: flex; align-items: center; gap: 8px;
  padding: 4px 10px 4px 4px;
  background: var(--color-paper); border: 1px solid var(--color-border);
  border-radius: var(--radius-full); cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.user-chip:hover, .user-chip.open { border-color: var(--color-border-hover); background: var(--color-surface); }
.user-avatar {
  width: 26px; height: 26px; border-radius: 50%;
  background: var(--color-accent); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; font-family: var(--font-ui); flex-shrink: 0;
}
.user-chip-name { font-size: 13px; font-weight: 500; color: var(--color-ink); max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.chevron { color: var(--color-ink-muted); transition: transform 0.2s; }
.user-chip.open .chevron { transform: rotate(180deg); }

.user-dropdown {
  position: absolute; top: calc(100% + 8px); right: 0; min-width: 200px;
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); box-shadow: var(--shadow-lg); overflow: hidden; z-index: 200;
}
.dropdown-header { padding: 12px 16px 10px; }
.dropdown-name { font-size: 13px; font-weight: 600; color: var(--color-ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.dropdown-email { font-size: 12px; color: var(--color-ink-muted); margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.dropdown-divider { height: 1px; background: var(--color-border); }
.dropdown-item {
  display: flex; align-items: center; gap: 10px;
  width: 100%; padding: 10px 16px; background: none; border: none;
  font-family: var(--font-ui); font-size: 13px; font-weight: 500; color: var(--color-ink);
  cursor: pointer; text-align: left; transition: background 0.12s;
}
.dropdown-item:hover { background: var(--color-paper); }
.dropdown-item.danger { color: #C0431F; }
.dropdown-item.danger:hover { background: rgba(192,67,31,0.06); }

/* Page body */
.rooms-body { flex: 1; padding: 40px 48px 80px; overflow-y: auto; }
.page-hero { margin-bottom: 36px; animation: fadeUp 0.45s var(--ease-out); }
@keyframes fadeUp { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }
.page-title { font-family: var(--font-display); font-size: 32px; font-weight: 400; color: var(--color-ink); letter-spacing: -0.03em; margin-bottom: 6px; }
.page-sub { font-size: 14px; color: var(--color-ink-muted); }

/* Grid */
.rooms-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 18px; }

/* Cards */
.room-card {
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); padding: 20px 22px;
  cursor: pointer; position: relative;
  transition: transform 0.2s var(--ease-out), box-shadow 0.2s, border-color 0.2s;
  animation: cardIn 0.38s var(--ease-out) backwards;
  display: flex; flex-direction: column; gap: 5px;
}
@keyframes cardIn { from { opacity:0; transform:translateY(10px) } to { opacity:1; transform:translateY(0) } }
.room-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); border-color: var(--color-border-hover); }
.room-card:hover .card-arrow { opacity: 1; transform: translateX(0); }

.card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.card-icon { color: var(--color-accent); flex-shrink: 0; }
.card-header-right { display: flex; align-items: center; gap: 6px; }
.card-vis-badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 10px; font-weight: 600; padding: 2px 7px; border-radius: var(--radius-full);
  font-family: var(--font-ui); letter-spacing: 0.01em;
}
.card-vis-badge.public { background: #E8F4EC; color: var(--color-sage); }
.card-vis-badge.private { background: #FDF3E5; color: #A05C00; }

/* Visibility toggle in create modal */
.modal-vis-toggle {
  display: flex; gap: 8px; margin-bottom: 10px;
}
.vis-opt {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 7px;
  padding: 9px 12px; border-radius: var(--radius-sm);
  border: 1.5px solid var(--color-border); background: var(--color-paper);
  font-family: var(--font-ui); font-size: 13px; font-weight: 500; color: var(--color-ink-muted);
  cursor: pointer; transition: border-color 0.15s, background 0.15s, color 0.15s;
}
.vis-opt:hover { border-color: var(--color-border-hover); }
.vis-opt.active { border-color: var(--color-accent); background: var(--color-accent-dim); color: var(--color-accent); }
.vis-hint { font-size: 12px; color: var(--color-ink-muted); margin-bottom: 20px; line-height: 1.5; }

.card-badge { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: var(--radius-full); font-family: var(--font-ui); }
.card-badge.owner { background: var(--color-accent-dim); color: var(--color-accent); }
.card-badge.guest { background: #FDF3E5; color: #A05C00; }

.card-menu-wrap { position: relative; }
.card-menu-btn {
  display: flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; border: 1px solid transparent;
  border-radius: var(--radius-xs); background: transparent; color: var(--color-ink-muted);
  cursor: pointer; transition: background 0.12s, border-color 0.12s, color 0.12s;
}
.card-menu-btn:hover, .card-menu-btn.active { background: var(--color-paper); border-color: var(--color-border); color: var(--color-ink); }

.card-dropdown {
  position: absolute; top: calc(100% + 6px); right: 0; min-width: 148px;
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); box-shadow: var(--shadow-lg); overflow: hidden; z-index: 100;
}
.card-dd-item {
  display: flex; align-items: center; gap: 9px;
  width: 100%; padding: 9px 14px; background: none; border: none;
  font-family: var(--font-ui); font-size: 13px; font-weight: 500; color: var(--color-ink);
  cursor: pointer; text-align: left; transition: background 0.12s;
}
.card-dd-item:hover { background: var(--color-paper); }
.card-dd-item.danger { color: #C0431F; }
.card-dd-item.danger:hover { background: rgba(192,67,31,0.06); }
.card-dd-divider { height: 1px; background: var(--color-border); margin: 2px 0; }

.card-name { font-family: var(--font-display); font-size: 16px; font-weight: 500; color: var(--color-ink); letter-spacing: -0.02em; line-height: 1.3; }
.card-date { font-size: 11px; color: var(--color-ink-subtle); font-family: var(--font-mono); margin-top: 2px; }
.card-arrow { position: absolute; bottom: 18px; right: 18px; color: var(--color-accent); opacity: 0; transform: translateX(-4px); transition: opacity 0.2s, transform 0.2s; }

/* Skeleton */
.skeleton-card { height: 120px; background: linear-gradient(90deg, var(--color-border) 25%, var(--color-paper) 50%, var(--color-border) 75%); background-size: 200% 100%; border-radius: var(--radius-md); animation: shimmer 1.5s infinite; }
@keyframes shimmer { 0% { background-position: 200% 0 } 100% { background-position: -200% 0 } }

/* Empty / error */
.empty-state, .error-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 40px; text-align: center; gap: 12px; }
.empty-icon { color: var(--color-ink-subtle); margin-bottom: 8px; }
.empty-title { font-family: var(--font-display); font-size: 22px; font-weight: 400; color: var(--color-ink); letter-spacing: -0.02em; }
.empty-desc { font-size: 14px; color: var(--color-ink-muted); max-width: 300px; }
.empty-cta { margin-top: 8px; background: none; border: 1.5px solid var(--color-accent); border-radius: var(--radius-sm); color: var(--color-accent); padding: 9px 20px; font-family: var(--font-ui); font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.15s; }
.empty-cta:hover { background: var(--color-accent-dim); }

/* Modals */
.modal-backdrop { position: fixed; inset: 0; background: rgba(26,22,18,0.5); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 24px; }
.modal-box { background: var(--color-surface); border-radius: var(--radius-lg); padding: 32px; width: 100%; max-width: 460px; box-shadow: var(--shadow-xl); border: 1px solid var(--color-border); }
.modal-box--danger { border-color: rgba(192,67,31,0.3); }
.modal-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.modal-title { font-family: var(--font-display); font-size: 22px; font-weight: 400; color: var(--color-ink); letter-spacing: -0.03em; }
.modal-close { width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; background: none; border: 1px solid var(--color-border); border-radius: var(--radius-xs); color: var(--color-ink-muted); cursor: pointer; transition: border-color 0.15s, background 0.15s; }
.modal-close:hover { border-color: var(--color-border-hover); background: var(--color-paper); }
.modal-desc { font-size: 14px; color: var(--color-ink-muted); margin-bottom: 20px; line-height: 1.5; }
.modal-desc strong { color: var(--color-ink); font-weight: 600; }
.modal-input { width: 100%; background: var(--color-paper); border: 1.5px solid var(--color-border); border-radius: var(--radius-sm); color: var(--color-ink); font-family: var(--font-ui); font-size: 15px; padding: 11px 14px; outline: none; box-sizing: border-box; transition: border-color 0.2s, box-shadow 0.2s; margin-bottom: 24px; }
.modal-input:focus { border-color: var(--color-accent); box-shadow: 0 0 0 3px var(--color-accent-dim); }
.modal-input::placeholder { color: var(--color-ink-subtle); }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; }
.btn-ghost { background: none; border: 1px solid var(--color-border); border-radius: var(--radius-sm); color: var(--color-ink-muted); padding: 9px 18px; font-family: var(--font-ui); font-size: 13px; font-weight: 500; cursor: pointer; transition: border-color 0.15s, background 0.15s; }
.btn-ghost:hover { border-color: var(--color-border-hover); background: var(--color-paper); }
.btn-primary { background: var(--color-accent); color: #fff; border: none; border-radius: var(--radius-sm); padding: 9px 18px; font-family: var(--font-ui); font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.2s; box-shadow: var(--shadow-sm); }
.btn-primary:hover:not(:disabled) { background: var(--color-accent-hover); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-danger { background: #C0431F; color: #fff; border: none; border-radius: var(--radius-sm); padding: 9px 18px; font-family: var(--font-ui); font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
.btn-danger:hover:not(:disabled) { background: #A33518; }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }

.modal-enter-active, .modal-leave-active { transition: opacity 0.18s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-active .modal-box, .modal-leave-active .modal-box { transition: transform 0.22s var(--ease-out); }
.modal-enter-from .modal-box, .modal-leave-to .modal-box { transform: scale(0.97) translateY(8px); }

.dropdown-enter-active, .dropdown-leave-active { transition: opacity 0.14s ease, transform 0.14s ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-4px) scale(0.98); }

/* Toast */
.toast { position: fixed; bottom: 28px; left: 50%; transform: translateX(-50%); z-index: 2000; padding: 11px 22px; border-radius: var(--radius-sm); font-family: var(--font-ui); font-size: 14px; font-weight: 500; pointer-events: none; white-space: nowrap; box-shadow: var(--shadow-lg); }
.toast.success { background: var(--color-ink); color: var(--color-paper); }
.toast.error { background: #C0431F; color: #fff; }
.toast-enter-active, .toast-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(8px); }
</style>
