"""
Сервис для работы с пользователями.
Инкапсулирует бизнес-логику управления пользователями.
"""
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import User


class UserService:
    """Сервис для управления пользователями."""

    @staticmethod
    async def get_or_create_user(
        session: AsyncSession,
        tg_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: Optional[str] = None,
        referrer_code: Optional[str] = None
    ) -> User:
        """Получает или создает пользователя."""
        # Поиск существующего
        result = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        user = result.scalar_one_or_none()

        if user:
            # Обновление данных
            if username:
                user.username = username
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if language_code:
                user.language_code = language_code
            return user

        # Создание нового
        import secrets
        user = User(
            tg_id=tg_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code or "ru",
            referral_code=f"REF_{tg_id}_{secrets.token_hex(4)}".upper(),
            referrer_id=None
        )

        # Если есть реферер
        if referrer_code:
            referrer_result = await session.execute(
                select(User).where(User.referral_code == referrer_code)
            )
            referrer = referrer_result.scalar_one_or_none()
            if referrer:
                user.referrer_id = referrer.id

        session.add(user)
        await session.flush()
        return user

    @staticmethod
    async def get_user_by_tg_id(session: AsyncSession, tg_id: int) -> Optional[User]:
        """Получает пользователя по Telegram ID."""
        result = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def ban_user(
        session: AsyncSession,
        tg_id: int,
        reason: str,
        duration_days: Optional[int] = None,
        shadow: bool = False
    ) -> bool:
        """Банит пользователя."""
        user = await UserService.get_user_by_tg_id(session, tg_id)
        if not user:
            return False

        user.is_banned = True
        user.ban_reason = reason
        user.is_shadow_banned = shadow

        if duration_days:
            user.ban_until = datetime.utcnow() + timedelta(days=duration_days)
        else:
            user.ban_until = None

        await session.flush()
        return True

    @staticmethod
    async def unban_user(session: AsyncSession, tg_id: int) -> bool:
        """Разбанивает пользователя."""
        user = await UserService.get_user_by_tg_id(session, tg_id)
        if not user:
            return False

        user.is_banned = False
        user.ban_reason = None
        user.ban_until = None
        user.is_shadow_banned = False

        await session.flush()
        return True

    @staticmethod
    async def is_user_banned(session: AsyncSession, tg_id: int) -> tuple[bool, bool]:
        """
        Проверяет, забанен ли пользователь.

        Returns:
            Tuple[bool, bool]: (is_banned, is_shadow_banned)
        """
        user = await UserService.get_user_by_tg_id(session, tg_id)
        if not user:
            return False, False

        # Проверка временного бана
        if user.ban_until and datetime.utcnow() > user.ban_until:
            await UserService.unban_user(session, tg_id)
            return False, False

        return user.is_banned, user.is_shadow_banned

    @staticmethod
    async def get_referrals_count(session: AsyncSession, user_id: int) -> int:
        """Получает количество рефералов."""
        result = await session.execute(
            select(func.count(User.id)).where(User.referrer_id == user_id)
        )
        return result.scalar() or 0

    @staticmethod
    async def get_all_users(session: AsyncSession) -> List[User]:
        """Получает всех пользователей."""
        result = await session.execute(select(User))
        return list(result.scalars().all())

    @staticmethod
    async def get_users_count(session: AsyncSession) -> int:
        """Получает общее количество пользователей."""
        result = await session.execute(select(func.count(User.id)))
        return result.scalar() or 0


# Глобальный экземпляр
user_service = UserService()
