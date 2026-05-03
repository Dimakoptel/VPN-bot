"""
Мониторинг для NexusBot с использованием Prometheus.
Предоставляет метрики для отслеживания состояния бота.
"""
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    start_http_server
)

from config.settings import settings
from utils.logging_config import get_logger

logger = get_logger("monitoring")


# Метрики сообщений
MESSAGE_COUNTER = Counter(
    "nexusbot_messages_total",
    "Total number of messages processed",
    ["type", "status"]
)

# Метрики пользователей
ACTIVE_USERS_GAUGE = Gauge(
    "nexusbot_active_users",
    "Number of active users"
)

BANNED_USERS_GAUGE = Gauge(
    "nexusbot_banned_users",
    "Number of banned users"
)

# Метрики лицензий
LICENSE_STATUS_GAUGE = Gauge(
    "nexusbot_license_status",
    "License status (1=valid, 0=invalid)",
    ["license_type"]
)

# Метрики производительности
REQUEST_DURATION = Histogram(
    "nexusbot_request_duration_seconds",
    "Request duration in seconds",
    ["handler"]
)

DB_QUERY_DURATION = Histogram(
    "nexusbot_db_query_duration_seconds",
    "Database query duration in seconds",
    ["query_type"]
)

# Метрики ошибок
ERROR_COUNTER = Counter(
    "nexusbot_errors_total",
    "Total number of errors",
    ["error_type", "module"]
)

# Метрики платежей
PAYMENT_COUNTER = Counter(
    "nexusbot_payments_total",
    "Total number of payments",
    ["status", "currency"]
)

PAYMENT_AMOUNT = Summary(
    "nexusbot_payment_amount",
    "Payment amounts",
    ["currency"]
)


class MonitoringService:
    """Сервис мониторинга для NexusBot."""

    def __init__(self):
        self._server_started: bool = False
        self._port: int = settings.PROMETHEUS_PORT

    async def start(self) -> None:
        """Запуск сервера метрик Prometheus."""
        if not settings.PROMETHEUS_ENABLED:
            logger.info("ℹ️ Мониторинг Prometheus отключен")
            return

        try:
            # Запуск HTTP сервера для метрик
            start_http_server(self._port)
            self._server_started = True
            logger.info(f"✅ Сервер метрик Prometheus запущен на порту {self._port}")
            logger.info(f"📊 Метрики доступны по адресу http://localhost:{self._port}/metrics")
        except Exception as e:
            logger.error(f"❌ Ошибка запуска сервера метрик: {e}")
            raise

    async def stop(self) -> None:
        """Остановка сервера метрик."""
        if self._server_started:
            logger.info("🛑 Остановка сервера метрик Prometheus")
            # Prometheus client не предоставляет метода остановки,
            # сервер остановится вместе с приложением

    # Методы для обновления метрик

    def inc_message(self, message_type: str, status: str = "success") -> None:
        """Увеличивает счетчик сообщений."""
        MESSAGE_COUNTER.labels(type=message_type, status=status).inc()

    def set_active_users(self, count: int) -> None:
        """Устанавливает количество активных пользователей."""
        ACTIVE_USERS_GAUGE.set(count)

    def set_banned_users(self, count: int) -> None:
        """Устанавливает количество заблокированных пользователей."""
        BANNED_USERS_GAUGE.set(count)

    def set_license_status(self, license_type: str, is_valid: bool) -> None:
        """Устанавливает статус лицензии."""
        LICENSE_STATUS_GAUGE.labels(license_type=license_type).set(1 if is_valid else 0)

    def observe_request_duration(self, handler: str, duration: float) -> None:
        """Фиксирует длительность запроса."""
        REQUEST_DURATION.labels(handler=handler).observe(duration)

    def observe_db_query(self, query_type: str, duration: float) -> None:
        """Фиксирует длительность SQL запроса."""
        DB_QUERY_DURATION.labels(query_type=query_type).observe(duration)

    def inc_error(self, error_type: str, module: str) -> None:
        """Увеличивает счетчик ошибок."""
        ERROR_COUNTER.labels(error_type=error_type, module=module).inc()

    def record_payment(self, status: str, currency: str, amount: float) -> None:
        """Фиксирует платеж."""
        PAYMENT_COUNTER.labels(status=status, currency=currency).inc()
        PAYMENT_AMOUNT.labels(currency=currency).observe(amount)


# Глобальный экземпляр сервиса мониторинга
monitoring_service = MonitoringService()


async def get_monitoring_service() -> MonitoringService:
    """Получает сервис мониторинга."""
    return monitoring_service
