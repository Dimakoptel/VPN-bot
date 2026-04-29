"""
Основной файл запуска NexusBot.
Инициализирует бота, базу данных и регистрирует обработчики.
"""
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.settings import settings
from core.database import db_manager
from middleware.ban_checker import BanCheckMiddleware, LicenseCheckMiddleware
from licenses.manager import license_manager
from handlers import user_router, admin_router
from utils.logging_config import setup_logging, get_logger
from utils.monitoring import monitoring_service


# Настройка логирования
logger = setup_logging()


async def on_startup(bot: Bot):
    """Выполняется при запуске бота."""
    logger.info(f"🚀 Запуск {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Запуск мониторинга
    await monitoring_service.start()
    
    # Инициализация базы данных
    await db_manager.initialize()
    logger.info("✅ База данных инициализирована")
    
    # Проверка лицензии (если настроена)
    if settings.LICENSE_KEY:
        async with db_manager.get_session() as session:
            is_valid, message = await license_manager.check_local_license(session)
            if is_valid:
                logger.info(f"✅ Лицензия действительна: {message}")
                monitoring_service.set_license_status("main", True)
            else:
                logger.warning(f"⚠️ Проблема с лицензией: {message}")
                monitoring_service.set_license_status("main", False)
    else:
        logger.info("ℹ️ Режим разработки (лицензия не установлена)")
    
    # Отправка уведомления администраторам
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(
                admin_id,
                f"✅ <b>{settings.APP_NAME}</b> запущен!\n"
                f"Версия: {settings.APP_VERSION}",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление админу {admin_id}: {e}")
            monitoring_service.inc_error("startup_notification", "bot")


async def on_shutdown(bot: Bot):
    """Выполняется при остановке бота."""
    logger.info("🛑 Остановка бота...")
    
    # Остановка мониторинга
    await monitoring_service.stop()
    
    # Закрытие подключения к БД
    await db_manager.close()
    logger.info("✅ Подключение к БД закрыто")
    
    # Уведомление администраторов
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(
                admin_id,
                f"🛑 <b>{settings.APP_NAME}</b> остановлен",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление админу {admin_id}: {e}")
    
    await bot.session.close()
    logger.info("✅ Бот полностью остановлен")


def register_handlers(dp: Dispatcher):
    """Регистрирует все обработчики."""
    dp.include_router(user_router)
    dp.include_router(admin_router)
    logger.info("✅ Обработчики зарегистрированы")


def register_middlewares(dp: Dispatcher):
    """Регистрирует middleware."""
    # Middleware для проверки банов
    ban_middleware = BanCheckMiddleware(db_manager.get_session)
    dp.message.middleware(ban_middleware)
    dp.callback_query.middleware(ban_middleware)
    
    # Middleware для проверки лицензии
    license_middleware = LicenseCheckMiddleware(license_manager)
    dp.message.middleware(license_middleware)
    dp.callback_query.middleware(license_middleware)
    
    logger.info("✅ Middleware зарегистрированы")


async def main():
    """Основная функция запуска."""
    # Создание бота
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Создание диспетчера
    dp = Dispatcher()
    
    # Регистрация обработчиков и middleware
    register_handlers(dp)
    register_middlewares(dp)
    
    # Регистрация онстартап/оншатдаун хуков
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Запуск polling
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Остановка по Ctrl+C")
    finally:
        await on_shutdown(bot)


if __name__ == "__main__":
    asyncio.run(main())
