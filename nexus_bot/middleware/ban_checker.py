"""
Middleware для проверки банов пользователей.
Перехватывает все сообщения и проверяет, не забанен ли пользователь.
"""
from typing import Callable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from services.user_service import user_service
from config.settings import settings


class BanCheckMiddleware(BaseMiddleware):
    """Проверяет, не забанен ли пользователь."""
    
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
    
    async def __call__(
        self,
        handler: Callable,
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Обрабатывает событие."""
        # Получаем пользователя из события
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        
        if not user:
            return await handler(event, data)
        
        # Пропускаем администраторов
        if user.id in settings.admin_ids:
            return await handler(event, data)
        
        # Получаем сессию БД
        session: AsyncSession = data.get("session")
        if not session:
            # Если сессии нет в data, создаем временную
            async with self.db_session_factory() as session:
                return await self._check_ban_and_handle(handler, event, data, user.id, session)
        
        return await self._check_ban_and_handle(handler, event, data, user.id, session)
    
    async def _check_ban_and_handle(
        self,
        handler: Callable,
        event: TelegramObject,
        data: Dict[str, Any],
        tg_id: int,
        session: AsyncSession
    ) -> Any:
        """Проверяет бан и вызывает обработчик или блокирует."""
        is_banned, is_shadow_banned = await user_service.is_user_banned(session, tg_id)
        
        # Сохраняем статусы в data для использования в хендлерах
        data["user_banned"] = is_banned
        data["user_shadow_banned"] = is_shadow_banned
        
        if is_banned and not is_shadow_banned:
            # Обычный бан - пользователь видит сообщение
            if isinstance(event, Message):
                await event.answer(
                    "🚫 Вы заблокированы в этом боте.\n"
                    f"Причина: {await self._get_ban_reason(session, tg_id)}\n"
                    "Обратитесь в поддержку для разблокировки."
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "🚫 Вы заблокированы в этом боте.",
                    show_alert=True
                )
            return None
        
        if is_shadow_banned:
            # Теневой бан - пользователь не знает о блокировке
            # Просто игнорируем все его действия
            return None
        
        # Пользователь не забанен - продолжаем обработку
        return await handler(event, data)
    
    async def _get_ban_reason(self, session: AsyncSession, tg_id: int) -> str:
        """Получает причину бана."""
        from models.database import User
        from sqlalchemy import select
        
        result = await session.execute(
            select(User.ban_reason).where(User.tg_id == tg_id)
        )
        reason = result.scalar_one_or_none()
        return reason or "Не указана"


class LicenseCheckMiddleware(BaseMiddleware):
    """Проверяет наличие активной лицензии при запуске бота."""
    
    def __init__(self, license_manager):
        self.license_manager = license_manager
        self._is_checked = False
    
    async def __call__(
        self,
        handler: Callable,
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Проверяет лицензию только один раз при старте."""
        if not self._is_checked:
            session: AsyncSession = data.get("session")
            if session:
                is_valid, message = await self.license_manager.check_local_license(session)
                if not is_valid:
                    # Лицензия недействительна - логируем, но не блокируем (для разработки)
                    print(f"⚠️ WARNING: {message}")
            
            self._is_checked = True
        
        return await handler(event, data)
