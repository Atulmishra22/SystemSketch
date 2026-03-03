/**
 * HomeView Component Tests
 * Tests landing page functionality
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

// Create a mock router for the test
const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/rooms', component: { template: '<div>Rooms</div>' } },
    { path: '/login', component: { template: '<div>Login</div>' } },
  ],
})

describe('HomeView', () => {
  it('renders without crashing', () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [router],
      },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('displays main title', () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [router],
      },
    })
    const title = wrapper.find('.display-title')
    
    expect(title.exists()).toBe(true)
    expect(title.text()).toContain('SKETCH THE FUTURE')
  })

  it('has blinking cursor', () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [router],
      },
    })
    const cursor = wrapper.find('.blinking-cursor')
    
    expect(cursor.exists()).toBe(true)
    expect(cursor.text()).toBe('_')
  })

  it('displays mouse coordinates', () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [router],
      },
    })
    const coordinates = wrapper.find('.coordinates')
    
    expect(coordinates.exists()).toBe(true)
    // Default coordinates should be 0,0
    expect(coordinates.text()).toContain('0')
  })

  it('updates mouse coordinates on mousemove', async () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [router],
      },
      attachTo: document.body, // Need to attach to body for window events
    })

    // Trigger mousemove on window
    const event = new MouseEvent('mousemove', {
      clientX: 250,
      clientY: 350,
    })
    window.dispatchEvent(event)

    await wrapper.vm.$nextTick()

    const coordLabels = wrapper.findAll('.coord-label')
    expect(coordLabels[0].text()).toBe('250')
    expect(coordLabels[1].text()).toBe('350')

    wrapper.unmount()
  })

  it('has correct styling classes', () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [router],
      },
    })
    
    expect(wrapper.classes()).toContain('home-container')
  })

  it('has action zone with router links', () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [router],
      },
    })
    
    const actionZone = wrapper.find('.action-zone')
    expect(actionZone.exists()).toBe(true)
    
    const links = wrapper.findAll('.huge-link')
    expect(links).toHaveLength(2)
    expect(links[0].text()).toBe('EXPLORE ROOMS')
    expect(links[1].text()).toBe('SIGN IN')
  })
})
