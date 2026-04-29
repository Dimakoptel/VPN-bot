"""
Утилиты логирования для NexusBot.
Настраивает продвинутое логирование с ротацией файлов.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from config.settings import settings


def setup_logging() -> logging.Logger:
    """
    Настраивает логирование для приложения.
    
    Returns:
        Logger: Настроенный логгер
    """
    # Создаем директорию для логов если она не существует
    log_file_path = Path(settings.LOG_FILE)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Получаем уровень логирования
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Создаем основной логгер
    logger = logging.getLogger("nexusbot")
    logger.setLevel(log_level)
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # Форматтер для логов
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Обработчик для файла с ротацией
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Логгер для aiogram
    aiogram_logger = logging.getLogger("aiogram")
    aiogram_logger.setLevel(log_level)
    aiogram_logger.handlers.clear()
    aiogram_logger.addHandler(file_handler)
    aiogram_logger.addHandler(console_handler)
    
    # Логгер для SQLAlchemy
    sqlalchemy_logger = logging.getLogger("sqlalchemy")
    sqlalchemy_logger.setLevel(logging.WARNING)  # SQLalchemy может быть очень шумным
    sqlalchemy_logger.handlers.clear()
    sqlalchemy_logger.addHandler(file_handler)
    
    logger.info(f"📝 Логирование настроено. Уровень: {settings.LOG_LEVEL}")
    logger.info(f"📄 Файл логов: {settings.LOG_FILE}")
    logger.info(f"🔄 Максимальный размер: {settings.LOG_MAX_BYTES / 1024 / 1024:.1f} MB")
    logger.info(f"💾 Резервных копий: {settings.LOG_BACKUP_COUNT}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Получает логгер с указанным именем.
    
    Args:
        name: Имя логгера
        
    Returns:
        Logger: Логгер с указанным именем
    """
    return logging.getLogger(f"nexusbot.{name}")
