/**
 * SystemSketch TypeScript Type Definitions
 * Rynzhuk Edition
 */

export interface User {
  id: string
  username: string
  email: string
  created_at: string
  last_login?: string
}

export interface Room {
  id: string
  name: string
  is_saved: boolean
  created_at: string
  last_activity: string
  creator_id?: string
  permission_level: string
  user_permission?: PermissionLevel
  is_owner?: boolean
}

export enum PermissionLevel {
  OWNER = 'owner',
  EDITOR = 'editor',
  VIEWER = 'viewer',
}

export interface RoomPermission {
  id: string
  user_id: string
  room_id: string
  permission: PermissionLevel
  granted_at: string
  granted_by?: string
}

export enum ShapeType {
  RECTANGLE = 'rectangle',
  CIRCLE = 'circle',
  ARROW = 'arrow',
  TEXT = 'text',
}

export interface BaseShape {
  id: string
  type: ShapeType
  x: number
  y: number
  userId?: string
  color?: string
}

export interface Rectangle extends BaseShape {
  type: ShapeType.RECTANGLE
  width: number
  height: number
  fill?: string
  stroke?: string
  strokeWidth?: number
}

export interface Circle extends BaseShape {
  type: ShapeType.CIRCLE
  radius: number
  fill?: string
  stroke?: string
  strokeWidth?: number
}

export interface Arrow extends BaseShape {
  type: ShapeType.ARROW
  points: number[]
  stroke?: string
  strokeWidth?: number
  pointerLength?: number
  pointerWidth?: number
}

export interface TextShape extends BaseShape {
  type: ShapeType.TEXT
  text: string
  fontSize?: number
  fontFamily?: string
  fill?: string
}

export type Shape = Rectangle | Circle | Arrow | TextShape

export interface CursorPosition {
  userId: string
  username: string
  x: number
  y: number
  color: string
}

export interface ConnectedUser {
  userId: string
  username: string
  color: string
}

// WebSocket Message Types
export enum WSAction {
  SYNC_STATE = 'sync_state',
  DRAW = 'draw',
  CURSOR = 'cursor',
  CLEAR = 'clear',
  UNDO = 'undo',
  REDO = 'redo',
  USER_JOINED = 'user_joined',
  USER_LEFT = 'user_left',
  ERROR = 'error',
}

export interface WSMessage {
  action: WSAction
  [key: string]: any
}

export interface WSSyncState extends WSMessage {
  action: WSAction.SYNC_STATE
  shapes: Shape[]
}

export interface WSDraw extends WSMessage {
  action: WSAction.DRAW
  shape: Shape
}

export interface WSCursor extends WSMessage {
  action: WSAction.CURSOR
  userId: string
  x: number
  y: number
}

export interface WSUserJoined extends WSMessage {
  action: WSAction.USER_JOINED
  userId: string
  username: string
  color: string
}

export interface WSUserLeft extends WSMessage {
  action: WSAction.USER_LEFT
  userId: string
}

export interface WSError extends WSMessage {
  action: WSAction.ERROR
  message: string
  code: string
}

// Auth
export interface LoginCredentials {
  username_or_email: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
}

export interface AuthToken {
  access_token: string
  token_type: string
}

// API Response
export interface ApiError {
  detail: string
}
