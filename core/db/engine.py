"""Database engine va session boshqaruvi."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from core.config import settings
from .base import Base


# Async engine yaratish
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.LOG_LEVEL == "DEBUG",
    future=True,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Async session olish."""
    async with async_session_maker() as session:
        yield session


async def init_db() -> None:
    """Database jadvallarini yaratish."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
