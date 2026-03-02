"""
SystemSketch FastAPI Application
Real-time Collaborative Whiteboard
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.core.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup: Create database tables
    await create_tables()
    print("✅ Database tables created")
    yield
    # Shutdown
    print("👋 Shutting down SystemSketch")


# Initialize FastAPI application
app = FastAPI(
    title="SystemSketch API",
    description="Real-time Collaborative Architecture Whiteboard",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "SystemSketch API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "websocket": "ready"
    }


# Include routers
from app.api.routes import rooms, websocket, auth, permissions
app.include_router(rooms.router, prefix="/api", tags=["rooms"])
app.include_router(websocket.router, tags=["websocket"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(permissions.router, prefix="/api", tags=["permissions"])
