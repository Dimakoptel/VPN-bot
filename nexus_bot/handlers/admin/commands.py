"""
Обработчики команд администратора.
/ban, /unban, /users, /stats и другие команды для админов.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.database import User, AuditLog
from services.user_service import user_service
from config.settings import settings

admin_router = Router(name="admin")


# Фильтр для проверки прав администратора
async def admin_filter(message: Message) -> bool:
    """Проверяет, является ли пользователь администратором."""
    return message.from_user.id in settings.admin_ids


@admin_router.message(Command("ban"), admin_filter)
async def cmd_ban(message: Message, session: AsyncSession):
    """Банит пользователя."""
    # Парсинг аргументов: /ban @username причина
    args = message.text.split(maxsplit=2)
    
    if len(args) < 3:
        await message.answer(
            "❌ Использование: /ban @username или /ban user_id причина\n"
            "Пример: /ban @spammer Рассылка спама"
        )
        return
    
    target = args[1]
    reason = args[2] if len(args) > 2 else "Без причины"
    
    # Поиск пользователя
    user_to_ban = None
    if target.startswith("@"):
        username = target[1:]
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user_to_ban = result.scalar_one_or_none()
    elif target.isdigit():
        tg_id = int(target)
        user_to_ban = await user_service.get_user_by_tg_id(session, tg_id)
    
    if not user_to_ban:
        await message.answer(f"❌ Пользователь {target} не найден")
        return
    
    # Бан
    success = await user_service.ban_user(
        session=session,
        tg_id=user_to_ban.tg_id,
        reason=reason
    )
    
    if success:
        await message.answer(
            f"✅ Пользователь {user_to_ban.first_name} (@{user_to_ban.username}) забанен.\n"
            f"Причина: {reason}"
        )
        
        # Логирование
        audit_log = AuditLog(
            action="admin_ban_user",
            user_tg_id=message.from_user.id,
            details=f"Banned user {user_to_ban.tg_id}: {reason}"
        )
        session.add(audit_log)
    else:
        await message.answer("❌ Ошибка при бане пользователя")


@admin_router.message(Command("unban"), admin_filter)
async def cmd_unban(message: Message, session: AsyncSession):
    """Разбанивает пользователя."""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer(
            "❌ Использование: /unban @username или /unban user_id"
        )
        return
    
    target = args[1]
    
    # Поиск пользователя
    user_to_unban = None
    if target.startswith("@"):
        username = target[1:]
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user_to_unban = result.scalar_one_or_none()
    elif target.isdigit():
        tg_id = int(target)
        user_to_unban = await user_service.get_user_by_tg_id(session, tg_id)
    
    if not user_to_unban:
        await message.answer(f"❌ Пользователь {target} не найден")
        return
    
    # Разбан
    success = await user_service.unban_user(session=session, tg_id=user_to_unban.tg_id)
    
    if success:
        await message.answer(
            f"✅ Пользователь {user_to_unban.first_name} (@{user_to_unban.username}) разбанен."
        )
        
        # Логирование
        audit_log = AuditLog(
            action="admin_unban_user",
            user_tg_id=message.from_user.id,
            details=f"Unbanned user {user_to_unban.tg_id}"
        )
        session.add(audit_log)
    else:
        await message.answer("❌ Ошибка при разбане пользователя")


@admin_router.message(Command("users"), admin_filter)
async def cmd_users(message: Message, session: AsyncSession):
    """Показывает статистику пользователей."""
    total_users = await user_service.get_users_count(session)
    
    # Получаем всех пользователей для подсчета забаненных
    result = await session.execute(select(User))
    all_users = list(result.scalars().all())
    
    banned_count = sum(1 for u in all_users if u.is_banned)
    shadow_banned_count = sum(1 for u in all_users if u.is_shadow_banned)
    
    stats_text = (
        f"📊 <b>Статистика пользователей</b>\n\n"
        f"Всего пользователей: {total_users}\n"
        f"🚫 Забанено: {banned_count}\n"
        f"👻 Теневой бан: {shadow_banned_count}\n"
        f"✅ Активных: {total_users - banned_count - shadow_banned_count}"
    )
    
    await message.answer(text=stats_text, parse_mode="HTML")


@admin_router.message(Command("stats"), admin_filter)
async def cmd_stats(message: Message, session: AsyncSession):
    """Показывает общую статистику бота."""
    from sqlalchemy import func
    from models.database import Subscription, Payment
    
    # Подсчет пользователей
    users_count = await user_service.get_users_count(session)
    
    # Подсчет подписок
    result = await session.execute(select(func.count(Subscription.id)))
    subscriptions_count = result.scalar() or 0
    
    # Подсчет активных подписок
    result = await session.execute(
        select(func.count(Subscription.id)).where(
            Subscription.status == "active"
        )
    )
    active_subscriptions = result.scalar() or 0
    
    # Подсчет платежей
    result = await session.execute(select(func.count(Payment.id)))
    payments_count = result.scalar() or 0
    
    stats_text = (
        f"📈 <b>Статистика {settings.APP_NAME}</b>\n\n"
        f"👥 Пользователей: {users_count}\n"
        f"📦 Подписок всего: {subscriptions_count}\n"
        f"✅ Активных подписок: {active_subscriptions}\n"
        f"💳 Платежей: {payments_count}\n\n"
        f"Версия: {settings.APP_VERSION}"
    )
    
    await message.answer(text=stats_text, parse_mode="HTML")


@admin_router.message(Command("license"), admin_filter)
async def cmd_license(message: Message, session: AsyncSession):
    """Создает новый ключ лицензии."""
    from licenses.manager import license_manager
    
    args = message.text.split()
    duration_days = 365
    max_instances = 1
    
    if len(args) > 1 and args[1].isdigit():
        duration_days = int(args[1])
    
    if len(args) > 2 and args[2].isdigit():
        max_instances = int(args[2])
    
    # Создание лицензии
    new_key = await license_manager.create_license(
        session=session,
        duration_days=duration_days,
        max_instances=max_instances
    )
    
    await message.answer(
        f"✅ <b>Новый ключ лицензии создан</b>\n\n"
        f"Ключ: <code>{new_key}</code>\n"
        f"Срок действия: {duration_days} дн.\n"
        f"Макс. активаций: {max_instances}\n\n"
        f"⚠️ Сохраните этот ключ в безопасном месте!"
    )
