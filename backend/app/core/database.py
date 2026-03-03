"""
Async SQLAlchemy 2.0 Database Configuration
https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool
from typing import AsyncGenerator

from app.config import settings


def _build_engine():
    """Build the async engine with settings appropriate for the database backend."""
    if settings.is_sqlite:
        # SQLite: use StaticPool so the same in-memory/file connection is reused
        # across async tasks; check_same_thread=False is required by SQLite driver.
        return create_async_engine(
            settings.db_url,
            echo=settings.DEBUG,
            future=True,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    # PostgreSQL (and other networked databases)
    return create_async_engine(
        settings.db_url,
        echo=settings.DEBUG,
        future=True,
        pool_pre_ping=True,
    )


# Create async engine
engine = _build_engine()

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Modern SQLAlchemy 2.0 declarative base
class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions
    Usage: session: AsyncSession = Depends(get_async_session)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all tables in the database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Drop all tables from the database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
