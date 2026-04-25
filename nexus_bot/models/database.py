"""
Модели данных для NexusBot.
Использует SQLAlchemy 2.0 с асинхронной поддержкой.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Integer, BigInteger, DateTime, Boolean, 
    Float, Text, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
)
import enum


class SubscriptionStatus(enum.Enum):
    """Статусы подписки."""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"
    BANNED = "banned"


class PaymentStatus(enum.Enum):
    """Статусы платежа."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )


class User(Base):
    """Модель пользователя."""
    __tablename__ = "users"
    
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    language_code: Mapped[Optional[str]] = mapped_column(String(10), default="ru")
    
    # Статусы
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    ban_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ban_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_shadow_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Реферальная система
    referrer_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), 
        nullable=True,
        index=True
    )
    referral_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    
    # Связи
    subscriptions: Mapped[List["Subscription"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    payments: Mapped[List["Payment"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    referrals: Mapped[List["User"]] = relationship(
        back_populates="referrer",
        remote_side=[id]
    )
    referrer: Mapped[Optional["User"]] = relationship(
        back_populates="referrals",
        remote_side=[referrer_id]
    )
    
    def __repr__(self) -> str:
        return f"<User(tg_id={self.tg_id}, username={self.username})>"


class Subscription(Base):
    """Модель подписки на сервис."""
    __tablename__ = "subscriptions"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    status: Mapped[SubscriptionStatus] = mapped_column(
        SQLEnum(SubscriptionStatus), 
        default=SubscriptionStatus.PENDING
    )
    
    # Тариф
    tariff_name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Период действия
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # VPN ключи (список ключей в формате JSON или текст)
    vpn_keys: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    device_limit: Mapped[int] = mapped_column(Integer, default=1)
    
    # Связи
    user: Mapped["User"] = relationship(back_populates="subscriptions")
    
    @property
    def is_active(self) -> bool:
        """Проверяет, активна ли подписка."""
        if self.status != SubscriptionStatus.ACTIVE:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def __repr__(self) -> str:
        return f"<Subscription(user_id={self.user_id}, status={self.status.value})>"


class Payment(Base):
    """Модель платежа."""
    __tablename__ = "payments"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="RUB")
    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus), 
        default=PaymentStatus.PENDING
    )
    
    # Внешний ID платежа от провайдера
    provider_payment_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Описание
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Связи
    user: Mapped["User"] = relationship(back_populates="payments")
    
    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, amount={self.amount}, status={self.status.value})>"


class LicenseKey(Base):
    """Модель лицензии для защиты продукта."""
    __tablename__ = "license_keys"
    
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Ограничения
    max_instances: Mapped[int] = mapped_column(Integer, default=1)
    current_instances: Mapped[int] = mapped_column(Integer, default=0)
    
    # Срок действия
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Владелец
    owner_tg_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<LicenseKey(key={self.key[:8]}..., active={self.is_active})>"


class AuditLog(Base):
    """Журнал аудита для отслеживания действий."""
    __tablename__ = "audit_logs"
    
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    user_tg_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    
    def __repr__(self) -> str:
        return f"<AuditLog(action={self.action}, user={self.user_tg_id})>"
