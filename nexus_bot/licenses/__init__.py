"""Пакет системы лицензирования."""
from .manager import LicenseManager, LicenseError, license_manager

__all__ = [
    "LicenseManager",
    "LicenseError",
    "license_manager"
]
