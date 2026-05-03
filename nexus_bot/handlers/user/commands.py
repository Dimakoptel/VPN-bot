"""
Обработчики команд пользователя.
/start, /profile, /buy, /help и другие команды для обычных пользователей.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from services.user_service import user_service
from config.settings import settings

user_router = Router(name="user")


@user_router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession):
    """Обрабатывает команду /start."""
    # Извлекаем реферальный код из аргументов (если есть)
    referrer_code = None
    if message.args:
        referrer_code = message.args[0].upper()

    # Получаем или создаем пользователя
    _ = await user_service.get_or_create_user(
        session=session,
        tg_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        language_code=message.from_user.language_code,
        referrer_code=referrer_code if referrer_code != message.from_user.username else None
    )

    # Приветственное сообщение
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"Добро пожаловать в <b>{settings.APP_NAME}</b>!\n\n"
        "Я помогу вам управлять подпиской и получить доступ к сервису.\n\n"
        "📌 Доступные команды:\n"
        "• /profile - Мой профиль\n"
        "• /buy - Купить подписку\n"
        "• /help - Помощь\n"
        "• /support - Связаться с поддержкой"
    )

    await message.answer(
        text=welcome_text,
        parse_mode="HTML"
    )


@user_router.message(Command("profile"))
async def cmd_profile(message: Message, session: AsyncSession):
    """Показывает профиль пользователя."""
    user = await user_service.get_user_by_tg_id(session, message.from_user.id)

    if not user:
        await message.answer("❌ Пользователь не найден. Используйте /start")
        return

    # Получаем количество рефералов
    referrals_count = await user_service.get_referrals_count(session, user.id)

    # Получаем активную подписку
    active_subscription = None
    for sub in user.subscriptions:
        if sub.is_active:
            active_subscription = sub
            break

    profile_text = (
        f"👤 <b>Профиль пользователя</b>\n\n"
        f"ID: <code>{user.tg_id}</code>\n"
        f"Имя: {user.first_name or 'Не указано'}\n"
        f"Реферальный код: <code>{user.referral_code}</code>\n"
        f"Приглашено друзей: {referrals_count}\n\n"
    )

    if active_subscription:
        expires = active_subscription.expires_at.strftime(
            "%d.%m.%Y %H:%M") if active_subscription.expires_at else "Бессрочно"
        profile_text += (
            f"✅ <b>Активная подписка</b>\n"
            f"Тариф: {active_subscription.tariff_name}\n"
            f"Истекает: {expires}\n"
        )
    else:
        profile_text += "❌ Нет активной подписки\n"

    await message.answer(text=profile_text, parse_mode="HTML")


@user_router.message(Command("buy"))
async def cmd_buy(message: Message):
    """Показывает информацию о покупке подписки."""
    buy_text = (
        "💳 <b>Покупка подписки</b>\n\n"
        "Выберите тариф для покупки:\n\n"
        "1️⃣ <b>Месяц</b> - 299₽\n"
        "2️⃣ <b>3 месяца</b> - 799₽ (выгода 10%)\n"
        "3️⃣ <b>6 месяцев</b> - 1499₽ (выгода 15%)\n"
        "4️⃣ <b>Год</b> - 2499₽ (выгода 30%)\n\n"
        "Нажмите на кнопку ниже, чтобы выбрать тариф."
    )

    # Здесь можно добавить InlineKeyboard с тарифами
    await message.answer(text=buy_text, parse_mode="HTML")


@user_router.message(Command("help"))
async def cmd_help(message: Message):
    """Показывает справку."""
    help_text = (
        f"ℹ️ <b>Помощь по {settings.APP_NAME}</b>\n\n"
        "<b>Команды для пользователей:</b>\n"
        "/start - Запустить бота\n"
        "/profile - Мой профиль\n"
        "/buy - Купить подписку\n"
        "/help - Эта справка\n"
        "/support - Связаться с поддержкой\n\n"
        "<b>Вопросы?</b>\n"
        f"Пишите в поддержку: {settings.SUPPORT_USERNAME}"
    )

    await message.answer(text=help_text, parse_mode="HTML")


@user_router.message(Command("support"))
async def cmd_support(message: Message):
    """Показывает контакты поддержки."""
    support_text = (
        "📞 <b>Поддержка</b>\n\n"
        f"Если у вас возникли вопросы, напишите нам:\n"
        f"👉 {settings.SUPPORT_USERNAME}\n\n"
        "Мы ответим в ближайшее время!"
    )

    await message.answer(text=support_text, parse_mode="HTML")


@user_router.callback_query(F.data == "tariff_month")
async def tariff_month_callback(callback: CallbackQuery, session: AsyncSession):
    """Обработка выбора месячного тарифа."""
    await callback.answer("Выбран тариф: 1 месяц", show_alert=True)
    # Здесь логика создания платежа


@user_router.callback_query(F.data == "tariff_3months")
async def tariff_3months_callback(callback: CallbackQuery, session: AsyncSession):
    """Обработка выбора тарифа на 3 месяца."""
    await callback.answer("Выбран тариф: 3 месяца", show_alert=True)


@user_router.callback_query(F.data == "tariff_6months")
async def tariff_6months_callback(callback: CallbackQuery, session: AsyncSession):
    """Обработка выбора тарифа на 6 месяцев."""
    await callback.answer("Выбран тариф: 6 месяцев", show_alert=True)


@user_router.callback_query(F.data == "tariff_year")
async def tariff_year_callback(callback: CallbackQuery, session: AsyncSession):
    """Обработка выбора годового тарифа."""
    await callback.answer("Выбран тариф: 1 год", show_alert=True)
