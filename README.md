# SystemSketch

**Real-time Collaborative Architecture Whiteboard**

A lightweight, developer-focused web-based whiteboard for quickly visualizing system architectures with real-time collaboration.

## 🚀 Features

- **Real-time Collaboration**: Multiple users can draw simultaneously on the same canvas
- **WebSocket Synchronization**: Instant updates across all connected clients
- **Ghost Cursors**: See where other users are pointing with color-coded cursors
- **Authentication**: Optional JWT-based authentication for room ownership
- **Room Persistence**: Save and restore your architecture diagrams
- **Undo/Redo**: Full history management for your drawings
- **Permissions**: Control who can edit vs view your rooms

## 🏗️ Tech Stack

### Backend
- **FastAPI 0.110+** - Modern async Python web framework
- **SQLAlchemy 2.0** - Async ORM with PostgreSQL
- **WebSockets** - Real-time bidirectional communication
- **JWT** - Secure authentication
- **Alembic** - Database migrations

### Frontend (Coming Soon)
- **Vue.js 3** - Progressive JavaScript framework
- **Canvas API** - High-performance drawing
- **WebSocket Client** - Real-time sync

### Database
- **PostgreSQL 16** - Primary data store
- **In-memory Python dict** - Active room state (Redis-ready)

## 📦 Installation

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/Atulmishra22/SystemSketch.git
cd SystemSketch/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start PostgreSQL**
```bash
docker-compose up -d postgres
```

6. **Run database migrations**
```bash
cd backend
alembic upgrade head
```

7. **Start the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

8. **Access the API**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## 🧪 Testing

```bash
cd backend
pytest tests/ -v --cov=app
```

## 📖 API Documentation

Interactive API documentation is available at `/docs` when the server is running.

### Key Endpoints

- `POST /api/rooms` - Create a new drawing room
- `GET /api/rooms/{room_id}` - Get room details and state
- `PUT /api/rooms/{room_id}/save` - Save room to database
- `WS /ws/{room_id}` - WebSocket connection for real-time collaboration
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

## 🔒 WebSocket Message Format

```json
{
  "action": "draw",
  "shape": "rect",
  "params": {
    "x": 100,
    "y": 150,
    "width": 50,
    "height": 50,
    "color": "#2D5BFF"
  }
}
```

**Actions**: `draw`, `cursor`, `clear`, `undo`, `redo`

## 🗺️ Project Structure

```
SystemSketch/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Settings configuration
│   │   ├── api/
│   │   │   └── routes/          # API endpoints
│   │   ├── core/
│   │   │   ├── database.py      # Database setup
│   │   │   └── websocket_manager.py
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   └── utils/               # Utilities
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Test suite
│   ├── requirements.txt
│   └── .env.example
├── frontend/                    # Vue.js app (coming soon)
├── docker-compose.yml
└── README.md
```

## 🌳 Development Workflow

This project follows a **feature branch strategy**:

1. `main` - Production-ready code
2. `setup/project-structure` - Initial infrastructure
3. `feature/websocket-collaboration` - Core WebSocket functionality
4. `feature/jwt-authentication` - Authentication system
5. `feature/undo-redo-permissions` - Advanced features

### Commit Convention
- `feat:` - New features
- `fix:` - Bug fixes
- `chore:` - Infrastructure, dependencies
- `docs:` - Documentation
- `test:` - Tests

## 🎨 Design Philosophy

**Technical Brutalism meets High-Fashion Editorial**

See [frontendui.md](frontendui.md) for detailed UI/UX specifications.

## 📝 License

MIT License - see LICENSE file for details

## 👥 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 🐛 Issues

Found a bug? Please open an issue with:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details

## 📧 Contact

**Atul Mishra**
- GitHub: [@Atulmishra22](https://github.com/Atulmishra22)

---

Built with ❤️ for developers who sketch systems
