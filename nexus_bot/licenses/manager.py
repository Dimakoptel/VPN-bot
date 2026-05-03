"""
Система лицензирования для NexusBot.
Защищает продукт от нелегального коммерческого использования.
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import LicenseKey, AuditLog
from config.settings import settings


class LicenseError(Exception):
    """Исключение при ошибке лицензии."""


class LicenseManager:
    """Управление лицензиями продукта."""

    def __init__(self):
        self._local_license: Optional[LicenseKey] = None

    @staticmethod
    def generate_key() -> str:
        """Генерирует новый ключ лицензии."""
        # Формат: NEXUS-XXXX-XXXX-XXXX-XXXX
        parts = [secrets.token_hex(4).upper() for _ in range(4)]
        return f"NEXUS-{'-'.join(parts)}"

    @staticmethod
    def hash_key(key: str) -> str:
        """Хеширует ключ для безопасного хранения."""
        return hashlib.sha256(key.encode()).hexdigest()

    async def validate_license(
        self,
        session: AsyncSession,
        license_key: str,
        tg_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Проверяет валидность лицензии.

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        # Поиск лицензии в БД
        result = await session.execute(
            select(LicenseKey).where(LicenseKey.key == license_key)
        )
        db_license = result.scalar_one_or_none()

        if not db_license:
            await self._log_audit(
                session,
                "license_validation_failed",
                tg_id,
                f"Invalid key: {license_key[:8]}..."
            )
            return False, "Неверный ключ лицензии"

        # Проверка активности
        if not db_license.is_active:
            await self._log_audit(
                session,
                "license_deactivated",
                tg_id,
                f"Key: {license_key[:8]}..."
            )
            return False, "Лицензия деактивирована"

        # Проверка срока действия
        if db_license.expires_at and datetime.utcnow() > db_license.expires_at:
            await self._log_audit(
                session,
                "license_expired",
                tg_id,
                f"Key: {license_key[:8]}..."
            )
            return False, "Срок действия лицензии истек"

        # Проверка лимита экземпляров
        if db_license.current_instances >= db_license.max_instances:
            await self._log_audit(
                session,
                "license_limit_reached",
                tg_id,
                f"Key: {license_key[:8]}..."
            )
            return False, "Превышен лимит активаций"

        # Успешная валидация
        self._local_license = db_license
        await self._log_audit(
            session,
            "license_validated",
            tg_id,
            f"Key: {license_key[:8]}..."
        )
        return True, "Лицензия действительна"

    async def activate_license(
        self,
        session: AsyncSession,
        license_key: str,
        tg_id: int
    ) -> Tuple[bool, str]:
        """Активирует лицензию для текущего экземпляра."""
        # Валидация
        is_valid, message = await self.validate_license(session, license_key, tg_id)
        if not is_valid:
            return False, message

        # Обновление счетчика и владельца
        self._local_license.current_instances += 1
        self._local_license.owner_tg_id = tg_id
        self._local_license.activated_at = datetime.utcnow()

        await session.merge(self._local_license)
        await session.flush()

        await self._log_audit(
            session,
            "license_activated",
            tg_id,
            f"Key: {license_key[:8]}..."
        )

        return True, "Лицензия успешно активирована"

    async def check_local_license(self, session: AsyncSession) -> Tuple[bool, str]:
        """Проверяет локальную активированную лицензию."""
        if not settings.LICENSE_KEY:
            return False, "Ключ лицензии не установлен"

        return await self.validate_license(session, settings.LICENSE_KEY)

    async def _log_audit(
        self,
        session: AsyncSession,
        action: str,
        user_tg_id: Optional[int],
        details: str
    ) -> None:
        """Логирует действие в журнал аудита."""
        audit_log = AuditLog(
            action=action,
            user_tg_id=user_tg_id,
            details=details
        )
        session.add(audit_log)

    async def create_license(
        self,
        session: AsyncSession,
        duration_days: int = 365,
        max_instances: int = 1,
        owner_tg_id: Optional[int] = None
    ) -> str:
        """Создает новую лицензию (только для администратора)."""
        # Гарантируем что duration_days это int
        duration_days = int(duration_days) if duration_days else 365
        key = self.generate_key()

        license_obj = LicenseKey(
            key=key,
            is_active=True,
            max_instances=max_instances,
            current_instances=0,
            expires_at=datetime.utcnow() + timedelta(days=duration_days),
            owner_tg_id=owner_tg_id
        )

        session.add(license_obj)
        await session.flush()

        await self._log_audit(
            session,
            "license_created",
            owner_tg_id,
            f"Key: {key[:8]}..., instances: {max_instances}, days: {duration_days}"
        )

        return key


# Глобальный экземпляр
license_manager = LicenseManager()
