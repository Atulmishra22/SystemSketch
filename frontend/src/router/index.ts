import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/rooms',
      name: 'rooms',
      component: () => import('../views/RoomsView.vue'),
    },
    {
      path: '/workspace/:roomId',
      name: 'workspace',
      component: () => import('../views/WorkspaceView.vue'),
      props: true,
    },
  ],
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Check authentication status on first navigation
  if (!authStore.user && !authStore.loading) {
    await authStore.checkAuth()
  }

  // Redirect authenticated users away from login/register
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'rooms' })
    return
  }

  next()
})

export default router

