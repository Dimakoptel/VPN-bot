"""
Конфигурация приложения NexusBot.
Использует pydantic-settings для валидации и загрузки из .env файла.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Bot Configuration
    BOT_TOKEN: str = Field(..., description="Telegram Bot Token")
    BOT_ADMIN_IDS: str = Field(..., description="Список ID администраторов через запятую")
    
    @property
    def admin_ids(self) -> List[int]:
        """Возвращает список ID администраторов как integers."""
        return [int(x.strip()) for x in self.BOT_ADMIN_IDS.split(",") if x.strip().isdigit()]

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///nexus_bot.db",
        description="URL подключения к базе данных"
    )

    # License System
    LICENSE_SERVER_URL: str | None = Field(
        default=None,
        description="URL сервера проверки лицензий"
    )
    LICENSE_KEY: str | None = Field(
        default=None,
        description="Ключ лицензии для данного экземпляра"
    )

    # Payment
    PAYMENT_PROVIDER_TOKEN: str | None = Field(
        default=None,
        description="Токен платежного провайдера"
    )
    PAYMENT_CURRENCY: str = Field(
        default="RUB",
        description="Валюта платежей"
    )

    # VPN Panel
    VPN_PANEL_URL: str = Field(
        default="http://localhost:8080",
        description="URL панели управления VPN"
    )
    VPN_PANEL_LOGIN: str = Field(
        default="admin",
        description="Логин для панели VPN"
    )
    VPN_PANEL_PASSWORD: str = Field(
        default="change_me",
        description="Пароль для панели VPN"
    )

    # App Info
    APP_NAME: str = Field(default="NexusBot", description="Название бота")
    APP_VERSION: str = Field(default="1.0.0", description="Версия бота")
    SUPPORT_USERNAME: str = Field(
        default="@nexus_support",
        description="Юзернейм поддержки"
    )

    # Redis (optional)
    REDIS_URL: str | None = Field(
        default=None,
        description="URL для Redis кэша"
    )

    @property
    def is_production(self) -> bool:
        """Проверяет, является ли окружение продакшеном."""
        return self.LICENSE_KEY is not None and len(self.LICENSE_KEY) > 10


# Глобальный экземпляр настроек
settings = Settings()
