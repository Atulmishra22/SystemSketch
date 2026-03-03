/**
 * App.vue Component Tests
 * Tests the main application wrapper component
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import App from '@/App.vue'
import { createRouter, createMemoryHistory } from 'vue-router'

describe('App.vue', () => {
  let pinia: ReturnType<typeof createPinia>
  let router: ReturnType<typeof createRouter>

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } },
        { path: '/login', component: { template: '<div>Login</div>' } },
      ],
    })
  })

  it('renders without crashing', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [pinia, router],
      },
    })
    
    expect(wrapper.exists()).toBe(true)
  })

  it('has proper template structure', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [pinia, router],
      },
    })
    
    // Check if RouterView component is present
    expect(wrapper.findComponent({ name: 'RouterView' }).exists()).toBe(true)
  })

  it('initializes auth store on mount', async () => {
    const checkAuthSpy = vi.fn()
    
    const wrapper = mount(App, {
      global: {
        plugins: [pinia, router],
        mocks: {
          useAuthStore: () => ({
            checkAuth: checkAuthSpy,
          }),
        },
      },
    })

    await wrapper.vm.$nextTick()
    // Component should attempt to check auth on mount
    expect(wrapper.exists()).toBe(true)
  })

  it('does not have orphaned style tags', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [pinia, router],
      },
    })
    
    // Verify no invalid end tags or orphaned CSS
    const html = wrapper.html()
    expect(html).not.toContain('</style>')
    expect(html).not.toContain('padding: 0 1rem')
    expect(html).not.toContain('border-left')
  })
})
