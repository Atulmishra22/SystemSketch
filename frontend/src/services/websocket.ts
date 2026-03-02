/**
 * WebSocket Service - Real-time Collaboration
 */
import type { WSMessage, WSAction, Shape, ConnectedUser, CursorPosition } from '@/types'

type MessageHandler = (message: WSMessage) => void

export class WebSocketService {
  private ws: WebSocket | null = null
  private roomId: string | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private messageHandlers: Map<WSAction | 'all', Set<MessageHandler>> = new Map()
  private isIntentionallyClosed = false

  connect(roomId: string, token?: string, username?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.roomId = roomId
      this.isIntentionallyClosed = false

      const wsUrl = import.meta.env.VITE_WS_URL || 
        (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host

      const params = new URLSearchParams()
      if (token) params.append('token', token)
      if (username) params.append('username', username)
      
      const url = `${wsUrl}/ws/${roomId}?${params.toString()}`

      try {
        this.ws = new WebSocket(url)

        this.ws.onopen = () => {
          console.log(`✅ WebSocket connected to room: ${roomId}`)
          this.reconnectAttempts = 0
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WSMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          reject(error)
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason)
          this.ws = null

          // Attempt reconnection if not intentionally closed
          if (!this.isIntentionallyClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++
            console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
            
            setTimeout(() => {
              if (this.roomId && !this.isIntentionallyClosed) {
                this.connect(this.roomId, token, username)
              }
            }, this.reconnectDelay * this.reconnectAttempts)
          }
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  disconnect(): void {
    this.isIntentionallyClosed = true
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.roomId = null
    this.messageHandlers.clear()
  }

  send(message: WSMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket not connected. Message not sent:', message)
    }
  }

  // Message handlers
  on(action: WSAction | 'all', handler: MessageHandler): void {
    if (!this.messageHandlers.has(action)) {
      this.messageHandlers.set(action, new Set())
    }
    this.messageHandlers.get(action)!.add(handler)
  }

  off(action: WSAction | 'all', handler: MessageHandler): void {
    const handlers = this.messageHandlers.get(action)
    if (handlers) {
      handlers.delete(handler)
    }
  }

  private handleMessage(message: WSMessage): void {
    // Call specific action handlers
    const actionHandlers = this.messageHandlers.get(message.action)
    if (actionHandlers) {
      actionHandlers.forEach(handler => handler(message))
    }

    // Call 'all' handlers
    const allHandlers = this.messageHandlers.get('all')
    if (allHandlers) {
      allHandlers.forEach(handler => handler(message))
    }
  }

  // Convenience methods
  drawShape(shape: Shape): void {
    this.send({ action: 'draw' as WSAction, shape })
  }

  moveCursor(x: number, y: number, userId: string): void {
    this.send({ action: 'cursor' as WSAction, userId, x, y })
  }

  clearCanvas(): void {
    this.send({ action: 'clear' as WSAction })
  }

  undo(): void {
    this.send({ action: 'undo' as WSAction })
  }

  redo(): void {
    this.send({ action: 'redo' as WSAction })
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

export const websocketService = new WebSocketService()
