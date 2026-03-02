<template>
  <div class="rooms-container">
    <header class="rooms-header">
      <h1 class="page-title">ROOMS</h1>
      <button @click="showCreateModal = true" class="create-btn">
        CREATE NEW ROOM
      </button>
    </header>

    <div class="rooms-grid" v-if="!loading">
      <div v-for="room in displayRooms" :key="room.id" class="room-card" @click="openRoom(room.id)">
        <h3 class="room-name">{{ room.name }}</h3>
        <div class="room-meta">
          <span class="meta-item">{{ formatDate(room.created_at) }}</span>
          <span v-if="room.is_owner" class="owner-badge">OWNER</span>
          <span v-else-if="room.user_permission" class="permission-badge">
            {{ room.user_permission.toUpperCase() }}
          </span>
        </div>
      </div>
    </div>

    <div v-else class="loading-state">LOADING ROOMS...</div>

    <!-- Create Room Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal-content">
        <h2 class="modal-title">NEW ROOM</h2>
        <input
          v-model="newRoomName"
          type="text"
          class="modal-input"
          placeholder="Enter room name"
          @keyup.enter="createRoom"
          autofocus
        />
        <div class="modal-actions">
          <button @click="createRoom" class="modal-btn primary" :disabled="!newRoomName.trim()">
            CREATE
          </button>
          <button @click="showCreateModal = false" class="modal-btn">CANCEL</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRoomStore } from '@/stores/room'

const router = useRouter()
const authStore = useAuthStore()
const roomStore = useRoomStore()

const showCreateModal = ref(false)
const newRoomName = ref('')
const loading = ref(true)

const displayRooms = computed(() => {
  if (authStore.isAuthenticated) {
    return roomStore.myRooms
  }
  return roomStore.publicRooms
})

onMounted(async () => {
  loading.value = true
  try {
    if (authStore.isAuthenticated) {
      await roomStore.loadMyRooms()
    } else {
      await roomStore.loadPublicRooms()
    }
  } finally {
    loading.value = false
  }
})

async function createRoom() {
  if (!newRoomName.value.trim()) return
  
  try {
    const room = await roomStore.createRoom(newRoomName.value.trim())
    showCreateModal.value = false
    newRoomName.value = ''
    router.push({ name: 'workspace', params: { roomId: room.id } })
  } catch (error) {
    console.error('Failed to create room:', error)
  }
}

function openRoom(roomId: string) {
  router.push({ name: 'workspace', params: { roomId } })
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
</script>

<style scoped>
.rooms-container {
  width: 100vw;
  height: 100vh;
  background-color: var(--color-deep-void);
  padding: 60px;
  overflow-y: auto;
}

.rooms-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 80px;
}

.page-title {
  font-family: var(--font-display);
  font-size: 96px;
  font-weight: 800;
  color: var(--color-bone);
  letter-spacing: -0.05em;
}

.create-btn {
  background-color: var(--color-neon-cobalt);
  color: var(--color-deep-void);
  border: none;
  padding: 20px 40px;
  font-family: var(--font-system);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-transform: uppercase;
}

.create-btn:hover {
  background-color: var(--color-bone);
  transform: translateX(5px);
}

.rooms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
}

.room-card {
  background-color: var(--color-muted-obsidian);
  padding: 32px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.room-card:hover {
  border-color: var(--color-neon-cobalt);
  transform: translateY(-4px);
}

.room-name {
  font-family: var(--font-system);
  font-size: 28px;
  font-weight: 600;
  color: var(--color-bone);
  margin-bottom: 16px;
  letter-spacing: -0.04em;
}

.room-meta {
  display: flex;
  gap: 16px;
  align-items: center;
}

.meta-item {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--color-bone);
  opacity: 0.5;
  text-transform: uppercase;
}

.owner-badge,
.permission-badge {
  font-family: var(--font-mono);
  font-size: 10px;
  background-color: var(--color-neon-cobalt);
  color: var(--color-deep-void);
  padding: 4px 8px;
  text-transform: uppercase;
}

.permission-badge {
  background-color: var(--color-acid-lime);
}

.loading-state {
  font-family: var(--font-mono);
  font-size: 24px;
  color: var(--color-bone);
  opacity: 0.5;
  text-align: center;
  margin-top: 100px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(8, 8, 8, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--color-muted-obsidian);
  padding: 60px;
  max-width: 600px;
  width: 90%;
}

.modal-title {
  font-family: var(--font-display);
  font-size: 48px;
  font-weight: 800;
  color: var(--color-bone);
  margin-bottom: 32px;
  letter-spacing: -0.05em;
}

.modal-input {
  width: 100%;
  background-color: transparent;
  border: none;
  border-bottom: 2px solid var(--color-bone);
  color: var(--color-bone);
  font-family: var(--font-system);
  font-size: 24px;
  padding: 16px 0;
  outline: none;
  margin-bottom: 40px;
}

.modal-input::placeholder {
  color: var(--color-bone);
  opacity: 0.3;
}

.modal-actions {
  display: flex;
  gap: 16px;
}

.modal-btn {
  flex: 1;
  background-color: transparent;
  border: 2px solid var(--color-bone);
  color: var(--color-bone);
  padding: 16px;
  font-family: var(--font-system);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-transform: uppercase;
}

.modal-btn.primary {
  background-color: var(--color-neon-cobalt);
  border-color: var(--color-neon-cobalt);
  color: var(--color-deep-void);
}

.modal-btn:hover:not(:disabled) {
  background-color: var(--color-bone);
  border-color: var(--color-bone);
  color: var(--color-deep-void);
}

.modal-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
</style>
