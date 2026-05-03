"""
Скрипт инициализации базы данных для NexusBot.
Создает таблицы без запуска бота.
"""
import asyncio
import logging
import sys
from pathlib import Path
from sqlalchemy import text

# Добавляем директорию nexus_bot в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "nexus_bot"))

from nexus_bot.core.database import db_manager
from nexus_bot.config.settings import settings


async def init_database():
    """Инициализация базы данных."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        logger.info("🚀 Инициализация базы данных...")
        await db_manager.initialize()
        logger.info("✅ База данных успешно инициализирована!")
        logger.info(f"📍 Файл БД: {settings.DATABASE_URL}")

        # Проверяем подключение
        # Вместо async with, используем прямой доступ к сессии
        session_maker = db_manager._async_session_maker
        if session_maker:
            async with session_maker() as session:
                # Простой запрос для проверки
                result = await session.execute(text("SELECT 1"))
                logger.info("✅ Подключение к БД проверено")

    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        raise
    finally:
        # Закрываем подключение
        if db_manager._engine:
            await db_manager._engine.dispose()
            logger.info("🔌 Подключение к БД закрыто")


if __name__ == "__main__":
    asyncio.run(init_database())