"""
Менеджер базы данных для NexusBot.
Предоставляет асинхронный доступ к SQLite/PostgreSQL через SQLAlchemy.
"""
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
    async_scoped_session
)
from sqlalchemy.orm import sessionmaker

from config.settings import settings
from models.database import Base


class DatabaseManager:
    """Управление подключением к базе данных."""
    
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._async_session_maker: Optional[async_sessionmaker] = None
    
    async def initialize(self) -> None:
        """Инициализация подключения к БД."""
        self._engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,  # Включить для отладки SQL запросов
            future=True
        )
        
        self._async_session_maker = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
        
        # Создание таблиц (только если они не существуют)
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Генератор сессий для dependency injection."""
        if not self._async_session_maker:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self._async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self) -> None:
        """Закрытие подключения к БД."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._async_session_maker = None
    
    @property
    def is_initialized(self) -> bool:
        """Проверяет, инициализировано ли подключение."""
        return self._engine is not None


# Глобальный экземпляр
db_manager = DatabaseManager()


# Convenience функции для быстрого доступа
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Получить сессию БД."""
    async for session in db_manager.get_session():
        yield session
