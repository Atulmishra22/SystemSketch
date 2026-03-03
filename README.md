# SystemSketch

> **Real-time Collaborative Architecture Whiteboard** — the fastest way for developers to sketch, share, and iterate on system designs together.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D?logo=vue.js)](https://vuejs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture & Flow](#-architecture--flow)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Development](#local-development-recommended)
  - [Docker Setup](#docker-setup)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
  - [Authentication](#authentication-apiv1auth)
  - [Rooms](#rooms-apiv1rooms)
  - [Permissions](#permissions-apiv1permissions)
  - [WebSocket](#websocket-wsroom_id)
- [WebSocket Protocol](#-websocket-protocol)
- [Permission Model](#-permission-model)
- [Frontend](#-frontend)
- [Testing](#-testing)
- [Development Workflow](#-development-workflow)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🧭 Overview

SystemSketch solves a real friction point in remote technical collaboration: **existing tools like Miro and LucidChart are too heavy for a quick 5-minute system design sketch**.

SystemSketch gives developers a zero-overhead, URL-shareable whiteboard where every mouse stroke is synchronized to all participants in real time. Create a room, share the link, and start drawing — no sign-up required.

---

## 🚀 Features

| Feature | Description |
|---|---|
| **Real-time Collaboration** | Multiple users draw simultaneously on the same canvas |
| **WebSocket Sync** | Sub-100ms updates broadcast to all connected clients in a room |
| **Ghost Cursors** | Live color-coded cursors show exactly where teammates are pointing |
| **Optional Auth** | JWT-based authentication for room ownership; anonymous access supported for public rooms |
| **Room Persistence** | Save and restore canvas state to/from PostgreSQL |
| **Undo / Redo** | Full per-client history stack with server-side broadcast |
| **Granular Permissions** | `VIEWER` → `EDITOR` → `OWNER` access control per room |
| **Public / Private Rooms** | Toggle room visibility; private rooms require explicit invitation |
| **Export** | Download the canvas as a PNG for documentation |
| **Paginated Room Lists** | Browse public rooms or your own rooms with offset-based pagination |

---

## 🏗️ Tech Stack

### Backend
| Technology | Role |
|---|---|
| **FastAPI 0.110+** | Async REST + WebSocket API framework |
| **SQLAlchemy 2.0 (async)** | ORM with `asyncpg` for non-blocking DB calls |
| **Alembic** | Schema migration management |
| **Pydantic v2** | Request / response validation and serialization |
| **python-jose / passlib** | JWT signing and bcrypt password hashing |
| **PostgreSQL 16** | Persistent storage for users, rooms, permissions |
| **In-memory Python dict** | Active canvas state cache (Redis-ready drop-in) |

### Frontend
| Technology | Role |
|---|---|
| **Vue.js 3 (Composition API)** | Reactive UI framework |
| **Pinia** | Centralized state management |
| **Vue Router 4** | SPA routing |
| **HTML5 Canvas API** | High-performance drawing engine |
| **Native WebSocket** | Real-time bidirectional communication |
| **Vite** | Build tooling and dev server |

### Infrastructure
| Technology | Role |
|---|---|
| **Docker & Docker Compose** | Containerized local development |
| **PostgreSQL 16 (Alpine)** | Database container |

---

## 🔄 Architecture & Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT (Vue.js 3)                            │
│                                                                     │
│  onMouseDown / onMouseMove / onMouseUp                              │
│        │                         ▲                                  │
│        │ Local render             │ Incoming WS message             │
│        ▼                         │                                  │
│  Canvas Engine ◄──── shapes[] ───┤                                  │
│        │                         │                                  │
│        │ WebSocket send           │ shapes[] updated                │
└────────┼─────────────────────────┼────────────────────────────────-─┘
         │                         │
         ▼                         │
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                              │
│                                                                     │
│  WS /ws/{room_id}  ──► ConnectionManager.broadcast()               │
│                              │                                      │
│                        ┌─────▼──────┐                              │
│                        │ In-Memory  │  ◄── fast read/write         │
│                        │ StateStore │       for active rooms        │
│                        └─────┬──────┘                              │
│                              │  (on /save)                         │
│                        ┌─────▼──────┐                              │
│                        │ PostgreSQL │  ◄── persisted canvas state  │
│                        └────────────┘                              │
└─────────────────────────────────────────────────────────────────────┘
```

### Collaboration Step-by-Step

1. **User A** draws a rectangle — mouse events trigger a local canvas render and a WebSocket `draw` message.
2. **FastAPI** receives the message, updates the in-memory `StateStore`, and broadcasts to all other connections in the same room.
3. **User B** receives the broadcast, pushes the shape into their local `shapes[]` array, and re-renders the canvas.
4. When **User A** clicks *Save*, `PUT /rooms/{room_id}/save` persists the current `StateStore` snapshot to PostgreSQL.
5. A **new joiner** receives a `sync_state` message with the full existing canvas so they are immediately up to date.

---

## 🗺️ Project Structure

```
SystemSketch/
├── docker-compose.yml              # PostgreSQL service definition
├── README.md
├── systemsketch.md                 # Product specification
├── frontendui.md                   # UI/UX design specification
│
├── backend/
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/               # Database migration scripts
│   └── app/
│       ├── main.py                 # FastAPI app factory, router mounts
│       ├── config.py               # Pydantic settings (env vars)
│       ├── api/
│       │   ├── dependencies.py     # Auth dependency injection
│       │   └── routes/
│       │       ├── auth.py         # /api/v1/auth/*
│       │       ├── rooms.py        # /api/v1/* (rooms)
│       │       ├── permissions.py  # /api/v1/permissions/*
│       │       └── websocket.py    # /ws/{room_id}
│       ├── core/
│       │   ├── database.py         # Async SQLAlchemy engine + session
│       │   ├── state_manager.py    # In-memory canvas state store
│       │   └── websocket_manager.py # Connection pool + broadcast
│       ├── models/
│       │   ├── user.py             # User ORM model
│       │   ├── room.py             # Room ORM model
│       │   └── permission.py       # RoomPermission ORM model + PermissionLevel enum
│       ├── schemas/
│       │   ├── user.py             # UserCreate, UserResponse, Token
│       │   ├── room.py             # RoomCreate, RoomResponse, RoomState
│       │   ├── permission.py       # PermissionInvite, PermissionResponse
│       │   ├── shape.py            # Shape union type
│       │   └── websocket.py        # WS message schemas
│       └── services/
│           ├── auth_service.py     # Password hashing, JWT helpers
│           └── permission_service.py # Permission CRUD + guard logic
│
├── frontend/
│   ├── vite.config.ts
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── router/index.ts
│   │   ├── stores/
│   │   │   ├── auth.ts             # Pinia auth store
│   │   │   ├── canvas.ts           # Pinia canvas + undo/redo store
│   │   │   └── room.ts             # Pinia room list store
│   │   ├── services/
│   │   │   ├── api.ts              # Axios REST client
│   │   │   └── websocket.ts        # WS client wrapper
│   │   ├── views/
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   ├── RoomsView.vue       # Room browser
│   │   │   └── WorkspaceView.vue   # Canvas workspace
│   │   └── types/index.ts          # Shared TypeScript types
│   └── test/                       # Vitest unit tests
│
└── tests/                          # Backend pytest suite
```

---

## 🚦 Getting Started

### Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| Docker & Docker Compose | any recent | [docs.docker.com](https://docs.docker.com/get-docker/) |
| Git | any | [git-scm.com](https://git-scm.com/) |

---

### Local Development (Recommended)

#### 1. Clone the repository

```bash
git clone https://github.com/Atulmishra22/SystemSketch.git
cd SystemSketch
```

#### 2. Start PostgreSQL via Docker

```bash
docker-compose up -d postgres
```

#### 3. Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env   # Windows
cp .env.example .env     # Linux / macOS
# Edit .env — see Environment Variables section below

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Start the Vite dev server
npm run dev
```

#### 5. Verify everything is running

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health check | http://localhost:8000/health |

---

### Docker Setup

> Full Docker Compose orchestration (backend + frontend + DB) is planned for a future release. Currently only the PostgreSQL service is containerized.

```bash
# Start only the database
docker-compose up -d postgres

# Tear down
docker-compose down

# Tear down and remove volumes (wipes DB data)
docker-compose down -v
```

---

## ⚙️ Environment Variables

Create a `.env` file inside the `backend/` directory. All variables are read by `app/config.py` via Pydantic Settings.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | *(required)* | Async PostgreSQL DSN, e.g. `postgresql+asyncpg://user:pass@localhost:5432/systemsketch` |
| `SECRET_KEY` | *(required)* | 256-bit random string used to sign JWTs |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Lifetime of access tokens in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Lifetime of refresh tokens in days |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed CORS origins (JSON array) |

**Example `.env`**

```env
DATABASE_URL=postgresql+asyncpg://systemsketch:systemsketch@localhost:5432/systemsketch
SECRET_KEY=change-me-to-a-long-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256
CORS_ORIGINS=["http://localhost:5173"]
```

---

## 📖 API Reference

> Full interactive docs available at **http://localhost:8000/docs** when the server is running.
>
> All REST endpoints are prefixed with `/api/v1`.
> Authentication uses `Authorization: Bearer <access_token>` headers unless noted otherwise.

---

### Authentication — `/api/v1/auth`

#### `POST /auth/register`

Register a new user account. Returns a token pair immediately.

**Request body**
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "securepassword"
}
```

**Response `201 Created`** — `Token`
```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "alice",
    "email": "alice@example.com",
    "created_at": "2026-03-01T10:00:00Z",
    "last_login": "2026-03-01T10:00:00Z"
  }
}
```

**Errors**: `400` username or email already taken.

---

#### `POST /auth/login`

Authenticate with username **or** email and password.

**Request body**
```json
{
  "username": "alice",
  "password": "securepassword"
}
```

**Response `200 OK`** — `Token` *(same shape as register)*

**Errors**: `401` invalid credentials.

---

#### `GET /auth/me`

Get the currently authenticated user's profile.

**Headers**: `Authorization: Bearer <access_token>` *(required)*

**Response `200 OK`** — `UserResponse`
```json
{
  "id": "uuid",
  "username": "alice",
  "email": "alice@example.com",
  "created_at": "2026-03-01T10:00:00Z",
  "last_login": "2026-03-03T08:30:00Z"
}
```

**Errors**: `401` missing or invalid token.

---

#### `POST /auth/refresh`

Exchange a valid refresh token for a fresh access + refresh token pair (token rotation).

**Request body**
```json
{
  "refresh_token": "<jwt>"
}
```

**Response `200 OK`** — `Token` *(same shape as register)*

**Errors**: `401` invalid or expired refresh token.

---

### Rooms — `/api/v1`

#### `POST /rooms`

Create a new collaborative room.

- If **authenticated**: room is owned by the caller.
- If **anonymous**: room is created without an owner.

**Request body**
```json
{
  "name": "My System Design",
  "is_public": true
}
```

**Response `201 Created`** — `RoomResponse`
```json
{
  "id": "uuid",
  "name": "My System Design",
  "is_saved": false,
  "is_public": true,
  "created_at": "2026-03-03T09:00:00Z",
  "last_activity": "2026-03-03T09:00:00Z",
  "creator_id": "uuid-or-null",
  "permission_level": "public"
}
```

---

#### `GET /rooms`

List public rooms, sorted by most recent activity. Supports pagination.

**Query params**: `limit` (default `10`), `offset` (default `0`)

**Response `200 OK`** — `List[RoomResponse]`

---

#### `GET /rooms/{room_id}`

Get room metadata and the current canvas state.

- Public rooms are accessible without authentication.
- Private rooms require `VIEWER` permission or higher.

**Response `200 OK`** — `RoomState`
```json
{
  "id": "uuid",
  "name": "My System Design",
  "shapes": [
    { "type": "rect", "x": 100, "y": 150, "width": 120, "height": 60, "color": "#2D5BFF" }
  ]
}
```

**Errors**: `404` room not found, `403` access denied.

---

#### `PUT /rooms/{room_id}/save`

Persist the current in-memory canvas state to PostgreSQL. Requires `EDITOR` or `OWNER` permission.

**Request body**
```json
{
  "shapes": [ /* array of shape objects */ ]
}
```

**Response `200 OK`** — `RoomResponse`

**Errors**: `403` insufficient permission, `404` room not found.

---

#### `PATCH /rooms/{room_id}`

Rename a room. Requires `EDITOR` or `OWNER` permission.

**Request body**
```json
{
  "name": "New Room Name"
}
```

**Response `200 OK`** — `RoomResponse`

---

#### `PATCH /rooms/{room_id}/visibility`

Toggle a room between public and private. Requires `OWNER` permission.

**Request body**
```json
{
  "is_public": false
}
```

**Response `200 OK`** — `RoomResponse`

---

#### `DELETE /rooms/{room_id}`

Permanently delete a room and its canvas state. Requires `OWNER` permission and authentication.

**Response `204 No Content`**

**Errors**: `403` not the owner, `404` room not found.

---

#### `GET /users/me/rooms`

List all rooms accessible by the authenticated user (owned + explicitly shared). Supports pagination.

**Headers**: `Authorization: Bearer <access_token>` *(required)*

**Query params**: `limit` (default `50`), `offset` (default `0`)

**Response `200 OK`** — `List[RoomWithPermission]`
```json
[
  {
    "id": "uuid",
    "name": "My System Design",
    "is_saved": true,
    "is_public": false,
    "created_at": "...",
    "last_activity": "...",
    "creator_id": "uuid",
    "permission_level": "owner",
    "is_owner": true,
    "user_permission": "OWNER"
  }
]
```

---

### Permissions — `/api/v1/permissions`

All permission endpoints require authentication via `Authorization: Bearer <access_token>`.

#### `POST /permissions/rooms/{room_id}/invite`

Invite a user to a room by their username or email. Only `OWNER` can invite.

**Request body**
```json
{
  "username_or_email": "bob",
  "permission": "EDITOR"
}
```

**Response `201 Created`** — `RoomPermissionDetail`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "room_id": "uuid",
  "permission": "EDITOR",
  "user": { "username": "bob", "email": "bob@example.com" }
}
```

**Errors**: `404` target user not found, `403` caller is not the owner.

---

#### `GET /permissions/rooms/{room_id}`

List all users with access to a room. Only `OWNER` can list permissions.

**Response `200 OK`** — `List[RoomPermissionDetail]`

---

#### `PUT /permissions/rooms/{room_id}/users/{user_id}`

Update an existing user's permission level. Only `OWNER` can update.

**Request body**
```json
{
  "permission": "VIEWER"
}
```

**Response `200 OK`** — `PermissionResponse`

---

#### `DELETE /permissions/rooms/{room_id}/users/{user_id}`

Revoke a user's access to a room. Only `OWNER` can revoke.

**Response `204 No Content`**

**Errors**: `404` permission not found.

---

#### `GET /permissions/rooms/{room_id}/check`

Check the calling user's own permission level for a room.

**Response `200 OK`** — `PermissionCheck`
```json
{
  "has_access": true,
  "permission": "EDITOR",
  "is_owner": false
}
```

---

#### `GET /permissions/users/{user_id}/rooms/{room_id}`

Get a specific user's permission for a room. Accessible by the user themselves or the room owner.

**Response `200 OK`** — `PermissionResponse`

---

### WebSocket — `ws://{host}/ws/{room_id}`

**URL**: `ws://localhost:8000/ws/{room_id}`

**Optional query parameters**:

| Parameter | Description |
|---|---|
| `token` | JWT access token for authenticated sessions |
| `username` | Display name for anonymous sessions (fallback: `Anonymous`) |

**Example**
```
ws://localhost:8000/ws/my-room-uuid?token=<jwt>
ws://localhost:8000/ws/my-room-uuid?username=bob
```

---

## 🔌 WebSocket Protocol

All messages are JSON objects with an `action` discriminator field.

### Messages sent TO the server (client → server)

| Action | Description | Requires `canEdit` |
|---|---|---|
| `draw` | Add a shape to the canvas | ✅ Yes |
| `cursor` | Broadcast cursor position | No |
| `clear` | Wipe the entire canvas | ✅ Yes |
| `undo` | Undo last shape | ✅ Yes |
| `redo` | Redo last undone shape | ✅ Yes |

**`draw`**
```json
{
  "action": "draw",
  "shape": {
    "type": "rect",
    "x": 100,
    "y": 150,
    "width": 120,
    "height": 60,
    "color": "#2D5BFF"
  }
}
```

**`cursor`**
```json
{
  "action": "cursor",
  "userId": "client-uuid",
  "username": "alice",
  "color": "#FF5733",
  "x": 342.5,
  "y": 210.0
}
```

**`clear`**
```json
{ "action": "clear" }
```

**`undo` / `redo`**
```json
{ "action": "undo" }
{ "action": "redo" }
```

---

### Messages received FROM the server (server → client)

| Action | When | Description |
|---|---|---|
| `sync_state` | On connect | Full canvas snapshot for the joining client |
| `room_users` | On connect | List of all currently connected users |
| `user_joined` | When someone joins | Notifies all existing users of the new participant |
| `user_left` | When someone disconnects | Notifies remaining users |
| `draw` | When someone draws | Broadcasts the new shape to all other clients |
| `cursor` | On cursor move | Broadcasts cursor position to all other clients |
| `clear` | When canvas is cleared | Notifies all clients |
| `undo` / `redo` | On undo/redo | Updated shapes array broadcast |
| `error` | On invalid action | Error message with optional code |

**`sync_state`** *(sent to newly joined client)*
```json
{
  "action": "sync_state",
  "shapes": [ /* full array of current shapes */ ]
}
```

**`room_users`** *(sent to newly joined client)*
```json
{
  "action": "room_users",
  "users": [
    { "userId": "uuid", "username": "bob", "color": "#3498DB", "canEdit": true }
  ],
  "myUserId": "uuid",
  "myColor": "#E74C3C",
  "myUsername": "alice",
  "canEdit": true
}
```

**`user_joined`** *(broadcast to existing clients)*
```json
{
  "action": "user_joined",
  "userId": "uuid",
  "username": "alice",
  "color": "#E74C3C",
  "canEdit": true
}
```

**`error`**
```json
{
  "action": "error",
  "message": "You do not have permission to edit this room.",
  "code": "PERMISSION_DENIED"
}
```

---

## 🔐 Permission Model

SystemSketch uses a three-tier permission system stored in the `room_permissions` table.

| Level | Read | Draw / Edit | Save | Rename | Toggle Visibility | Delete | Invite / Revoke |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **VIEWER** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **EDITOR** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **OWNER** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

- The **room creator** is automatically the `OWNER`.
- **Public rooms** allow anonymous read access (via REST and WebSocket as `VIEWER`).
- **Private rooms** block all anonymous access; only users with an explicit permission row may enter.

---

## 🖥️ Frontend

The frontend is a Vue 3 SPA built with Vite.
### Running locally

```bash
cd frontend
npm install
npm run dev       # Dev server at http://localhost:5173
npm run build     # Production build → dist/
npm run test      # Run Vitest unit tests
npm run lint      # ESLint check
```

### Key views

| Route | View | Description |
|---|---|---|
| `/` | `HomeView` | Landing page |
| `/login` | `LoginView` | JWT login form |
| `/register` | `RegisterView` | User registration form |
| `/rooms` | `RoomsView` | Browse and create rooms |
| `/workspace/:id` | `WorkspaceView` | Canvas workspace with real-time collaboration |

---

## 🧪 Testing

### Backend

```bash
cd backend
# Activate virtual environment first
pytest tests/ -v --cov=app --cov-report=term-missing
```

Tests use an isolated async test client with a separate in-memory SQLite database seeded per test via fixtures in `tests/conftest.py`.

### Frontend

```bash
cd frontend
npm run test        # Run all Vitest unit tests
npm run test -- --coverage  # With coverage report
```

Test files live in `frontend/src/test/` and cover stores (`auth`, `canvas`, `room`) and key views.

---

## 🌿 Development Workflow

### Branch strategy

| Branch | Purpose |
|---|---|
| `main` | Production-ready, protected |
| `setup/project-structure` | Initial infrastructure scaffolding |
| `feature/websocket-collaboration` | Core WebSocket implementation |
| `feature/jwt-authentication` | JWT auth system |
| `feature/undo-redo-permissions` | Undo/redo and permission system |

### Commit convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short description>

[optional body]
[optional footer]
```

| Type | When to use |
|---|---|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `chore` | Build process, dependency updates, config |
| `test` | Adding or updating tests |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |

**Examples**
```
feat(rooms): add public/private visibility toggle
fix(websocket): handle disconnect before accept gracefully
docs(readme): add full API reference
test(auth): add refresh token rotation test
```

---

## 🤝 Contributing

Contributions are welcome and appreciated. Please follow these steps:

### 1. Fork & Clone

```bash
git clone https://github.com/<your-username>/SystemSketch.git
cd SystemSketch
```

### 2. Create a feature branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Set up the development environment

Follow the [Local Development](#local-development-recommended) instructions above.

### 4. Make your changes

- Keep changes focused on a single concern per PR.
- Follow the existing code style (Black + isort for Python, ESLint for TypeScript).
- Add or update tests for any changed behavior.
- Update documentation if your change affects the public API or configuration.

### 5. Run the test suite

```bash
# Backend
cd backend && pytest tests/ -v

# Frontend
cd frontend && npm run test
```

### 6. Commit and push

```bash
git add .
git commit -m "feat(scope): describe your change"
git push origin feature/your-feature-name
```

### 7. Open a Pull Request

- Target the `main` branch.
- Fill out the PR template (describe what, why, and any testing notes).
- Link any related issues.

### Code Style

| Language | Formatter | Linter |
|---|---|---|
| Python | [Black](https://black.readthedocs.io/) | [Ruff](https://docs.astral.sh/ruff/) |
| TypeScript / Vue | Prettier | ESLint |

### Reporting Bugs

Open a GitHub Issue and include:

- A clear, descriptive title.
- Steps to reproduce (ideally a minimal reproduction).
- Expected behavior vs. actual behavior.
- Environment details (OS, Python version, browser).
- Relevant logs or screenshots.

---

## 📝 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

**Atul Mishra**
- GitHub: [@Atulmishra22](https://github.com/Atulmishra22)

---

*Built with ❤️ for developers who sketch systems.*
